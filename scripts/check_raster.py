"""Check a raster file and count the number of non-zero values."""
import sys

import numpy
from osgeo import gdal


def main():
    """Go Main Go."""
    ntp = gdal.Open("/mesonet/ldmdata/gis/images/4326/USCOMP/ntp_0.png")
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
