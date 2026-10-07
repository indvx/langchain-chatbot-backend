from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
from core.config import settings

# Build connection string from environment variables
SQLALCHEMY_DATABASE_URL = "{}://{}:{}@{}:{}/{}".format(
    settings.db_connection,
    settings.db_user,
    settings.db_password,
    settings.db_host,
    settings.db_port,
    settings.db_name,
)

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_size=5,
    pool_pre_ping=True,
    isolation_level="READ COMMITTED",
)

# Use scoped session for thread safety across requests
SessionLocal = sessionmaker(bind=engine)
SessionLocal = scoped_session(SessionLocal)

Base = declarative_base()


def get_db():
    """Yield a database session context."""
    db = SessionLocal()
    try:
        return db
    finally:
        db.close()
        engine.dispose()
