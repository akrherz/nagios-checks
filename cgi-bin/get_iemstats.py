#!/usr/bin/env python
"""Get nagios stats.

NOTE: This needs to be exec for apache to use for CGI
"""
import datetime
import json
import sys

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


def main():
    """Go Main Go"""
    j = {
        "stats": {},
        "valid": datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
    }
    get_reqs(j)
    sys.stdout.write("Content-type: text/plain\n\n")
    sys.stdout.write(json.dumps(j))


if __name__ == "__main__":
    main()
