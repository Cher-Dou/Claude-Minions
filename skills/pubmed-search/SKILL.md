---
name: pubmed-search
description: Build reproducible literature queries and search the biomedical literature via Europe PMC and NCBI E-utilities. Use for systematic-style searches, deduplication, and generating a screening log for toxicology/environmental-health reviews. Provides a ready-to-run Python script (no API key required).
---

# PubMed / Europe PMC search

Runs reproducible literature searches against public APIs and returns structured records.

## When to use
For any systematic or semi-systematic evidence search. Prefer this over ad-hoc web search when reproducibility matters.

## APIs used (no key required)
- **Europe PMC** REST (`https://www.ebi.ac.uk/europepmc/webservices/rest/search`) — default; returns PMIDs, DOIs, abstracts.
- **NCBI E-utilities** (`esearch`/`efetch`) — optional cross-check.

> Set a real contact email in requests to comply with NCBI/Europe PMC etiquette. Pass `--email you@inst.edu`.

## Building a good query
1. Break the question into PECO concepts.
2. For each concept, OR together synonyms + MeSH terms.
3. AND the concepts together.

Example (EDC → adipogenesis):
```
(("endocrine disruptor" OR "bisphenol" OR "phthalate" OR "PFAS")
 AND ("adipogenesis" OR "obesity" OR "PPAR gamma" OR "adipocyte")
 AND ("in vitro" OR "cell"))
```

## Quick start
```bash
python scripts/europepmc_search.py \
  --query '("bisphenol A") AND ("adipogenesis" OR "PPAR gamma")' \
  --email you@inst.edu \
  --max 200 \
  --out results/search
```

Outputs:
- `results/search_records.csv` — pmid, doi, title, authors, journal, year, abstract, source
- `results/search_query.txt` — the exact query + timestamp + count (top of a PRISMA flow)

Options: `--from-year 2010`, `--open-access-only`, `--source MED` (MED=PubMed, PMC=full text, PPR=preprints).

## Screening workflow (do this after retrieval)
1. Record counts: found → after dedup.
2. State inclusion/exclusion criteria explicitly.
3. Screen title/abstract into an include/exclude log with a reason per record.
4. Never fabricate a PMID/DOI — every included record traces to a retrieved row.

## Dependencies
`requests`, `pandas`. Install: `pip install requests pandas`
