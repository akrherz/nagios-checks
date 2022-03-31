"""
Check the production of N0Q data!
"""
import json
import datetime
import sys


def main(argv):
    """Do Great Things"""
    prod = argv[1]
    fn = f"/mesonet/ldmdata/gis/images/4326/USCOMP/{prod}_0.json"
    with open(fn, encoding="utf-8") as fp:
        j = json.load(fp)
    prodtime = datetime.datetime.strptime(
        j["meta"]["valid"], "%Y-%m-%dT%H:%M:%SZ"
    )
    radarson = int(j["meta"]["radar_quorum"].split("/")[0])
    gentime = j["meta"]["processing_time_secs"]

    utcnow = datetime.datetime.utcnow()
    latency = (utcnow - prodtime).total_seconds()

    stats = f"gentime={gentime};180;240;300 radarson={radarson};100;75;50"

    if prod == "n0r" or (
        gentime < 300 and radarson > 50 and latency < 60 * 10
    ):
        print(f"OK |{stats}")
        return 0
    if gentime > 300:
        print(f"CRITICAL - gentime {gentime}|{stats}")
        return 2
    if latency > 600:
        print(f"CRITICAL - radtime:{prodtime} latency:{latency}s|{stats}")
        return 2
    if radarson < 50:
        print(f"CRITICAL - radarson {radarson}|{stats}")
        return 2
    print(f"CRITICAL - radarson {radarson}|{stats}")
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
