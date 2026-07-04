#!/usr/bin/env python3
"""Margin of exposure between an in vitro effect concentration and human exposure.

Usage:
    python exposure_context.py --ec50 0.5 --ec50-unit uM --exposure 12 --exposure-unit nM
    python exposure_context.py --ec50 0.5 --ec50-unit uM --exposure 2.3 --exposure-unit ng/mL --mw 228.29

Mass-based units (g/L, ng/mL, ...) require --mw (g/mol). No third-party dependencies.
"""
import argparse
import json
import sys

# Molar units -> factor to nanomolar (nM)
MOLAR_TO_NM = {"M": 1e9, "mM": 1e6, "uM": 1e3, "nM": 1.0, "pM": 1e-3}
# Mass-concentration units -> factor to grams per litre (g/L)
MASS_TO_GL = {"g/L": 1.0, "mg/L": 1e-3, "ug/mL": 1e-3, "mg/mL": 1.0,
              "ng/mL": 1e-6, "pg/mL": 1e-9, "ug/L": 1e-6, "ng/L": 1e-9}


def to_nM(value, unit, mw=None):
    """Convert a concentration to nanomolar. mw (g/mol) needed for mass units."""
    if unit in MOLAR_TO_NM:
        return value * MOLAR_TO_NM[unit]
    if unit in MASS_TO_GL:
        if mw is None:
            sys.exit(f"Unit '{unit}' is mass-based; provide --mw (molecular weight, g/mol).")
        g_per_L = value * MASS_TO_GL[unit]
        mol_per_L = g_per_L / mw          # mol/L
        return mol_per_L * 1e9            # -> nM
    sys.exit(f"Unknown unit '{unit}'. Supported: {sorted(MOLAR_TO_NM) + sorted(MASS_TO_GL)}")


def interpret(moe):
    if moe < 1:
        return ("HIGH CONCERN",
                "In vitro effect occurs at or below realistic human exposure. Prioritize.")
    if moe < 100:
        return ("POTENTIALLY RELEVANT",
                "Effect concentration is within a few orders of magnitude of exposure.")
    return ("LOWER PRIORITY",
            "Effect concentration is far above realistic exposure (on this endpoint alone).")


def main():
    ap = argparse.ArgumentParser(description="Margin of exposure: in vitro potency vs human exposure.")
    ap.add_argument("--ec50", type=float, required=True, help="In vitro effect concentration (EC50/IC50/AC50).")
    ap.add_argument("--ec50-unit", required=True)
    ap.add_argument("--exposure", type=float, required=True, help="Human exposure / plasma concentration.")
    ap.add_argument("--exposure-unit", required=True)
    ap.add_argument("--mw", type=float, default=None, help="Molecular weight (g/mol); required for mass units.")
    ap.add_argument("--label", default="")
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    ec50_nM = to_nM(args.ec50, args.ec50_unit, args.mw)
    exp_nM = to_nM(args.exposure, args.exposure_unit, args.mw)
    if exp_nM <= 0:
        sys.exit("Exposure concentration must be > 0.")

    moe = ec50_nM / exp_nM
    band, message = interpret(moe)

    result = {
        "label": args.label,
        "ec50_input": f"{args.ec50} {args.ec50_unit}",
        "exposure_input": f"{args.exposure} {args.exposure_unit}",
        "ec50_nM": ec50_nM,
        "exposure_nM": exp_nM,
        "margin_of_exposure": moe,
        "band": band,
        "interpretation": message,
        "caveats": [
            "Screening-level comparison, not a formal risk assessment.",
            "Nominal in vitro concentration may differ from free/bioavailable concentration.",
            "In vitro medium vs plasma concentrations are only approximately comparable; "
            "consider formal IVIVE (e.g. httk) for a rigorous estimate.",
        ],
    }

    print(json.dumps(result, indent=2))
    if args.out:
        with open(args.out, "w") as f:
            json.dump(result, f, indent=2)
        print(f"\nSaved -> {args.out}")
    print(f"\nMOE = {moe:,.2f}  ->  {band}\n{message}")


if __name__ == "__main__":
    main()
