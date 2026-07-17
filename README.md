# dwd-ingest

**dwd-ingest** is a Python script that consumes [German weather data](https://opendata.dwd.de/) made publicly available by [DWD (Deutscher Wetterdienst)](https://www.dwd.de/) under a [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) license and stores it in a PostgreSQL database.

# Run

## Docker

```
docker compose up
```

## Using a local Postgres instance

Assuming you have a Postgres server running locally on port 5432:

* Create a database called "dwd"
* Add tables and users according to `postgres_init/`

```
python main.py
```
