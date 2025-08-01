import logging
import time

import requests
from jsonschema import ValidationError, validate
from tenacity import retry, stop_after_attempt, wait_exponential_jitter

logger = logging.getLogger(__name__)
CoDOT_URL = 'https://data.cotrip.org/api/v1/weatherStations'

CoDOT_response_schema = {
    '$schema': 'http://json-schema.org/draft-07/schema#',
    'additionalProperties': False,
    'properties': {
        'features': {
            'items': {
                'additionalProperties': False,
                'properties': {
                    'attributes': {'type': ['object', 'null']},
                    'geometry': {
                        'additionalProperties': False,
                        'properties': {
                            'coordinates': {
                                'items': {'items': {'type': 'number'}, 'type': 'array'},
                                'type': 'array',
                            },
                            'type': {'type': 'string'},
                        },
                        'type': 'object',
                    },
                    'properties': {
                        'additionalProperties': False,
                        'properties': {
                            'currentConditions': {
                                'items': {
                                    'properties': {
                                        'additionalData': {'type': ['string', 'null']},
                                        'conditionDescription': {'type': 'string'},
                                        'conditionId': {'type': 'integer'},
                                        'confirmationTime': {'type': 'integer'},
                                        'confirmationUserName': {'type': 'string'},
                                        'endTime': {'type': 'integer'},
                                        'id': {'type': 'integer'},
                                        'sourceType': {'type': 'string'},
                                        'startTime': {'type': 'integer'},
                                        'updateTime': {'type': 'integer'},
                                    },
                                    'required': [
                                        'id',
                                        'userName',
                                        'updateTime',
                                        'startTime',
                                        'conditionId',
                                        'conditionDescription',
                                        'confirmationUserName',
                                        'confirmationTime',
                                        'sourceType',
                                        'endTime',
                                    ],
                                    'type': 'object',
                                },
                                'type': 'array',
                            },
                            'id': {'type': 'string'},
                            'name': {'type': 'string'},
                            'nameId': {'type': 'string'},
                            'parentAreaId': {'type': 'integer'},
                            'parentSubAreaId': {'type': 'integer'},
                            'primaryLatitude': {'type': 'number'},
                            'primaryLongitude': {'type': 'number'},
                            'primaryMP': {'type': 'number'},
                            'routeId': {'type': 'integer'},
                            'routeName': {'type': 'string'},
                            'routeSegmentIndex': {'type': 'integer'},
                            'secondaryLatitude': {'type': 'number'},
                            'secondaryLongitude': {'type': 'number'},
                            'secondaryMP': {'type': 'number'},
                            'sortOrder': {'type': 'integer'},
                        },
                        'required': [
                            'id',
                            'name',
                            'nameId',
                            'routeId',
                            'routeName',
                            'primaryMP',
                            'secondaryMP',
                            'primaryLatitude',
                            'primaryLongitude',
                            'secondaryLatitude',
                            'secondaryLongitude',
                            'sortOrder',
                            'parentAreaId',
                            'parentSubAreaId',
                            'routeSegmentIndex',
                            'currentConditions',
                        ],
                        'type': 'object',
                    },
                    'type': {'type': 'string'},
                },
                'required': ['type', 'geometry', 'properties', 'attributes'],
                'type': 'object',
            },
            'type': 'array',
        },
        'type': {'type': 'string'},
    },
    'required': ['type', 'features'],
    'type': 'object',
}


class CoDOTParser:
    """Parser for Colorado DOT weather station data via COTRIP API.

    Handles authentication and pagination when fetching real-time weather
    station data from Colorado's DOT stations. The parser manages
    API rate limits through built-in retry logic and session management.

    Attributes:
        api_key: Authentication key for COTRIP API access.
        session: Persistent HTTP session for efficient requests.
        CoDOT_URL: Base endpoint for weather station data.

    Example:
        parser = CoDOTParser(api_key="your-key-here")
        stations = parser.fetch_met_data()
    """

    def __init__(self, api_key: str):
        """Initialize the CoDOT parser with API credentials.

        Sets up an authenticated session for making requests to the COTRIP
        weather station API. Configures standard headers for consistent
        communication with the service.

        Args:
            api_key: Valid COTRIP API key for authentication. Required for
                all API requests. Get one at data.cotrip.org.

        Raises:
            ValueError: When api_key is empty or None.
        """
        if not api_key:
            raise ValueError('API key is required')
        self.api_key = api_key

        self.session = requests.Session()

        # Configure session with headers
        self.session.headers.update(
            {
                'User-Agent': 'CoDOT-Weather-Parser/1.0',
                'Accept': 'application/json',
            }
        )

    @retry(
        stop=stop_after_attempt(3), wait=wait_exponential_jitter(initial=4, max=10), reraise=True
    )
    def _api_request(self):
        """Fetch weather station data from COTRIP API with pagination.

        Makes paginated requests to retrieve all available weather stations.
        Handles API pagination through the Next-Offset header, collecting
        results across multiple requests. Automatically retries failed
        requests with exponential backoff.

        Returns:
            list: Raw feature data from all weather stations. Each station
                is represented as a dictionary containing location and
                current weather observations.

        Raises:
            requests.HTTPError: When API returns error status codes.
            requests.Timeout: When request exceeds 30 second timeout.
        """
        params = {'apiKey': self.api_key, 'limit': 100}
        all_data = []
        logger.info(f'Requesting data from: {CoDOT_URL}')

        while True:
            try:
                response = requests.get(CoDOT_URL, params=params, timeout=30)
                response.raise_for_status()

                content_type = response.headers.get('Content-Type', '')
                if 'application/json' not in content_type:
                    logger.error(f'Unexpected content type: {content_type}')

                    return None

                raw_json = response.json()
                valid_data = self._check_response_schema(raw_json, CoDOT_response_schema)
                data = valid_data.get('features', [])
                all_data.extend(data)

                next_offset = response.headers.get('Next-Offset')
                if not next_offset or next_offset == 'None':
                    break

                params['offset'] = next_offset
            except requests.exceptions.ConnectionError:
                logger.error(f'Connection error for URL: {CoDOT_URL}')
                return None
            except requests.exceptions.HTTPError as e:
                if e.response.status_code <= 500:
                    logger.error(f'Client error: {e.response.status_code}: {e}')
                    return None
                raise

        return all_data

    def _check_response_schema(self, response_data, expected_schema):
        try:
            validate(response_data, expected_schema)
            return response_data
        except ValidationError as e:
            logger.error(f'Schema change detected: {e.message}')
            logger.error(f'Path: {" -> ".join(str(p) for p in e.absolute_path)}')
            logger.error(f'Expected: {e.validator} {e.validator_value}')
            # Still return data but flag the issue
            return response_data

    def fetch_met_data(self):
        """Retrieve current weather data from all Colorado DOT stations.

        Public interface for fetching meteorological observations. Wraps
        the internal paginated API request with timing and logging for
        monitoring performance. This is the primary method users should
        call to get weather station data.

        Returns:
            list: Collection of weather station features, where each item
                contains station metadata and current observations including
                temperature, wind speed, visibility, and road conditions.

        Example:
            parser = CoDOTParser(api_key="abc123")
            weather_data = parser.fetch_met_data()
            print(f"Found {len(weather_data)} stations")
        """
        start_time = time.time()

        result = self._api_request()
        elapsed = time.time() - start_time
        logger.info(f'Fetched {len(result)} stations in {elapsed:.2f} seconds')
        return result
