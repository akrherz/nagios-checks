"""
Make sure we have archived N0R/N0Q so that things do not freak out!
"""

import os
import sys
from datetime import datetime, timedelta, timezone


def main(argv) -> int:
    """Do Great Things!"""
    if len(argv) != 2:
        print(f"Usage: {argv[0]} N0R|N0Q")
        return 2
    prod = argv[1]
    now = datetime.now(timezone.utc)
    now = now - timedelta(minutes=now.minute % 5)
    base = now

    miss = []
    for _ in range(12):
        fn = now.strftime(
            f"/mesonet/ARCHIVE/data/%Y/%m/%d/GIS/uscomp/{prod}_%Y%m%d%H%M.png"
        )
        if not os.path.isfile(fn):
            miss.append(now.strftime("%Y%m%d_%H%M"))
        now -= timedelta(minutes=5)

    if not miss:
        print("OK")
        return 0
    print(f"CRITICAL - {base:%d_%H%M} archive miss {prod} {', '.join(miss)}")
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
