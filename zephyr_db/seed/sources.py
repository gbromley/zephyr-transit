from zephyr_db.models import Source

from .utils import seed_table

SOURCES = [
    {
        'name': 'Colorado DOT',
        'description': 'Data from the Colorado DOT API',
        'api_endpoint': 'https://data.cotrip.org/api/v1/weatherStations',
    },
]


def seed_sources() -> None:
    """Populate database with predefined data sources."""
    seed_table(Source, SOURCES)
