from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import engine, Base
from .routes import auth, users, checks, admin, websocket

app = FastAPI(title="Netease Checker API", version="1.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create tables
Base.metadata.create_all(bind=engine)

# Routes
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(users.router, prefix="/api/users", tags=["users"])
app.include_router(checks.router, prefix="/api/checks", tags=["checks"])
app.include_router(admin.router, prefix="/api/admin", tags=["admin"])
app.include_router(websocket.router, prefix="/api/ws", tags=["websocket"])

@app.get("/")
def root():
    return {"message": "Netease Checker API", "status": "running"}

@app.get("/health")
def health():
    return {"status": "healthy"}