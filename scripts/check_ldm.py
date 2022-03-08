"""
process the output of ldmadmin printmetrics

getTime(), getLoad(), getPortCount(), getPq(), getCpu()

20121019.190728   date -u +%Y%m%d.%H%M%S
1.35 2.01 2.24    last three vals of `uptime`
49 8              downstream hosts, upstream hosts
3699 230388 7999874360  queue age, product count, byte count
21 2 77 0           $userTime, $sysTime, $idleTime, $waitTime,
49104080e3 305612e3 438048e3 $memUsed, $memFree, $swapUsed,
24137944e3 21514 $swapFree, $contextSwitches

"""
from __future__ import print_function
import subprocess
import sys
import os


def main():
    """Go Main Go."""
    for username in ["ldm", "meteor_ldm"]:
        fn = f"/home/{username}/bin/ldmadmin"
        if not os.path.isfile(fn):
            continue
        proc = subprocess.Popen([fn, "printmetrics"], stdout=subprocess.PIPE)
        break
    data = proc.stdout.read().decode("ascii")
    tokens = data.split()
    if len(tokens) != 18:
        print(f"CRITICAL - can not parse output {data} ")
        sys.exit(2)

    # We are downstream of how many hosts
    downstream = int(tokens[4])
    # We are the upstream of how many hosts
    upstream = int(tokens[5])
    queue_age = tokens[6]
    product_count = tokens[7]
    byte_count = tokens[8]

    msg = "OK"
    estatus = 0
    # CHECK that the registry has a valid netstat command not `true`!
    if downstream < 1:
        msg = "CRITICAL"
        estatus = 2
    print(
        f"{msg} - Down:{downstream} Up:{upstream} Raw:{data}| "
        f"downstream={downstream};; upstream={upstream};; "
        f"queue_age={queue_age};; product_count={product_count};; "
        f"byte_count={byte_count};;"
    )
    return estatus


if __name__ == "__main__":
    sys.exit(main())
