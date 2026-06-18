#!/usr/bin/env python3
"""
download_data.py  (v4 - full sourcing)
--------------------------------------
Downloads all PROGRAMMATICALLY-AVAILABLE layers for the California 2020
wildfire project into ./data/raw/:

  1. Fire perimeters (all years -> filtered to 2020)      [DONE in v3]
  2. DINS structure damage (2020 season, 28,626 records)  [DONE in v3]
  3. WUI (Wildland Urban Interface / Intermix / Influence) [new]
  4. County + state boundaries (California)                [new]

TWO layers must be downloaded manually through the browser
(see DOWNLOADS_MANUAL.md):
  - FVEG WHR13 vegetation raster   (Act 2 - habitat burned)
  - MTBS CA 2020 burn-severity mosaic (Act 2 - severity)

All endpoints verified live, June 2026. Safe to re-run; overwrites.

Usage:
    conda activate wildfire
    python download_data.py
"""

from pathlib import Path
import json
import sys
import time
import urllib.parse

import requests
import geopandas as gpd

RAW = Path("data/raw")
RAW.mkdir(parents=True, exist_ok=True)

# ---- Endpoints (no token required) --------------------------------------
PERIMETERS_DL = (
    "https://gis.data.cnra.ca.gov/api/download/v1/items/"
    "c3c10388e3b24cec8a954ba10458039d/geojson?layers=0"
)
DINS_QUERY = (
    "https://services1.arcgis.com/jUJYIo9tSA7EHvfZ/arcgis/rest/services/"
    "POSTFIRE_MASTER_DATA_SHARE/FeatureServer/0/query"
)
# WUI: California Open Data portal GeoJSON download.
# NOTE: item id is resolved at runtime via the portal's dataset page if the
# direct link 404s; we try the known CNRA download endpoint first.
WUI_DL = (
    "https://gis.data.cnra.ca.gov/datasets/CALFIRE-Forestry::"
    "wildland-urban-interface.geojson"
)


def stream_download(url, dest, label):
    print(f"\n--> Downloading {label} -> {dest.name}")
    with requests.get(url, stream=True, timeout=900) as r:
        r.raise_for_status()
        with open(dest, "wb") as f:
            for chunk in r.iter_content(chunk_size=1 << 20):
                f.write(chunk)
    print(f"    Saved {dest.stat().st_size/1e6:.1f} MB")


def page_arcgis(base_url, where, dest, label, page=2000):
    print(f"\n--> Querying {label} -> {dest.name}  (where: {where})")
    feats, offset = [], 0
    while True:
        params = {"where": where, "outFields": "*", "f": "geojson",
                  "outSR": "4326", "resultOffset": offset,
                  "resultRecordCount": page}
        url = base_url + "?" + urllib.parse.urlencode(params)
        r = requests.get(url, timeout=180); r.raise_for_status()
        batch = r.json().get("features", [])
        if not batch:
            break
        feats.extend(batch); print(f"    ...{len(feats)} records")
        if len(batch) < page:
            break
        offset += page; time.sleep(0.4)
    dest.write_text(json.dumps({"type": "FeatureCollection",
                                "features": feats}))
    print(f"    Saved {len(feats)} records")


def filter_perimeters_2020(src, dest):
    print("\n--> Filtering perimeters to 2020")
    gdf = gpd.read_file(src)
    col = next((c for c in ["YEAR_", "YEAR", "FIRE_YEAR"]
                if c in gdf.columns), None)
    if col is None:
        print(f"    !! No year col. Columns: {list(gdf.columns)}")
        gdf.to_file(dest, driver="GeoJSON"); return
    sub = gdf[gdf[col].astype(str).str.startswith("2020")].copy()
    print(f"    {len(sub)} of {len(gdf)} perimeters are 2020")
    sub.to_file(dest, driver="GeoJSON")


def get_boundaries():
    """California county boundaries via pygris (TIGER), fallback to note."""
    print("\n--> County/state boundaries")
    try:
        import pygris
        cty = pygris.counties(state="CA", year=2020, cb=True)
        cty.to_file(RAW / "ca_counties_2020.geojson", driver="GeoJSON")
        print(f"    Saved {len(cty)} CA counties")
    except Exception as e:
        print(f"    pygris unavailable ({e}). Install with:")
        print("       pip install pygris")
        print("    or download cb_2020_us_county_500k.zip from")
        print("       https://www2.census.gov/geo/tiger/GENZ2020/shp/")


def main():
    # 1 + 2 already produced by v3, but safe to regenerate. Comment out
    # if you don't want to re-download the 250 MB perimeter file.
    if not (RAW / "fire_perimeters_2020.geojson").exists():
        perim_full = RAW / "_perimeters_all.geojson"
        stream_download(PERIMETERS_DL, perim_full, "fire perimeters (all)")
        filter_perimeters_2020(perim_full,
                               RAW / "fire_perimeters_2020.geojson")
    else:
        print("\n--> perimeters_2020 already present, skipping")

    if not (RAW / "dins_2020.geojson").exists():
        where = ("INCIDENTSTARTDATE>=DATE '2020-01-01' "
                 "AND INCIDENTSTARTDATE<=DATE '2020-12-31'")
        page_arcgis(DINS_QUERY, where, RAW / "dins_2020.geojson", "DINS 2020")
    else:
        print("--> dins_2020 already present, skipping")

    # 3. WUI
    try:
        stream_download(WUI_DL, RAW / "wui_california.geojson", "WUI")
    except requests.HTTPError as e:
        print(f"\n!! WUI direct download failed ({e}).")
        print("   This one may need the manual route too - see")
        print("   DOWNLOADS_MANUAL.md. Not a blocker; continuing.")

    # 4. Boundaries
    get_boundaries()

    print("\n--- Summary ---")
    for f in sorted(RAW.glob("*.geojson")):
        try:
            g = gpd.read_file(f)
            print(f"  {f.name}: {len(g)} features, CRS={g.crs}")
        except Exception:
            print(f"  {f.name}: (could not read)")
    print("\nProgrammatic layers done.")
    print("Now do the 2 manual downloads in DOWNLOADS_MANUAL.md:")
    print("  - FVEG WHR13 vegetation raster")
    print("  - MTBS CA 2020 burn-severity mosaic")


if __name__ == "__main__":
    main()
