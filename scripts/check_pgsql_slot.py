#!/usr/bin/env python3
"""
Nagios/Icinga plugin to check PostgreSQL physical replication slot lag and
health. Run on the primary database host or a dedicated monitoring host.
"""

import argparse
import sys

from pyiem.database import get_sqlalchemy_conn, sql_helper
from sqlalchemy.engine import Connection

# Nagios Exit Codes
OK = 0
WARNING = 1
CRITICAL = 2
UNKNOWN = 3


def parse_args():
    """See how we are called..."""
    parser = argparse.ArgumentParser(
        description="Check PostgreSQL replication slot status and lag."
    )
    parser.add_argument(
        "-s", "--slot", required=True, help="Replication slot name to monitor"
    )
    parser.add_argument(
        "-w",
        "--warning",
        type=int,
        default=1073741824,
        help="Warning threshold for byte lag (default: 1073741824 bytes)",
    )
    parser.add_argument(
        "-c",
        "--critical",
        type=int,
        default=5368709120,
        help="Critical threshold for byte lag (default: 5368709120 bytes)",
    )
    return parser.parse_args()


def fetch_slot_metrics(conn: Connection, args) -> dict:
    """Query the database and get the result."""

    # Query combining pg_replication_slots and pg_stat_replication
    query = """
        SELECT
            s.slot_name,
            s.active,
            s.wal_status,
            s.plugin,
            COALESCE(pg_wal_lsn_diff(pg_current_wal_lsn(),
            s.restart_lsn), 0)::bigint AS byte_lag,
            COALESCE(pg_wal_lsn_diff(pg_current_wal_lsn(),
            s.confirmed_flush_lsn), 0)::bigint AS confirmed_flush_lag,
            r.state AS replication_state,
            r.sync_state,
            COALESCE(pg_wal_lsn_diff(
                pg_current_wal_lsn(), r.write_lsn), 0)::bigint
                AS write_lag,
            COALESCE(
                pg_wal_lsn_diff(pg_current_wal_lsn(),
                r.flush_lsn), 0)::bigint AS flush_lag,
            COALESCE(pg_wal_lsn_diff(
                pg_current_wal_lsn(), r.replay_lsn), 0)::bigint
                AS replay_lag
        FROM pg_replication_slots s
        LEFT JOIN pg_stat_replication r ON s.active_pid = r.pid
        WHERE s.slot_name = :slot;
    """
    res = conn.execute(sql_helper(query), {"slot": args.slot})
    row = res.mappings().fetchone()
    return row


def main():
    """Go Main Go."""
    args = parse_args()
    try:
        with get_sqlalchemy_conn(
            "postgres", host="localhost", user="postgres", rw=False
        ) as conn:
            data = fetch_slot_metrics(conn, args)
    except Exception as e:
        print(f"CRITICAL - Database connection or query failed: {str(e)}")
        sys.exit(CRITICAL)

    if not data:
        print(f"CRITICAL - Replication slot '{args.slot}' does not exist")
        sys.exit(CRITICAL)

    slot_name = data["slot_name"]
    active = data["active"]
    wal_status = data["wal_status"]
    byte_lag = data["byte_lag"]
    rep_state = data["replication_state"] or "disconnected"
    replay_lag = data["replay_lag"]

    # Construct Nagios Performance Data (perfdata)
    perfdata = (
        f"| byte_lag={byte_lag}B;{args.warning};{args.critical};0; "
        f"replay_lag={replay_lag}B;;;0; "
        f"active={1 if active else 0};;;0;1"
    )

    # Evaluation Logic
    status = OK
    messages = []

    # 1. Check slot active status
    if not active:
        status = CRITICAL
        messages.append("Slot is INACTIVE (Standby disconnected)")

    # 2. Check WAL status for WAL loss
    if wal_status in ("unreserved", "lost"):
        status = CRITICAL
        messages.append(f"WAL status is '{wal_status}'")

    # 3. Check byte lag thresholds
    if byte_lag >= args.critical:
        status = CRITICAL
        messages.append(
            f"Byte lag critical ({byte_lag} bytes >= {args.critical} bytes)"
        )
    elif byte_lag >= args.warning and status != CRITICAL:
        status = WARNING
        messages.append(
            f"Byte lag warning ({byte_lag} bytes >= {args.warning} bytes)"
        )

    # Format output summary
    mb_lag = round(byte_lag / (1024 * 1024), 2)
    summary_text = (
        f"Slot '{slot_name}' [Active: {active}, State: {rep_state}, "
        f"WAL Status: {wal_status}, Lag: {mb_lag} MB ({byte_lag} bytes)]"
    )

    if status == OK:
        print(f"OK - {summary_text} {perfdata}")
        sys.exit(OK)
    elif status == WARNING:
        print(f"WARNING - {', '.join(messages)} - {summary_text} {perfdata}")
        sys.exit(WARNING)
    else:
        print(f"CRITICAL - {', '.join(messages)} - {summary_text} {perfdata}")
        sys.exit(CRITICAL)


if __name__ == "__main__":
    main()
