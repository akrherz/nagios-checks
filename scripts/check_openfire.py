"""Ensure that Openfire is somewhat running"""

import sys

import httpx


def main() -> int:
    """Go Main Go"""
    try:
        resp = httpx.get("http://xmpp.weather.im:7070")
        resp.raise_for_status()
    except Exception as exp:
        print(f"FATAL - {exp}")
        return 2
    print("OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
