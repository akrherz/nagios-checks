"""Retrieve zpool statistics."""

import subprocess
import sys


def main(argv) -> int:
    """Go Main Go."""
    pool = "tank" if len(argv) == 1 else argv[1]
    with subprocess.Popen(
        ["zpool", "iostat", "-H", "-p", "-l", "-q", pool, "1", "2"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    ) as proc:
        out, err = proc.communicate()
        if proc.returncode != 0:
            print(f"Error retrieving zpool stats: {err.decode().strip()}")
            return 3
        stats = out.decode().strip().splitlines()[1]
    tokens = stats.split()
    columns = (
        "pool alloc free read_ops write_ops read_bytes write_bytes "
        "total_wait_read total_wait_write disk_wait_read disk_wait_write "
        "syncq_wait_read syncq_wait_write asyncq_wait_read asyncq_wait_write "
        "scrub_wait_read scrub_wait_write trim_wait rebuild_wait "
        "syncq_read_pend syncq_read_active "
        "syncq_write_pend syncq_write_active "
        "asyncq_read_pend asyncq_read_active "
        "asyncq_write_pend asyncq_write_active "
        "scrubq_read_pend scrubq_read_active "
        "trimq_read_pend trimq_read_active "
        "rebuildq_read_pend rebuildq_read_active"
    ).split()
    data = dict(zip(columns, tokens))
    stats = []
    for key, val in data.items():
        if key == "pool" or val == "-":
            continue
        units = ""
        if key in ["alloc", "free", "read_bytes", "write_bytes"]:
            units = "B"
        stats.append(f"{key}={data[key]}{units};;")
    freeGB = int(data["free"]) // 1_000_000_000
    msg = f"OK - zpool {pool} free: {freeGB}GB | {' '.join(stats)}"
    print(msg)

    return 0 if freeGB > 100 else 3


if __name__ == "__main__":
    sys.exit(main(sys.argv))
