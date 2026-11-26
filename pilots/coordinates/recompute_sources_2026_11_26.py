"""Recompute the printed figures read on 26 November 2026.

Written by Claude (AI). See docs/2026-11-26-positions-remaining-sources.md.
Needs: geographiclib==2.1, pyproj==3.8.0, utm==0.8.1 (utm is used only as a
cross-check of the zone rule derived from DMA TM 8358.1, never as a reference).

Run:  python pilots/coordinates/recompute_sources_2026_11_26.py
"""
from geographiclib.geodesic import Geodesic
import geographiclib
import pyproj
from pyproj import Geod
import utm

G = Geodesic.WGS84
P = Geod(ellps="WGS84")
print("geographiclib", geographiclib.__version__, "| pyproj", pyproj.__version__,
      "| PROJ", pyproj.proj_version_str)

print("\nKarney 2013, Table 2 (direct): phi1 40, alpha1 30, s12 10 000 000 m")
d = G.Direct(40, 0, 30, 10e6, Geodesic.ALL)
lon2, lat2, back = P.fwd(0, 40, 30, 10e6)
print("  printed     phi2 41.79331020506  lambda12 137.84490004377  alpha2 149.09016931807")
print("  GeographicLib phi2 %.11f  lambda12 %.11f  alpha2 %.11f" % (d["lat2"], d["lon2"], d["azi2"]))
print("  PROJ          phi2 %.11f  lambda12 %.11f  alpha2 %.11f" % (lat2, lon2, back + 180))

for label, a, b, dl, printed in [
    ("Table 3 (short inverse)", -30.12345, -30.12344, 0.00005,
     "alpha1 77.04353354237  alpha2 77.04350844913  s12 4.944208"),
    ("Table 6 (nearly antipodal inverse)", -30, 29.9, 179.8,
     "alpha1 161.89052473633  alpha2 18.09073724574  s12 19989832.827610"),
]:
    print("\nKarney 2013, %s: phi1 %s, phi2 %s, lambda12 %s" % (label, a, b, dl))
    i = G.Inverse(a, 0, b, dl)
    a1, a2, s = P.inv(0, a, dl, b)
    print("  printed       " + printed)
    print("  GeographicLib alpha1 %.11f  alpha2 %.11f  s12 %.6f" % (i["azi1"], i["azi2"], i["s12"]))
    print("  PROJ          alpha1 %.11f  alpha2 %.11f  s12 %.6f" % (a1, a2 + 180, s))

print("\nKarney 2013, Table 7 (area between the Table 2 geodesic and the equator)")
lat = [0, 40, 41.79331020506, 0]
lon = [0, 0, 137.84490004377, 137.84490004377]
poly = G.Polygon()
for la, lo in zip(lat, lon):
    poly.AddPoint(la, lo)
_, per_gl, area_gl = poly.Compute(False, True)
area_pj, per_pj = P.polygon_area_perimeter(lon, lat)
print("  printed       S12 84 275 623.422 35 km2")
print("  GeographicLib %.5f km2 (signed; negative = clockwise)" % (area_gl / 1e6))
print("  PROJ          %.5f km2 (signed; negative = clockwise)" % (area_pj / 1e6))

print("\nGDA manuals: a line of points (Flinders Peak, Buninyong, Flinders Peak)")


def dms(d, m, s):
    sign = -1 if d < 0 else 1
    return sign * (abs(d) + m / 60 + s / 3600)


grs80 = Geod(ellps="GRS80")
fp = (dms(-37, 57, 3.72030), dms(144, 25, 29.52440))
bu = (dms(-37, 39, 10.15610), dms(143, 55, 35.38390))
one = grs80.line_length([fp[1], bu[1]], [fp[0], bu[0]])
two = grs80.line_length([fp[1], bu[1], fp[1]], [fp[0], bu[0], fp[0]])
print("  printed one leg 54 972.271 m; two legs therefore 109 944.542 m")
print("  PROJ one leg %.4f m, two legs %.4f m" % (one, two))

print("\nUTM zones: rule derived from DMA TM 8358.1, para. 3-2.2.1; cross-check with utm",
      utm.__version__ if hasattr(utm, "__version__") else "")
cases = [(60.4, 5.3, 32), (60.4, 2.0, 31), (50.0, 5.3, 31), (70.0, 10.5, 32),
         (78.2, 15.6, 33), (78.5, 10.5, 33), (79.0, 7.0, 31), (78.0, 25.0, 35),
         (80.0, 35.0, 37)]
for la, lo, expected in cases:
    got = utm.latlon_to_zone_number(la, lo)
    print("  %5.1f N %5.1f E  derived %d  utm %d  %s" % (la, lo, expected, got,
          "agree" if got == expected else "DIFFER"))
