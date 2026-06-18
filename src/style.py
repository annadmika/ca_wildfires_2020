"""
style.py — Shared conservation-aesthetic theme for the CA 2020 wildfire analysis.

Provides:
  - Color constants (palette)
  - apply_mpl_theme()      -> set matplotlib rcParams (parchment bg, sage land, etc.)
  - severity_cmap()        -> matplotlib LinearSegmentedColormap for MTBS burn severity
  - severity_listed_cmap() -> ListedColormap for the 6 categorical MTBS classes
  - damage_palette()       -> dict {DAMAGE class -> hex} (DINS)
  - wui_palette()          -> dict {WUI class -> hex}
  - habitat_color()        -> a stable green-family color for habitat bars
  - save_fig(fig, name, subdir) -> save PNG at publication DPI to outputs/

All figures are designed to drop straight into PowerPoint: parchment background,
generous whitespace, thin neutral gridlines, 200+ DPI.
"""

from __future__ import annotations

import os
from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap, ListedColormap

# --------------------------------------------------------------------------- #
# PALETTE
# --------------------------------------------------------------------------- #

# Backgrounds
PARCHMENT = "#F4F1E8"
CREAM = "#FBFAF5"

# Land / neutral — warm sage greens
SAGE_DARK = "#6B7F5C"
SAGE_MID = "#8B9D77"
SAGE_LIGHT = "#A8B894"
FOREST_DEEP = "#3E4F3C"

# Neutral ink / gridlines
INK = "#2E2A22"
GRID = "#D8D2C2"
MUTED = "#9A9A8C"

# Severity ramp (low -> high burn)
SEV_AMBER = "#E8C547"
SEV_RUST = "#D17A22"
SEV_CHAR = "#8B3A1E"
SEV_CHARRED = "#3D1F14"
SEVERITY_RAMP = [SEV_AMBER, SEV_RUST, SEV_CHAR, SEV_CHARRED]

# DINS damage classes
DAMAGE_COLORS = {
    "No Damage": "#6B7F5C",
    "Affected (1-9%)": "#E8C547",
    "Affected (>0-10%)": "#E8C547",
    "Minor (10-25%)": "#D9A03C",
    "Major (25-50%)": "#D17A22",
    "Destroyed (>50%)": "#8B3A1E",
    "Inaccessible": "#9A9A8C",
}

# WUI classes
WUI_COLORS = {
    "Interface": "#B5651D",
    "Intermix": "#C99A4E",
    "Influence Zone": "#D9C9A3",
    "Influence": "#D9C9A3",
    "Non-WUI": "#E8E4D6",
}

# Ordered damage categories (least -> most severe) for consistent sorting.
# Labels match the DINS 2020 dataset exactly (confirmed via value_counts).
DAMAGE_ORDER = [
    "No Damage",
    "Affected (>0-10%)",
    "Minor (10-25%)",
    "Major (25-50%)",
    "Destroyed (>50%)",
    "Inaccessible",
]

# Preferred humanist sans fonts (fall back gracefully)
FONT_STACK = ["Source Sans Pro", "Source Sans 3", "Inter", "Helvetica Neue",
              "Arial", "DejaVu Sans"]


# --------------------------------------------------------------------------- #
# MATPLOTLIB THEME
# --------------------------------------------------------------------------- #

def apply_mpl_theme() -> None:
    """Apply the conservation theme to matplotlib rcParams (call once per notebook)."""
    mpl.rcParams.update({
        # canvas
        "figure.facecolor": CREAM,
        "axes.facecolor": CREAM,
        "savefig.facecolor": CREAM,
        "figure.figsize": (11, 6.5),
        "figure.dpi": 110,
        "savefig.dpi": 220,
        "savefig.bbox": "tight",
        # fonts
        "font.family": "sans-serif",
        "font.sans-serif": FONT_STACK,
        "font.size": 11,
        "axes.titlesize": 15,
        "axes.titleweight": "semibold",
        "axes.labelsize": 11.5,
        "axes.labelcolor": INK,
        "text.color": INK,
        "xtick.color": INK,
        "ytick.color": INK,
        # spines & grid — minimal chartjunk
        "axes.edgecolor": GRID,
        "axes.linewidth": 0.8,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.grid": True,
        "axes.axisbelow": True,
        "grid.color": GRID,
        "grid.linewidth": 0.6,
        "grid.alpha": 0.7,
        # ticks
        "xtick.direction": "out",
        "ytick.direction": "out",
        "xtick.major.size": 3,
        "ytick.major.size": 3,
        # legend
        "legend.frameon": False,
        "legend.fontsize": 10,
        # title padding
        "axes.titlepad": 12,
    })


