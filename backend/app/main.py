import sys
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Ensure app is in Python path when running from backend root
sys.path.insert(0, str(Path(__file__).resolve().parent))

from app.api.routes import health
from app.core.config import settings

app = FastAPI(
    title="ShikshaFlow API",
    description="Backend API for ShikshaFlow lesson planner",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS configuration
# Allowing localhost:3000 for frontend development
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes under /api/v1 prefix
app.include_router(health.router, prefix="/api/v1", tags=["Health"])

@app.get("/")
def read_root():
    return {"message": "Welcome to ShikshaFlow API. Access docs at /docs."}
