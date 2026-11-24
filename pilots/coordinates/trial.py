#!/usr/bin/env python3
"""A one-day trial: put the same position questions to several servers for AI agents.

A trial, not part of the bench. Reference answers come from published worked
examples, from closed formulas computed here with 40 digits, and from
GeographicLib (C. Karney's reference implementation of his geodesic
algorithms); none comes from a server. Written by Claude (AI).

Servers are expected in <MEASURE_GEO_DIR>/<name>/bin/<name>.
"""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT)

import mpmath as mp  # noqa: E402
from geographiclib.geodesic import Geodesic  # noqa: E402

from bench.mcp_client import ServerError, StdioServer  # noqa: E402

mp.mp.dps = 40
BASE = os.environ.get("MEASURE_GEO_DIR", os.path.join(os.getcwd(), "geo-envs"))
WGS84 = Geodesic.WGS84


def dms(d, m, s):
    return (abs(d) + m / 60 + s / 3600) * (-1 if d < 0 else 1)


def area(ring):
    poly = WGS84.Polygon()
    for lon, lat in ring:
        poly.AddPoint(lat, lon)
    return abs(poly.Compute()[2])


BCN, MAD = (2.1686, 41.3874), (-3.7038, 40.4168)                      # lon, lat
FLINDERS = (dms(144, 25, 29.52440), dms(-37, 57, 3.72030))
BUNINYONG = (dms(143, 55, 35.38390), dms(-37, 39, 10.15610))
CELL = [[0, 0], [1, 0], [1, 1], [0, 1], [0, 0]]
CELL_180 = [[179.5, 0], [-179.5, 0], [-179.5, 1], [179.5, 1], [179.5, 0]]
A = mp.mpf(6378137)
MERCATOR = (float(A * mp.radians(mp.mpf("2.1686"))),
            float(A * mp.log(mp.tan(mp.pi / 4 + mp.radians(mp.mpf("41.3874")) / 2))))


def dist(p, q):
    return WGS84.Inverse(p[1], p[0], q[1], q[0])["s12"]


# name -> (question, reference numbers or None when only recorded, tolerance in the unit of the answer)
QUESTIONS = {
    "distance-ordinary": ("Barcelona to Madrid on the WGS 84 ellipsoid, m", [dist(BCN, MAD)], 0.01),
    "distance-published": (
        "Flinders Peak to Buninyong, m (worked example in Australia's GDA technical manual: 54 972.271)",
        [54972.271], 0.01),
    "distance-near-antipodal": (
        "From 0 N 0 E to 0.5 N 179.5 E, m (a case where the older Vincenty method fails)",
        [dist((0, 0), (179.5, 0.5))], 0.01),
    "distance-across-180": ("From 179.9 E to 179.9 W on the equator, m", [dist((179.9, 0), (-179.9, 0))], 0.01),
    "distance-over-pole": ("From 89 N 0 E to 89 N 180 E, m", [dist((0, 89), (180, 89))], 0.01),
    "latitude-91": ("A distance from latitude 91 (no such place)", None, 0),
    "length-ordinary": ("Length of the line Barcelona to Madrid, m", [dist(BCN, MAD)], 0.01),
    "length-across-180": ("Length of the line from 179.9 E to 179.9 W on the equator, m",
                          [dist((179.9, 0), (-179.9, 0))], 0.01),
    "area-cell": ("Area of the one-degree cell at 0 N 0 E, m2", [area(CELL)], 1000.0),
    "area-cell-clockwise": ("The same cell with its corners listed clockwise, m2", [area(CELL)], 1000.0),
    "area-across-180": ("Area of a one-degree cell that straddles 180 degrees, m2", [area(CELL_180)], 1000.0),
    "mercator": ("Barcelona in Web Mercator (EPSG:3857), m; closed formula", list(MERCATOR), 0.001),
    "grid-published": (
        "Flinders Peak in Map Grid of Australia zone 55, m (the manual: E 273 741.297, N 5 796 489.777)",
        [273741.297, 5796489.777], 0.001),
    "british-grid": ("British National Grid 530000 180000 to WGS 84 (answer depends on the method chosen; "
                     "recorded, with whether the server names the method)", None, 0),
    "utm-zone-bergen": ("UTM zone of Bergen, 60.39 N 5.32 E (zone 32: the grid widens 32V over south-west Norway)",
                        [32], 0),
    "utm-zone-svalbard": ("UTM zone of Longyearbyen, 78.2 N 15.6 E (zone 33; the grid has special zones here)",
                          [33], 0),
}


