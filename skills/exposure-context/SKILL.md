---
name: exposure-context
description: Put an in vitro potency value in human-relevance terms — compute the margin of exposure (MOE) / bioactivity-exposure ratio between an assay EC50/IC50/AC50 and a realistic human exposure or plasma concentration. Handles unit conversion. Use to judge whether an in vitro effect concentration is near real-world exposure. Provides a ready-to-run Python script.
---

# Exposure context (margin of exposure)

Answers the question every in vitro result raises: **is this effect concentration anywhere near what people are actually exposed to?**

Computes:
```
MOE = in vitro effect concentration / human exposure concentration
```
A large MOE (effect only at concentrations far above exposure) is reassuring; an MOE near or below 1 (effect at or below realistic exposure) flags concern.

## When to use
After `dose-response-fitting` gives an EC50/IC50/AC50, and you have a human exposure estimate — e.g. a biomonitoring plasma/serum concentration, or an estimated internal dose. Pair with `tox-profiler` for the molecular weight when converting mass↔molar units.

## Quick start
```bash
# Both values already in molar units:
python scripts/exposure_context.py \
  --ec50 0.5 --ec50-unit uM \
  --exposure 12 --exposure-unit nM \
  --label "BPA, ERalpha reporter"

# Mixing molar and mass units needs the molecular weight:
python scripts/exposure_context.py \
  --ec50 0.5 --ec50-unit uM \
  --exposure 2.3 --exposure-unit ng/mL \
  --mw 228.29 --label "BPA"
```

Supported units: `M, mM, uM, nM, pM, g/L, mg/L, ug/mL, ng/mL, pg/mL` (mass units require `--mw`).

Output: MOE, both values normalized to nM, and a plain-language interpretation band.

## Interpretation bands (report, don't overstate)
- **MOE < 1** — in vitro effect at or below realistic exposure: prioritize; strongest concern.
- **1–100** — effect within a few orders of magnitude of exposure: potentially relevant.
- **> 100** — effect far above exposure: lower priority on this endpoint alone.

## Honesty rules (enforce these)
- This is a **screening-level** comparison, not a risk assessment. State that.
- Nominal in vitro concentration ≠ free/bioavailable concentration; protein binding and partitioning can shift it. Note it.
- A plasma biomonitoring concentration and an in vitro medium concentration are only *approximately* comparable — full in vitro–in vivo extrapolation (e.g. `httk`) is more rigorous. Flag when that's warranted.
- Always cite the source and type of the exposure estimate (which biomonitoring study, population, percentile).

## Dependencies
None beyond the Python standard library.
