from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
from core.config import settings

# Connection string reused by SQLAlchemy and LangChain SQLDatabase
SQLALCHEMY_DATABASE_URL = "{}://{}:{}@{}:{}/{}".format(
    settings.db_connection,
    settings.db_user,
    settings.db_password,
    settings.db_host,
    settings.db_port,
    settings.db_name,
)

# pool_pre_ping ensures stale connections are reconnected automatically
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_size=5,
    pool_pre_ping=True,
    isolation_level="READ COMMITTED",
)

# Scoped session for thread safety across background workers and API requests
SessionLocal = sessionmaker(bind=engine)
SessionLocal = scoped_session(SessionLocal)

Base = declarative_base()


def get_db():
    """Create and return a database session."""
    db = SessionLocal()
    try:
        return db
    finally:
        db.close()
        engine.dispose()
