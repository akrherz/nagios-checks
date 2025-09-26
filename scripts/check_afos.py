"""
Check how much AFOS data we are ingesting
"""

from __future__ import annotations

import sys
from typing import TYPE_CHECKING

from pyiem.database import sql_helper, with_sqlalchemy_conn

if TYPE_CHECKING:
    from sqlalchemy.engine import Connection


@with_sqlalchemy_conn("afos", user="nobody")
def check(conn: Connection | None = None) -> int:
    """Do the check"""
    res = conn.execute(
        sql_helper(
            "SELECT count(*) from products WHERE "
            "entered > now() - '1 hour'::interval"
        )
    )
    return res.fetchone()[0]


def main():
    """Go Main."""
    count = check()
    msg = f"{count} count |count={count};100;500;1000"
    if count > 1000:
        print(f"OK - {msg}")
        return 0
    if count > 500:
        print(f"WARNING - {msg}")
        return 1
    print(f"CRITICAL - {msg}")
    return 2


if __name__ == "__main__":
    sys.exit(main())
