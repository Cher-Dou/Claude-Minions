#!/usr/bin/env python3
"""Build a metabolic-target potency panel for the four UV filters.

Simulates reporter-gene concentration-response for each compound x target,
fits each with the dose-response-fitting skill, and writes an EC50 matrix +
a potency (pEC50) heatmap. SIMULATED data for pipeline demonstration only.

Run from repo root:  python examples/uv-filters/build_panel.py
"""
import csv
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(REPO, "skills", "dose-response-fitting", "scripts"))
sys.path.insert(0, os.path.join(REPO, "skills", "pub-figures", "scripts"))
from fit_dose_response import fit  # noqa: E402
from mpl_style import apply_style, PALETTE  # noqa: E402

OUT = os.path.join(REPO, "examples", "uv-filters", "out")
os.makedirs(OUT, exist_ok=True)

COMPOUNDS = ["4-MBC", "Oxybenzone (BP-3)", "Octinoxate (OMC)", "Octocrylene"]
TARGETS = ["ERa", "PPARg", "TRb", "GR", "RXRa"]

# Illustrative EC50 (uM); None = no effect up to 100 uM (bounded result).
# Rows = compounds, cols = targets. Values informed only loosely by literature
# breadth (BP-3 broadest; octocrylene lipophilic -> PPARg/RXR); DEMONSTRATION ONLY.
EC50_TRUE = {
    "4-MBC":             {"ERa": 2.0,  "PPARg": None, "TRb": 25.0, "GR": None, "RXRa": None},
    "Oxybenzone (BP-3)": {"ERa": 7.9,  "PPARg": 40.0, "TRb": 15.0, "GR": 60.0, "RXRa": None},
    "Octinoxate (OMC)":  {"ERa": 15.0, "PPARg": None, "TRb": 30.0, "GR": None, "RXRa": None},
    "Octocrylene":       {"ERa": 63.0, "PPARg": 55.0, "TRb": None, "GR": None, "RXRa": 45.0},
}

CONCS = [0.03, 0.1, 0.3, 1, 3, 10, 30, 100]
# Deterministic pseudo-noise (no RNG: Date/random unavailable in some contexts; keep reproducible)
def jitter(i):
    return ((i * 37) % 11 - 5) * 0.9  # small deterministic wobble in +/-4.5 % units


def simulate_normalized(ec50, hill=1.05):
    """Return (concs, responses) as % of positive control (0-100)."""
    xs, ys = [], []
    k = 0
    for c in CONCS:
        base = 100.0 / (1.0 + (ec50 / c) ** hill)
        for _ in range(3):
            xs.append(c)
            ys.append(round(base + jitter(k), 1))
            k += 1
    return xs, ys


def main():
    matrix = {}      # (compound,target) -> dict(ec50, ci, r2, flag)
    for comp in COMPOUNDS:
        matrix[comp] = {}
        for tgt in TARGETS:
            ec50_true = EC50_TRUE[comp][tgt]
            if ec50_true is None:
                matrix[comp][tgt] = {"ec50": None, "note": "no effect up to 100 uM"}
                continue
            xs, ys = simulate_normalized(ec50_true)
            res = fit(xs, ys, direction="up", fix_bottom=0, fix_top=100)
            matrix[comp][tgt] = {
                "ec50": res["ec50_ic50"],
                "ci": res["ec50_ic50_95ci"],
                "r2": res["r_squared"],
                "note": "; ".join(res["warnings"]) if res["warnings"] else "",
            }

    # --- write EC50 matrix CSV ---
    csv_path = os.path.join(OUT, "panel_ec50_matrix.csv")
    with open(csv_path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["compound"] + TARGETS)
        for comp in COMPOUNDS:
            row = [comp]
            for tgt in TARGETS:
                cell = matrix[comp][tgt]
                row.append(f"{cell['ec50']:.1f}" if cell["ec50"] is not None else "n.e.")
            w.writerow(row)
    print(f"Saved matrix -> {csv_path}")

    # --- heatmap of pEC50 = -log10(EC50 in M); higher = more potent ---
    import math
    import numpy as np
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    apply_style(base_fontsize=9)
    grid = np.full((len(COMPOUNDS), len(TARGETS)), np.nan)
    for i, comp in enumerate(COMPOUNDS):
        for j, tgt in enumerate(TARGETS):
            ec50 = matrix[comp][tgt]["ec50"]
            if ec50:
                grid[i, j] = 6.0 - math.log10(ec50)  # uM -> pEC50

    fig, ax = plt.subplots(figsize=(6, 3.4), dpi=200)
    cmap = plt.cm.viridis.copy()
    cmap.set_bad("#e8e8e8")  # grey for "no effect"
    im = ax.imshow(grid, cmap=cmap, aspect="auto", vmin=4.0, vmax=5.6)
    ax.set_xticks(range(len(TARGETS)), TARGETS)
    ax.set_yticks(range(len(COMPOUNDS)), COMPOUNDS)
    ax.set_title("Simulated potency panel (pEC50; grey = no effect ≤100 µM)", fontsize=9)
    for i in range(len(COMPOUNDS)):
        for j in range(len(TARGETS)):
            ec50 = matrix[COMPOUNDS[i]][TARGETS[j]]["ec50"]
            txt = f"{ec50:.0f}" if ec50 else "n.e."
            val = grid[i, j]
            color = "white" if (not np.isnan(val) and val > 5.0) else "#222"
            ax.text(j, i, txt, ha="center", va="center", fontsize=8, color=color)
    cbar = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    cbar.set_label("pEC50 (higher = more potent)", fontsize=8)
    fig.tight_layout()
    png_path = os.path.join(OUT, "panel_heatmap.png")
    fig.savefig(png_path, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved heatmap -> {png_path}")

    # print a quick text view
    print("\nEC50 matrix (uM; n.e. = no effect up to 100 uM):")
    print(f"{'compound':22}" + "".join(f"{t:>9}" for t in TARGETS))
    for comp in COMPOUNDS:
        cells = "".join(
            (f"{matrix[comp][t]['ec50']:>9.1f}" if matrix[comp][t]["ec50"] else f"{'n.e.':>9}")
            for t in TARGETS)
        print(f"{comp:22}{cells}")


if __name__ == "__main__":
    main()
