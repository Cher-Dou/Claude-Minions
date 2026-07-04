---
name: dose-response-fitting
description: Fit concentration-response data to a 4-parameter logistic (Hill) model and report EC50/IC50 with confidence intervals, Hill slope, and R². Use when analyzing reporter-gene, viability, or high-content dose-response data. Provides a ready-to-run Python script.
---

# Dose-response fitting

Fits the 4-parameter logistic (4PL / Hill) model:

```
y = bottom + (top - bottom) / (1 + (EC50 / x) ** hill)
```

## When to use
After plate QC and normalization (see the `assay-qc` skill). Input is a tidy CSV of concentration vs response, optionally with replicates.

## Quick start

Input CSV must have a concentration column and a response column (long format; multiple rows per concentration = replicates):

```
concentration,response
0.001,2.1
0.001,3.0
0.01,5.5
...
```

Run:

```bash
python scripts/fit_dose_response.py data.csv \
  --conc-col concentration --resp-col response \
  --out results/fit
```

Outputs:
- `results/fit_params.json` — EC50/IC50, 95% CI, Hill slope, top, bottom, R², RMSE
- `results/fit_curve.png` — points + fitted curve on a log-dose axis

Options:
- `--direction auto|up|down` — agonist (up) vs inhibitor/IC50 (down); `auto` infers from data.
- `--log-fit` — fit on log10(concentration) for better conditioning (recommended).
- `--fix-bottom 0 --fix-top 100` — constrain plateaus when normalized to %.

## Interpretation rules (enforce these when reporting)
- Report EC50/IC50 **with its 95% CI and R²** — never the point estimate alone.
- If the top plateau is not reached, the EC50 is an **extrapolation** — flag it; consider reporting only a lower bound.
- A poor R² (< ~0.9) or a Hill slope wildly off (|slope| > ~4 or < ~0.3) signals a bad fit — inspect, don't trust the number.
- "No effect up to the highest concentration tested" is a valid, bounded result — prefer it over forcing a curve.

## Dependencies
`numpy`, `scipy`, `pandas`, `matplotlib`. Install: `pip install numpy scipy pandas matplotlib`
