"""Ensure that /api/ is returning results."""
import sys
from datetime import datetime

import requests

ENDPOINTS = {
    "MOS": "/mos.txt?station=KDSM&model=GFS",
    "DRYDOWN": "/drydown.json?lat=42.99&lon=-93.99",
}


def main(argv):
    """Go Main Go."""
    uri = f"http://iem-web-services.local:8000{ENDPOINTS[argv[1]]}"
    sts = datetime.utcnow()
    try:
        req = requests.get(uri, timeout=20)
        status_code = req.status_code
    except Exception:
        status_code = 999
    ets = datetime.utcnow()

    msg = "%s: %s %s |timing=%.3fs;10;5;3" % (
        "OK" if status_code == 200 else "CRITICAL",
        status_code,
        uri,
        (ets - sts).total_seconds(),
    )
    print(msg)
    return 0 if status_code == 200 else 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
