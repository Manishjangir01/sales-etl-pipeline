# Sales ETL Pipeline

A small, end-to-end **data engineering** project: it takes a messy raw sales CSV, cleans and validates it, loads it into a SQLite warehouse, and answers business questions with SQL.

## Pipeline

```
raw CSV  ->  Extract  ->  Transform (clean + validate)  ->  Load (SQLite)  ->  SQL analytics
```

| Stage | What it does |
|-------|--------------|
| Extract | Reads the CSV and checks that all required columns exist |
| Transform | Drops duplicate orders, parses dates, normalises city names, rejects invalid rows (missing city, bad date, quantity <= 0), adds `revenue` and `order_month` |
| Load | Writes `fact_sales` and a `rejected_sales` audit table to SQLite, with indexes |
| Analytics | Monthly revenue, top cities, best-selling products, top customers |

## Project structure

```
src/generate_data.py   # creates a synthetic raw dataset with injected data-quality issues
src/etl.py             # extract / transform / load
src/report.py          # runs sql/analytics.sql against the warehouse
sql/analytics.sql      # business queries
tests/test_etl.py      # unit + end-to-end tests
```

## Run it

```bash
pip install -r requirements.txt
python src/generate_data.py --rows 1000
python src/etl.py
python src/report.py
pytest
```

Sample run: 1,020 raw rows -> 20 duplicates removed -> 49 rejected -> **951 clean rows** loaded.

## Skills demonstrated

- ETL design with separate extract, transform and load steps
- Data quality handling: deduplication, validation, and a rejected-rows audit table
- Python (pandas), SQL (aggregations, indexes), SQLite
- Logging, CLI arguments and automated tests

## Ideas for next steps

- Orchestrate with Airflow or cron
- Swap SQLite for PostgreSQL
- Add incremental loads and data-quality reporting
