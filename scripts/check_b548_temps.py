"""
Gateway for B548 temps to nagios, this way I can setup alerts via it

Array("In Air Handler", "Out Air Handler", "Out Rack", "In Rack")
0 70.25
1 57.88
2 88.25
3 62.04
"""

import os
import sys


def main():
    """Go Main Go."""
    fn = "/home/meteor_ldm/onewire/onewire.txt"
    if not os.path.isfile(fn):
        print(f"ERROR: {fn} does not exist")
        return 2
    with open(fn, "r", encoding="utf-8") as fh:
        data = fh.readlines()
    if len(data) != 4:
        print("WARNING - Could not read file!")
        return 1

    v = []
    for line in data:
        tokens = line.strip().split()
        if len(tokens) == 2:
            v.append(float(tokens[1]))
        else:
            v.append(-99)

    ds = ""
    ks = ["in_handler", "out_handler", "out_rack", "in_rack"]
    maxes = [80, 70, 100, 75]
    msg = ""
    for k, d, m in zip(ks, v, maxes):
        ds += f"{k}={d};{m};{m + 5};{m + 10} "
        msg += f"{k} {d},"
    if v[3] < 75:
        print(f"OK - {msg} |{ds}")
        status = 0
    elif v[3] < 80:
        print(f"WARNING - {msg} |%{ds}")
        status = 1
    else:
        print(f"CRITICAL - {msg} |{ds}")
        status = 2
    return status


if __name__ == "__main__":
    sys.exit(main())
