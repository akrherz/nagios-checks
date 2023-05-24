"""Audit the NOAAPort data flow."""
import sys
from datetime import timedelta

from pyiem.util import get_dbconn, utc


def main():
    """Do some auditing."""
    utcnow = utc().replace(second=0, microsecond=0)
    # Go find this product in the afos database
    cursor = get_dbconn("id3b", user="nobody").cursor()
    cursor.execute(
        "SELECT entered_at, valid_at, wmo_valid_at, awips_id from "
        "ldm_product_log where awips_id in ('TSTNCF', 'WTSNCF') and "
        "entered_at > %s ORDER by wmo_valid_at DESC LIMIT 1",
        (utcnow - timedelta(minutes=15),),
    )
    if cursor.rowcount == 0:
        print("TSTNCF,WTSNCF missing in ldm_product_log")
        return 1
    row = cursor.fetchone()
    if (utcnow - row[2]) > timedelta(minutes=10):
        print(f"TSTNCF,WTSNCF wmo_valid_at is too old {row[2]}")
        return 1
    # noaaport_latency is the valid_at minus product valid
    noaaport_latency = (row[1] - row[2]).total_seconds()
    # idd latency is the entered_at minues valid_at
    idd_latency = (row[0] - row[1]).total_seconds()
    # Create the nagios stats line
    print(
        f"{row[3]} {row[2]} NP:{noaaport_latency:.2f}s "
        f"IDD:{idd_latency:.2f}s "
        f"|NOAAPORT_LATENCY={noaaport_latency:.4f};180;300;600 "
        f"IDD_LATENCY={idd_latency:.4f};180;300;600"
    )
    if max([idd_latency, noaaport_latency]) > 300:
        return 2
    if max([idd_latency, noaaport_latency]) > 180:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
