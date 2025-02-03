"""Check to make sure we have HRRR model data flowing to the IEM archives"""

import os
import sys
from datetime import datetime, timedelta, timezone


def check():
    """Do the chec please"""
    now = datetime.now(timezone.utc)
    diff = None
    for hr in range(8):
        fn = now.strftime(
            "/mesonet/ARCHIVE/data/%Y/%m/%d/model/hrrr/%H/"
            "hrrr.t%Hz.3kmf00.grib2"
        )
        now = now - timedelta(hours=1)
        if not os.path.isfile(fn):
            continue
        diff = hr
        break

    return diff, now


def main():
    """Go Main Go"""
    diff, now = check()
    stats = f"|age={diff if diff is not None else -1};4;5;6"
    if diff is not None and diff < 6:
        print(f"OK - {now:%H}z found {stats}")
        status = 0
    elif diff is not None:
        print(f"WARNING - {now:%H}z found {stats}")
        status = 1
    else:
        print(f"CRITICAL - no HRRR found {stats}")
        status = 2
    return status


if __name__ == "__main__":
    sys.exit(main())
