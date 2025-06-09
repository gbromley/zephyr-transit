import os


from zephyr_db.models import Station, Source, Unit, Variable, Observation



def test_create_units(db_session):
    
    unit = Unit(name='meters per second')
    db_session.add(unit)
    db_session.flush()
    
    assert unit.id is not None
    assert unit.name == 'meters per second'




