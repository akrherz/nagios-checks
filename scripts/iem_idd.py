"""
 Nagios check to make sure we have data flowing through LDM
"""
import sys
import os
import stat
import datetime


def main():
    """Go Main Go."""
    FN = "/mesonet/ldmdata/gis/images/4326/USCOMP/n0q_0.png"
    now = datetime.datetime.now()
    mtime = os.stat(FN)[stat.ST_MTIME]
    ts = datetime.datetime.fromtimestamp(mtime)
    diff = (now - ts).days * 86400.0 + (now - ts).seconds
    if diff < 600:
        print("OK - n0q_0.png %s" % (ts,))
        status = 0
    elif diff < 700:
        print("WARNING - n0q_0.png %s" % (ts,))
        status = 1
    else:
        print("CRITICAL - n0q_0.png %s" % (ts,))
        status = 2
    return status


if __name__ == "__main__":
    sys.exit(main())
