#!/usr/bin/env python3
"""Self-test: keyword-only decks must fail, data-complete decks must pass."""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


def run_checker(script: Path, pptx: Path, report: Path | None) -> int:
    command = [sys.executable, str(script), str(pptx)]
    if report is not None:
        command += ["--report", str(report)]
    result = subprocess.run(command, capture_output=True, text=True, encoding="utf-8")
    sys.stdout.write(result.stdout)
    if result.stderr:
        sys.stderr.write(result.stderr)
    return result.returncode


def main() -> int:
    parser = argparse.ArgumentParser(description="QCC method compliance self-test.")
    parser.add_argument("--fixtures", type=Path, default=Path("examples/fixtures"))
    parser.add_argument("--reports", type=Path, default=None)
    args = parser.parse_args()

    skill_dir = Path(__file__).resolve().parent.parent
    generator = skill_dir / "scripts" / "make_qcc_method_fixtures.py"
    checker = skill_dir / "scripts" / "check_qcc_method_compliance.py"
    reports = args.reports if args.reports is not None else args.fixtures / "reports"
    reports.mkdir(parents=True, exist_ok=True)

    subprocess.run(
        [sys.executable, str(generator), "--outdir", str(args.fixtures)],
        check=True,
    )

    negative = run_checker(
        checker,
        args.fixtures / "keyword-only.qcc.pptx",
        reports / "keyword-only.report.md",
    )
    theater = run_checker(
        checker,
        args.fixtures / "method-theater.qcc.pptx",
        reports / "method-theater.report.md",
    )
    positive = run_checker(
        checker,
        args.fixtures / "data-complete.qcc.pptx",
        reports / "data-complete.report.md",
    )

    failures: list[str] = []
    if negative == 0:
        failures.append("keyword-only fixture unexpectedly PASSED")
    if theater == 0:
        failures.append("method-theater fixture unexpectedly PASSED")
    if positive != 0:
        failures.append("data-complete fixture unexpectedly FAILED")

    if failures:
        print("SELFTEST FAILED:")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print(
        "SELFTEST PASSED: keyword-only and method-theater are NON-COMPLIANT, "
        "data-complete is PASS."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
