#!/usr/bin/env python3
"""Evaluate lit-scout predictions against a scientist-reviewed benchmark.

The evaluator is intentionally lightweight: it uses exact matching for categorical
fields and token-overlap matching for free-text fields. It is a first-pass guard
rail for regressions, not a substitute for expert review.
"""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from metrics import accuracy, exact_match, normalize, precision_recall, token_overlap, yes_no


CATEGORICAL_FIELDS = [
    "predicted_include",
    "direct_intervention_test",
]

FREE_TEXT_FIELDS = [
    "topic",
    "chemical",
    "intervention",
    "model",
    "evidence_type",
    "main_endpoint",
]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--gold", default="evals/lit_scout/gold_standard.csv")
    parser.add_argument("--predictions", required=True)
    parser.add_argument(
        "--text-threshold",
        type=float,
        default=0.60,
        help="Minimum expected-token recall for free-text field matches.",
    )
    args = parser.parse_args()

    gold_rows = {row["pmid"]: row for row in read_csv(Path(args.gold))}
    prediction_rows = {row["pmid"]: row for row in read_csv(Path(args.predictions))}

    missing = sorted(set(gold_rows) - set(prediction_rows))
    extra = sorted(set(prediction_rows) - set(gold_rows))

    results: list[dict[str, str]] = []
    include_tp = include_fp = include_fn = 0
    include_exact = 0
    citation_valid = 0
    unsupported_claims = 0
    field_scores = {field: 0 for field in CATEGORICAL_FIELDS + FREE_TEXT_FIELDS}
    compared = 0

    for pmid, gold in gold_rows.items():
        pred = prediction_rows.get(pmid)
        if not pred:
            continue
        compared += 1

        expected_include = normalize(gold["expected_include"])
        predicted_include = normalize(pred.get("predicted_include", ""))
        exact_include = exact_match(expected_include, predicted_include)
        include_exact += int(exact_include)

        expected_positive = expected_include == "yes"
        predicted_positive = predicted_include == "yes"
        include_tp += int(expected_positive and predicted_positive)
        include_fp += int(not expected_positive and predicted_positive)
        include_fn += int(expected_positive and not predicted_positive)

        citation_valid += int(bool(normalize(pred.get("pmid", ""))))
        unsupported_claims += int(normalize(pred.get("claim_supported", "yes")) == "no")

        row_result = {"pmid": pmid, "include_exact": yes_no(exact_include)}
        for field in CATEGORICAL_FIELDS:
            expected_field = "expected_include" if field == "predicted_include" else field
            ok = exact_match(gold.get(expected_field, ""), pred.get(field, ""))
            field_scores[field] += int(ok)
            row_result[field] = yes_no(ok)
        for field in FREE_TEXT_FIELDS:
            overlap = token_overlap(gold.get(field, ""), pred.get(field, ""))
            ok = overlap >= args.text_threshold
            field_scores[field] += int(ok)
            row_result[field] = f"{overlap:.2f}"
        results.append(row_result)

    precision, recall = precision_recall(include_tp, include_fp, include_fn)

    print("# lit-scout evaluation")
    print(f"Gold rows: {len(gold_rows)}")
    print(f"Predicted rows compared: {compared}")
    print(f"Missing PMIDs: {', '.join(missing) if missing else 'none'}")
    print(f"Extra PMIDs: {', '.join(extra) if extra else 'none'}")
    print()
    print("## Screening")
    print(f"Include exact accuracy: {accuracy(include_exact, compared):.3f}" if compared else "Include exact accuracy: n/a")
    print(f"Screening precision: {precision:.3f}")
    print(f"Screening recall: {recall:.3f}")
    print()
    print("## Field Accuracy")
    for field, count in field_scores.items():
        label = "include" if field == "predicted_include" else field
        print(f"{label}: {accuracy(count, compared):.3f}" if compared else f"{label}: n/a")
    print()
    print("## Safety")
    print(f"Citation validity proxy: {accuracy(citation_valid, compared):.3f}" if compared else "Citation validity proxy: n/a")
    print(f"Unsupported-claim count: {unsupported_claims}")

    return 0 if not missing else 1


if __name__ == "__main__":
    raise SystemExit(main())
