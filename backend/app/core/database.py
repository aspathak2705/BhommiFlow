from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from app.core.config import settings

# In case psycopg2 is used, we can format DATABASE_URL
db_url = settings.DATABASE_URL
# SQLAlchemy 2.0 requires postgresql:// instead of postgres:// if using postgresql dialect.
# Pydantic Settings handles database url loading.
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
