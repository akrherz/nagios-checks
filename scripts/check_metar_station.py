"""Ensure that a station is getting ingested properly

python check_metar_station.py <network> <id> <minute_of_synop>
"""

import sys
from datetime import datetime, timedelta

from pyiem.database import get_dbconn


def check(network, station, minute):
    """Do the check"""
    # Do IEMaccess
    res = {"rt_temp": "M", "arch_temp": "M"}
    now = datetime.now() - timedelta(minutes=75)
    res["rt_valid"] = now.replace(minute=minute, second=0, microsecond=0)
    pgconn = get_dbconn("iem", user="nobody")
    icursor = pgconn.cursor()
    icursor.execute(
        "SELECT tmpf from current_log c JOIN stations s on "
        "(s.iemid = c.iemid) WHERE id = %s and network = %s and valid = %s",
        (station, network, res["rt_valid"]),
    )
    if icursor.rowcount > 0:
        row = icursor.fetchone()
        res["rt_temp"] = "NaN" if row[0] is None else int(row[0])
    # Do ASOS
    now = datetime.now() - timedelta(minutes=135)
    res["arch_valid"] = now.replace(minute=minute, second=0, microsecond=0)
    pgconn = get_dbconn("asos", user="nobody")
    icursor = pgconn.cursor()
    icursor.execute(
        "SELECT tmpf from alldata where station = %s and valid = %s",
        (station, res["arch_valid"]),
    )
    if icursor.rowcount > 0:
        row = icursor.fetchone()
        res["arch_temp"] = "NaN" if row[0] is None else int(row[0])

    return res


def main(argv):
    """Go Main"""
    network = argv[1]
    station = argv[2]
    minute = int(argv[3])
    res = check(network, station, minute)
    msg = (
        "OK"
        if (res["rt_temp"] != "M" and res["arch_temp"] != "M")
        else "CRITICAL"
    )
    print(
        f"{msg} - RT:{res['rt_valid']:%d%H%M}({res['rt_temp']}) "
        f"ARCH:{res['arch_valid']:%d%H%M}({res['arch_temp']}) "
        f"|rttemp={res['rt_temp']};;; archtemp={res['arch_temp']};;;"
    )
    if msg == "OK":
        sys.exit(0)
    sys.exit(2)


if __name__ == "__main__":
    main(sys.argv)
