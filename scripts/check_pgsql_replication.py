"""Stats on how streaming replication is going."""

from __future__ import annotations

import sys
from typing import TYPE_CHECKING

from pyiem.database import sql_helper, with_sqlalchemy_conn

if TYPE_CHECKING:
    from sqlalchemy.engine import Connection


@with_sqlalchemy_conn("postgres", host="localhost", user="postgres")
def main(conn: Connection | None = None) -> int:
    """Go Main Go."""
    res = conn.execute(
        sql_helper(
            "SELECT pg_last_wal_receive_lsn() = pg_last_wal_replay_lsn() "
            "as synced, (EXTRACT(EPOCH FROM now()) - "
            "EXTRACT(EPOCH FROM pg_last_xact_replay_timestamp()))::int AS lag"
        )
    )
    row = res.fetchone()
    # If synced, we are goldness, lag is effectively zero
    if row[0]:
        print("Synced |lag=0;60;120;240")
        return 0
    lag = row[1]
    if lag is None:
        print("Unknown Sync Status")
        return 2
    print(f"Not Synced by {lag}s |lag={lag};60;120;240")
    if lag > 600:
        return 2
    # Prevent some noisiness due to slow disks involved
    if lag > 400:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
