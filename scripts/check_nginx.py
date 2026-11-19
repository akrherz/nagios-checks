"""Check what nginux stub_status reports."""

import getpass
import json
import re
import sys
from datetime import datetime, timezone

import requests

STATUS = re.compile(
    r"Active connections: (\d+)\s*\n"
    r"server accepts handled requests\s*\n"
    r" (\d+) (\d+) (\d+)\s*\n"
    r"Reading: (\d+) Writing: (\d+) Waiting: (\d+)"
)


def write_stats(payload: dict):
    """Write to disk for later processing."""
    fn = f"/tmp/check_nginx_{getpass.getuser()}.json"
    with open(fn, "w", encoding="utf-8") as fp:
        json.dump(payload, fp)


def read_stats():
    """Read the stats from disk."""
    fn = f"/tmp/check_nginx_{getpass.getuser()}.json"
    with open(fn, encoding="utf-8") as fp:
        return json.load(fp)


def main(argv: list[str]):
    """Go Main Go."""
    port = 80
    if len(argv) > 1:
        port = int(argv[1])
    try:
        last = read_stats()
    except Exception:
        last = None
    try:
        resp = requests.get(
            f"http://localhost:{port}/nginx_status", timeout=30
        )
        resp.raise_for_status()
    except Exception as exp:
        print(f"CRITICAL - {exp}")
        return 2
    m = STATUS.match(resp.text)
    if not m:
        print(f"CRITICAL - failed to parse {resp.text}")
        return 2
    present = {
        "timestamp": datetime.now(timezone.utc).timestamp(),
    }
    (
        present["connections"],
        present["accepts"],
        present["handled"],
        present["requests"],
        present["reading"],
        present["writing"],
        present["waiting"],
    ) = m.groups()
    write_stats(present)
    if last is None:
        print("OK - first run")
        return 0
    diff = max(1, present["timestamp"] - last["timestamp"])
    dh = max(0, int(present["handled"]) - int(last["handled"]))
    dr = max(0, int(present["requests"]) - int(last["requests"]))
    print(
        f"nginx |connections={present['connections']};;;; "
        f"reading={present['reading']};;;; "
        f"writing={present['writing']};;;; "
        f"waiting={present['waiting']};;;; "
        f"handled_per_sec={dh / diff:.2f};;;; "
        f"requests_per_sec={dr / diff:.2f};;;; "
    )
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
