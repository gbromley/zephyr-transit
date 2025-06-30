from zephyr_db.models import Unit


def test_create_units(db_session):
    """Test creating and persisting a Unit model.
    
    Args:
        db_session: Database session fixture.
    """
    unit = Unit(name='meters per second', symbol='m/s')
    db_session.add(unit)
    db_session.commit()

    assert unit.id is not None
    assert unit.name == 'meters per second'


def test_verify_rollback(db_session):
    """Verify test isolation through transaction rollback.
    
    Args:
        db_session: Database session fixture.
    """
    # This should find nothing from previous test
    units = db_session.query(Unit).filter_by(name='meters per second').all()
    assert len(units) == 0
