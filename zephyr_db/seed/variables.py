import polars as pl

from zephyr_db import engine
from zephyr_db.models import Variable

from .utils import seed_table

VARIABLES = [{'name': 'wind speed', 'unit': 'wind speed'},
             {'name': 'wind direction', 'unit': 'wind dir'}]




def seed_variables() -> None:
    """Populate database with measurement variables."""
    units_df = pl.read_database("SELECT * FROM units", engine)

    variables = []

    for var in VARIABLES:

        if "unit" not in var:
            continue


        unit_id = units_df.filter(pl.col("name") == var["unit"]).select("id").item()


        variables.append(
            {
                "name": var['name'],
                "unit": var['unit'],
                "unit_id": unit_id,
            }
        )
    seed_table(Variable, variables)
