# California 2020 Wildfire Spatial Analysis

A modular, two-notebook geospatial analysis of the 2020 California wildfire
season. It zooms from statewide context down to individual damaged structures,
culminating in a **dollar valuation of built assets damaged by wildfire**, plus
a written roadmap for predictive / insurance / mitigation extensions.

## Headline results

- **504** fires burned a **4.18 M-acre** footprint; **89%** of the acreage fell
  in August–September (the mid-August dry-lightning siege).
- **3.81 M acres** mapped for burn severity (MTBS); **728 k acres** at High
  severity. Habitat burned led by Hardwood Forest, Shrub, and Conifer Forest
  (~1.1 M acres each).
- **28,626** structures inspected (DINS); **9,494 destroyed**. The **Intermix**
  WUI class held the most structures (14,479) **and** the most destroyed (5,140).
- **Built-asset loss = \$1.8–2.6 billion** — an assessed-improved-value lower
  bound for DINS-inspected structures, *not* total economic loss.
- Data-selected hotspot = the **Glass fire** (Napa/Sonoma Wine Country): 1,506
  destroyed, ~\$0.67 B observed loss.

> Scope: the **2020 season only** — not an all-time ranking (e.g. the 2018 Camp
> Fire and 2025 Palisades Fire are out of scope by construction).

## The 5-act story (notebook 02)

1. **Where it burned** — statewide context: fires, acres, timing.
2. **What nature lost** — vegetation/habitat (WHR13) burned + MTBS burn severity.
3. **Where fire met people** — Wildland-Urban Interface (WUI) crossover.
4. **What it cost** — structure-damage valuation (observed lower bound + imputed).
5. **What's next** — written roadmap for insurance & mitigation (no fitted model).

## Project layout

```
ca-wildfire-2020/
├── data/                      # symlink -> ../data  (raw + processed)
│   ├── raw/                   # ORIGINAL inputs — do not modify
│   └── processed/             # cleaned/reprojected/joined outputs (nb 01 writes)
├── notebooks/
│   ├── 01_data_prep.ipynb     # cleaning, CRS, joins, raster clips  (run first)
│   └── 02_analysis_viz.ipynb  # the 5 acts, maps, charts, animations
├── outputs/
│   ├── charts/                # static .png (220 DPI)
│   ├── maps/                  # static .png + interactive .html
│   ├── animations/            # .gif (no ffmpeg in env -> GIF, not MP4)
│   ├── figure_captions.md     # copy-paste captions for every visual asset
│   └── slide_outline.md       # 27-slide deck outline (methodology -> results)
├── src/style.py               # shared conservation palette + theme helpers
├── _build_nb01.py             # regenerates notebooks/01 (authoring script)
├── _build_nb02.py             # regenerates notebooks/02 (authoring script)
└── README.md
```

## Environment

Runs in the `wildfire` conda env (geopandas 1.1, rasterio 1.4, rioxarray,
fiona, folium, branca; pillow for GIF animations).

```bash
conda activate wildfire
jupyter lab            # then run 01_data_prep.ipynb, then 02_analysis_viz.ipynb
```

To re-execute headless / verify end-to-end:

```bash
jupyter nbconvert --to notebook --execute --inplace notebooks/01_data_prep.ipynb
jupyter nbconvert --to notebook --execute --inplace notebooks/02_analysis_viz.ipynb
```

Both notebooks currently run with **0 errors** (01: 21 code cells; 02: 28 cells).

## Key technical conventions

- **`CRS_EQUAL_AREA = "EPSG:3310"`** (California Albers) for *all* area, distance,
  buffer, and spatial-join math; CRS is asserted before every spatial op.
- **`CRS_WEB = "EPSG:4326"`** for Folium display; interactive raster overlays are
  reprojected to **EPSG:3857** to align with the Leaflet basemap.
- Rasters are **clipped to the buffered 2020 fire perimeters first** (dissolved +
  100 m buffer + exploded into 556 non-overlapping parts), before any zonal
  tabulation — never zonal stats against the full-state raster.
- Notebook 01 writes every intermediate to `data/processed/`; notebook 02 reads
  **only** from `data/processed/` (heavy prep never re-runs).

## Input data (in `data/raw/`) and provenance

