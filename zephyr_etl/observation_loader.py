import logging
import polars as pl
from sqlalchemy import insert

from zephyr_db import zephyr_db_session
from zephyr_db.models import Observation, StationVariable

logger = logging.getLogger(__name__)

class ObservationLoader:
    """Loads weather observation data into the database.

    Handles validation, chunking, and batch insertion of observation records
    from a Polars DataFrame into the observations table.
    """

    def __init__(self, observations_df: pl.DataFrame, chunksize: int = 5000) -> None:
        """Initialize the observation loader.

        Args:
            observations_df: DataFrame with columns [station_id, variable_id, time, value]
            chunksize: Number of records to insert per batch

        Raises:
            AssertionError: If DataFrame schema doesn't match expected format
        """
        self.obs_df = self._validate_df(observations_df)  # Simple defensive check
        self.chunksize = chunksize
        logger.info(f'Initial Number of Observations to Load:{len(self.obs_df)}')

    def _validate_df(self, df: pl.DataFrame) -> pl.DataFrame:
        """Validate DataFrame schema and data types.

        Args:
            df: DataFrame to validate

        Returns:
            Validated DataFrame

        Raises:
            AssertionError: If schema or data types don't match requirements
        """
        # Ensure exact column names match expected schema
        assert df.columns == ['station_id', 'variable_id', 'time', 'value']
        # Ensure data types match database constraints
        assert df.dtypes == [pl.Int64, pl.Int64, pl.Datetime, pl.Float64]
        return df

    def _insert_observations(self, session, df: pl.DataFrame) -> int:
        """Insert a batch of observations into the database.

        Args:
            df: DataFrame chunk to insert

        Returns:
            Number of records inserted
        """
        data = df.to_dicts()
        # Using stmt seems to be the sqlalchemy way
        stmt = insert(Observation).values(data)
        result = session.execute(stmt)
        num_inserted_observations = result.rowcount
        logger.info(f'batch of {num_inserted_observations} observations loaded.')

        return num_inserted_observations

    def _bulk_insert_obs(self, session, df: pl.DataFrame) -> int:
        """Insert observations in chunks to avoid memory issues.

        Args:
            df: Full DataFrame to insert

        Returns:
            Total number of records inserted
        """
        total_inserted = 0
        num_chunks = (len(df) + self.chunksize - 1) // self.chunksize
        logger.info(f'Processing {num_chunks} batches.')
        for frame in df.iter_slices(n_rows=self.chunksize):
            total_inserted += self._insert_observations(session, frame)
        return total_inserted

    def _update_station_vars(self, session):
        # Get existing combinations
        existing = set(session.query(StationVariable.station_id, StationVariable.variable_id).all())

        # Create new records
        new_records = [
            StationVariable(station_id=s_id, variable_id=v_id)
            for s_id, v_id in self.obs_df.select(['station_id', 'variable_id']).unique().iter_rows()
            if (s_id, v_id) not in existing
        ]
        logger.info(f'{len(new_records)} new Station-Variable combinations added.')
        if new_records:
            session.add_all(new_records)

    def load(self) -> int:
        """Load all observations into the database.

        Returns:
            Total number of records inserted, 0 if DataFrame is empty
        """
        if self.obs_df.is_empty():
            logger.warning('Dataframe empty!')
            return 0

        with zephyr_db_session() as session:
            total_inserted = self._bulk_insert_obs(session, self.obs_df)

            self._update_station_vars(session)

            session.commit()
            logger.info(f'{total_inserted} observations successfully loaded into the database.')
        return total_inserted
