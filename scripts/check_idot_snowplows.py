"""
Nagios check to see how much snowplow data we are currently ingesting
"""

import sys
from datetime import date

from pyiem.database import get_dbconn


def main():
    """Do Great Things"""
    pgconn = get_dbconn("postgis", user="nobody")
    pcursor = pgconn.cursor()

    pcursor.execute(
        """
        select sum(case when valid > now() - '30 minutes'::interval
            then 1 else 0 end),
         sum(case when valid > now() - '1 day'::interval then 1 else 0 end)
         from idot_snowplow_current
    """
    )
    row = pcursor.fetchone()
    count = row[0]
    daycount = row[1]

    msg = (
        f"snowplows {count}/{daycount} |"
        f"count={count};2;1;0 daycount={daycount};2;1;0"
    )
    today = date.today()
    # Don't complain on offseason or weekend
    if today.month in (4, 5, 6, 7, 8, 9, 10) or today.isoweekday() in (6, 7):
        print(f"OK - {msg}")
        sys.exit(0)
    elif daycount > 2:
        print(f"OK - {msg}")
        sys.exit(0)
    elif daycount > 1:
        print(f"OK - {msg}")
        sys.exit(1)
    print(f"CRITICAL - {msg}")
    sys.exit(2)


if __name__ == "__main__":
    main()
