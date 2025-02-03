"""
A crude check for IEM Webfarm nodes against the NFS archive.
"""

import pathlib
import random
import sys
from datetime import datetime, timedelta


def main():
    """Go Main Go."""
    # Pick a time modulo five over the past 3 days
    now = datetime.now() - timedelta(minutes=10)
    now = now.replace(minute=0)
    offset = random.randint(0, 12 * 24 * 3) * 5
    now = now - timedelta(minutes=offset)
    pngfn = (
        f"/mesonet/ARCHIVE/data/{now:%Y/%m/%d}/GIS/uscomp/n0q_"
        f"{now:%Y%m%d%H%M}.png"
    )
    # Check 1, stat
    sts = datetime.now()
    pathlib.Path(pngfn).stat
    stat_secs = (datetime.now() - sts).total_seconds()

    # Check 2, read
    sts = datetime.now()
    with open(pngfn, "rb") as fh:
        fh.read()
    read_secs = (datetime.now() - sts).total_seconds()

    maxsecs = max([stat_secs, read_secs])
    msg = (
        f"N0Q Read {now:%Y%m%d %H%M} |"
        f"read_secs={read_secs:.6f};2;5;10 "
        f"stat_secs={stat_secs:.6f};2;5;10 "
    )
    if maxsecs < 2:
        print(f"OK - {msg}")
        return 0
    if maxsecs > 5:
        print(f"CRITICAL - {msg}")
        return 2
    print(f"WARNING - {msg}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
