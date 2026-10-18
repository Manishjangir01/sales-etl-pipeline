"""Generate a messy synthetic sales dataset to simulate a raw source system."""
import argparse
import random
from datetime import date, timedelta
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent

PRODUCTS = {
    "Laptop": 55000,
    "Phone": 22000,
    "Headphones": 3500,
    "Monitor": 12000,
    "Keyboard": 1800,
    "Mouse": 900,
}
CITIES = ["Jaipur", "Delhi", "Mumbai", "Bengaluru", "Pune", "Chennai"]


def generate(n_rows: int = 1000, seed: int = 42) -> pd.DataFrame:
    rng = random.Random(seed)
    start = date(2026, 1, 1)
    rows = []
    for i in range(1, n_rows + 1):
        product = rng.choice(list(PRODUCTS))
        rows.append(
            {
                "order_id": 1000 + i,
                "order_date": (start + timedelta(days=rng.randint(0, 270))).isoformat(),
                "customer_id": f"C{rng.randint(1, 200):04d}",
                "city": rng.choice(CITIES),
                "product": product,
                "quantity": rng.randint(1, 5),
                "unit_price": PRODUCTS[product],
            }
        )
    df = pd.DataFrame(rows)

    # Inject realistic data quality problems
    df.loc[df.sample(frac=0.03, random_state=seed).index, "city"] = None
    df.loc[df.sample(frac=0.02, random_state=seed + 1).index, "quantity"] = -1
    df.loc[df.sample(frac=0.02, random_state=seed + 2).index, "city"] = (
        df["city"].str.upper()
    )
    df = pd.concat([df, df.sample(frac=0.02, random_state=seed + 3)])  # duplicates
    return df.sample(frac=1, random_state=seed).reset_index(drop=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--rows", type=int, default=1000)
    parser.add_argument("--out", default=str(ROOT / "data/raw/sales_raw.csv"))
    args = parser.parse_args()
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    generate(args.rows).to_csv(out, index=False)
    print(f"Wrote {args.rows} raw rows to {out}")
