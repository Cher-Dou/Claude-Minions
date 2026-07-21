# Evaluations

This folder contains reproducible benchmarks for the environmental toxicology
agents and skills.

The first benchmark is `lit_scout`, a 20-record PubMed gold standard for
screening and structured evidence extraction.

Evaluation is part of the scientific contract of this project: agents should be
useful, traceable, and honest about evidence level before their outputs are used
for reviews, reports, or decision support.

## Structure

| Path | Purpose |
|---|---|
| `metrics.py` | Shared dependency-free scoring helpers for benchmarks. |
| `lit_scout/` | First literature screening and extraction benchmark. |
| `reports/` | Human-readable evaluation reports and summaries. |

## Benchmark roadmap

The long-term benchmark plan is documented in
[`../benchmarks/AIToxBench/`](../benchmarks/AIToxBench/). Start small, keep each
benchmark expert-reviewable, and expand only when the evaluation question is
clear.
