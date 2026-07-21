# lit-scout Evaluation v1

Status: benchmark scaffold added; predictions not yet generated.

## Scope

The first benchmark evaluates whether `lit-scout` can:

- include clearly relevant EDC/MDC and nutrient-protection records
- reject exposure-only or analytical-method keyword matches
- keep human, animal, in vitro, review, and ecotoxicology evidence distinct
- avoid unsupported claims about nutrient protection
- preserve traceability to PMID and DOI

## Dataset

`evals/lit_scout/gold_standard.csv` contains 20 PubMed records:

- 12 expected include
- 4 borderline
- 4 expected exclude

## Next Step

Run `lit-scout` against these 20 PMIDs, save outputs to
`evals/lit_scout/predictions.csv`, then run:

```bash
python evals/lit_scout/evaluate.py --predictions evals/lit_scout/predictions.csv
```

Record the first results and error analysis in this report.
