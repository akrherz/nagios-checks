"""Check how much local AWOS data ingest we have."""

from __future__ import annotations

import sys
from typing import TYPE_CHECKING

from pyiem.database import sql_helper, with_sqlalchemy_conn

if TYPE_CHECKING:
    from sqlalchemy.engine import Connection


@with_sqlalchemy_conn("iem", user="nobody")
def check(conn: Connection | None = None) -> int:
    """Do the check"""
    res = conn.execute(
        sql_helper(
            "SELECT count(*) from current_log c JOIN stations s on "
            "(s.iemid = c.iemid) WHERE network = 'IA_ASOS' and "
            "valid > now() - '75 minutes'::interval and "
            "extract(minute from valid) not in (15, 35, 55)"
        )
    )
    return res.fetchone()[0]


def main():
    """Go Main"""
    count = check()
    msg = f"{count} count |count={count};20;25;30"
    if count > 30:
        prefix = "OK"
        res = 0
    elif count > 2000:
        prefix = "WARNING"
        res = 1
    else:
        prefix = "CRITICAL"
        res = 2
    print(f"{prefix} {count} - {msg}")
    return res


if __name__ == "__main__":
    sys.exit(main())
