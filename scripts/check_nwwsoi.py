"""Check that NWWS-OI ingest is saving files."""

import os
import sys
from datetime import datetime, timedelta, timezone


def main() -> int:
    """Go Main Go."""
    utcnow = datetime.now(timezone.utc)
    for offset in [0, 1]:
        dt = utcnow - timedelta(hours=offset)
        fn = f"/mesonet/tmp/nwwsoi/{dt:%Y%m%d%H}.txt"
        if not os.path.isfile(fn):
            if offset == 1:
                print(f"CRITICAL - {fn} missing")
                return 2
            continue
        # Get the file size
        size = os.path.getsize(fn)
        print(f"OK - {fn} exists with size of {size} bytes|size={size}")
        return 0


if __name__ == "__main__":
    sys.exit(main())
