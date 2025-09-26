"""Nagios check to make sure we have NEXRAD attribute data"""

from __future__ import annotations

import sys
from typing import TYPE_CHECKING

from pyiem.database import sql_helper, with_sqlalchemy_conn

if TYPE_CHECKING:
    from sqlalchemy.engine import Connection


@with_sqlalchemy_conn("radar", user="nobody")
def main(conn: Connection | None = None) -> int:
    """Go Main Go"""
    res = conn.execute(
        sql_helper(
            "select count(*) from nexrad_attributes WHERE "
            "valid > now() - '30 minutes'::interval"
        )
    )
    count = res.fetchone()[0]

    msg = f"L3 NEXRAD attr count {count} |count={count};2;1;0"
    if count > 2:
        print(f"OK - {msg}")
        return 0
    if count > 1:
        print(f"OK - {msg}")
        return 1
    print(f"CRITICAL - {msg}")
    return 2


if __name__ == "__main__":
    sys.exit(main())
