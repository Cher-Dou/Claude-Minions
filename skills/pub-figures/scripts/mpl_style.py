"""Publication-ready matplotlib defaults + colorblind-safe palette.

Import and call apply_style() before plotting. See the skill SKILL.md for usage.
"""
import os

# Okabe-Ito colorblind-safe palette
PALETTE = [
    "#000000",  # black
    "#E69F00",  # orange
    "#56B4E9",  # sky blue
    "#009E73",  # bluish green
    "#F0E442",  # yellow
    "#0072B2",  # blue
    "#D55E00",  # vermillion
    "#CC79A7",  # reddish purple
]


def apply_style(base_fontsize=8):
    """Apply journal-friendly rcParams globally."""
    import matplotlib as mpl

    mpl.rcParams.update({
        "figure.dpi": 150,
        "savefig.dpi": 300,
        "font.family": "sans-serif",
        "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans"],
        "font.size": base_fontsize,
        "axes.titlesize": base_fontsize + 1,
        "axes.labelsize": base_fontsize,
        "xtick.labelsize": base_fontsize - 1,
        "ytick.labelsize": base_fontsize - 1,
        "legend.fontsize": base_fontsize - 1,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.linewidth": 0.8,
        "xtick.direction": "out",
        "ytick.direction": "out",
        "lines.linewidth": 1.5,
        "lines.markersize": 5,
        "legend.frameon": False,
        "figure.autolayout": True,
        "axes.prop_cycle": mpl.cycler(color=PALETTE),
    })


def save(fig, path_stem, formats=("png", "pdf")):
    """Save a figure to multiple formats. path_stem has no extension."""
    os.makedirs(os.path.dirname(path_stem) or ".", exist_ok=True)
    written = []
    for fmt in formats:
        p = f"{path_stem}.{fmt}"
        fig.savefig(p, bbox_inches="tight")
        written.append(p)
    return written
