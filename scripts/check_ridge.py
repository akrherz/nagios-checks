"""
Make sure we have current RIDGE imagery
"""

import sys
from datetime import datetime
from pathlib import Path

SAMPLES = ["DVN", "GRK", "ABC", "DTX", "HTX", "LOT", "TLX"]


def check():
    """Check things."""
    now = datetime.now()
    count = []
    for nexrad in SAMPLES:
        fn = Path(f"/mesonet/ldmdata/gis/images/4326/ridge/{nexrad}/N0B_0.png")
        if not fn.exists():
            count.append(nexrad)
            continue
        mtime = fn.stat().st_mtime
        ts = datetime.fromtimestamp(mtime)
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