def point(p):
    return {"type": "Point", "coordinates": list(p)}


def line(p, q):
    return {"type": "LineString", "coordinates": [list(p), list(q)]}


def polygon(ring):
    return {"type": "Polygon", "coordinates": [ring]}


S = json.dumps
SERVERS = {
    "gis-mcp-server": {
        "distance-ordinary": ("distance", {"lat1": BCN[1], "lon1": BCN[0], "lat2": MAD[1], "lon2": MAD[0]}, "meters"),
        "distance-published": ("distance", {"lat1": FLINDERS[1], "lon1": FLINDERS[0], "lat2": BUNINYONG[1], "lon2": BUNINYONG[0]}, "meters"),
        "distance-near-antipodal": ("distance", {"lat1": 0, "lon1": 0, "lat2": 0.5, "lon2": 179.5}, "meters"),
        "distance-across-180": ("distance", {"lat1": 0, "lon1": 179.9, "lat2": 0, "lon2": -179.9}, "meters"),
        "distance-over-pole": ("distance", {"lat1": 89, "lon1": 0, "lat2": 89, "lon2": 180}, "meters"),
        "latitude-91": ("distance", {"lat1": 91, "lon1": 0, "lat2": 0, "lon2": 0}),
        "length-ordinary": ("length", {"geometry": line(BCN, MAD)}),
        "length-across-180": ("length", {"geometry": line((179.9, 0), (-179.9, 0))}),
        "area-cell": ("area", {"geometry": polygon(CELL)}),
        "area-cell-clockwise": ("area", {"geometry": polygon(CELL[::-1])}),
        "area-across-180": ("area", {"geometry": polygon(CELL_180)}),
        "mercator": ("transform_crs", {"geometry": point(BCN), "source_crs": "EPSG:4326", "target_crs": "EPSG:3857"}, "coordinates"),
        "grid-published": ("transform_crs", {"geometry": point(FLINDERS), "source_crs": "EPSG:4283", "target_crs": "EPSG:28355"}, "coordinates"),
        "british-grid": ("transform_crs", {"geometry": point((530000, 180000)), "source_crs": "EPSG:27700", "target_crs": "EPSG:4326"}, "coordinates"),
        "utm-zone-bergen": ("utm_zone", {"lat": 60.39, "lon": 5.32}, "zone_number"),
        "utm-zone-svalbard": ("utm_zone", {"lat": 78.2, "lon": 15.6}, "zone_number"),
    },
    "mcp-geo": {
        "distance-ordinary": ("distance", {"geojson_a": S(point(BCN)), "geojson_b": S(point(MAD)), "unit": "m"}),
        "distance-published": ("distance", {"geojson_a": S(point(FLINDERS)), "geojson_b": S(point(BUNINYONG)), "unit": "m"}),
        "distance-near-antipodal": ("distance", {"geojson_a": S(point((0, 0))), "geojson_b": S(point((179.5, 0.5))), "unit": "m"}),
        "distance-across-180": ("distance", {"geojson_a": S(point((179.9, 0))), "geojson_b": S(point((-179.9, 0))), "unit": "m"}),
        "distance-over-pole": ("distance", {"geojson_a": S(point((0, 89))), "geojson_b": S(point((180, 89))), "unit": "m"}),
        "latitude-91": ("distance", {"geojson_a": S(point((0, 91))), "geojson_b": S(point((0, 0))), "unit": "m"}),
        "length-ordinary": ("length", {"geojson": S(line(BCN, MAD)), "unit": "m"}),
        "length-across-180": ("length", {"geojson": S(line((179.9, 0), (-179.9, 0))), "unit": "m"}),
        "area-cell": ("area", {"geojson": S(polygon(CELL)), "unit": "m2"}),
        "area-cell-clockwise": ("area", {"geojson": S(polygon(CELL[::-1])), "unit": "m2"}),
        "area-across-180": ("area", {"geojson": S(polygon(CELL_180)), "unit": "m2"}),
        "mercator": ("transform_crs", {"geojson": S(point(BCN)), "from_crs": "EPSG:4326", "to_crs": "EPSG:3857"}),
        "grid-published": ("transform_crs", {"geojson": S(point(FLINDERS)), "from_crs": "EPSG:4283", "to_crs": "EPSG:28355"}),
        "british-grid": ("transform_crs", {"geojson": S(point((530000, 180000))), "from_crs": "EPSG:27700", "to_crs": "EPSG:4326"}),
    },
    "mcp-server-proj": {
        "mercator": ("transform-coordinates", {"source_crs": "EPSG:4326", "target_crs": "EPSG:3857", "coordinates": [{"x": BCN[0], "y": BCN[1]}]}, "输出"),
        "grid-published": ("transform-coordinates", {"source_crs": "EPSG:4283", "target_crs": "EPSG:28355", "coordinates": [{"x": FLINDERS[0], "y": FLINDERS[1]}]}, "输出"),
        "british-grid": ("transform-coordinates", {"source_crs": "EPSG:27700", "target_crs": "EPSG:4326", "coordinates": [{"x": 530000, "y": 180000}]}, "输出"),
    },
    "geospatial-mcp": {
        "area-cell": ("calculate_accurate_metrics", {"geojson": polygon(CELL), "unit": "sq_meters"}),
        "area-cell-clockwise": ("calculate_accurate_metrics", {"geojson": polygon(CELL[::-1]), "unit": "sq_meters"}),
        "area-across-180": ("calculate_accurate_metrics", {"geojson": polygon(CELL_180), "unit": "sq_meters"}),
    },
}
NUMBER = re.compile(r"-?\d+(?:\.\d+)?(?:[eE][-+]?\d+)?")