# --------------------------------------------------------------------------- #
# COLORMAPS / PALETTE HELPERS
# --------------------------------------------------------------------------- #

def severity_cmap(name: str = "wildfire_severity"):
    """Continuous amber->rust->char->charred colormap for burn severity."""
    return LinearSegmentedColormap.from_list(name, SEVERITY_RAMP, N=256)


def severity_listed_cmap():
    """
    Categorical colormap for the 6 MTBS severity classes:
      1 Unburned/Low, 2 Low, 3 Moderate, 4 High,
      5 Increased Greenness, 6 Non-mapping/Mask
    Returns (ListedColormap, label_dict).
    """
    colors = {
        1: "#C9D6A3",   # unburned to low — pale sage
        2: SEV_AMBER,   # low severity
        3: SEV_RUST,    # moderate
        4: SEV_CHAR,    # high
        5: "#5B8A4A",   # increased greenness — green
        6: "#E8E4D6",   # non-mapping / mask — parchment
    }
    # Labels confirmed from the MTBS .xml sidecar (edomv definitions).
    labels = {
        1: "Unburned / Low",
        2: "Low",
        3: "Moderate",
        4: "High",
        5: "Increased Greenness",
        6: "Non-Processing Mask",
    }
    cmap = ListedColormap([colors[i] for i in range(1, 7)])
    return cmap, colors, labels


def damage_palette() -> dict:
    """Return {DAMAGE class -> hex} for DINS structures."""
    return dict(DAMAGE_COLORS)


def wui_palette() -> dict:
    """Return {WUI class -> hex}."""
    return dict(WUI_COLORS)


# Folium/Plotly-friendly ordered color list for severity (hex strings)
def severity_color_list() -> list:
    return list(SEVERITY_RAMP)


def habitat_palette(n: int) -> list:
    """A stable sequence of green/earth tones for habitat bar charts."""
    base = [FOREST_DEEP, SAGE_DARK, SAGE_MID, SAGE_LIGHT, "#B9C4A0",
            "#C9A86A", "#A87D4A", "#7E6B4A", "#5B6E4C", "#9DAE84"]
    if n <= len(base):
        return base[:n]
    # cycle if more classes than base colors
    return [base[i % len(base)] for i in range(n)]


# --------------------------------------------------------------------------- #
# SAVE HELPER
# --------------------------------------------------------------------------- #

# Resolve outputs/ relative to this file (src/ is sibling of outputs/)
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
_OUTPUTS = _PROJECT_ROOT / "outputs"


def outputs_dir(subdir: str = "charts") -> Path:
    d = _OUTPUTS / subdir
    d.mkdir(parents=True, exist_ok=True)
    return d


def save_fig(fig, name: str, subdir: str = "charts", dpi: int = 220) -> Path:
    """
    Save a matplotlib figure as PNG at publication DPI with tight bbox.

    name: filename without extension (e.g. 'act1_perimeters')
    subdir: one of 'charts', 'maps', 'animations'
    """
    if not name.lower().endswith(".png"):
        name = name + ".png"
    path = outputs_dir(subdir) / name
    fig.savefig(path, dpi=dpi, bbox_inches="tight", facecolor=fig.get_facecolor())
    return path


# --------------------------------------------------------------------------- #
# CAPTION HELPER
# --------------------------------------------------------------------------- #

def add_caption(fig, text: str, y: float = -0.02) -> None:
    """Add a small muted source/caveat caption beneath a figure."""
    fig.text(0.01, y, text, ha="left", va="top", fontsize=8.5,
             color=MUTED, wrap=True)
