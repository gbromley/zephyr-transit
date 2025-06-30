import pytest

from zephyr_db import engine
from zephyr_db.database import SessionLocal
from zephyr_db.models import Base


@pytest.fixture()
def db_engine():
    """Provide a clean database engine for testing.
    
    Yields:
        Engine: SQLAlchemy engine with fresh tables.
    """
    Base.metadata.create_all(engine)
    yield engine
    Base.metadata.drop_all(engine)


@pytest.fixture
def db_session(db_engine):
    """Provide an isolated database session for testing.

    Args:
        db_engine: Database engine fixture.

    Yields:
        Session: SQLAlchemy session with automatic rollback.
    """
    connection = db_engine.connect()
    transaction = connection.begin()
    session = SessionLocal(bind=connection)

    try:
        yield session
    finally:
        session.close()
        transaction.rollback()
        connection.close()
