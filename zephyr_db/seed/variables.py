import polars as pl

from zephyr_db import zephyr_db_session
from zephyr_db.models import Variable

from .utils import _seed_data

VARIABLES = [
    {'name': 'wind speed', 'unit': 'wind speed'},
    {'name': 'wind direction', 'unit': 'wind dir'},
]


def seed_variables() -> None:
    """Populate database with measurement variables.
    
    Links variables to their corresponding units by querying the units table
    and building relationships based on unit names.
    """
    with zephyr_db_session() as session:
        units_df = pl.read_database('SELECT * FROM units', session.connection())

        variables = []

        for var in VARIABLES:
            if 'unit' not in var:
                continue

            # Find the corresponding unit ID for this variable
            unit_id = units_df.filter(pl.col('name') == var['unit']).select('id').item()

            variables.append(
                {
                    'name': var['name'],
                    'unit_id': unit_id,
                }
            )

        _seed_data(session, Variable, variables)
