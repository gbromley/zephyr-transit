from zephyr_db.models import Variable

from .utils import seed_table

VARIABLES = [{'name': 'wind speed', 'unit': 'wind speed'}]


def seed_variables() -> None:
    """Populate database with measurement variables."""
    seed_table(Variable, VARIABLES)