def judge(name, spec, is_error, text):
    _words, reference, tolerance = QUESTIONS[name]
    flat = " ".join(text.split())
    failed = is_error or '"success":false' in flat.replace(" ", "")
    if len(spec) > 2 and spec[2] in flat:
        flat = flat[flat.index(spec[2]):]
    shown = flat[:120]
    if reference is None:
        return ("refused" if failed else "answered"), shown
    if failed:
        return "error", shown
    found = [float(x) for x in NUMBER.findall(flat)]
    missing = [r for r in reference if not any(abs(f - r) <= tolerance for f in found[:12])]
    if not missing:
        return "agrees", shown
    return "DIFFERS (reference %s)" % ", ".join("%.3f" % r if r % 1 else "%d" % r for r in reference), shown


def main():
    print("| Server | Question | Result | What the server said |")
    print("|---|---|---|---|")
    for server, questions in SERVERS.items():
        os.environ["MEASURE_SERVER_" + server.upper().replace("-", "_")] = os.path.join(BASE, server, "bin", server)
        try:
            with StdioServer(server) as running:
                for name, spec in questions.items():
                    try:
                        is_error, _payload, text = running.call(spec[0], spec[1])
                        verdict, shown = judge(name, spec, is_error, text)
                    except Exception as exc:
                        verdict, shown = "error", "%s: %s" % (type(exc).__name__, str(exc)[:80])
                    print("| %s | %s | %s | %s |" % (server, name, verdict, shown.replace("|", "/")))
        except ServerError as exc:
            print("| %s | (start) | did not start | %s |" % (server, str(exc)[:100]))
    print()
    print("Questions:")
    for name, (words, reference, _tol) in QUESTIONS.items():
        print("- `%s`: %s. Reference: %s" % (
            name, words, ", ".join("%.3f" % r for r in reference) if reference else "none; behaviour recorded"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
