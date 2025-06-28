# zephyr-transit

### Introduction 
Zephyr-transit will be an end-to-end pipeline that extracts data from various DOT APIs and loads it into a Postgres database. Zephyr-transit is a data engineering project to my existing skillset, learn new technologies, and create a portfolio project for potential employers. 

### Motivation

In January of 2025, I achieved the worst gas mileage (< 8 mpg) my dashboard has ever displayed. I drove 14 hours from Madison, WI to Fort Collins, CO. The biggest factor for the terrible gas mileage was strong westerly winds that made my car work harder to keep speed. While fuming at each gas stop, I thought about how my decision making might have been different if I had realized how bad the winds were. Moving the departure date to a less windy day might have saved a significant amount of money...

Zephyr-transit will start with a simple milestone; acquiring the meteorological data from a DOT source and putting it into the database. Future features will focus on taking this project from simple ETL, to an app that can be used by anyone. 


### Current Tech Stack

#### Data Storage

- PostgreSQL - Time-series database for storing weather observations with optimized schema for wind measurements

#### Data Processing

- Polars - Lightning-fast dataframe library for transforming large volumes of weather station data with lazy evaluation and memory efficiency

#### Database Operations

- SQLAlchemy - SQL toolkit and ORM for type-safe database interactions and declarative model definitions
- Alembic - Database migration framework for version-controlled schema evolution

#### ETL Pipeline

- Airflow - Native handling of weather station API responses
- Google Cloud Platform 


