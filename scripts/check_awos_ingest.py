"""Check how much local AWOS data ingest we have."""
import sys

from pyiem.util import get_dbconn


def check():
    """Do the check"""
    pgconn = get_dbconn("iem", user="nobody")
    icursor = pgconn.cursor()
    icursor.execute(
        "SELECT count(*) from current_log c JOIN stations s on "
        "(s.iemid = c.iemid) WHERE network = 'AWOS' and "
        "valid > now() - '75 minutes'::interval and "
        "extract(minute from valid) not in (15, 35, 55)"
    )
    return icursor.fetchone()[0]


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
