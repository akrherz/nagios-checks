"""
Return the maximum xmin in the database, having too large of a value leads to
bad things and eventual database not accepting new writes.  I had to lower
the default postgresql setting from 200 mil to 180 mil as the database does
lots of writes and autovac sometimes can not keep up.
"""

import sys

from pyiem.database import get_dbconn


def check(dbname):
    """Do the database check."""
    pgconn = get_dbconn(dbname, user="nobody")
    icursor = pgconn.cursor()
    icursor.execute(
        "SELECT datname, age(datfrozenxid) FROM pg_database "
        "ORDER by age DESC LIMIT 1"
    )
    row = icursor.fetchone()
    icursor.close()
    pgconn.close()

    return row


def main(argv):
    """Go Main Go."""
    if len(argv) != 2:
        print(f"USAGE: {argv[0]} dbname")
        return 2
    dbname, count = check(argv[1])
    msg = f"{count} {dbname} |count={count};201000000;205000000;220000000"
    if count < 201000000:
        print(f"OK - {msg}")
        return 0
    elif count < 205000000:
        print(f"WARNING - {msg}")
        return 1
    print(f"CRITICAL - {msg}")
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
