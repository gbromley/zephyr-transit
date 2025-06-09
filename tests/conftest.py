import os

os.environ['DB_NAME'] = 'zephyr_transit_test'
import pytest

from zephyr_db import engine
from zephyr_db.database import SessionLocal
from zephyr_db.models import Base


@pytest.fixture(scope='session')
def db_engine():
    Base.metadata.create_all(engine)
    yield engine
    Base.metadata.drop_all(engine)


@pytest.fixture
def db_session(db_engine):
    connection = db_engine.connect()
    transaction = connection.begin()
    session = SessionLocal(bind=connection)

    try:
        yield session
    finally:
        session.close()
        transaction.rollback()
        connection.close()
