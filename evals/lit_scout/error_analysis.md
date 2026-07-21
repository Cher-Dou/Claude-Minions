# lit-scout Error Analysis

Status: template; fill after the first prediction run.

## Summary

| Metric | Result | Target | Pass? |
|---|---:|---:|---|
| Screening precision | TBD | >= 0.90 | TBD |
| Screening recall | TBD | >= 0.85 | TBD |
| Citation validity | TBD | 1.00 | TBD |
| Chemical extraction | TBD | >= 0.95 | TBD |
| Intervention extraction | TBD | >= 0.90 | TBD |
| Model classification | TBD | >= 0.90 | TBD |
| Unsupported claims | TBD | 0 | TBD |

## Error Categories

Use these categories when reviewing failed rows:

| Category | Meaning |
|---|---|
| False positive | Agent included a record that should be excluded or treated as borderline. |
| False negative | Agent excluded a clearly relevant record. |
| Evidence-category error | Agent confused human, animal, in vitro, review, computational, or ecotoxicology evidence. |
| Directness error | Agent treated a nutrient/intervention as tested when it was only mentioned. |
| Mechanism overclaim | Agent inferred a pathway not supported by the source. |
| Citation mismatch | PMID, DOI, title, or link does not resolve to the same record. |

## Row-Level Notes

| PMID | Error category | What happened | Fix idea |
|---|---|---|---|
| TBD | TBD | TBD | TBD |
