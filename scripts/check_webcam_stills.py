"""Check the acquistion of stills from the webcams."""

from __future__ import annotations

import sys
from datetime import timedelta
from typing import TYPE_CHECKING

from pyiem.database import sql_helper, with_sqlalchemy_conn

if TYPE_CHECKING:
    from sqlalchemy.engine import Connection


@with_sqlalchemy_conn("mesosite", user="nobody")
def main(argv: list[str], conn: Connection | None = None) -> int:
    """Go Main Go."""

    networks = ["KCRG", "KCCI", "MCFC"]
    duration = 30
    if len(argv) > 1 and argv[1] == "RWIS":
        networks = ["IDOT"]
        duration = 120

    res = conn.execute(
        sql_helper(
            "select count(*) from camera_current where "
            "valid > now() - :sts and "
            "substr(cam, 1, 4) = ANY(:networks)"
        ),
        {"sts": timedelta(minutes=duration), "networks": networks},
    )
    count = res.fetchone()[0]

    msg = f"{count} images within {duration} minutes|count={count}"
    if count > 20:
        print(f"OK - {msg}")
        return 0
    print(f"CRITICAL - {msg}")
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
