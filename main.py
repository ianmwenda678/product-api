from fastapi import FastAPI, HTTPException, Depends, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy import select
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from datetime import datetime
import os
import time
import logging
from logging.handlers import RotatingFileHandler
from typing import Optional

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

start_time = time.time()

# Rate Limiting
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Logging Middleware
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

# Authentication Endpoints
@app.post("/register", status_code=201)
def register_user(
    user_data: UserCreate,
    db: Session = Depends(get_session)
):
    existing = db.execute(select(User).where(User.username == user_data.username)).scalar_one_or_none()
    if existing:
        raise HTTPException(409, "Username already exists")
    
    existing = db.execute(select(User).where(User.email == user_data.email)).scalar_one_or_none()
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
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return {"message": "User created successfully", "user": db_user}

@app.post("/login")
def login_user(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_session)
):
    user = db.execute(select(User).where(User.username == form_data.username)).scalar_one_or_none()
    if not user:
        raise HTTPException(401, "Invalid credentials")
    
    if not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(401, "Invalid credentials")
    
    if not user.is_active:
        raise HTTPException(403, "User is inactive")
    
    user.last_login = datetime.utcnow()
    db.commit()
    
    token = create_access_token({"sub": user.username})
    return {
        "access_token": token,
        "token_type": "bearer",
        "expires_in": 30 * 60,
        "username": user.username,
        "role": user.role
    }

# Product Endpoints
@app.post("/products", status_code=201)
def create_product(
    product_data: ProductCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_session)
):
    db_product = Product(
        **product_data.dict(),
        owner_id=current_user.id
    )
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

@app.get("/products")
def list_products(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_session)
):
    query = select(Product)
    if current_user.role != "admin":
        query = query.where(Product.owner_id == current_user.id)
    return db.execute(query).scalars().all()

@app.get("/products/{product_id}")
def get_product(
    product_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_session)
):
    product = db.execute(select(Product).where(Product.id == product_id)).scalar_one_or_none()
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
    db: Session = Depends(get_session)
):
    product = db.execute(select(Product).where(Product.id == product_id)).scalar_one_or_none()
    if not product:
        raise HTTPException(404, "Product not found")
    
    if current_user.role != "admin" and product.owner_id != current_user.id:
        raise HTTPException(403, "Access denied")
    
    update_data = product_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(product, key, value)
    
    product.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(product)
    return product

@app.delete("/products/{product_id}", status_code=204)
def delete_product(
    product_id: int,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_session)
):
    product = db.execute(select(Product).where(Product.id == product_id)).scalar_one_or_none()
    if not product:
        raise HTTPException(404, "Product not found")
    
    db.delete(product)
    db.commit()

# Health and Monitoring
@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0",
        "uptime": time.time() - start_time
    }

@app.get("/metrics")
def get_metrics(current_user: User = Depends(get_current_admin)):
    try:
        import psutil
        return {
            "cpu_percent": psutil.cpu_percent(),
            "memory_percent": psutil.virtual_memory().percent,
            "disk_usage": psutil.disk_usage('/').percent
        }
    except ImportError:
        return {"message": "psutil not installed"}
