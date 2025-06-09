import os
os.environ["DB_NAME"] = "zephyr_transit_test"
import pytest
from zephyr_db import engine
from zephyr_db.models import Base



@pytest.fixture(scope="session")
def setup_test_db():
    Base.metadata.create_all(engine)
    yield
    Base.metadata.drop_all(engine)