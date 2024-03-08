"""Wrote my own tcptraffic nagios script, sigh"""

from __future__ import print_function

import datetime
import getpass
import json
import os
import sys


def compute_rate(old, new, seconds):
    """Compute a rate that makes sense"""
    delta = new - old
    if delta < 0:
        delta = new
    return delta / seconds


def read_stats(device):
    """read the stats"""
    fn = f"/tmp/check_tcptraffic_py_{device}_{getpass.getuser()}"
    if not os.path.isfile(fn):
        return None
    try:
        with open(fn, encoding="utf-8") as fp:
            payload = json.load(fp)
    except Exception:
        # remove the file
        os.unlink(fn)
        return None
    payload["valid"] = datetime.datetime.strptime(
        payload["valid"], "%Y-%m-%dT%H:%M:%SZ"
    )
    return payload


def write_stats(device, payload):
    """write to tmp file"""
    fn = f"/tmp/check_tcptraffic_py_{device}_{getpass.getuser()}"
    with open(fn, "w", encoding="utf-8") as fp:
        json.dump(payload, fp)


def get_stats(device):
    """Get the stats"""
    with open("/proc/net/dev", encoding="utf-8") as fp:
        lines = fp.readlines()
    for line in lines:
        if not line.strip().startswith(device + ":"):
            continue
        tokens = line.strip().split()
        if len(tokens) == 17:
            rxbytes = int(tokens[1])
            txbytes = int(tokens[9])
            payload = dict(
                valid=datetime.datetime.utcnow().strftime(
                    "%Y-%m-%dT%H:%M:%SZ"
                ),
                rxbytes=rxbytes,
                txbytes=txbytes,
                device=device,
            )
            return payload


def main(argv):
    """Go Main Go"""
    device = argv[1]
    old = read_stats(device)
    current = get_stats(device)
    if current is None:
        print("CRITICAL - nodata")
        return 2
    write_stats(device, current)
    if old is None:
        print("NOTICE - initializing counter")
        return 0
    # need to support rhel6 hosts, so no total_seconds()
    seconds = (datetime.datetime.utcnow() - old["valid"]).days * 86400 + (
        datetime.datetime.utcnow() - old["valid"]
    ).seconds
    if seconds < 1 or seconds > 700:
        print(f"NOTICE - seconds timer is too large {seconds}")
        return 0
    rxrate = compute_rate(old["rxbytes"], current["rxbytes"], seconds)
    txrate = compute_rate(old["txbytes"], current["txbytes"], seconds)

    print(
        f"TCPTRAFFIC OK - {device} RX: {(rxrate / 1e6):.4f} MB/s "
        f"TX: {(txrate / 1e6):.4f} MB/s | "
        f"TOTAL={(txrate + rxrate):.0f}B;400000000;500000000 "
        f"IN={rxrate:.0f}B;; OUT={txrate:.0f}B;; TIME={seconds:.1f};;"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
