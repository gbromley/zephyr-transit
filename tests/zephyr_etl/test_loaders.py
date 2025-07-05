import polars as pl

from zephyr_db import zephyr_db_session
from zephyr_db.models import Source, Station
from zephyr_db.seed import seed_sources
from zephyr_etl.station_loader import StationLoader


def test_get_current_stations(db_session):
    """Test that StationLoader can retrieve current stations from the database."""
    seed_sources()

    sources = db_session.query(Source).filter(Source.name == 'Colorado DOT').first()
    test_station = Station(name='Station1', source_id = sources.id, latitude=45, longitude=-105)

    db_session.add(test_station)
    db_session.flush()

    df = pl.DataFrame()

    loader = StationLoader(df)

    current_stations = loader._get_current_stations()

    assert len(current_stations) == 1

    with zephyr_db_session() as sess:
        # This query should see the uncommitted data because it's the same transaction
        count = sess.query(Station).count()
        assert count == 1


def test_isolation_check(db_session):
    """Test that this test doesn't see data from other tests."""
    df = pl.DataFrame()
    loader = StationLoader(df)

    # Should be empty since we haven't added any stations in this test
    current_stations = loader._get_current_stations()

    assert len(current_stations) == 0



