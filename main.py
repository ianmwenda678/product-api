from fastapi import FastAPI, HTTPException, Depends, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session, select
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from datetime import datetime
import os
import time
import logging
from logging.handlers import RotatingFileHandler
from typing import Optional

# Import all models and modules
from database.session import get_session
from models.user import User, UserCreate, UserResponse
from models.product import Product, ProductCreate, ProductUpdate
from auth import (
    hash_password, verify_password, create_access_token,
    get_current_user, get_current_admin, get_current_active_user
)

# Configure logging
LOG_FILE = os.getenv("LOG_FILE", "app.log")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        RotatingFileHandler(LOG_FILE, maxBytes=10485760, backupCount=5),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

app = FastAPI(title="Product API", version="1.0.0")

# Start time for uptime tracking
start_time = time.time()

# ============================================================
# RATE LIMITING
# ============================================================
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# ============================================================
# LOGGING MIDDLEWARE
# ============================================================
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    logger.info(
        f"{request.method} {request.url.path} - "
        f"Status: {response.status_code} - "
        f"Time: {process_time:.3f}s"
    )
    return response

# ============================================================
# AUTHENTICATION ENDPOINTS
# ============================================================
@app.post("/register", status_code=201)
def register_user(
    user_data: UserCreate,
    session: Session = Depends(get_session)
):
    existing = session.exec(select(User).where(User.username == user_data.username)).first()
    if existing:
        raise HTTPException(409, "Username already exists")
    
    existing = session.exec(select(User).where(User.email == user_data.email)).first()
    if existing:
        raise HTTPException(409, "Email already exists")
    
    hashed = hash_password(user_data.password)
    db_user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hashed,
        full_name=user_data.full_name,
        role=user_data.role
    )
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    
    return {"message": "User created successfully", "user": db_user}

@app.post("/login")
def login_user(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: Session = Depends(get_session)
):
    user = session.exec(select(User).where(User.username == form_data.username)).first()
    if not user:
        raise HTTPException(401, "Invalid credentials")
    
    if not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(401, "Invalid credentials")
    
    if not user.is_active:
        raise HTTPException(403, "User is inactive")
    
    user.last_login = datetime.utcnow()
    session.commit()
    
    token = create_access_token({"sub": user.username})
    return {
        "access_token": token,
        "token_type": "bearer",
        "expires_in": 30 * 60,
        "username": user.username,
        "role": user.role
    }

# ============================================================
# PRODUCT ENDPOINTS
# ============================================================
@app.post("/products", status_code=201)
def create_product(
    product_data: ProductCreate,
    current_user: User = Depends(get_current_active_user),
    session: Session = Depends(get_session)
):
    db_product = Product(
        **product_data.dict(),
        owner_id=current_user.id
    )
    session.add(db_product)
    session.commit()
    session.refresh(db_product)
    return db_product

@app.get("/products")
def list_products(
    current_user: User = Depends(get_current_active_user),
    session: Session = Depends(get_session)
):
    query = select(Product)
    if current_user.role != "admin":
        query = query.where(Product.owner_id == current_user.id)
    return session.exec(query).all()

@app.get("/products/{product_id}")
def get_product(
    product_id: int,
    current_user: User = Depends(get_current_active_user),
    session: Session = Depends(get_session)
):
    product = session.get(Product, product_id)
    if not product:
        raise HTTPException(404, "Product not found")
    
    if current_user.role != "admin" and product.owner_id != current_user.id:
        raise HTTPException(403, "Access denied")
    
    return product

@app.patch("/products/{product_id}")
def update_product(
    product_id: int,
    product_update: ProductUpdate,
    current_user: User = Depends(get_current_active_user),
    session: Session = Depends(get_session)
):
    product = session.get(Product, product_id)
    if not product:
        raise HTTPException(404, "Product not found")
    
    if current_user.role != "admin" and product.owner_id != current_user.id:
        raise HTTPException(403, "Access denied")
    
    for key, value in product_update.dict(exclude_unset=True).items():
        setattr(product, key, value)
    
    product.updated_at = datetime.utcnow()
    session.commit()
    session.refresh(product)
    return product

@app.delete("/products/{product_id}", status_code=204)
def delete_product(
    product_id: int,
    current_user: User = Depends(get_current_admin),
    session: Session = Depends(get_session)
):
    product = session.get(Product, product_id)
    if not product:
        raise HTTPException(404, "Product not found")
    
    session.delete(product)
    session.commit()

# ============================================================
# HEALTH AND MONITORING ENDPOINTS
# ============================================================
@app.get("/health")
def health_check():
    """Health check endpoint for monitoring."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0",
        "uptime": time.time() - start_time
    }

@app.get("/metrics")
def get_metrics(current_user: User = Depends(get_current_admin)):
    """Metrics endpoint for monitoring (admin only)."""
    return {"message": "Metrics available only with psutil installed"}
