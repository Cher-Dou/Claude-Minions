---
name: pub-figures
description: Publication-ready matplotlib styling for toxicology/biology figures — consistent fonts, sizing, DPI, and a colorblind-safe palette. Use when producing figures for manuscripts or posters. Provides an importable style module.
---

# Publication figures

Applies journal-friendly defaults so figures look consistent and print cleanly.

## When to use
Any figure headed for a manuscript, thesis, or poster (dose-response curves, bar charts, heatmaps).

## Usage
Import and call before plotting:

```python
import sys; sys.path.insert(0, "skills/pub-figures/scripts")
from mpl_style import apply_style, PALETTE, save

apply_style()          # sets fonts, sizes, dpi, spines
fig, ax = ...          # your plot, using colors from PALETTE
save(fig, "figures/fig1", formats=("png", "pdf", "svg"))  # multi-format export
```

## What it sets
- Font: sans-serif, ~7–9 pt (journal body-text scale), tight layout.
- 300+ DPI raster; vector PDF/SVG for line art.
- De-cluttered spines (top/right off), outward ticks.
- **Colorblind-safe palette** (Okabe–Ito) exposed as `PALETTE`.

## Conventions
- Dose-response: log-scale x-axis, points + fitted line, error bars = SD or 95% CI (state which in the legend).
- One idea per panel; label panels A, B, C.
- Always include units on axes and n in the legend.

## Dependencies
`matplotlib`. Install: `pip install matplotlib`
