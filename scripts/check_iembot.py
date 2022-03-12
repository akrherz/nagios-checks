"""Ensure iembot is up."""
import sys

import requests


def main():
    """Go Main Go."""
    try:
        req = requests.get("http://iembot:9004/room/kdmx.xml")
    except Exception as exp:
        print(f"CRITICAL - {exp}")
        return 2
    if req.status_code == 200:
        print(f"OK - len(kdmx.xml) is {len(req.content)}")
        return 0
    print(f"CRITICAL - /room/kdmx.xml returned code {req.status_code}")
    return 2


if __name__ == "__main__":
    sys.exit(main())
