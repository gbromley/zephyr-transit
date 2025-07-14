import logging
import time

import polars as pl
from sqlalchemy import insert

from zephyr_db import zephyr_db_session
from zephyr_db.models import Station

logger = logging.getLogger(__name__)


class StationLoader:
    """Class to handle loading stations into the database."""

    def __init__(self, df: pl.DataFrame):
        """Initialize with dataframe.

        Args:
            df:
                - source_id
                - name
                - latitude
                - longitude
                - elevation
                - road_name
                - road_direction
        """
        self.stations_df = df
        self._current_stations = None

    def _get_current_stations(self) -> pl.DataFrame:
        """Get current stations from the database with caching.

        Returns:
            DataFrame with columns [id, name] of existing stations
        """
        if self._current_stations is None:
            with zephyr_db_session() as sess:
                result = pl.read_database('SELECT id, name FROM stations', sess.connection())
                # Handle empty table case - polars needs explicit schema when no rows exist
                if result.is_empty():
                    self._current_stations = pl.DataFrame(
                        {'id': [], 'name': []}, schema={'id': pl.Int64, 'name': pl.String}
                    )
                else:
                    self._current_stations = result
        logger.info(f'Found {len(self._current_stations)} existing stations in database')
        return self._current_stations

    def _stations_to_insert(self) -> pl.DataFrame:
        """Identify new stations that don't exist in the database.

        Returns:
            DataFrame containing only stations not already in database
        """
        """Compare existing to stations_df, return only new."""
        existing_stations = self._get_current_stations()

        return self.stations_df.join(existing_stations.select('name'), on='name', how='anti')

    def insert_stations(self):
        """Inserts new stations into database, skipping existing ones.

        Returns:
            List[Station]: List of successfully inserted Station objects.

        Raises:
            ValueError: If required columns are missing from DataFrame.
        """
        df = self._stations_to_insert()

        if df.is_empty():
            logger.warning('No stations to insert - DataFrame is empty')
            return []

        start_time = time.time()
        with zephyr_db_session() as session:
            try:
                data = df.to_dicts()
                # Using stmt seems to be the sqlalchemy way
                stmt = insert(Station).returning(Station)
                result = session.scalars(stmt, data)
                inserted_stations = result.all()
                session.commit()
                # Reset current stations cache
                self._current_stations = None
                elapsed_time = time.time() - start_time
                logger.info(f'Inserted {len(inserted_stations)} stations in {elapsed_time:.2f}s')
                return inserted_stations
            except Exception:
                # Safely rollback transaction if still active
                logger.error('Failed to insert stations into database', exc_info=True)
                if session.is_active:
                    session.rollback()
                raise
