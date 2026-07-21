# lit-scout Evaluation

This directory contains the first scientist-reviewed benchmark for the `lit-scout`
agent. It is intentionally small and inspectable: 20 PubMed records covering
clearly relevant EDC/MDC papers, nutrient-protection papers, borderline cases,
and misleading keyword-only records.

## Files

| File | Purpose |
| --- | --- |
| `gold_standard.csv` | Manual benchmark labels and expected extracted fields. |
| `predictions_template.csv` | Empty prediction file for an agent run. |
| `evaluate.py` | Lightweight scoring script for screening and extraction fields. |
| `error_analysis.md` | Template for reviewing failures after the first prediction run. |

## How To Run

Fill `predictions_template.csv` with `lit-scout` outputs, save it as
`predictions.csv`, then run:

```bash
python evals/lit_scout/evaluate.py --predictions evals/lit_scout/predictions.csv
```

## Initial Acceptance Targets

These are early targets, not claims of production performance:

| Metric | Target |
| --- | ---: |
| Screening precision | >= 0.90 |
| Screening recall | >= 0.85 |
| Citation validity | 1.00 |
| Chemical extraction | >= 0.95 |
| Intervention extraction | >= 0.90 |
| Model classification | >= 0.90 |
| Unsupported claims | 0 |

## Notes

`Borderline` rows are deliberate. They test whether the agent can avoid
overclaiming when a record is adjacent to the EDC/MDC scope but not direct human
metabolic, reproductive, gut-hormone, or nutrient-protection evidence.
