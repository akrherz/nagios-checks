"""
 Make sure we have current RIDGE imagery
"""
import os
import sys
import stat
import datetime

SAMPLES = ["DVN", "GRK", "ABC", "DTX", "HTX", "LOT", "TLX"]


def check():
    """Check things."""
    now = datetime.datetime.now()
    count = []
    for nexrad in SAMPLES:
        fn = f"/mesonet/ldmdata/gis/images/4326/ridge/{nexrad}/N0Q_0.png"
        mtime = os.stat(fn)[stat.ST_MTIME]
        ts = datetime.datetime.fromtimestamp(mtime)
        diff = (now - ts).days * 86400.0 + (now - ts).seconds
        if diff > 600:
            count.append(nexrad)
    return count


def main():
    """Go Main Go."""
    badcount = check()
    msg = f"{len(badcount)}/{len(SAMPLES)} outage {','.join(badcount)}"
    if len(badcount) < 5:
        print(f"OK - {msg}")
        status = 0
    elif len(badcount) < 7:
        print(f"WARNING - {msg}")
        status = 1
    else:
        print(f"CRITICAL - {msg}")
        status = 2
    return status


if __name__ == "__main__":
    sys.exit(main())
