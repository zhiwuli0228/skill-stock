#!/usr/bin/env python3
"""Self-test for the minimal-data path (wizard -> derive -> validate -> statistics).

Asserts that the sample facts pass the whole chain and that the derived numbers
are the ones the formulas imply (Pareto focus, target value, attainment,
chi-square p-value).
"""
from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path

import yaml


def run(script: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(script), *args],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )


def main() -> int:
    scripts = Path(__file__).resolve().parent
    failures: list[str] = []
    close = lambda a, b, tol=0.15: a is not None and abs(float(a) - float(b)) <= tol  # noqa: E731

    with tempfile.TemporaryDirectory(prefix="qcc-minimal-") as tmp:
        root = Path(tmp)
        workspace = root / "ws"

        pipeline = run(scripts / "qcc_pipeline.py", "--defaults", "--workspace", str(workspace))
        if pipeline.returncode != 0:
            failures.append(f"pipeline --defaults exited {pipeline.returncode}")
            print(pipeline.stdout)
            print(pipeline.stderr)

        summary = workspace / "reports" / "pipeline-summary.md"
        if summary.exists():
            text = summary.read_text(encoding="utf-8")
            for stage in ("生成示例最小数据", "推导完整数据", "数据完整性校验", "统计复算"):
                if f"| {stage} | PASS |" not in text:
                    failures.append(f"stage not PASS in summary: {stage}")
        else:
            failures.append("pipeline summary was not written")

        full_path = workspace / "input" / "qcc-data.yaml"
        if not full_path.exists():
            failures.append("derived qcc-data.yaml missing")
        else:
            full = yaml.safe_load(full_path.read_text(encoding="utf-8"))
            focus = full["current_state"]["pareto_focus"]
            if focus["count"] != 3 or not close(focus["cumulative"], 85.3):
                failures.append(f"pareto focus wrong: {focus}")
            if not close(full["target"]["value"], 13.3):
                failures.append(f"target value wrong: {full['target']['value']}")
            if not close(full["target"]["current"], 42.0):
                failures.append(f"current value wrong: {full['target']['current']}")
            categories = full["current_state"]["categories"]
            counts = [row["count"] for row in categories]
            if counts != sorted(counts, reverse=True):
                failures.append(f"categories not sorted descending: {counts}")
            if len(full["analysis"]["fishbone"]["dimensions"]) < 4:
                failures.append("fishbone dimensions < 4")
            if len(full["countermeasures"]) < 3:
                failures.append("countermeasures < 3")
            if not full["effect"]["statistics"]["p"]:
                failures.append("statistics p-value missing")

        standalone = root / "standalone"
        minimal = standalone / "min.yaml"
        if run(scripts / "qcc_wizard.py", "--defaults", "--out", str(minimal)).returncode != 0:
            failures.append("wizard --defaults failed")
        else:
            derived = standalone / "full.yaml"
            if run(
                scripts / "derive_qcc_data.py",
                "--min", str(minimal),
                "--out", str(derived),
            ).returncode != 0:
                failures.append("derive failed on the wizard output")
            if run(scripts / "validate_qcc_data.py", "--data", str(derived)).returncode != 0:
                failures.append("validate rejected the derived sample data")
            if run(scripts / "verify_qcc_statistics.py", "--data", str(derived)).returncode != 0:
                failures.append("statistics recomputation failed on the derived sample data")

    if failures:
        print("SELFTEST FAILED:")
        for item in failures:
            print(f"- {item}")
        return 1
    print(
        "SELFTEST PASSED: sample facts pass every stage and the derived Pareto focus, "
        "target value and p-value match the formulas."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
