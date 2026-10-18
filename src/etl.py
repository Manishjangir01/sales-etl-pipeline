"""Extract -> Transform -> Load pipeline for raw sales data."""
import argparse
import logging
import sqlite3
from pathlib import Path

import pandas as pd

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("etl")

REQUIRED_COLUMNS = {
    "order_id", "order_date", "customer_id", "city",
    "product", "quantity", "unit_price",
}


def extract(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    missing = REQUIRED_COLUMNS - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")
    log.info("Extracted %d rows from %s", len(df), path)
    return df


def transform(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Clean data. Returns (clean_rows, rejected_rows)."""
    df = df.copy()
    start = len(df)

    df = df.drop_duplicates(subset="order_id", keep="first")
    log.info("Removed %d duplicate orders", start - len(df))

    df["order_date"] = pd.to_datetime(df["order_date"], errors="coerce")
    df["city"] = df["city"].str.strip().str.title()

    bad = (
        df["order_date"].isna()
        | df["city"].isna()
        | (df["quantity"] <= 0)
        | (df["unit_price"] <= 0)
    )
    rejected = df[bad].copy()
    clean = df[~bad].copy()
    log.info("Rejected %d invalid rows", len(rejected))

    clean["revenue"] = clean["quantity"] * clean["unit_price"]
    clean["order_month"] = clean["order_date"].dt.to_period("M").astype(str)
    clean["order_date"] = clean["order_date"].dt.strftime("%Y-%m-%d")
    return clean, rejected


def load(clean: pd.DataFrame, rejected: pd.DataFrame, db_path: str) -> None:
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(db_path) as conn:
        clean.to_sql("fact_sales", conn, if_exists="replace", index=False)
        rejected.astype(str).to_sql("rejected_sales", conn, if_exists="replace", index=False)
        conn.execute("CREATE INDEX IF NOT EXISTS idx_sales_month ON fact_sales(order_month)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_sales_city ON fact_sales(city)")
    log.info("Loaded %d clean rows into %s", len(clean), db_path)


def run(raw_path: str, db_path: str, processed_dir: str) -> dict:
    df = extract(raw_path)
    clean, rejected = transform(df)
    load(clean, rejected, db_path)
    Path(processed_dir).mkdir(parents=True, exist_ok=True)
    clean.to_csv(Path(processed_dir) / "sales_clean.csv", index=False)
    return {"raw": len(df), "clean": len(clean), "rejected": len(rejected)}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--raw", default="data/raw/sales_raw.csv")
    parser.add_argument("--db", default="data/warehouse.db")
    parser.add_argument("--processed", default="data/processed")
    args = parser.parse_args()
    print(run(args.raw, args.db, args.processed))
