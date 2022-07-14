"""Ensure iembot is up."""
import sys

import requests


def main():
    """Go Main Go."""
    try:
        req = requests.get("http://iembot:9003/status")
    except Exception as exp:
        print(f"CRITICAL - {exp}")
        return 2
    if req.status_code == 200:
        js = req.json()
        msg = f"working: {js['threadpool.working']}/{js['threadpool.max']}"
        status = 0
        if (js["threadpool.max"] - js["threadpool.working"]) < 10:
            status = 2
        print(f"{msg} |thread_working={js['threadpool.working']};;;")
        return status
    print(f"CRITICAL - /room/kdmx.xml returned code {req.status_code}")
    return 2


if __name__ == "__main__":
    sys.exit(main())
