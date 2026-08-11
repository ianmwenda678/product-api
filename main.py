from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import HTMLResponse
from datetime import datetime
import os

app = FastAPI(title="Product API", version="1.0.0")

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
        body { font-family: 'Segoe UI', Arial, sans-serif; margin: 40px; background: #f5f5f5; }
        .container { max-width: 900px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        h1 { color: #2c3e50; border-bottom: 3px solid #3498db; padding-bottom: 10px; }
        .student-info { background: #e8f4fd; padding: 15px; border-radius: 8px; margin: 20px 0; }
        .admission { font-size: 1.2em; color: #2980b9; font-weight: bold; }
        .assignment { margin: 12px 0; padding: 15px; background: #f8f9fa; border-radius: 8px; border-left: 4px solid #3498db; }
        .assignment a { color: #0366d6; text-decoration: none; font-weight: 500; }
        .badge { display: inline-block; background: #3498db; color: white; padding: 2px 10px; border-radius: 12px; font-size: 0.8em; margin-right: 10px; min-width: 70px; text-align: center; }
        .badge-lesson { background: #2c3e50; }
        .badge-lab { background: #27ae60; }
        .lesson-topic { color: #7f8c8d; font-size: 0.85em; margin-left: 10px; }
        .repo-link { font-size: 0.8em; color: #3498db; margin-left: 10px; }
        .footer { margin-top: 30px; text-align: center; color: #95a5a6; font-size: 0.9em; border-top: 1px solid #ecf0f1; padding-top: 20px; }
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

        <div class="assignment"><a href="https://github.com/ianmwenda678/fastapi-intro" target="_blank"><span class="badge badge-lesson">Lesson 1</span> HTTP &amp; Your First API <span class="lesson-topic">— FastAPI + Uvicorn, HTTP Methods, Status Codes</span><span class="repo-link">🔗 View on GitHub</span></a></div>
        <div class="assignment"><a href="https://github.com/ianmwenda678/docker-api" target="_blank"><span class="badge badge-lesson">Lesson 2</span> Docker - Packaging Your API <span class="lesson-topic">— Containers, Dockerfiles, Docker Compose</span><span class="repo-link">🔗 View on GitHub</span></a></div>
        <div class="assignment"><a href="https://github.com/ianmwenda678/fastapi-params" target="_blank"><span class="badge badge-lesson">Lesson 3</span> Routing, Parameters &amp; Request Bodies <span class="lesson-topic">— Path Parameters, Query Parameters, Pydantic Validation</span><span class="repo-link">🔗 View on GitHub</span></a></div>
        <div class="assignment"><a href="https://github.com/ianmwenda678/library-api" target="_blank"><span class="badge badge-lab">Lab 4</span> PostgreSQL &amp; SQLModel – Your First Database <span class="lesson-topic">— ORM, Database Migrations, SQLModel</span><span class="repo-link">🔗 View on GitHub</span></a></div>
        <div class="assignment"><a href="https://github.com/ianmwenda678/bookstore-api" target="_blank"><span class="badge badge-lab">Lab 5</span> CRUD Operations <span class="lesson-topic">— Create, Read, Update, Delete with Error Handling</span><span class="repo-link">🔗 View on GitHub</span></a></div>
        <div class="assignment"><a href="https://github.com/ianmwenda678/techvault-inventory-api" target="_blank"><span class="badge badge-lab">Lab 6</span> Error Handling &amp; Validation <span class="lesson-topic">— HTTPException, Custom Validators, Global Handlers</span><span class="repo-link">🔗 View on GitHub</span></a></div>
        <div class="assignment"><a href="https://github.com/ianmwenda678/healthtrack-api" target="_blank"><span class="badge badge-lab">Lab 7</span> User Authentication – JWT &amp; Password Hashing <span class="lesson-topic">— JWT Tokens, bcrypt, Login/Register Endpoints</span><span class="repo-link">🔗 View on GitHub</span></a></div>
        <div class="assignment"><a href="https://github.com/ianmwenda678/clinicguard-api" target="_blank"><span class="badge badge-lab">Lab 8</span> Authorization &amp; Rate Limiting <span class="lesson-topic">— RBAC, Dependency Injection, Rate Limiting</span><span class="repo-link">🔗 View on GitHub</span></a></div>
        <div class="assignment"><a href="https://github.com/ianmwenda678/sendit-api" target="_blank"><span class="badge badge-lab">Lab 9</span> File Uploads &amp; External APIs <span class="lesson-topic">— File Validation, httpx, Environment Variables</span><span class="repo-link">🔗 View on GitHub</span></a></div>
        <div class="assignment"><a href="https://github.com/ianmwenda678/product-api" target="_blank"><span class="badge badge-lab">Lab 10</span> Testing &amp; Deployment (Cloud) <span class="lesson-topic">— Pytest, CI/CD, Render Deployment</span><span class="repo-link">🔗 View on GitHub</span></a></div>

        <div class="footer"><p>📍 Deployed on Render | 📅 Last Updated: August 2026</p></div>
    </div>
</body>
</html>
"""
    return HTMLResponse(content=html_content)

# ============================================================
# HEALTH CHECK
# ============================================================
@app.get("/health")
def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}
