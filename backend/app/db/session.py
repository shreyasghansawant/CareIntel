from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from app.core.config import settings
from app.core.logging import logger
from app.db.base import Base

# Engine configuration with dialect detection
connect_args = {}
if settings.DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}
    engine = create_engine(
        settings.DATABASE_URL,
        connect_args=connect_args
    )
else:
    # PostgreSQL configuration with connection pooling
    engine = create_engine(
        settings.DATABASE_URL,
        pool_pre_ping=True,
        pool_size=10,
        max_overflow=20
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """FastAPI dependency for yielding database session with automatic cleanup."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """Initializes tables in database if they do not exist."""
    # Import models so they are registered with Base.metadata
    from app.models.lead import HealthcareLead  # noqa: F401
    Base.metadata.create_all(bind=engine)
    logger.info("Database schema verified and initialized.")
