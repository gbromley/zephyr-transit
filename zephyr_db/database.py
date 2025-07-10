import os
from contextlib import contextmanager
from contextvars import ContextVar
from typing import Optional

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

load_dotenv()

# Context variable to store current session for test isolation
_session_context: ContextVar[Optional[Session]] = ContextVar('_session_context', default=None)


def get_database_url() -> str:
    """Get the appropriate database URL based on environment.
    
    Returns:
        Database URL string for PostgreSQL connection
    """
    # Check for DATABASE_URL first (for CI/CD environments)
    DATABASE_URL = os.getenv('DATABASE_URL')

    if not DATABASE_URL:
        # Construct from individual variables (for local development)
        DB_USER = os.getenv('POSTGRES_USER')
        DB_PASSWORD = os.getenv('POSTGRES_PASSWORD')
        DB_HOST = os.getenv('POSTGRES_HOST', 'localhost')
        DB_PORT = os.getenv('POSTGRES_PORT', '5432')
        DB_NAME = os.getenv('POSTGRES_NAME', 'zephyr_transit')

        DATABASE_URL = f'postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'

    return DATABASE_URL


# Database setup
DATABASE_URL = get_database_url()
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@contextmanager
def zephyr_db_session():
    """Create a database session with automatic cleanup.

    If a session is already set in the context (e.g., during testing),
    it will be reused instead of creating a new one.

    Yields:
        Session: SQLAlchemy database session.

    Raises:
        Exception: Any database operation errors are re-raised after rollback.
    """
    # Check if there's an existing session in the context (for test isolation)
    existing_session = _session_context.get()
    if existing_session:
        yield existing_session
        return

    # Normal production behavior - create a new session
    session = SessionLocal()
    try:
        yield session
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


@contextmanager
def set_session_context(session: Session):
    """Set a session in the context for test isolation.

    This is primarily used by test fixtures to ensure all database
    operations within a test use the same transaction.

    Args:
        session: The SQLAlchemy session to use for the context.

    Yields:
        Session: The provided session.
    """
    token = _session_context.set(session)
    try:
        yield session
    finally:
        _session_context.reset(token)
