import polars as pl
from zephyr_db import zephyr_db_session


class StationLoader:

    def __init__(self, df: pl.DataFrame):
        self.df = df
        self.current_stations = None


    def _get_current_stations(self):
        """Get current stations from the database."""
        if self.current_stations is None:
            with zephyr_db_session() as sess:
                self.current_stations = pl.read_database(
                    'SELECT id, name FROM stations', sess.connection()
                )

        return self.current_stations

    



