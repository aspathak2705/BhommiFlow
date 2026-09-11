import sys
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

# Ensure app is in Python path when running from backend root
sys.path.insert(0, str(Path(__file__).resolve().parent))

from app.api.routes import health, auth, cases, guidance, projects, evidence_intelligence, intelligence_graph, prediction, explainability, decision_intelligence
from app.core.config import settings
from app.core.database import engine

# Database startup connectivity validation
try:
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
    # Mask credentials when logging database URL
    db_name = "Supabase/PostgreSQL" if settings.SUPABASE_DATABASE_URL else "PostgreSQL"
    print(f"[INFO] Database provider verification: {db_name} connection PASSED.")
except Exception as e:
    print(f"[ERROR] Database connection check failed: {str(e)}", file=sys.stderr)
    if settings.ENVIRONMENT == "production":
        print("[CRITICAL] Production database unreachable. Aborting startup.", file=sys.stderr)
        sys.exit(1)

app = FastAPI(
    title="BhoomiFlow / BhoomiSakha API",
    description="Predictive Land Acquisition Intelligence & Decision Support System API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS configuration
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
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
app.include_router(auth.router, prefix="/api/v1", tags=["Authentication"])
app.include_router(cases.router, prefix="/api/v1", tags=["Cases"])
app.include_router(guidance.router, prefix="/api/v1", tags=["Guidance"])
app.include_router(projects.router, prefix="/api/v1", tags=["Projects Foundation"])
app.include_router(evidence_intelligence.router, prefix="/api/v1", tags=["Evidence Intelligence"])
app.include_router(intelligence_graph.router, prefix="/api/v1", tags=["Intelligence Graph"])
app.include_router(prediction.router, prefix="/api/v1", tags=["Predictive Engine"])
app.include_router(explainability.router, prefix="/api/v1", tags=["Explainability & Interventions"])
app.include_router(decision_intelligence.router, prefix="/api/v1", tags=["Decision Intelligence & Officer Workflow"])





@app.get("/")
def read_root():
    return {"message": "Welcome to BhoomiFlow API. Access docs at /docs."}
