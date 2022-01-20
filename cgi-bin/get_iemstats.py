#!/usr/bin/env python
"""Get nagios stats.

NOTE: This needs to be exec for apache to use for CGI
"""
import json
import datetime
import sys

import rrdtool


def get_reqs(j):
    """Get requests"""
    count = 0
    for i in range(100, 110):
        fn = f"/var/lib/pnp4nagios/iemvs{i:03d}/Apache_Stats_II.rrd"
        ts = rrdtool.last(fn)
        data = rrdtool.fetch(fn, "AVERAGE", "-s", str(ts - 300), "-e", str(ts))
        samples = data[2]
        if len(samples) < 2:
            continue
        count += samples[-2][13]

    j["stats"]["apache_req_per_sec"] = count


def get_bandwidth(j):
    """get bandwith"""
    fn = "/var/lib/pnp4nagios/iem-director0/eth0.rrd"

    ts = rrdtool.last(fn)
    data = rrdtool.fetch(fn, "AVERAGE", "-s", str(ts - 300), "-e", str(ts))
    samples = data[2]

    fn = "/var/lib/pnp4nagios/iem-director1/eth0.rrd"
    ts = rrdtool.last(fn)
    data = rrdtool.fetch(fn, "AVERAGE", "-s", str(ts - 300), "-e", str(ts))
    samples2 = data[2]
    j["stats"]["bandwidth"] = samples[-2][2] + samples2[-2][2]


def main():
    """Go Main Go"""
    j = {
        "stats": {},
        "valid": datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
    }
    get_reqs(j)
    get_bandwidth(j)
    sys.stdout.write("Content-type: text/plain\n\n")
    sys.stdout.write(json.dumps(j))


if __name__ == "__main__":
    main()
