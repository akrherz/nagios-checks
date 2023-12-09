"""
Get some stats from the pg_stat_database view
"""
import datetime
import getpass
import json
import os
import sys

# Third party
import psycopg2

FN = f"/tmp/check_pgsql_stats_py_{getpass.getuser()}"


def compute_rate(old, new, seconds):
    """Compute a rate that makes sense"""
    delta = new - old
    if delta < 0:
        delta = new
    return delta / seconds


def read_stats():
    """read the stats"""
    if not os.path.isfile(FN):
        return None
    try:
        with open(FN, encoding="utf-8") as fp:
            payload = json.load(fp)
    except Exception:
        # remove the file
        os.unlink(FN)
        return None
    payload["valid"] = datetime.datetime.strptime(
        payload["valid"], "%Y-%m-%dT%H:%M:%SZ"
    )
    return payload


def write_stats(payload):
    """write to tmp file"""
    with open(FN, "w", encoding="utf-8") as fp:
        payload["valid"] = payload["valid"].strftime("%Y-%m-%dT%H:%M:%SZ")
        json.dump(payload, fp)


def check():
    """Do the database check."""
    pgconn = psycopg2.connect("dbname=postgres user=nobody")
    icursor = pgconn.cursor()
    icursor.execute(
        "select sum(numbackends), sum(xact_commit + xact_rollback) "
        "from pg_stat_database"
    )
    row = icursor.fetchone()
    pgconn.close()
    return {
        "valid": datetime.datetime.utcnow(),
        "backends": float(row[0]),
        "xacts": float(row[1]),
    }


def main():
    """Go Main Go."""
    current = check()
    old = read_stats()
    if old is None:
        write_stats(current)
        print("OK - first run")
        return 0
    seconds = (current["valid"] - old["valid"]).total_seconds()
    qps = compute_rate(old["xacts"], current["xacts"], seconds)
    print(
        f"TCPTRAFFIC OK - {qps:.1f} qps | "
        f"QPS={(qps):.1f};4000;5000 BACKENDS={current['backends']:.0f};; "
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
