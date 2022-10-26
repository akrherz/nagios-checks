"""Ensure that /api/ is returning results."""
import sys
from datetime import datetime

import requests

ENDPOINTS = {
    "MOS": "/mos.txt?station=KDSM&model=GFS",
    "DRYDOWN": "/drydown.json?lat=42.99&lon=-93.99",
    "BUFKIT": "/bufkit.json?lat=42.5&lon=-92.5",
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

    tt = "OK" if status_code == 200 else "CRITICAL"
    tm = (ets - sts).total_seconds()
    print(f"{tt}: {status_code} {uri} |timing={tm:.3f}s;10;5;3")
    return 0 if status_code == 200 else 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
