"""Check the acquistion of stills from the webcams."""
import sys

from pyiem.util import get_dbconn


def main():
    """Go Main Go."""
    with get_dbconn("mesosite", user="nobody") as pgconn:
        cursor = pgconn.cursor()
        cursor.execute(
            "select count(*) from camera_current where "
            "valid > now() - '30 minutes'::interval and "
            "substr(cam, 1, 4) in ('KCRG', 'KCCI', 'MCFC')"
        )
        count = cursor.fetchone()[0]

    msg = f"{count} images|count={count}"
    if count > 20:
        print(f"OK - {msg}")
        return 0
    print(f"CRITICAL - {msg}")
    return 2


if __name__ == "__main__":
    sys.exit(main())
