"""
Check how much AFOS data we are ingesting
"""

import sys

from pyiem.util import get_dbconn


def check():
    """Do the check"""
    pgconn = get_dbconn("afos", user="nobody")
    icursor = pgconn.cursor()
    icursor.execute(
        "SELECT count(*) from products WHERE "
        "entered > now() - '1 hour'::interval"
    )
    row = icursor.fetchone()

    return row[0]


def main():
    """Go Main."""
    count = check()
    msg = f"{count} count |count={count};100;500;1000"
    if count > 1000:
        print(f"OK - {msg}")
        return 0
    if count > 500:
        print(f"WARNING - {msg}")
        return 1
    print(f"CRITICAL - {msg}")
    return 2


if __name__ == "__main__":
    sys.exit(main())
