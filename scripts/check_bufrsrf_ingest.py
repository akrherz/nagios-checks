"""
See how much BUFR surface data we got.
"""

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
            "SELECT count(*) from current c JOIN stations s on "
            "(s.iemid = c.iemid) WHERE valid > now() - '75 minutes'::interval "
            "and network = 'WMO_BUFR_SRF'"
        )
    )
    return res.fetchone()[0]


def main():
    """Go Main"""
    count = check()
    stats = f"{count} count |count={count};1000;5000;10000"
    if count > 3000:
        print(f"OK - {stats}")
        return 0
    if count > 2000:
        print(f"WARNING - {stats}")
        return 1
    print(f"CRITICAL - {stats}")
    return 2


if __name__ == "__main__":
    sys.exit(main())
