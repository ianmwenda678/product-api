from fastapi import FastAPI
from datetime import datetime
import os

app = FastAPI(title="Product API", version="1.0.0")

@app.get("/")
def root():
    return {
        "message": "Product API is running on Render!",
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/health")
def health():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    }

@app.get("/info")
def info():
    return {
        "python_version": os.sys.version,
        "platform": os.sys.platform
    }
