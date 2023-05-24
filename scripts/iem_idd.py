"""
 Nagios check to make sure we have data flowing through LDM
"""
import datetime
import json
import os
import stat
import sys


def main():
    """Go Main Go."""
    fn = "/mesonet/ldmdata/gis/images/4326/USCOMP/n0q_0.png"
    # Ensure that our JSON file is working too per 23 May 2023 explosion
    with open(fn.replace("png", "json"), encoding="ascii") as fh:
        data = json.load(fh)
    fmt = "%Y-%m-%dT%H:%M:%SZ"
    valid = datetime.datetime.strptime(data["meta"]["valid"], fmt)
    valid = valid.replace(tzinfo=datetime.timezone.utc)
    now = datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc)
    mtime = os.stat(fn)[stat.ST_MTIME]
    ts = datetime.datetime.fromtimestamp(mtime, tz=datetime.timezone.utc)
    ts = min([ts, valid])
    diff = (now - ts).days * 86400.0 + (now - ts).seconds
    if diff < 600:
        print(f"OK - n0q_0.png {ts}")
        status = 0
    elif diff < 700:
        print(f"WARNING - n0q_0.png {ts}")
        status = 1
    else:
        print(f"CRITICAL - n0q_0.png {ts}")
        status = 2
    return status


if __name__ == "__main__":
    sys.exit(main())
