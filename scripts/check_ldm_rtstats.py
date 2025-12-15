"""Parse the files generated from LDM rtstats


snprintf(stats_data, sizeof(stats_data),
        "%14.14s %14.14s %32.*s %7.10s %32.*s %12.0lf %12.0lf %.8g
        %10.2f %4.0f@%4.4s %20.20s\n",
        s_time(buf, sizeof(buf), sb->recent.tv_sec),
        s_time(buf_a, sizeof(buf_a), sb->recent_a.tv_sec),
        (int)_POSIX_HOST_NAME_MAX,
        myname,
        s_feedtypet(sb->feedtype),
        (int)HOSTNAMESIZE,
        sb->origin,
        sb->nprods,
        sb->nbytes,
        d_diff_timestamp(&sb->recent_a, &sb->recent),
        sb->latency_sum/(sb->nprods == 0 ? 1: sb->nprods),
        sb->max_latency,
        s_time_abrv(sb->slowest_at),
        PACKAGE_VERSION
);


20121029204759 20121029204759
laptop.local IDS|DDPLUS
chico.unidata.ucar.edu_v_metfs1.agron.iastate.edu
8949
20333883
0.01361
982.48
2207@0001
6.10.1
"""

import glob
import os
import stat
import sys
from datetime import datetime


def get_fileage(fn):
    """Return the age of the file in seconds"""
    now = datetime.now()
    mtime = os.stat(fn)[stat.ST_MTIME]
    ts = datetime.fromtimestamp(mtime)
    return (now - ts).total_seconds()


def runner(hostname: str, feedtype: str):
    """Do something!"""
    for username in ["ldm", "meteor_ldm"]:
        mm = feedtype if feedtype != "IDS" else "IDS|DDPLUS"
        mydir = f"/home/{username}/rtstats/{hostname}/{mm}"
        if os.path.isdir(mydir):
            os.chdir(mydir)
            break
    min_latency = 1e6
    tot_bytes = 0
    tot_prods = 0
    time_threshold = 120 if feedtype in ["CONDUIT", "LIGHTNING"] else 15
    for fn in glob.glob("*_v_*"):
        # Skip a local feed
        if fn.find("missouri") > -1:
            continue
        age = get_fileage(fn)
        if age > (time_threshold * 60):
            continue
        with open(fn, encoding="utf-8") as fp:
            line = fp.read()
            tokens = line.split()
            tot_prods += float(tokens[5])
            tot_bytes += float(tokens[6])
            latency = float(tokens[7])
            # Don't trust values below zero, likely bad clocks
            if latency > 0:
                min_latency = min([latency, min_latency])

    exitcode = 2
    msg = f"LDM {feedtype} latency {min_latency:.4f}s"
    thresholds = [300, 1200]
    if feedtype == "CONDUIT":
        thresholds = [600, 2400]
    elif feedtype == "LIGHTNING":
        thresholds = [1200, 3600]
    if min_latency < thresholds[0]:
        exitcode = 0
    elif min_latency < thresholds[1]:
        exitcode = 1
    tt = f"{min_latency:.4f}" if min_latency < 1e6 else "U"
    stats = (
        f"prods={tot_prods:.0f};;;0; bytes={tot_bytes:.0f}B;;;; "
        f"latency={tt};;;;"
    )
    print(f"{msg} | {stats}")
    return exitcode


def main(argv):
    """Run for a given hostname and feedtype."""
    if len(argv) < 3:
        print("Usage: python check_ldm_rtstats.py <hostname> <feedtype>")
        return 2
    return runner(argv[1], argv[2])


if __name__ == "__main__":
    sys.exit(main(sys.argv))
