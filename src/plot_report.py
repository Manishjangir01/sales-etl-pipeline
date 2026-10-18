"""Create the charts used in the README from the SQLite warehouse."""
import argparse
import sqlite3
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent


def main(db_path: str, out_dir: str) -> None:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(db_path) as conn:
        monthly = pd.read_sql_query(
            "SELECT order_month, SUM(revenue) AS revenue FROM fact_sales "
            "GROUP BY order_month ORDER BY order_month", conn)
        cities = pd.read_sql_query(
            "SELECT city, SUM(revenue) AS revenue FROM fact_sales "
            "GROUP BY city ORDER BY revenue DESC LIMIT 5", conn)

    fig, axes = plt.subplots(1, 2, figsize=(12, 4.2))
    axes[0].plot(monthly["order_month"], monthly["revenue"] / 1e6, marker="o", color="#2563eb")
    axes[0].set_title("Monthly revenue")
    axes[0].set_ylabel("Revenue (millions)")
    axes[0].tick_params(axis="x", rotation=45)
    axes[1].barh(cities["city"][::-1], cities["revenue"][::-1] / 1e6, color="#16a34a")
    axes[1].set_title("Top 5 cities by revenue")
    axes[1].set_xlabel("Revenue (millions)")
    for ax in axes:
        ax.spines[["top", "right"]].set_visible(False)
        ax.grid(alpha=0.25)
    fig.tight_layout()
    fig.savefig(out / "revenue_overview.png", dpi=150)
    print(f"Saved {out / 'revenue_overview.png'}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--db", default=str(ROOT / "data/warehouse.db"))
    parser.add_argument("--out", default=str(ROOT / "docs"))
    args = parser.parse_args()
    main(args.db, args.out)
