"""
Make sure our nexrad files are current!
"""

import datetime
import os
import stat
import sys

SAMPLES = ["KDMX", "KAMA", "KLWX", "KFFC", "KBMX", "KBGM", "KCLE"]


def check():
    """Check things please"""
    now = datetime.datetime.now()
    missing = []
    for nexrad in SAMPLES:
        fn = f"/mnt/level2/raw/{nexrad}/dir.list"
        if not os.path.isfile(fn):
            missing.append(nexrad)
            continue
        mtime = os.stat(fn)[stat.ST_MTIME]
        ts = datetime.datetime.fromtimestamp(mtime)
        diff = (now - ts).days * 86400.0 + (now - ts).seconds
        if diff > 300:
            missing.append(nexrad)
    return missing


def main():
    """Go Main Go"""
    badcount = check()
    msg = f"{len(badcount)}/{len(SAMPLES)} outage {','.join(badcount)}"
    if len(badcount) < 3:
        print(f"OK - {msg}")
        return 0
    elif len(badcount) < 4:
        print(f"WARNING - {msg}")
        return 1
    else:
        print(f"CRITICAL - {msg}")
        return 2


if __name__ == "__main__":
    sys.exit(main())
