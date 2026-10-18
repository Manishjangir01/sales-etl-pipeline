"""Run the analytics queries against the warehouse and print results."""
import argparse
import sqlite3

import pandas as pd


def main(db_path: str, sql_path: str) -> None:
    queries = [q.strip() for q in open(sql_path).read().split(";") if "SELECT" in q]
    with sqlite3.connect(db_path) as conn:
        for q in queries:
            title = q.splitlines()[0].lstrip("- ").strip()
            print(f"\n=== {title} ===")
            print(pd.read_sql_query(q, conn).to_string(index=False))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--db", default="data/warehouse.db")
    parser.add_argument("--sql", default="sql/analytics.sql")
    args = parser.parse_args()
    main(args.db, args.sql)
