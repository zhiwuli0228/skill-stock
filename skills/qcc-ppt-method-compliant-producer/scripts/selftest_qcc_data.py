#!/usr/bin/env python3
"""Self-test for the data-intake tooling (init / validate / statistics)."""
from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path


def run(script: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(script), *args],
        capture_output=True,
        text=True,
        encoding="utf-8",
    )


def main() -> int:
    scripts = Path(__file__).resolve().parent
    init = scripts / "init_qcc_data.py"
    validate = scripts / "validate_qcc_data.py"
    statistics = scripts / "verify_qcc_statistics.py"
    failures: list[str] = []

    with tempfile.TemporaryDirectory(prefix="qcc-data-") as tmp:
        workspace = Path(tmp)
        blank = workspace / "blank.yaml"
        sample = workspace / "sample.yaml"

        if run(init, "--out", str(blank)).returncode != 0:
            failures.append("init: blank template failed")
        if run(init, "--out", str(sample), "--sample").returncode != 0:
            failures.append("init: sample failed")

        blank_result = run(validate, "--data", str(blank))
        if blank_result.returncode == 0:
            failures.append("validate: blank template unexpectedly ready")

        sample_result = run(validate, "--data", str(sample))
        if sample_result.returncode != 0:
            failures.append("validate: sample data not ready")
            print(sample_result.stdout)

        stats_result = run(statistics, "--data", str(sample))
        if stats_result.returncode != 0:
            failures.append("statistics: sample recomputation failed")
        elif "p=" not in stats_result.stdout:
            failures.append("statistics: no p-value printed")

    if failures:
        print("SELFTEST FAILED:")
        for item in failures:
            print(f"- {item}")
        return 1
    print(
        "SELFTEST PASSED: blank template reports gaps, sample data is ready, "
        "statistics recompute."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
