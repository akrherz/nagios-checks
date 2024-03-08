"""Make sure we are producing webcam lapses!"""

import datetime
import os
import stat
import sys

BASEDIR = "/mesonet/share/lapses/auto"


def check():
    """Do the actual check"""
    good = 0
    now = datetime.datetime.now()
    for filename in os.listdir(BASEDIR):
        fn = f"{BASEDIR}/{filename}"
        mtime = os.stat(fn)[stat.ST_MTIME]
        ts = datetime.datetime.fromtimestamp(mtime)
        diff = (now - ts).days * 86400.0 + (now - ts).seconds
        if diff < 86400:
            good += 1
    return good


def main():
    """Go Main Go."""
    good = check()
    msg = f"{good} good lapses"
    if good > 30:
        print(f"OK - {msg}")
        return 0
    print(f"CRITICAL - {msg}")
    return 2


if __name__ == "__main__":
    sys.exit(main())
