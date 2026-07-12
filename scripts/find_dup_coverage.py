#!/usr/bin/env python3
"""Find test coverage duplicates by comparing per-test covered line sets.

Usage:
    coverage run --context=test -m pytest tests/ 2>/dev/null
    coverage json
    uv run python scripts/find_dup_coverage.py coverage_data.json

Output: pairs of tests whose covered-line Jaccard index > threshold (default 0.8).
"""

import json
import sys
from collections import defaultdict
from pathlib import Path


def _parse_context(context: str) -> str:
    parts = context.rsplit(".", 2)
    return parts[0] + "." + parts[1] if len(parts) >= 2 else context


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else "coverage_data.json"
    threshold = float(sys.argv[2]) if len(sys.argv) > 2 else 0.8

    with Path(path).open(encoding="utf-8") as f:
        data = json.load(f)

    files = data.get("files", {})
    test_lines: dict[str, set] = defaultdict(set)

    for filepath, file_data in files.items():
        for line_num, line_data in file_data.items():
            contexts = line_data.get("contexts", [])
            for ctx in contexts:
                test_name = _parse_context(ctx)
                test_lines[test_name].add(f"{filepath}:{line_num}")

    test_list = list(test_lines.items())
    results = []

    for i in range(len(test_list)):
        name_a, lines_a = test_list[i]
        for j in range(i + 1, len(test_list)):
            name_b, lines_b = test_list[j]
            intersection = len(lines_a & lines_b)
            union = len(lines_a | lines_b)
            if union < 5:
                continue
            jaccard = intersection / union
            if jaccard > threshold:
                results.append((jaccard, intersection, union, name_a, name_b))

    results.sort(key=lambda x: -x[0])

    print(f"Coverage duplicate pairs (Jaccard > {threshold}):")
    print(f"{'Jaccard':>8}  {'Overlap':>7}  {'Union':>6}  Tests")
    print("-" * 70)
    for jaccard, inter, union, a, b in results:
        print(f"{jaccard:>7.3f}  {inter:>5}/{union:<5}  {a}")
        print(f"{'':8}  {'':7}  {'':6}  {b}")
        print()


if __name__ == "__main__":
    main()
