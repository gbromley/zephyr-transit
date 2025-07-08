# zephyr-transit

### Introduction 
Zephyr-transit will be an end-to-end pipeline that extracts data from various DOT APIs and loads it into a Postgres database. Zephyr-transit is a data engineering project to my existing skillset, learn new technologies, and create a portfolio project for potential employers. 

### Motivation

In January of 2025, I achieved the worst gas mileage (< 8 mpg) my car has ever displayed. I drove 14 hours from Madison, WI to Fort Collins, CO. The biggest factor for the terrible gas mileage was strong westerly winds that made my car work harder to keep speed. While fuming at each gas stop, I thought about how my decision making might have been different if I had realized how bad the winds were. Moving the departure date to a less windy day might have saved a significant amount of money...

Zephyr-transit will start with a simple milestone; acquiring the meteorological data from a DOT source and putting it into the database. Future features will focus on taking this project from simple ETL, to an app that plans routes according to wind conditions. 


### Current Tech Stack

#### Data Storage

- PostgreSQL 

#### Database Operations

- SQLAlchemy 
- Alembic 

#### Data Processing

- Polars 

#### ETL Pipeline

- Beam
- Airflow 
- Google Cloud Platform 


