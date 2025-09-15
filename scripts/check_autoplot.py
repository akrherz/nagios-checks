"""Check autoplot stats"""

import sys

from pyiem.database import sql_helper, with_sqlalchemy_conn
from sqlalchemy.engine import Connection


@with_sqlalchemy_conn("mesosite", user="nobody")
def main(conn: Connection | None = None) -> int:
    """Go Main Go"""
    res = conn.execute(
        sql_helper(
            "select count(*), avg(timing) from autoplot_timing "
            "where valid > now() - '4 hours'::interval"
        )
    )
    (count, speed) = res.fetchone()
    speed = 0 if speed is None else speed

    print(
        f"Autoplot cnt:{count} speed:{speed:.2f} | "
        f"COUNT={count};; SPEED={speed:.3f};;"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
