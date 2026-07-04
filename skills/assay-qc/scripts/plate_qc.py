#!/usr/bin/env python3
"""Plate QC + normalization for in vitro assays.

Usage:
    python plate_qc.py plate.csv --signal-col signal --role-col role --normalize percent_pos --out results/qc

Expects a long-format CSV with a role column: neg, pos, blank (optional), sample.
Outputs <out>_metrics.json and <out>_normalized.csv.
"""
import argparse
import json
import os
import sys

import numpy as np
import pandas as pd


def cv_percent(x):
    x = np.asarray(x, dtype=float)
    m = np.mean(x)
    return float(100.0 * np.std(x, ddof=1) / m) if m != 0 and len(x) > 1 else float("nan")


def z_prime(pos, neg):
    pos, neg = np.asarray(pos, float), np.asarray(neg, float)
    if len(pos) < 2 or len(neg) < 2:
        return float("nan")
    sep = abs(np.mean(pos) - np.mean(neg))
    if sep == 0:
        return float("nan")
    return float(1.0 - (3.0 * (np.std(pos, ddof=1) + np.std(neg, ddof=1))) / sep)


def mad_outliers(values, k=3.5):
    v = np.asarray(values, float)
    med = np.median(v)
    mad = np.median(np.abs(v - med))
    if mad == 0:
        return np.zeros(len(v), dtype=bool)
    modified_z = 0.6745 * (v - med) / mad
    return np.abs(modified_z) > k


def main():
    ap = argparse.ArgumentParser(description="Plate QC and normalization.")
    ap.add_argument("csv")
    ap.add_argument("--signal-col", default="signal")
    ap.add_argument("--role-col", default="role")
    ap.add_argument("--well-col", default="well")
    ap.add_argument("--conc-col", default="concentration")
    ap.add_argument("--normalize", choices=["percent_vehicle", "percent_pos", "fold"], default="percent_pos")
    ap.add_argument("--out", default="qc")
    args = ap.parse_args()

    df = pd.read_csv(args.csv)
    for col in (args.signal_col, args.role_col):
        if col not in df.columns:
            sys.exit(f"Column '{col}' not found. Available: {list(df.columns)}")

    roles = df[args.role_col].astype(str).str.lower()
    sig = df[args.signal_col].astype(float)

    blank = sig[roles == "blank"]
    blank_val = float(blank.mean()) if len(blank) else 0.0

    neg = sig[roles == "neg"] - blank_val
    pos = sig[roles == "pos"] - blank_val

    metrics = {
        "n_wells": int(len(df)),
        "blank_mean": blank_val,
        "n_neg": int(len(neg)),
        "n_pos": int(len(pos)),
        "neg_mean": float(neg.mean()) if len(neg) else None,
        "pos_mean": float(pos.mean()) if len(pos) else None,
        "neg_cv_percent": cv_percent(neg) if len(neg) else None,
        "pos_cv_percent": cv_percent(pos) if len(pos) else None,
        "z_prime": z_prime(pos, neg) if len(pos) and len(neg) else None,
        "signal_window_fold": float(pos.mean() / neg.mean()) if len(neg) and neg.mean() != 0 else None,
    }

    # Verdict
    verdict, notes = "PASS", []
    zp = metrics["z_prime"]
    if zp is None:
        verdict, notes = "UNKNOWN", ["Missing pos/neg controls; cannot compute Z'."]
    else:
        if zp < 0:
            verdict = "FAIL"; notes.append(f"Z'={zp:.2f} < 0: assay window unusable.")
        elif zp < 0.5:
            verdict = "MARGINAL"; notes.append(f"Z'={zp:.2f}: marginal separation.")
    for label, cv in (("neg", metrics["neg_cv_percent"]), ("pos", metrics["pos_cv_percent"])):
        if cv is not None and cv > 20:
            if verdict == "PASS":
                verdict = "MARGINAL"
            notes.append(f"{label} control CV={cv:.1f}% (>20%).")
    metrics["verdict"] = verdict
    metrics["notes"] = notes

    # Outliers among sample wells
    sample_mask = (roles == "sample").values
    out_flags = np.zeros(len(df), dtype=bool)
    if sample_mask.any():
        out_flags[sample_mask] = mad_outliers((sig - blank_val)[sample_mask].values)
    wells = df[args.well_col] if args.well_col in df.columns else pd.Series(df.index.astype(str))
    metrics["outlier_wells"] = [str(w) for w, f in zip(wells, out_flags) if f]

    # Normalization
    corrected = sig - blank_val
    neg_mean = neg.mean() if len(neg) else np.nan
    pos_mean = pos.mean() if len(pos) else np.nan
    if args.normalize == "percent_vehicle":
        norm = 100.0 * corrected / neg_mean
        norm_label = "% of vehicle control"
    elif args.normalize == "percent_pos":
        norm = 100.0 * (corrected - neg_mean) / (pos_mean - neg_mean)
        norm_label = "% of positive-control window"
    else:
        norm = corrected / neg_mean
        norm_label = "fold-change vs vehicle"

    out_df = df.copy()
    out_df["signal_blanksub"] = corrected
    out_df["normalized"] = norm
    out_df["outlier"] = out_flags
    metrics["normalization"] = norm_label

    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    metrics_path = f"{args.out}_metrics.json"
    norm_path = f"{args.out}_normalized.csv"
    with open(metrics_path, "w") as f:
        json.dump(metrics, f, indent=2)
    out_df.to_csv(norm_path, index=False)

    print(json.dumps(metrics, indent=2))
    print(f"\nSaved metrics    -> {metrics_path}")
    print(f"Saved normalized -> {norm_path}")
    print(f"\nVERDICT: {verdict}")
    for n in notes:
        print(f"  - {n}")


if __name__ == "__main__":
    main()
