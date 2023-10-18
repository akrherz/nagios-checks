"""Check website_telemetry"""
import sys

import pandas as pd
from pyiem.util import get_sqlalchemy_conn


def main():
    """Go Main Go"""
    with get_sqlalchemy_conn("mesosite", user="nobody") as conn:
        df = pd.read_sql(
            "select timing from website_telemetry "
            "where valid > now() - '5 minutes'::interval",
            conn,
        )
    levels = df["timing"].quantile([0.5, 0.95, 0.99])

    print(
        f"Telemetry rate:{len(df.index) / 300.:.4f} "
        f"mean:{levels[0.50]:.5f} | "
        f"RATE={len(df.index) / 300.:.4f};; MEAN={levels[0.5]:.5f};; "
        f"P95={levels[0.95]:.5f};; P99={levels[0.99]:.5f};;"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
