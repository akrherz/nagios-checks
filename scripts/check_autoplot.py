"""Check autoplot stats"""

import sys

from pyiem.util import get_dbconn


def main():
    """Go Main Go"""
    pgconn = get_dbconn("mesosite", user="nobody")
    cursor = pgconn.cursor()
    cursor.execute(
        "select count(*), avg(timing) from autoplot_timing "
        "where valid > now() - '4 hours'::interval"
    )
    (count, speed) = cursor.fetchone()
    speed = 0 if speed is None else speed

    print(
        f"Autoplot cnt:{count} speed:{speed:.2f} | "
        f"COUNT={count};; SPEED={speed:.3f};;"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
