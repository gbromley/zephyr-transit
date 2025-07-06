import polars as pl
from sqlalchemy import insert

from zephyr_db import zephyr_db_session
from zephyr_db.models import Station


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

    def _get_current_stations(self):
        """Get current stations from the database."""
        if self._current_stations is None:
            with zephyr_db_session() as sess:
                result = pl.read_database('SELECT id, name FROM stations', sess.connection())
                # Fix the schema for empty tables
                if result.is_empty():
                    self._current_stations = pl.DataFrame(
                        {'id': [], 'name': []}, schema={'id': pl.Int64, 'name': pl.String}
                    )
                else:
                    self._current_stations = result

        return self._current_stations

    def _stations_to_insert(self):
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
            return []

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
                return inserted_stations
            except Exception:
                session.rollback()
                raise
