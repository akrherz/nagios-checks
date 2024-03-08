"""Check website_telemetry"""

import sys

import pandas as pd
from pyiem.util import get_sqlalchemy_conn


def main():
    """Go Main Go"""
    with get_sqlalchemy_conn("mesosite", user="nobody") as conn:
        df = pd.read_sql(
            "select timing, status_code from website_telemetry "
            "where valid > now() - '5 minutes'::interval",
            conn,
        )
    size = len(df.index)
    # HTTP 500 is deliniated as uncaught exception
    ok = 100.0 - len(df[df["status_code"] == 500].index) / size * 100.0
    levels = df["timing"].quantile([0.5, 0.95, 0.99])

    print(
        f"Telemetry OK: {ok:.2f}% rate:{len(df.index) / 300.:.4f} "
        f"mean:{levels[0.50]:.5f} | "
        f"RATE={len(df.index) / 300.:.4f};; MEAN={levels[0.5]:.5f};; "
        f"P95={levels[0.95]:.5f};; P99={levels[0.99]:.5f};; "
        f"OK={ok:.5f};;"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
