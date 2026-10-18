import sqlite3
import sys
from pathlib import Path

import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
import etl  # noqa: E402
from generate_data import generate  # noqa: E402


def test_transform_removes_duplicates_and_invalid_rows():
    raw = generate(500, seed=1)
    clean, rejected = etl.transform(raw)
    assert clean["order_id"].is_unique
    assert (clean["quantity"] > 0).all()
    assert clean["city"].notna().all()
    assert len(rejected) > 0


def test_revenue_is_quantity_times_price():
    raw = generate(200, seed=2)
    clean, _ = etl.transform(raw)
    assert (clean["revenue"] == clean["quantity"] * clean["unit_price"]).all()


def test_city_names_are_normalised():
    raw = generate(500, seed=3)
    clean, _ = etl.transform(raw)
    assert (clean["city"] == clean["city"].str.title()).all()


def test_extract_fails_on_missing_columns(tmp_path):
    bad = tmp_path / "bad.csv"
    pd.DataFrame({"order_id": [1]}).to_csv(bad, index=False)
    with pytest.raises(ValueError):
        etl.extract(str(bad))


def test_full_pipeline_loads_warehouse(tmp_path):
    raw = tmp_path / "raw.csv"
    generate(300, seed=4).to_csv(raw, index=False)
    db = tmp_path / "wh.db"
    stats = etl.run(str(raw), str(db), str(tmp_path / "processed"))
    with sqlite3.connect(db) as conn:
        n = conn.execute("SELECT COUNT(*) FROM fact_sales").fetchone()[0]
    assert n == stats["clean"]
    assert stats["clean"] + stats["rejected"] <= stats["raw"]
