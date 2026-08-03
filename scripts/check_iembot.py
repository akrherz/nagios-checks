"""Ensure iembot is up."""

import sys
from datetime import datetime

import requests


def main():
    """Go Main Go."""
    try:
        sts = datetime.now()
        resp = requests.get("http://iembot:9003/status", timeout=30)
        timing = (datetime.now() - sts).total_seconds()
    except Exception as exp:
        print(f"CRITICAL - {exp}")
        return 2
    if resp.status_code == 200:
        js = resp.json()
        msg = (
            f"working: {js['threadpool.working']}/{js['threadpool.max']} "
            f"in {timing:.4f}s"
        )
        status = 0
        if (js["threadpool.max"] - js["threadpool.working"]) < 10:
            status = 2
        print(
            f"{msg} |thread_working={js['threadpool.working']};;;; "
            f"timing={timing:.4f};10;5;3;"
        )
        return status
    print(f"CRITICAL - /status returned code {resp.status_code}")
    return 2


if __name__ == "__main__":
    sys.exit(main())
