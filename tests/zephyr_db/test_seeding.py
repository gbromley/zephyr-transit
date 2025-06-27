import pytest 
from zephyr_db.seed import seed_table, seed_sources, seed_units
from zephyr_db.models import Unit, Source, Variable
from zephyr_db import zephyr_db_session
import os

def test_seed_tables(db_session):
    print(os.getenv('DB_NAME'))
    
    data_to_seed = {"name": "miles per hour", "symbol": "mph"}

    unit = Unit(**data_to_seed)
    
    seed_table(Unit, [data_to_seed])


    query = db_session.query(Unit).first()

    assert query.name == unit.name





def test_seed_sources(db_session):

    seed_sources()
    source_query = db_session.query(Source).first()


    assert source_query.name is not None


def test_seed_units(db_session):
    seed_units()

    unit_query = db_session.query(Unit).first()

    assert unit_query.name is not None


def test_seed_variables(db_session):

    seed_units()
    unit = db_session.query(Unit).filter(Unit.name == 'wind speed').first()
    
    wind_speed_var = Variable(name="average wind speed", unit_id=unit.id)
    db_session.add(wind_speed_var)
    db_session.flush()

    var = db_session.query(Variable).filter(Variable.name == 'average wind speed').first()

    assert var.name == wind_speed_var.name

    