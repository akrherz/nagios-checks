"""
Check how much HADS data we have
"""

import sys

from pyiem.util import get_dbconn

IEM = get_dbconn("iem", user="nobody")
icursor = IEM.cursor()


def check():
    """check!"""
    icursor.execute(
        "SELECT count(*) from current_shef "
        "WHERE valid > now() - '1 hour'::interval"
    )
    row = icursor.fetchone()

    return row[0]


def main():
    """Go Main."""
    count = check()
    stats = f"{count} count |count={count};1000;5000;10000"
    if count > 10000:
        print(f"OK - {stats}")
        return 0
    if count > 5000:
        print(f"WARNING - {stats}")
        return 1
    print(f"CRITICAL  - {stats}")
    return 2


if __name__ == "__main__":
    sys.exit(main())
