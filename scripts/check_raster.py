"""Check a raster file and count the number of non-zero values."""

import sys
from pathlib import Path

import numpy
from osgeo import gdal

gdal.UseExceptions()


def main():
    """Go Main Go."""
    fn = "/mesonet/ldmdata/gis/images/4326/USCOMP/ntp_0.png"
    path = Path(fn)
    if not path.exists():
        print("CRITICAL - ntp_0.png does not exist")
        return 2
    ntp = gdal.Open(fn)
    data = ntp.ReadAsArray()
    count = numpy.sum(numpy.where(data > 0, 1, 0))
    sz = data.shape[0] * data.shape[1]

    msg = f"{count}/{sz}|count={count};100;500;1000"
    if count > 1000:
        print(f"OK - {msg}")
        return 0
    elif count > 500:
        print(f"WARNING - {msg}")
        return 1
    print(f"CRITICAL - {msg}")
    return 2


if __name__ == "__main__":
    sys.exit(main())
