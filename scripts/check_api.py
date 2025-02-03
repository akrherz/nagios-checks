"""Ensure that /api/ is returning results."""

import sys
from datetime import datetime, timezone

import httpx

ENDPOINTS = {
    "MOS": "/mos.txt?station=KDSM&model=GFS",
    "DRYDOWN": "/drydown.json?lat=42.99&lon=-93.99",
    "BUFKIT": "/nws/bufkit.json?lat=42.5&lon=-92.5",
}


def main(argv):
    """Go Main Go."""
    uri = f"https://iem-web-services.agron.iastate.edu{ENDPOINTS[argv[1]]}"
    sts = datetime.now(timezone.utc)
    try:
        req = httpx.get(uri, timeout=20)
        status_code = req.status_code
    except Exception:
        status_code = 999
    ets = datetime.now(timezone.utc)

    tt = "OK" if status_code == 200 else "CRITICAL"
    tm = (ets - sts).total_seconds()
    print(f"{tt}: {status_code} {uri} |timing={tm:.3f}s;10;5;3")
    return 0 if status_code == 200 else 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
