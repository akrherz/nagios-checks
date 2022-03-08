"""Audit the NOAAPort data flow."""
import os
import sys

from pyiem.nws.product import TextProduct
from pyiem.util import get_dbconn


def main():
    """Do some auditing."""
    prod = None
    for pil in ["TSTNCF", "WTSNCF"]:
        fn = f"/home/meteor_ldm/{pil}.txt"
        if os.path.isfile(fn):
            with open(fn, encoding="utf-8") as fh:
                _prod = TextProduct(fh.read().replace("\r", ""))
            if prod is None or _prod.valid > prod.valid:
                prod = _prod
    if prod is None:
        print("No /home/meteor_ldm/{TSTNCF,WTSNCF}.txt")
        return 1
    # Go find this product in the afos database
    cursor = get_dbconn("id3b", user="nobody").cursor()
    cursor.execute(
        "SELECT entered_at, valid_at from ldm_product_log where "
        "awips_id = %s and wmo_valid_at = %s",
        (prod.afos, prod.valid),
    )
    if cursor.rowcount == 0:
        print(f"{prod.get_product_id()} missing in ldm_product_log")
        return 1
    row = cursor.fetchone()
    # noaaport_latency is the valid_at minus product valid
    noaaport_latency = (row[1] - prod.valid).total_seconds()
    # idd latency is the entered_at minues valid_at
    idd_latency = (row[0] - row[1]).total_seconds()
    # Create the nagios stats line
    print(
        f"{prod.afos} {prod.valid} NP:{noaaport_latency:.2f}s "
        f"IDD:{idd_latency:.2f}s "
        f"|NOAAPORT_LATENCY={noaaport_latency:.1f};180;300;600 "
        f"IDD_LATENCY={idd_latency:.1f};180;300;600"
    )
    if max([idd_latency, noaaport_latency]) > 300:
        return 2
    if max([idd_latency, noaaport_latency]) > 180:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
