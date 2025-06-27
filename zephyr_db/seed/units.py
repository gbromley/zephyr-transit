from zephyr_db.models import Unit

from .utils import seed_table

UNITS = [{'name': 'wind speed', 'symbol': 'm/s'}]


def seed_units() -> None:
    """Seeds units to a clean database"""

    seed_table(Unit, UNITS)
