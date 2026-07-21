"""Shared evaluation metrics for scientific-agent benchmarks.

The functions here are deliberately small and dependency-free so every agent
benchmark can reuse the same scoring logic in local runs and CI.
"""

from __future__ import annotations

import re


STOPWORDS = {"and", "or", "the", "of", "in", "with", "none"}


def normalize(value: str) -> str:
    """Normalize a value for exact categorical comparison."""
    return " ".join(value.strip().lower().split())


def tokens(value: str) -> set[str]:
    """Tokenize free-text fields for lightweight overlap scoring."""
    return {
        token
        for token in re.findall(r"[a-z0-9]+", normalize(value))
        if token not in STOPWORDS
    }


def exact_match(expected: str, predicted: str) -> bool:
    return normalize(expected) == normalize(predicted)


def token_overlap(expected: str, predicted: str) -> float:
    """Return recall of expected tokens in the predicted text."""
    expected_tokens = tokens(expected)
    predicted_tokens = tokens(predicted)
    if not expected_tokens and not predicted_tokens:
        return 1.0
    if not expected_tokens or not predicted_tokens:
        return 0.0
    return len(expected_tokens & predicted_tokens) / len(expected_tokens)


def accuracy(correct: int, total: int) -> float:
    return correct / total if total else 0.0


def precision_recall(tp: int, fp: int, fn: int) -> tuple[float, float]:
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    return precision, recall


def yes_no(value: bool) -> str:
    return "yes" if value else "no"
