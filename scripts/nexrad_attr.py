"""Nagios check to make sure we have NEXRAD attribute data"""
import sys

from pyiem.util import get_dbconn


def main():
    """Go Main Go"""
    pgconn = get_dbconn("radar", user="nobody")
    pcursor = pgconn.cursor()

    pcursor.execute(
        "select count(*) from nexrad_attributes WHERE "
        "valid > now() - '30 minutes'::interval"
    )
    row = pcursor.fetchone()
    count = row[0]

    msg = f"L3 NEXRAD attr count {count} |count={count};2;1;0"
    if count > 2:
        print(f"OK - {msg}")
        return 0
    if count > 1:
        print(f"OK - {msg}")
        return 1
    print(f"CRITICAL - {msg}")
    return 2


if __name__ == "__main__":
    sys.exit(main())
