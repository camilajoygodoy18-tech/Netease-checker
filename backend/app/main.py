from fastapi import FastAPI, Depends, HTTPException, status, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from typing import List, Optional
import os
import asyncio
from datetime import datetime

from .database import engine, get_db, Base
from .routes import auth, users, checks, admin, websocket
from .utils import netease

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Netease Checker API",
    description="Check Netease game accounts with modern UI",
    version="2.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(users.router, prefix="/api/users", tags=["Users"])
app.include_router(checks.router, prefix="/api/checks", tags=["Checks"])
app.include_router(admin.router, prefix="/api/admin", tags=["Admin"])
app.include_router(websocket.router, prefix="/api/ws", tags=["WebSocket"])

# ============ ROOT ENDPOINTS ============
@app.get("/")
def root():
    return {
        "message": "Netease Checker API",
        "version": "2.0.0",
        "status": "running",
        "docs": "/docs",
        "redoc": "/redoc"
    }

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "Netease Checker"
    }

@app.get("/api/status")
def get_status():
    return {
        "status": "operational",
        "version": "2.0.0",
        "uptime": "N/A",
        "checks_running": False
    }

# ============ RUN ============
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )