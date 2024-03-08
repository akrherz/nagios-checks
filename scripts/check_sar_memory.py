"""Capture some stats from sar memory"""

import subprocess
import sys


def process(res):
    """Parse and do stuff with the output"""
    lines = res.strip().split("\n")
    if len(lines) < 2 or not lines[-1].startswith("Average:"):
        print(f"CRITICAL: ERROR {'|'.join(lines)}")
        sys.exit(2)
    tokens = lines[-1].strip().split()
    print(
        f"OK: Memory free: {tokens[1]} | KBMEMFREE={tokens[1]};;;; "
        f"KBMEMUSED={tokens[2]};;;; MEMUSED={tokens[3]};;;; "
        f"KBBUFFERS={tokens[4]};;;; KBCACHED={tokens[5]};;;; "
        f"KBCOMMIT={tokens[6]};;;; COMMIT={tokens[7]};;;; "
        f"KBACTIVE={tokens[8]};;;; KBBINACT={tokens[9]};;;; "
        f"KBDIRTY={tokens[10]};;;; "
    )
    status = 0
    if float(tokens[1]) < 150000:
        status = 2
    elif float(tokens[1]) < 200000:
        status = 1
    return status


def main():
    """Do Something"""
    with subprocess.Popen(
        ["sar", "-r", "1", "5"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    ) as proc:
        stdout = proc.stdout.read().decode("ascii")
    return process(stdout)


if __name__ == "__main__":
    sys.exit(main())
