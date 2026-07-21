# AIToxBench

AIToxBench is an open benchmark suite for evaluating AI agents that perform
environmental toxicology research.

The goal is to make scientific AI systems measurable, reproducible, and
transparent through expert-reviewed datasets spanning literature screening,
chemical profiling, bioassay interpretation, adverse outcome pathways, and
scientific writing.

AIToxBench is designed for Claude-Minions and future AI-for-science agent
platforms that work with endocrine-disrupting chemicals, metabolic disrupting
chemicals, and protective nutrient evidence.

## Why AIToxBench Exists

Current AI benchmarks evaluate general reasoning, mathematics, coding, or
language understanding. They do not evaluate whether an AI system can perform
reliable scientific research in environmental toxicology.

AIToxBench fills this gap by providing expert-reviewed benchmark datasets
covering endocrine disruption, metabolic disruption, bioassays, adverse outcome
pathways, and scientific evidence synthesis.

## Evaluation Philosophy

AIToxBench evaluates scientific reasoning rather than language fluency.

Benchmarks are designed to measure:

- evidence retrieval
- literature screening
- structured evidence extraction
- mechanistic reasoning
- exposure interpretation
- citation accuracy
- scientific writing fidelity

General language tasks are intentionally excluded.

The first implemented benchmark lives in `evals/lit_scout/`. This folder records
the broader benchmark roadmap so future datasets grow in a consistent way.

## Version Roadmap

| Version | Focus | Status |
|---|---|---|
| v0.1 | `lit-scout` literature screening and structured extraction | In progress |
| v0.2 | Chemical profiling and exposure context | Planned |
| v0.3 | Bioassay QC and dose-response interpretation | Planned |
| v0.4 | AOP mapping and mechanism-to-endpoint reasoning | Planned |
| v0.5 | Scientific writing fidelity and citation support | Planned |

## Planned Benchmark Areas

| Area | Purpose | Initial size |
|---|---|---:|
| EDC literature screening | Include/exclude decisions for EDC/MDC literature. | 100 papers |
| Nutrient protection | Direct nutrient/intervention evidence against toxicant effects. | 50 papers |
| Female fertility | Ovarian, follicular, oocyte, embryo, and reproductive endocrine outcomes. | 50 papers |
| Male fertility | Testicular, sperm, steroidogenesis, and reproductive endocrine outcomes. | 50 papers |
| Metabolic disruption | Insulin, adipocyte biology, obesity, MASLD/MASH, and metabolic syndrome. | 50 papers |
| Gut mechanisms | Gut hormones, enteroendocrine biology, microbiome, and barrier function. | 50 papers |
| Chemical profiling | CAS/name resolution, PubChem/CompTox fields, and exposure context. | 50 chemicals |
| Bioassay analysis | QC, normalization, dose-response fitting, and reporting. | 50 assays |
| AOP mapping | Mechanism-to-endpoint chains with evidence strength. | 25 pathways |
| Scientific writing | Citation accuracy, claim support, and unsupported-claim checks. | 50 writing tasks |

## Standard Metrics

Every benchmark should report one or more of:

- precision
- recall
- F1 score
- citation validity
- evidence extraction accuracy
- unsupported-claim rate
- structured output completeness
- JSON or table validity, when structured output is required
- human-review rate

## Minimal Shared Schema

Each literature benchmark should start with these fields:

```text
pmid
doi
title
topic
chemical
intervention
mechanism
main_endpoint
model
evidence_type
evidence_level
expected_include
ground_truth_summary
review_notes
```

## Design Principles

- Build benchmarks that answer a specific evaluation question.
- Prefer expert-reviewed annotations over automatically generated labels.
- Keep early datasets intentionally small so expert review stays practical.
- Expand through versioned releases rather than uncontrolled growth.
- Every benchmark should be reproducible and openly documented.
- Only add fields that support an evaluation question.

AIToxBench aims to become the reference benchmark for evaluating AI agents in
environmental toxicology and endocrine-disruptor research.
