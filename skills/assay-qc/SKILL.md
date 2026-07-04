---
name: assay-qc
description: Quality control and normalization for in vitro plate assays (reporter-gene, high-content, viability). Computes Z'-factor, control CV, signal window, flags outliers, and normalizes wells to controls. Use before fitting any dose-response curve. Provides a ready-to-run Python script.
---

# Assay QC & normalization

Runs the checks that decide whether a plate's data is trustworthy, then normalizes it.

## When to use
On raw plate data, **before** `dose-response-fitting`. If a plate fails QC, say so — do not fit curves on it silently.

## Metrics computed
- **Z'-factor** — separation between positive and negative controls. Rule of thumb: `Z' > 0.5` excellent, `0–0.5` marginal, `< 0` unusable.
- **Signal window / fold-change** — positive vs vehicle control.
- **%CV of controls** — precision; > ~20% is a red flag.
- **Outlier flags** — wells beyond a median ± k·MAD threshold.

## Input format
Long-format CSV with a role column marking control types:

```
well,role,concentration,signal
A1,neg,,102
A2,pos,,1580
A3,sample,0.01,240
...
```
`role` values: `neg` (vehicle/negative control), `pos` (positive control), `blank` (optional), `sample`.

## Quick start
```bash
python scripts/plate_qc.py plate.csv \
  --signal-col signal --role-col role \
  --normalize percent_pos \
  --out results/qc
```

Normalization modes (`--normalize`):
- `percent_vehicle` — % of vehicle control (fold over baseline).
- `percent_pos` — % of positive-control max (0–100 scale; good for agonist EC50).
- `fold` — fold-change vs vehicle.

Outputs:
- `results/qc_metrics.json` — Z', CV, signal window, outlier list, pass/fail verdict
- `results/qc_normalized.csv` — per-well normalized values (blank-subtracted), ready for curve fitting

## Reporting rules
- Always report Z' and control CV alongside any downstream EC50.
- Blank-subtract before normalizing.
- Cross-check the viability/cytotoxicity channel: apparent activity under cytotoxic conditions is an artifact.

## Dependencies
`numpy`, `pandas`. Install: `pip install numpy pandas`
