"""Check the acquistion of stills from the webcams."""

import sys
from datetime import timedelta

from pyiem.util import get_dbconn


def main(argv):
    """Go Main Go."""

    networks = ["KCRG", "KCCI", "MCFC"]
    duration = 30
    if len(argv) > 1 and argv[1] == "RWIS":
        networks = ["IDOT"]
        duration = 120

    with get_dbconn("mesosite", user="nobody") as pgconn:
        cursor = pgconn.cursor()
        cursor.execute(
            "select count(*) from camera_current where "
            "valid > now() - %s and "
            "substr(cam, 1, 4) = ANY(%s)",
            (timedelta(minutes=duration), networks),
        )
        count = cursor.fetchone()[0]

    msg = f"{count} images within {duration} minutes|count={count}"
    if count > 20:
        print(f"OK - {msg}")
        return 0
    print(f"CRITICAL - {msg}")
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