| File | What | Source | Native CRS |
|---|---|---|---|
| `fire_perimeters_2020.geojson` | 504 CA 2020 fire perimeters | CAL FIRE FRAP (CNRA open-data portal), filtered to 2020 | EPSG:3857 |
| `dins_2020.geojson` | 28,626 inspected structures (DINS) | CAL FIRE DINS / POSTFIRE_MASTER_DATA_SHARE (ArcGIS) | EPSG:4326 |
| `wui_california.geojson` | 36,157 WUI polygons (`WUI_DESC`) | CAL FIRE / CNRA Wildland-Urban Interface | EPSG:4326 |
| `ca_counties_2020.geojson` | 58 CA counties | US Census TIGER/Line 2020 (via `pygris`) | EPSG:4269 |
| `fveg22_1.gdb` | FVEG vegetation raster, WHR13 habitat | CAL FIRE FRAP "Vegetation by WHR 2022" (LANDFIRE 2020 EVT) | EPSG:3310 |
| `mtbs_CA_2020/mtbs_CA_2020.tif` | MTBS 2020 burn-severity mosaic | USGS/USFS Monitoring Trends in Burn Severity | EPSG:5070 |

Confirmed schema (see notebook 01 §1.1 for the full in-notebook writeup):
- **DINS damage** classes: No Damage 17,801 · Destroyed (>50%) 9,494 · Affected
  (>0-10%) 826 · Inaccessible 204 · Minor (10-25%) 194 · Major (25-50%) 107.
- **WUI** class field = **`WUI_DESC`** ∈ {Interface, Intermix, Influence Zone}.
- **FVEG** = single-band raster; Raster Attribute Table (42,032 rows) →
  13-class **`WHR13NAME`**.
- **MTBS** classes: 0 nodata · 1 Unburned/Low · 2 Low · 3 Moderate · 4 High ·
  5 Increased Greenness · 6 Non-processing Mask. Severity charts use **1–4 only**;
  5 reported separately; 0 & 6 excluded. MTBS maps fires > ~1,000 ac → covers
  **91%** of burned acreage (91 of 504 perimeters).

## Valuation methodology (Act 4) — honest framing

Assessed improved value ≠ replacement cost ≠ market value. Under Prop 13,
assessed values often understate true replacement cost, so the **observed**
figure is a defensible **lower bound**.

1. **Artifact filter (run first).** Raw `ASSESSEDIMPROVEDVALUE` summed to an
   implausible \$30 B because of parcel-aggregate / sentinel values repeated
   across many structures (e.g. \$54,139,901 on 258 buildings). A value is
   flagged suspect if it exceeds a **\$5 M** per-structure ceiling **or** is an
   improbable constant repeated ≥10× above \$2 M. **849 flagged** (77% via the
   repeated-constant rule); excluding them errs toward understatement (an audit
   shows adding every borderline \$5–8 M flag back moves the floor < \$0.05 B).
2. **damage_fraction weights:** Destroyed 1.0 · Major 0.375 · Minor 0.175 ·
   Affected 0.05 · No Damage 0 · Inaccessible shown both ways.
3. **Observed loss** = Σ(credible value × damage_fraction) over structures with a
   positive, non-suspect value → **\$1.8 B** lower bound.
4. **Imputed loss** = fill missing/suspect with the county × structure-type
   median of credible values → **\$2.6 B**.
5. **Winsorised** (suspects capped at \$5 M) = \$3.6 B sensitivity check.

The headline is presented as a **range (\$1.8–2.6 B) with methodology visible** —
never a single false-precision number.

## Processed outputs (`data/processed/`, written by nb 01)

`dins_clean_3310.parquet` · `perims_clean_3310.parquet` ·
`wui_dissolved_3310.parquet` · `counties_3310.parquet` ·
`fveg_whr13_burned.csv` · `mtbs_severity_burned.csv` ·
`mtbs_severity_by_fire.csv` · `mtbs_clipped_perims.tif`

## Visual outputs (`outputs/`, written by nb 02)

**Charts** (`outputs/charts/`): `act1_monthly_acres` · `act2_habitat_bar` ·
`act2_severity_bar` · `act3_wui_damage_stack` · `act3_wui_by_fire` ·
`act4_loss_by_class` · `act4_top_fires_loss` · `act5_survivor_contrast` ·
`act5_model_pipeline`.

**Maps** (`outputs/maps/`): `act1_county_choropleth.png` ·
`act2_severity_map.png` · `act4_hotspot_static.png` +
interactive `act1_perimeters_interactive.html` ·
`act2_severity_interactive.html` · `act4_hotspot_interactive.html`.

**Animations** (`outputs/animations/`): `act_timelapse_2020.gif` (season
time-lapse) · `act_zoom_glass.gif` (statewide → Glass-fire flythrough).
