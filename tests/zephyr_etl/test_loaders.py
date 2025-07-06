import polars as pl
import pytest
from polars.testing import assert_frame_equal

from zephyr_db.models import Source, Station
from zephyr_db.seed import seed_sources
from zephyr_etl.station_loader import StationLoader


@pytest.fixture
def colorado_source(db_session):
    """Fixture for Colorado DOT source."""
    seed_sources()
    return db_session.query(Source).filter(Source.name == 'Colorado DOT').first()


@pytest.fixture
def station_data(colorado_source):
    """Standard test station data."""
    return {
        'name': ['Station1', 'Station2'],
        'source_id': [colorado_source.id, colorado_source.id],
        'latitude': [45.0, 46.0],
        'longitude': [-105.0, -95.0],
    }


def test_station_insert(db_session, station_data):
    """Test that we can add stations to the database."""
    stations_to_insert = pl.DataFrame(station_data)

    StationLoader(stations_to_insert).insert_stations()

    stations_in_db = pl.read_database('SELECT * FROM stations', db_session.connection()).select(
        ['name', 'source_id', 'latitude', 'longitude']
    )

    assert_frame_equal(stations_to_insert, stations_in_db)


def test_insert_identifies_existing_stations(db_session, station_data):
    """Test trying to insert twice"""
    station_df = pl.DataFrame(station_data)
    # Insert a station
    StationLoader(station_df).insert_stations()

    # Try to insert it again
    result = StationLoader(station_df).insert_stations()

    # Verify it was identified as existing
    assert len(result) == 0  # Nothing inserted


def test_isolation_check(db_session):
    """Test that this test doesn't see data from other tests."""
    df = pl.DataFrame()
    loader = StationLoader(df)

    # Should be empty since we haven't added any stations in this test
    current_stations = loader._get_current_stations()

    assert len(current_stations) == 0


def test_insert_empty_dataframe(db_session):
    """Test that inserting empty DataFrame returns empty list."""
    empty_df = pl.DataFrame(
        {'name': [], 'source_id': [], 'latitude': [], 'longitude': []},
        schema={  # use schema for empty dataframe
            'name': pl.String,
            'source_id': pl.Int64,
            'latitude': pl.Float64,
            'longitude': pl.Float64,
        },
    )

    result = StationLoader(empty_df).insert_stations()

    assert result == []
    assert db_session.query(Station).count() == 0


def test_insert_stations_handles_database_errors(db_session):
    """Test that database errors are properly handled with rollback."""
    # Create invalid data that will cause database constraint violation
    invalid_df = pl.DataFrame(
        {
            'name': ['TestStation'],
            'source_id': [99999],  # Non-existent source_id (foreign key violation)
            'latitude': [45.0],
            'longitude': [-105.0],
        }
    )

    with pytest.raises(Exception):
        StationLoader(invalid_df).insert_stations()

    # Verify no partial data was committed (rollback worked)
    assert db_session.query(Station).count() == 0
