"""
See how much BUFR surface data we got.
"""
import sys

from pyiem.util import get_dbconn


def check():
    """Do the check"""
    pgconn = get_dbconn("iem", host=sys.argv[1], user="nobody")
    icursor = pgconn.cursor()
    icursor.execute(
        "SELECT count(*) from current c JOIN stations s on "
        "(s.iemid = c.iemid) WHERE valid > now() - '75 minutes'::interval "
        "and network = 'WMO_BUFR_SRF'"
    )
    row = icursor.fetchone()

    return row[0]


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
