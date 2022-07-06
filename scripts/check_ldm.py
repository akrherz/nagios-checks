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
import subprocess
import sys
import os


def find_ldmpath():
    """Figure out where LDM is."""
    for username in ["ldm", "meteor_ldm"]:
        fn = f"/home/{username}/bin/ldmadmin"
        if os.path.isfile(fn):
            return f"/home/{username}/bin"
    return None


def main():
    """Go Main Go."""
    ldmpath = find_ldmpath()
    with subprocess.Popen(
        [f"{ldmpath}/ldmadmin", "printmetrics"],
        stdout=subprocess.PIPE,
    ) as proc:
        data = proc.stdout.read().decode("ascii").strip()
    tokens = data.split()
    if len(tokens) != 18:
        print(f"CRITICAL - can not parse output {data} ")
        sys.exit(2)

    # Get pqmon stats
    with subprocess.Popen(
        [f"{ldmpath}/pqmon", "-S"],
        stdout=subprocess.PIPE,
    ) as proc:
        data = proc.stdout.read().decode("ascii").strip()
    pqmon_tokens = data.split()
    if len(pqmon_tokens) != 12:
        print(f"CRITICAL - can not parse pqmon output {data} ")
        sys.exit(2)

    queue_size_total = int(pqmon_tokens[1])
    queue_size_used = int(pqmon_tokens[3])
    queue_size_util = queue_size_used / queue_size_total * 100.0
    queue_slots_total = int(pqmon_tokens[4])
    queue_slots_used = int(pqmon_tokens[6])
    queue_slots_util = queue_slots_used / queue_slots_total * 100.0

    # We are downstream of how many hosts
    downstream = int(tokens[4])
    # We are the upstream of how many hosts
    upstream = int(tokens[5])
    queue_age = tokens[6]
    product_count = tokens[7]
    byte_count = tokens[8]

    msg = "OK"
    estatus = 0
    if downstream < 1:
        msg = "CRITICAL"
        estatus = 2
    # Ideally, the LDM queue is close to full on size, but still has some
    # slots available, so if slots > 95% and size < 75%, we have trouble
    if queue_size_util < 75 and queue_slots_util > 95:
        msg = "CRITICAL Slot Exhaustion"
        estatus = 2

    print(
        f"{msg} - Down:{downstream} Up:{upstream} Raw:{data}| "
        f"downstream={downstream};; upstream={upstream};; "
        f"queue_age={queue_age};; product_count={product_count};; "
        f"byte_count={byte_count};; queue_slot_util={queue_slots_util:.3f};; "
        f"queue_size_util={queue_size_util:.3f};;"
    )
    return estatus


if __name__ == "__main__":
    sys.exit(main())
