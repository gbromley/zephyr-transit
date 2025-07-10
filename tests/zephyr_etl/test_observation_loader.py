from datetime import datetime, timedelta

import polars as pl
import pytest

from zephyr_db.models import Observation, Source, Variable
from zephyr_db.seed import seed_sources, seed_units, seed_variables
from zephyr_etl.observation_loader import ObservationLoader
from zephyr_etl.station_loader import StationLoader


@pytest.fixture
def station_df(db_session):
    """Standard test station data."""
    colorado_source = db_session.query(Source).filter(Source.name == 'Colorado DOT').first()
    data = {
        'name': ['Station1', 'Station2'],
        'source_id': [colorado_source.id, colorado_source.id],
        'latitude': [45.0, 46.0],
        'longitude': [-105.0, -95.0],
    }
    return pl.DataFrame(data)


@pytest.fixture
def seeded_database(db_session):
    """Database with sources, units, and variables seeded."""
    seed_sources()
    seed_units()
    seed_variables()
    return db_session


@pytest.fixture
def test_stations(seeded_database, station_df):
    """Insert test stations and return their IDs."""
    stations = StationLoader(station_df).insert_stations()
    station_ids = [station.id for station in stations]

    return sorted(station_ids)


def test_load_observations(seeded_database, test_stations):
    """Test loading observations into database."""
    wind_speed_id = (
        seeded_database.query(Variable.id).filter(Variable.name == 'wind speed').scalar()
    )
    wind_dir_id = (
        seeded_database.query(Variable.id).filter(Variable.name == 'wind direction').scalar()
    )

    observations_df = pl.DataFrame(
        {
            'station_id': [test_stations[0], test_stations[1]],
            'variable_id': [wind_speed_id, wind_dir_id],
            'time': [datetime.now()] * 2,
            'value': [25.5, 30.2],
        }
    )

    loader = ObservationLoader(observations_df)
    inserted = loader.load()

    assert inserted == 2

    # Additional verification - check data was actually inserted
    obs_count = seeded_database.query(Observation).count()
    assert obs_count == 2


def test_load_empty(seeded_database):
    """Make sure loading empty dataframe does nothing."""
    ['station_id', 'variable_id', 'time', 'value']
    [pl.Int64, pl.Int64, pl.Datetime, pl.Float64]
    observations_df = pl.DataFrame(
        {'station_id': [], 'variable_id': [], 'time': [], 'value': []},
        schema={
            'station_id': pl.Int64,
            'variable_id': pl.Int64,
            'time': pl.Datetime,
            'value': pl.Float64,
        },
    )

    loader = ObservationLoader(observations_df)
    inserted = loader.load()

    assert inserted == 0

    obs_count = seeded_database.query(Observation).count()
    assert obs_count == 0


def test_chunking_large_dataset(seeded_database, test_stations):
    """Test that large datasets are properly chunked."""
    n_obs = 12000
    wind_speed_id = (
        seeded_database.query(Variable.id).filter(Variable.name == 'wind speed').scalar()
    )

    # Create unique timestamps for each observation
    base_time = datetime.now()
    timestamps = [base_time + timedelta(seconds=i) for i in range(n_obs)]

    observations_df = pl.DataFrame(
        {
            'station_id': [test_stations[0]] * n_obs,
            'variable_id': [wind_speed_id] * n_obs,
            'time': timestamps,
            'value': list(range(n_obs)),  # Different values to verify, casted to float using schema
        },
        schema={
            'station_id': pl.Int64,
            'variable_id': pl.Int64,
            'time': pl.Datetime,
            'value': pl.Float64,
        },
    )

    loader = ObservationLoader(observations_df, chunksize=5000)
    inserted = loader.load()

    assert inserted == n_obs
    assert seeded_database.query(Observation).count() == n_obs
