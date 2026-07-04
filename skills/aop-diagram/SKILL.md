---
name: aop-diagram
description: Render an Adverse Outcome Pathway (node/edge list) into a diagram — a Mermaid flowchart that renders on GitHub/Markdown and a standalone PNG. Use after aop-mapper produces a structured MIE/KE/AO/KER list. Provides a ready-to-run Python script.
---

# AOP diagram

Turns a structured Adverse Outcome Pathway into a picture: Molecular Initiating Event → Key Events → Adverse Outcome, with edges styled by weight of evidence.

## When to use
After the `aop-mapper` agent produces a node/edge JSON. This skill only *draws* it — the mechanistic reasoning and evidence weighting happen upstream.

## Input format
A JSON file describing the pathway:

```json
{
  "title": "PPARγ activation → adipogenesis",
  "mie": {"id": "MIE", "label": "PPARγ activation"},
  "key_events": [
    {"id": "KE1", "label": "Adipocyte differentiation", "level": "cellular"},
    {"id": "KE2", "label": "Lipid accumulation", "level": "cellular"},
    {"id": "KE3", "label": "Adipose tissue expansion", "level": "tissue"}
  ],
  "ao": {"id": "AO", "label": "Obesity"},
  "kers": [
    {"from": "MIE", "to": "KE1", "confidence": "strong",   "evidence": "in vitro + animal"},
    {"from": "KE1", "to": "KE2", "confidence": "strong",   "evidence": "in vitro"},
    {"from": "KE2", "to": "KE3", "confidence": "moderate", "evidence": "animal"},
    {"from": "KE3", "to": "AO",  "confidence": "moderate", "evidence": "human assoc."}
  ]
}
```

`confidence` ∈ `strong | moderate | weak` (controls line style). Order `key_events` from molecular → organism.

## Quick start
```bash
python scripts/render_aop.py aop.json --out results/aop
```

Outputs:
- `results/aop.mmd` — Mermaid flowchart source (paste into a `.md` file; GitHub renders it)
- `results/aop.md` — the Mermaid wrapped in a fenced ```mermaid block, ready to drop in a README
- `results/aop.png` — standalone raster (if matplotlib is installed)

## Conventions
- MIE at top, AO at bottom, Key Events in between ordered by biological level.
- Edge style encodes confidence: solid = strong, dashed = moderate, dotted = weak.
- Keep the diagram chemical-agnostic; the specific chemical that triggers the MIE is stated in the caption, not the boxes.

## Dependencies
Mermaid/Markdown output needs nothing. PNG output needs `matplotlib` (`pip install matplotlib`).
