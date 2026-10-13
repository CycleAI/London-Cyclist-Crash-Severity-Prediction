#!/usr/bin/env python3
"""
generate_london_grid_full.py

Generate a 50 m spacing point grid covering Greater London (full coverage, no max cap)
and save all lat,lon pairs to a CSV file.

Dependencies:
  pip install shapely pyproj requests numpy tqdm

Notes:
 - This will generate a LOT of points (hundreds of thousands). The script prints
   a rough estimate of grid cell count before iterating.
 - The script writes rows incrementally to avoid high memory usage.
"""

!pip install shapely pyproj requests numpy tqdm
import requests
import json
import csv
import math
import sys
import time
from shapely.geometry import shape, Point
from shapely.ops import transform
from pyproj import Transformer
import numpy as np
from tqdm import tqdm

# -----------------------
# USER CONFIG
# -----------------------
PLACE_NAME = "Greater London"            # query for Nominatim
OUTPUT_CSV = "greater_london_grid_50m_full.csv"
SPACING_METERS = 50                      # grid spacing in meters
USER_AGENT = "grid-gen/1.0 (contact: you@example.com)"
# Choose projection for meter-accurate grid:
# Default uses Web Mercator (EPSG:3857). If you prefer British National Grid
# (EPSG:27700) for slightly better local accuracy inside UK, set USE_BNG = True.
USE_BNG = True
# -----------------------

def fetch_place_geojson(place_name: str, user_agent: str = None):
    url = "https://nominatim.openstreetmap.org/search"
    headers = {"User-Agent": user_agent or USER_AGENT}
    params = {"q": place_name, "format": "json", "polygon_geojson": 1, "limit": 1}
    r = requests.get(url, params=params, headers=headers, timeout=60)
    r.raise_for_status()
    results = r.json()
    if not results:
        raise RuntimeError(f"No results from Nominatim for '{place_name}'")
    geojson = results[0].get("geojson")
    if not geojson:
        raise RuntimeError(f"Nominatim result for '{place_name}' has no geojson polygon")
    return geojson

def estimate_grid_count(bounds, spacing):
    minx, miny, maxx, maxy = bounds
    nx = math.ceil((maxx - minx) / spacing)
    ny = math.ceil((maxy - miny) / spacing)
    return nx * ny, nx, ny

def generate_grid_within_polygon(polygon_geojson, spacing_meters, out_csv_path, use_bng=False):
    """
    polygon_geojson: GeoJSON geometry (EPSG:4326)
    spacing_meters: grid spacing in meters
    Writes CSV with header "lat,lon".
    """
    poly_ll = shape(polygon_geojson)

    # choose projection
    if use_bng:
        # British National Grid (EPSG:27700) -- better local distance accuracy in UK
        to_m = Transformer.from_crs("EPSG:4326", "EPSG:27700", always_xy=True).transform
        to_ll = Transformer.from_crs("EPSG:27700", "EPSG:4326", always_xy=True).transform
        proj_name = "EPSG:27700 (BNG)"
    else:
        # Web Mercator, easy and available everywhere
        to_m = Transformer.from_crs("EPSG:4326", "EPSG:3857", always_xy=True).transform
        to_ll = Transformer.from_crs("EPSG:3857", "EPSG:4326", always_xy=True).transform
        proj_name = "EPSG:3857 (Web Mercator)"

    poly_m = transform(to_m, poly_ll)
    minx, miny, maxx, maxy = poly_m.bounds

    est_count, nx, ny = estimate_grid_count((minx, miny, maxx, maxy), spacing_meters)
    print(f"Projection: {proj_name}")
    print(f"Projected bounding box (meters): minx={minx:.1f}, miny={miny:.1f}, maxx={maxx:.1f}, maxy={maxy:.1f}")
    print(f"Rough grid cells: nx={nx}, ny={ny}, total ≈ {est_count:,}")
    print("This will test every grid cell and keep only points inside the polygon.")
    print(f"Output CSV: {out_csv_path}")
    print("Starting... (this may take several minutes depending on CPU and how many points are inside)")

    # Create coordinate arrays
    xs = np.arange(minx, maxx + spacing_meters, spacing_meters)
    ys = np.arange(miny, maxy + spacing_meters, spacing_meters)

    checked = 0
    saved = 0
    t0 = time.time()

    with open(out_csv_path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        writer.writerow(["lat", "lon"])

        # iterate rows for locality; show progress over rows
        with tqdm(total=len(ys), desc="rows", unit="row") as pbar_rows:
            for yi, y in enumerate(ys):
                # iterate x across this row
                for x in xs:
                    checked += 1
                    pt_m = Point(x, y)
                    if poly_m.contains(pt_m):
                        lon, lat = to_ll(x, y)
                        # write lat,lon with reasonable precision
                        writer.writerow([f"{lat:.7f}", f"{lon:.7f}"])
                        saved += 1
                pbar_rows.update(1)

    t1 = time.time()
    print(f"Done. points_checked={checked:,}, points_saved={saved:,}, elapsed={t1-t0:.1f}s")
    return out_csv_path, checked, saved

def main():
    print("=== Generate 50 m grid covering the whole Greater London polygon ===")
    print("Fetching polygon from Nominatim...")
    geojson = fetch_place_geojson(PLACE_NAME, USER_AGENT)
    if geojson is None:
        raise SystemExit("Failed to fetch polygon geojson.")
    print("Polygon retrieved. Geometry type:", geojson.get("type"))

    out_csv, checked, saved = generate_grid_within_polygon(geojson, SPACING_METERS, OUTPUT_CSV, use_bng=USE_BNG)
    print(f"CSV saved to: {out_csv}")
    print("Finished.")

if __name__ == "__main__":
    main()
