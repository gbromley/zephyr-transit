import os

import pytest
import requests

from zephyr_etl.sources.co_dot import CoDOT_response_schema, CoDOTParser


@pytest.fixture
def api_key():
    """Returns api key from environment."""
    return os.getenv('CDOT_API_KEY', 'test-api-key')


@pytest.mark.integration
def test_parser_pagination(api_key):
    """Ensure pagination works correctly."""
    # Use the parser to fetch data
    parser = CoDOTParser(api_key=api_key)
    parser_results = parser.fetch_met_data()

    # Fetch directly from API with high limit to get all data in one request
    response = requests.get(
        'https://data.cotrip.org/api/v1/weatherStations',
        params={'apiKey': api_key, 'limit': 10000},  # High limit
        timeout=30,
    )
    direct_results = response.json()['features']

    # Compare counts
    assert len(parser_results) == len(direct_results)

    # Compare unique IDs to ensure no duplicates/missing
    parser_ids = {station['properties']['id'] for station in parser_results}
    direct_ids = {station['properties']['id'] for station in direct_results}
    assert parser_ids == direct_ids


def test_check_response_schema_valid_data():
    """Test _check_response_schema with valid data."""
    parser = CoDOTParser('dummy-key')

    valid_data = {
        'type': 'FeatureCollection',
        'features': [
            {
                'type': 'Feature',
                'geometry': {'type': 'Point', 'coordinates': [[-105.123, 40.456]]},
                'properties': {
                    'id': 'test-station',
                    'name': 'Test Station',
                    'nameId': 'TEST',
                    'routeId': 1,
                    'routeName': 'Test Route',
                    'primaryMP': 1.5,
                    'secondaryMP': 2.0,
                    'primaryLatitude': 40.456,
                    'primaryLongitude': -105.123,
                    'secondaryLatitude': 40.457,
                    'secondaryLongitude': -105.124,
                    'sortOrder': 1,
                    'parentAreaId': 1,
                    'parentSubAreaId': 1,
                    'routeSegmentIndex': 1,
                    'currentConditions': [],
                },
                'attributes': None,
            }
        ],
    }

    result = parser._check_response_schema(valid_data, CoDOT_response_schema)
    assert result == valid_data


def test_check_response_schema_invalid_data():
    """Test _check_response_schema with invalid data returns data but logs error."""
    parser = CoDOTParser('dummy-key')

    invalid_data = {
        'type': 'FeatureCollection',
        'features': [
            {
                'type': 'Feature',
                'geometry': {'type': 'Point'},  # Missing coordinates
                'properties': {'id': 'test'},  # Missing required fields
                'attributes': None,
            }
        ],
    }

    # Should return data even if invalid (defensive approach)
    result = parser._check_response_schema(invalid_data, CoDOT_response_schema)
    assert result == invalid_data
