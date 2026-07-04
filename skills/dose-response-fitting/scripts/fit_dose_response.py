#!/usr/bin/env python3
"""Fit a 4-parameter logistic (Hill) dose-response curve.

Usage:
    python fit_dose_response.py data.csv --conc-col concentration --resp-col response --out results/fit

Outputs <out>_params.json and <out>_curve.png.
"""
import argparse
import json
import os
import sys

import numpy as np
import pandas as pd
from scipy.optimize import curve_fit


def logistic4(x, bottom, top, ec50, hill):
    """4PL / Hill model. x is concentration (linear units)."""
    return bottom + (top - bottom) / (1.0 + (ec50 / x) ** hill)


def fit(conc, resp, direction="auto", fix_bottom=None, fix_top=None):
    conc = np.asarray(conc, dtype=float)
    resp = np.asarray(resp, dtype=float)
    mask = (conc > 0) & np.isfinite(conc) & np.isfinite(resp)
    conc, resp = conc[mask], resp[mask]
    if len(conc) < 4:
        raise ValueError("Need at least 4 valid (concentration, response) points to fit 4 parameters.")

    lo, hi = float(np.min(resp)), float(np.max(resp))
    b0 = fix_bottom if fix_bottom is not None else lo
    t0 = fix_top if fix_top is not None else hi
    ec0 = float(np.median(conc))

    if direction == "down" or (direction == "auto" and resp[np.argmax(conc)] < resp[np.argmin(conc)]):
        hill0 = -1.0
        curve_direction = "down (IC50)"
    else:
        hill0 = 1.0
        curve_direction = "up (EC50)"

    p0 = [b0, t0, ec0, hill0]

    # Optionally constrain plateaus by fixing them via bounds collapse.
    lower = [-np.inf, -np.inf, 1e-12, -10.0]
    upper = [np.inf, np.inf, np.inf, 10.0]
    if fix_bottom is not None:
        lower[0], upper[0] = fix_bottom - 1e-9, fix_bottom + 1e-9
    if fix_top is not None:
        lower[1], upper[1] = fix_top - 1e-9, fix_top + 1e-9

    popt, pcov = curve_fit(logistic4, conc, resp, p0=p0, bounds=(lower, upper), maxfev=100000)
    perr = np.sqrt(np.diag(pcov))

    pred = logistic4(conc, *popt)
    ss_res = float(np.sum((resp - pred) ** 2))
    ss_tot = float(np.sum((resp - np.mean(resp)) ** 2))
    r2 = 1.0 - ss_res / ss_tot if ss_tot > 0 else float("nan")
    rmse = float(np.sqrt(ss_res / len(resp)))

    bottom, top, ec50, hill = popt
    ec50_se = perr[2]
    ci95 = 1.96 * ec50_se
    reached_top = np.max(resp) >= (bottom + 0.9 * (top - bottom)) if hill > 0 else np.min(resp) <= (top - 0.9 * (top - bottom))

    warnings = []
    if not np.isfinite(r2) or r2 < 0.9:
        warnings.append(f"Low R^2 ({r2:.3f}); fit may be unreliable.")
    if abs(hill) > 4 or abs(hill) < 0.3:
        warnings.append(f"Unusual Hill slope ({hill:.2f}); inspect curve shape.")
    if not reached_top:
        warnings.append("Response plateau not reached; EC50/IC50 is an extrapolation.")

    return {
        "model": "4-parameter logistic (Hill)",
        "direction": curve_direction,
        "ec50_ic50": float(ec50),
        "ec50_ic50_95ci": [float(ec50 - ci95), float(ec50 + ci95)],
        "ec50_ic50_se": float(ec50_se),
        "hill_slope": float(hill),
        "top": float(top),
        "bottom": float(bottom),
        "r_squared": r2,
        "rmse": rmse,
        "n_points": int(len(conc)),
        "warnings": warnings,
        "_popt": [float(x) for x in popt],
    }


def plot(conc, resp, popt, out_png, direction_label):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    conc = np.asarray(conc, dtype=float)
    resp = np.asarray(resp, dtype=float)
    mask = conc > 0
    conc, resp = conc[mask], resp[mask]

    xs = np.logspace(np.log10(conc.min()), np.log10(conc.max()), 200)
    ys = logistic4(xs, *popt)

    fig, ax = plt.subplots(figsize=(4.5, 3.5), dpi=200)
    ax.scatter(conc, resp, s=28, color="#1b3a5c", alpha=0.75, zorder=3, label="data")
    ax.plot(xs, ys, color="#c1272d", lw=2, zorder=2, label="4PL fit")
    ax.axvline(popt[2], color="#888", ls="--", lw=1, zorder=1)
    ax.set_xscale("log")
    ax.set_xlabel("Concentration")
    ax.set_ylabel("Response")
    ax.set_title(f"Dose-response ({direction_label})", fontsize=10)
    ax.legend(frameon=False, fontsize=8)
    fig.tight_layout()
    os.makedirs(os.path.dirname(out_png) or ".", exist_ok=True)
    fig.savefig(out_png, bbox_inches="tight")
    plt.close(fig)


def main():
    ap = argparse.ArgumentParser(description="Fit a 4PL dose-response curve.")
    ap.add_argument("csv")
    ap.add_argument("--conc-col", default="concentration")
    ap.add_argument("--resp-col", default="response")
    ap.add_argument("--direction", choices=["auto", "up", "down"], default="auto")
    ap.add_argument("--fix-bottom", type=float, default=None)
    ap.add_argument("--fix-top", type=float, default=None)
    ap.add_argument("--out", default="fit")
    args = ap.parse_args()

    df = pd.read_csv(args.csv)
    for col in (args.conc_col, args.resp_col):
        if col not in df.columns:
            sys.exit(f"Column '{col}' not found. Available: {list(df.columns)}")

    result = fit(
        df[args.conc_col].values,
        df[args.resp_col].values,
        direction=args.direction,
        fix_bottom=args.fix_bottom,
        fix_top=args.fix_top,
    )

    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    params_path = f"{args.out}_params.json"
    popt = result.pop("_popt")
    with open(params_path, "w") as f:
        json.dump(result, f, indent=2)

    png_path = f"{args.out}_curve.png"
    plot(df[args.conc_col].values, df[args.resp_col].values, popt, png_path, result["direction"])

    print(json.dumps(result, indent=2))
    print(f"\nSaved parameters -> {params_path}")
    print(f"Saved figure     -> {png_path}")
    if result["warnings"]:
        print("\nWARNINGS:")
        for w in result["warnings"]:
            print(f"  - {w}")


if __name__ == "__main__":
    main()
