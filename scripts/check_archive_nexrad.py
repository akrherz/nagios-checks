"""
Make sure we have archived N0R/N0Q so that things do not freak out!
"""
import datetime
import os
import sys


def main(argv):
    """Do Great Things!"""
    prod = argv[1]
    now = datetime.datetime.utcnow()
    now = now - datetime.timedelta(minutes=now.minute % 5)
    base = now

    miss = []
    for _ in range(12):
        fn = now.strftime(
            f"/mesonet/ARCHIVE/data/%Y/%m/%d/GIS/uscomp/{prod}_%Y%m%d%H%M.png"
        )
        if not os.path.isfile(fn):
            miss.append(now.strftime("%Y%m%d_%H%M"))
        now -= datetime.timedelta(minutes=5)

    if not miss:
        print("OK")
        return 0
    print(f"CRITICAL - {base:%d_%H%M} archive miss {prod} {', '.join(miss)}")
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
