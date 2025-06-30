from zephyr_db import zephyr_db_session


def seed_table(model, data: list[dict], session=None) -> None:
    """Seed database table with data, skipping duplicates by name.

    Args:
        model: SQLAlchemy model class to seed.
        data: List of dictionaries containing record data.
        session: Optional database session. If not provided, creates a new one.
    """
    if not data:
        return
    if session:
        _seed_data(session, model, data)
    else:
        with zephyr_db_session() as sess:
            _seed_data(sess, model, data)


def _seed_data(session, model, data: list[dict]) -> None:
    """Insert new records into database, avoiding duplicates.

    Args:
        session: Active database session.
        model: SQLAlchemy model class.
        data: List of dictionaries containing record data.
    """
    existing_names = {r.name for r in session.query(model.name)}
    new_records = [model(**row) for row in data if row['name'] not in existing_names]
    if new_records:
        session.add_all(new_records)
        session.commit()
