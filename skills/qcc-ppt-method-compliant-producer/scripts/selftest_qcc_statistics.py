#!/usr/bin/env python3
"""Self-test for the statistics recomputation library and CLI."""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

from qcc_statistics import evaluate_dataset


def main() -> int:
    failures: list[str] = []

    significant = evaluate_dataset(
        {
            "metric": "异常率",
            "direction": "lower",
            "before": {"defects": 126, "total": 300},
            "after": {"defects": 41, "total": 300},
        }
    )
    if not significant["significant_05"]:
        failures.append("chi-square: expected p < 0.05")
    if significant["test"] != "chi-square":
        failures.append("chi-square: wrong test selected")

    not_significant = evaluate_dataset(
        {
            "metric": "异常率",
            "direction": "lower",
            "before": {"defects": 126, "total": 300},
            "after": {"defects": 118, "total": 300},
        }
    )
    if not_significant["significant_05"]:
        failures.append("chi-square: expected p >= 0.05 for the null-like dataset")

    t_result = evaluate_dataset(
        {
            "metric": "处理时长",
            "direction": "lower",
            "before": {"n": 30, "mean": 12.4, "sd": 2.1},
            "after": {"n": 30, "mean": 9.8, "sd": 1.9},
        }
    )
    if t_result["test"] != "welch-t" or not 0.0 <= t_result["p"] <= 1.0:
        failures.append("welch-t: invalid result")

    with tempfile.TemporaryDirectory(prefix="qcc-stats-") as tmp:
        workspace = Path(tmp)
        mismatched = workspace / "mismatch.json"
        mismatched.write_text(
            json.dumps(
                {
                    "metric": "异常率",
                    "direction": "lower",
                    "before": {"defects": 126, "total": 300},
                    "after": {"defects": 118, "total": 300},
                    "claimed": {"test": "chi-square", "comparison": "<", "p": 0.05},
                }
            ),
            encoding="utf-8",
        )
        cli = Path(__file__).with_name("verify_qcc_statistics.py")
        completed = subprocess.run(
            [sys.executable, str(cli), "--data", str(mismatched)],
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        if completed.returncode == 0:
            failures.append("CLI: a mismatched claimed p-value was accepted")

    if failures:
        print("SELFTEST FAILED:")
        for item in failures:
            print(f"- {item}")
        return 1
    print("SELFTEST PASSED: statistics recomputation works (chi-square, welch-t, claimed-p guard).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
