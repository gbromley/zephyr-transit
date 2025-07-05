import polars as pl

from zephyr_db import zephyr_db_session
from zephyr_db.models import Variable

from .utils import seed_table

VARIABLES = [
    {'name': 'wind speed', 'unit': 'wind speed'},
    {'name': 'wind direction', 'unit': 'wind dir'},
]


def seed_variables() -> None:
    """Populate database with measurement variables."""
    with zephyr_db_session() as session:
        units_df = pl.read_database('SELECT * FROM units', session.connection())

        variables = []

        for var in VARIABLES:
            if 'unit' not in var:
                continue

            unit_id = units_df.filter(pl.col('name') == var['unit']).select('id').item()

            variables.append(
                {
                    'name': var['name'],
                    'unit': var['unit'],
                    'unit_id': unit_id,
                }
            )
        
        # Use the same session for seeding to ensure consistency
        from .utils import _seed_data
        _seed_data(session, Variable, variables)
