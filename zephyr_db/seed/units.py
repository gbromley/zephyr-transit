from zephyr_db.models import Unit

from .utils import seed_table

UNITS = [{'name': 'wind speed', 'symbol': 'm/s'}, {'name': 'wind dir', 'symbol': '°'}]


def seed_units() -> None:
    """Populate database with measurement units."""
    seed_table(Unit, UNITS)
