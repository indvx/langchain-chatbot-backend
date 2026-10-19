from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
from core.config import settings

# Database connection URL assembled from environment variables.
# Used by both SQLAlchemy models and LangChain's SQLDatabase utility.
SQLALCHEMY_DATABASE_URL = "{}://{}:{}@{}:{}/{}".format(
    settings.db_connection,
    settings.db_user,
    settings.db_password,
    settings.db_host,
    settings.db_port,
    settings.db_name,
)

# pool_pre_ping=True tests connections for liveness before checkout to prevent
# "MySQL/Postgres server has gone away" errors after periods of inactivity.
# pool_size=5 keeps resource usage modest for this deployment.
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_size=5,
    pool_pre_ping=True,
    isolation_level="READ COMMITTED",
)

# scoped_session gives each thread its own session instance,
# preventing cross-thread pollution between HTTP requests and background scheduler tasks.
SessionLocal = sessionmaker(bind=engine)
SessionLocal = scoped_session(SessionLocal)

# Base class for all ORM models (Employees, Documents, EmployeeAddresses)
Base = declarative_base()


def get_db():
    """
    Returns an active database session.
    Note: Always make sure callers manage transactions (.commit(), .rollback())
    and don't leak uncommitted changes across requests.
    """
    db = SessionLocal()
    try:
        return db
    finally:
        db.close()
        engine.dispose()
