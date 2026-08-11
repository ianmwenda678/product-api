from fastapi import FastAPI, HTTPException, Depends, status, Request
from fastapi.responses import HTMLResponse, JSONResponse
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
# PORTFOLIO PAGE
# ============================================================
@app.get("/", response_class=HTMLResponse)
async def portfolio():
    html_content = """
<!DOCTYPE html>
<html>
<head>
    <title>Student Portfolio - Backend Assignments</title>
    <style>
        body {
            font-family: 'Segoe UI', Arial, sans-serif;
            margin: 40px;
            background: #f5f5f5;
        }
        .container {
            max-width: 900px;
            margin: 0 auto;
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        h1 {
            color: #2c3e50;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
        }
        .student-info {
            background: #e8f4fd;
            padding: 15px;
            border-radius: 8px;
            margin: 20px 0;
        }
        .student-info strong {
            color: #2c3e50;
        }
        .admission {
            font-size: 1.2em;
            color: #2980b9;
            font-weight: bold;
        }
        .assignment {
            margin: 12px 0;
            padding: 15px;
            background: #f8f9fa;
            border-radius: 8px;
            border-left: 4px solid #3498db;
            transition: all 0.3s ease;
        }
        .assignment:hover {
            background: #e8f4fd;
            transform: translateX(5px);
        }
        .assignment a {
            color: #0366d6;
            text-decoration: none;
            font-weight: 500;
            display: flex;
            align-items: center;
            flex-wrap: wrap;
        }
        .assignment a:hover {
            text-decoration: underline;
        }
        .badge {
            display: inline-block;
            background: #3498db;
            color: white;
            padding: 2px 10px;
            border-radius: 12px;
            font-size: 0.8em;
            margin-right: 10px;
            min-width: 70px;
            text-align: center;
        }
        .badge-lesson {
            background: #2c3e50;
        }
        .badge-lab {
            background: #27ae60;
        }
        .lesson-topic {
            color: #7f8c8d;
            font-size: 0.85em;
            margin-left: 10px;
        }
        .repo-link {
            font-size: 0.8em;
            color: #3498db;
            margin-left: auto;
        }
        .footer {
            margin-top: 30px;
            text-align: center;
            color: #95a5a6;
            font-size: 0.9em;
            border-top: 1px solid #ecf0f1;
            padding-top: 20px;
        }
        @media (max-width: 768px) {
            .assignment a {
                flex-direction: column;
                align-items: flex-start;
            }
            .lesson-topic {
                margin-left: 0;
                margin-top: 5px;
            }
            .repo-link {
                margin-left: 0;
                margin-top: 5px;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>📚 Backend Development Portfolio</h1>

        <div class="student-info">
            <p><strong>👨‍🎓 Student Name:</strong> Ian Mwenda</p>
            <p><strong>🎓 Admission Number:</strong> <span class="admission">C027-01-0902/2024</span></p>
            <p><strong>📧 Email:</strong> mwenda.kathenya24@students.dkut.ac.ke</p>
        </div>

        <h2>📝 Backend Assignments</h2>
        <p style="color: #7f8c8d; margin-bottom: 20px;">Click on any assignment to view the complete code on GitHub</p>

        <!-- Lesson 1 -->
        <div class="assignment">
            <a href="https://github.com/ianmwenda678/fastapi-intro" target="_blank">
                <span class="badge badge-lesson">Lesson 1</span>
                <span>HTTP & Your First API</span>
                <span class="lesson-topic">— FastAPI + Uvicorn, HTTP Methods, Status Codes</span>
                <span class="repo-link">🔗 View on GitHub</span>
            </a>
        </div>

        <!-- Lesson 2 -->
        <div class="assignment">
            <a href="https://github.com/ianmwenda678/docker-api" target="_blank">
                <span class="badge badge-lesson">Lesson 2</span>
                <span>Docker - Packaging Your API</span>
                <span class="lesson-topic">— Containers, Dockerfiles, Docker Compose</span>
                <span class="repo-link">🔗 View on GitHub</span>
            </a>
        </div>

        <!-- Lesson 3 -->
        <div class="assignment">
            <a href="https://github.com/ianmwenda678/fastapi-params" target="_blank">
                <span class="badge badge-lesson">Lesson 3</span>
                <span>Routing, Parameters & Request Bodies</span>
                <span class="lesson-topic">— Path Parameters, Query Parameters, Pydantic Validation</span>
                <span class="repo-link">🔗 View on GitHub</span>
            </a>
        </div>

        <!-- Lesson 4 -->
        <div class="assignment">
            <a href="https://github.com/ianmwenda678/library-api" target="_blank">
                <span class="badge badge-lesson">Lab 4</span>
                <span>PostgreSQL & SQLModel – Your First Database</span>
                <span class="lesson-topic">— ORM, Database Migrations, SQLModel</span>
                <span class="repo-link">🔗 View on GitHub</span>
            </a>
        </div>

        <!-- Lesson 5 -->
        <div class="assignment">
            <a href="https://github.com/ianmwenda678/bookstore-api" target="_blank">
                <span class="badge badge-lesson">Lab 5</span>
                <span>CRUD Operations</span>
                <span class="lesson-topic">— Create, Read, Update, Delete with Error Handling</span>
                <span class="repo-link">🔗 View on GitHub</span>
            </a>
        </div>

        <!-- Lesson 6 -->
        <div class="assignment">
            <a href="https://github.com/ianmwenda678/techvault-inventory-api" target="_blank">
                <span class="badge badge-lesson">Lab 6</span>
                <span>Error Handling & Validation</span>
                <span class="lesson-topic">— HTTPException, Custom Validators, Global Handlers</span>
                <span class="repo-link">🔗 View on GitHub</span>
            </a>
        </div>

        <!-- Lesson 7 -->
        <div class="assignment">
            <a href="https://github.com/ianmwenda678/healthtrack-api" target="_blank">
                <span class="badge badge-lesson">Lab 7</span>
                <span>User Authentication – JWT & Password Hashing</span>
                <span class="lesson-topic">— JWT Tokens, bcrypt, Login/Register Endpoints</span>
                <span class="repo-link">🔗 View on GitHub</span>
            </a>
        </div>

        <!-- Lesson 8 - ClinicGuard API -->
        <div class="assignment">
            <a href="https://github.com/ianmwenda678/clinicguard-api" target="_blank">
                <span class="badge badge-lab">Lab 8</span>
                <span>Authorization & Rate Limiting</span>
                <span class="lesson-topic">— RBAC, Dependency Injection, Rate Limiting</span>
                <span class="repo-link">🔗 View on GitHub</span>
            </a>
        </div>

        <!-- Lesson 9 - SendIt API -->
        <div class="assignment">
            <a href="https://github.com/ianmwenda678/sendit-api" target="_blank">
                <span class="badge badge-lab">Lab 9</span>
                <span>File Uploads & External APIs</span>
                <span class="lesson-topic">— File Validation, httpx, Environment Variables</span>
                <span class="repo-link">🔗 View on GitHub</span>
            </a>
        </div>

        <!-- Lesson 10 - Product API -->
        <div class="assignment">
            <a href="https://github.com/ianmwenda678/product-api" target="_blank">
                <span class="badge badge-lab">Lab 10</span>
                <span>Testing & Deployment (Cloud)</span>
                <span class="lesson-topic">— Pytest, CI/CD, Render Deployment</span>
                <span class="repo-link">🔗 View on GitHub</span>
            </a>
        </div>

        <div class="footer">
            <p>📍 Deployed on Render | 📅 Last Updated: August 2026</p>
            <p style="font-size: 0.8em;">⚠️ Click on any assignment link to view the complete source code on GitHub</p>
        </div>
    </div>
</body>
</html>
"""
    return HTMLResponse(content=html_content)

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
