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
from pathlib import Path


def find_ldmpath():
    """Figure out where LDM is."""
    for username in ["ldm", "meteor_ldm"]:
        fn = Path(f"/home/{username}/bin/ldmadmin")
        if fn.exists():
            return fn.parent
    return None


def main() -> int:
    """Go Main Go."""
    ldmpath = find_ldmpath()
    if ldmpath is None:
        print("CRITICAL - can not find ldmadmin")
        return 2
    with subprocess.Popen(
        [ldmpath / "ldmadmin", "printmetrics"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    ) as proc:
        data = proc.stdout.read().decode("ascii").strip()
    tokens = data.split()
    if len(tokens) != 18:
        print(f"CRITICAL - can not parse output {data} ")
        return 2

    # Get pqmon stats
    with subprocess.Popen(
        [ldmpath / "pqmon", "-S"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    ) as proc:
        data = proc.stdout.read().decode("ascii").strip()
    pqmon_tokens = data.split()
    if len(pqmon_tokens) != 12:
        print(f"CRITICAL - can not parse pqmon output {data} ")
        return 2

    queue_size_total = int(pqmon_tokens[1])
    queue_size_used = int(pqmon_tokens[3])
    queue_size_util = queue_size_used / queue_size_total * 100.0
    queue_slots_total = int(pqmon_tokens[4])
    queue_slots_used = int(pqmon_tokens[6])
    queue_slots_util = queue_slots_used / queue_slots_total * 100.0

    # LDM 6.14.5 corrected this to be right.
    # https://github.com/Unidata/LDM/issues/120
    server_count = int(tokens[4])
    client_count = int(tokens[5])
    queue_age = tokens[6]
    product_count = tokens[7]
    byte_count = tokens[8]

    msg = "OK"
    estatus = 0
    if client_count < 1:
        msg = "CRITICAL"
        estatus = 2
    # Ideally, the LDM queue is close to full on size, but still has some
    # slots available, so if slots > 95% and size < 75%, we have trouble
    if queue_size_util < 75 and queue_slots_util > 95:
        msg = "CRITICAL Slot Exhaustion"
        estatus = 2

    print(
        f"{msg} - Down:{client_count} Up:{server_count} Raw:{data}| "
        f"downstream={client_count};; upstream={server_count};; "
        f"queue_age={queue_age};; product_count={product_count};; "
        f"byte_count={byte_count};; queue_slot_util={queue_slots_util:.3f};; "
        f"queue_size_util={queue_size_util:.3f};;"
    )
    return estatus


if __name__ == "__main__":
    sys.exit(main())
