"""Audit the NOAAPort data flow."""

from __future__ import annotations

import sys
from datetime import timedelta
from typing import TYPE_CHECKING

from pyiem.database import sql_helper, with_sqlalchemy_conn
from pyiem.util import utc

if TYPE_CHECKING:
    from sqlalchemy.engine import Connection


@with_sqlalchemy_conn("id3b", user="nobody")
def main(conn: Connection | None = None) -> int:
    """Do some auditing."""
    utcnow = utc().replace(second=0, microsecond=0)
    # Go find this product in the afos database
    res = conn.execute(
        sql_helper(
            "SELECT entered_at, valid_at, wmo_valid_at, awips_id from "
            "ldm_product_log where awips_id in ('TSTNCF', 'WTSNCF') and "
            "entered_at > :sts ORDER by wmo_valid_at DESC LIMIT 1"
        ),
        {"sts": utcnow - timedelta(minutes=15)},
    )
    if res.rowcount == 0:
        print("TSTNCF,WTSNCF missing in ldm_product_log")
        return 1
    row = res.fetchone()
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
