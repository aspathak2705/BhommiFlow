from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from app.core.config import settings

# Select connection URL with Supabase precedence
db_url = settings.SUPABASE_DATABASE_URL or settings.DATABASE_URL

if not db_url or db_url == "postgresql://postgres:postgres@localhost:5432/bhoomiflow":
    # If production environment is set, fail clearly on unconfigured database settings
    if settings.ENVIRONMENT == "production":
        raise RuntimeError("Database configuration is missing. SUPABASE_DATABASE_URL or DATABASE_URL must be set in production.")

# Clean up postgres:// format issues for SQLAlchemy 2.0
if db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)

engine = create_engine(db_url, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
