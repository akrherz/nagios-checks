"""
Measure how fast the ASOS database is responding to queries for data!
"""

import sys
from datetime import datetime

from pyiem.database import get_sqlalchemy_conn, sql_helper


def check():
    """Do the check"""
    with get_sqlalchemy_conn("asos", user="nobody") as pgconn:
        res = pgconn.execute(
            sql_helper(
                """
        SELECT station, count(*), min(tmpf), max(tmpf)
        from {table} WHERE station =
        (select id from stations where network ~* 'ASOS' and online and
        archive_begin < '1980-01-01'
        ORDER by random() ASC LIMIT 1) GROUP by station
        """,
                table=f"t{datetime.now().year}",
            )
        )
        row = res.fetchone()
    if row is None:
        return "XXX", 0
    return row[0], row[1]


def main():
    """Go Main"""
    t0 = datetime.now()
    station, count = check()
    t1 = datetime.now()
    delta = (t1 - t0).seconds + float((t1 - t0).microseconds) / 1000000.0
    msg = f"{station} {count} |qtime={delta:.3f};5;10;15"
    if delta < 5:
        print(f"OK - {msg}")
        return 0
    if delta < 10:
        print(f"WARNING - {msg}")
        return 1
    print(f"CRITICAL - {msg}")
    return 2


if __name__ == "__main__":
    sys.exit(main())
