#!/usr/bin/env python
"""Get nagios stats.

NOTE: This needs to be exec for apache to use for CGI
"""

import json
import sys
from datetime import datetime

import rrdtool


def process_fn(fn):
    """Get what we want."""
    ts = rrdtool.last(fn)
    data = rrdtool.fetch(fn, "AVERAGE", "-s", str(ts - 300), "-e", str(ts))
    samples = data[2]
    if len(samples) < 2:
        return 0, 0
    # req/s bytes/s
    return samples[-2][13], samples[-2][15]


def get_reqs(j):
    """Get requests"""
    count = 0
    bytes = 0
    for i in range(35, 45):
        fn = f"/var/lib/pnp4nagios/iemvs{i}-dc/Apache_Stats_II.rrd"
        vals = process_fn(fn)
        count += vals[0]
        bytes += vals[1]

    j["stats"]["apache_req_per_sec"] = count
    j["stats"]["bandwidth"] = bytes


def get_telemetry(j):
    """Add telemetry stats."""
    fn = "/var/lib/pnp4nagios/mesonet/telemetry.rrd"
    ts = rrdtool.last(fn)
    data = rrdtool.fetch(fn, "AVERAGE", "-s", str(ts - 300), "-e", str(ts))[2][
        0
    ]
    j["stats"]["telemetry_rate"] = data[0]
    j["stats"]["telemetry_ok"] = data[4]


def main():
    """Go Main Go"""
    j = {
        "stats": {},
        "valid": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
    }
    get_reqs(j)
    get_telemetry(j)
    sys.stdout.write("Content-type: text/plain\n\n")
    sys.stdout.write(json.dumps(j))


if __name__ == "__main__":
    main()
