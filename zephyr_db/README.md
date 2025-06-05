# Zephyr DB Module

Description of the zephyr_transit databse module. The goal is to have all the information for managing the database here. 

## Database Schema

### Core Tables

- **sources**: Data providers (State DOT agencies)
- **stations**: DOT station locations with coordinates and metadata
- **variables**: Measurement types (wind_speed, wind_dir)
- **units**: Measurement units (m/s, mph, °C, etc.)
- **observations**: Observations of wind data
- **station_variables**: Junction table tracking which variables each station measures


## Usage

### Database Connection

```python
from zephyr_db import db_session, engine

# Using context manager
with db_session() as session:
    stations = session.query(Station).all()

# Using engine directly (for pandas)
import pandas as pd
df = pd.read_sql("SELECT * FROM stations", engine)
```

## Migrations

This module uses Alembic for database migrations.

### Setup

1. Configure the database connection in `.env`:
   ```
   DB_USER=your_user
   DB_PASSWORD=your_password
   DB_HOST=localhost
   DB_PORT=5432
   DB_NAME=zephyr_transit
   ```

2. Run migrations:
   ```bash
   cd zephyr_db
   alembic upgrade head
   ```

### Creating New Migrations

```bash
# Auto-generate migration from model changes
alembic revision --autogenerate -m "Description of changes"

```

## Environment Variables

Required environment variables:
- `DB_USER`: PostgreSQL username
- `DB_PASSWORD`: PostgreSQL password
- `DB_HOST`: Database host (default: localhost)
- `DB_PORT`: Database port (default: 5432)
- `DB_NAME`: Database name (default: zephyr_transit)

## Development

### Adding New Models

1. Create model file in `models/`
2. Import in `models/__init__.py`
3. Generate migration: `alembic revision --autogenerate -m "Add new model"`
4. Review and apply migration using `alembic upgrade head`


