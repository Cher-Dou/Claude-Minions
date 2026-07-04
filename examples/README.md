# Worked example — from raw plate to human-relevance

This runs the core Claud-Minions analysis chain on a simulated ERα reporter-gene
agonist assay ([`sample_plate.csv`](sample_plate.csv)): 4 vehicle controls, 4 positive
controls, and an 8-point dose series in triplicate.

Run each step from the repository root. Outputs go to `examples/out/`.

```bash
mkdir -p examples/out
```

## 1. Quality control + normalization  (`assay-qc` skill)

```bash
python skills/assay-qc/scripts/plate_qc.py examples/sample_plate.csv \
  --normalize percent_pos --out examples/out/qc
```
Expected: **Z′ ≈ 0.90 → PASS**, control CVs < 5%. Produces `examples/out/qc_normalized.csv`
(per-well, blank-subtracted, on a 0–100% scale).

## 2. Dose-response fit  (`dose-response-fitting` skill)

```bash
python skills/dose-response-fitting/scripts/fit_dose_response.py \
  examples/out/qc_normalized.csv \
  --conc-col concentration --resp-col normalized \
  --fix-bottom 0 --fix-top 100 \
  --out examples/out/fit
```
Expected: **EC50 ≈ 0.29 µM**, Hill slope ≈ 1.2, **R² ≈ 0.999**, no warnings.
Produces `fit_params.json` and `fit_curve.png`.

## 3. Human-relevance context  (`exposure-context` skill)

Compare the EC50 against a (hypothetical) biomonitoring plasma level of 12 nM:

```bash
python skills/exposure-context/scripts/exposure_context.py \
  --ec50 0.285 --ec50-unit uM \
  --exposure 12 --exposure-unit nM \
  --label "test EDC, ERalpha reporter" \
  --out examples/out/moe.json
```
Expected: **MOE ≈ 24 → "POTENTIALLY RELEVANT"** — the in vitro effect concentration is
within ~1.5 orders of magnitude of the exposure estimate.

## Doing this via an agent instead

You don't have to run the scripts by hand. In Claude Code you can just say:

> use the **bioassay-analyst** agent to QC and fit `examples/sample_plate.csv`, then use
> **exposure-context** to compare the EC50 to a 12 nM plasma level

or use the command shortcut:

```
/analyze-assay examples/sample_plate.csv
```

The agent decides which skills to apply and reports the results with the appropriate caveats.

> Note: `sample_plate.csv` is **simulated** data for demonstration only.
