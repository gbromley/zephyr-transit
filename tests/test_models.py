import os


from zephyr_db.models import Station, Source, Unit, Variable, Observation



def test_create_units(db_session):
    
    unit = Unit(name='meters per second')
    db_session.add(unit)
    db_session.flush()
    
    assert unit.id is not None
    assert unit.name == 'meters per second'




def test_verify_rollback(db_session):
    
    # This should find nothing from previous test
    units = db_session.query(Unit).filter_by(name='test unit').all()
    assert len(units) == 0 
