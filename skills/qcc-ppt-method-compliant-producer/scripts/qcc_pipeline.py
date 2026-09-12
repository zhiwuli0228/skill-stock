#!/usr/bin/env python3
"""Run the whole QCC data intake in one command.

Stages, in order:

1. ``qcc_scan_inputs.py`` — scan the user's raw-data folder into evidence
   (skipped when ``--min`` is given, unless ``--dir`` is also given);
2. ``qcc_wizard.py`` — only with ``--defaults``, to build the sample facts;
3. ``derive_qcc_data.py`` — compute shares, Pareto focus, target, attainment,
   progress rate and the chi-square p-value from the raw facts;
4. ``validate_qcc_data.py`` — ten-step completeness + derived consistency;
5. ``verify_qcc_statistics.py`` — recompute the effect statistics from raw data;
6. ``check_qcc_method_compliance.py`` — only with ``--deck``.

    python scripts/qcc_pipeline.py --dir C:/path/to/raw --workspace qcc-workspace
    python scripts/qcc_pipeline.py --min qcc-workspace/input/qcc-min-data.yaml
    python scripts/qcc_pipeline.py --defaults --workspace qcc-workspace
    python scripts/qcc_pipeline.py --min data.yaml --deck output/deck.pptx

Exit codes: 0 = every stage passed, 1 = the data is still incomplete or a stage
failed (see the summary), 2 = setup problem (bad arguments / missing files).
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


def run(script: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(script), *args],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )


def tail(text: str, lines: int = 3) -> str:
    rows = [row for row in (text or "").strip().splitlines() if row.strip()]
    return " / ".join(rows[-lines:]) if rows else ""


def main() -> int:
    parser = argparse.ArgumentParser(description="QCC data intake pipeline.")
    parser.add_argument("--dir", dest="root", type=Path, default=None, help="使用者原始数据文件夹")
    parser.add_argument("--min", dest="minimal", type=Path, default=None, help="最小数据文件（原始事实）")
    parser.add_argument("--defaults", action="store_true", help="用示例数据跑通全流程（自检/演示）")
    parser.add_argument("--workspace", type=Path, default=Path("qcc-workspace"))
    parser.add_argument("--deck", type=Path, default=None, help="出片后附带做合规校验")
    parser.add_argument("--skip-scan", action="store_true")
    args = parser.parse_args()

    scripts = Path(__file__).resolve().parent
    workspace = args.workspace
    input_dir = workspace / "input"
    report_dir = workspace / "reports"
    for path in (input_dir, report_dir):
        path.mkdir(parents=True, exist_ok=True)

    steps: list[tuple[str, str, str]] = []  # (stage, status, detail)

    minimal = args.minimal
    if args.root is not None and not args.skip_scan:
        result = run(scripts / "qcc_scan_inputs.py", "--dir", str(args.root), "--workspace", str(workspace))
        draft = input_dir / "qcc-min-data.draft.yaml"
        steps.append(
            (
                "扫描数据目录",
                "PASS" if result.returncode == 0 else "FAIL",
                f"证据索引 {report_dir / 'data-scan-evidence.json'}｜{tail(result.stdout, 1)}",
            )
        )
        if minimal is None and draft.exists():
            minimal = draft

    if args.defaults:
        sample = input_dir / "qcc-min-data.yaml"
        if sample.exists():
            sample.unlink()
        result = run(scripts / "qcc_wizard.py", "--defaults", "--out", str(sample))
        steps.append(("生成示例最小数据", "PASS" if result.returncode == 0 else "FAIL", tail(result.stdout, 1)))
        minimal = sample if result.returncode == 0 else minimal

    if minimal is None:
        print(
            "需要数据来源：--dir <原始数据文件夹> / --min <最小数据.yaml> / --defaults",
            file=sys.stderr,
        )
        return 2
    if not minimal.exists():
        print(f"最小数据文件不存在：{minimal}", file=sys.stderr)
        return 2

    full = input_dir / "qcc-data.yaml"
    derive = run(
        scripts / "derive_qcc_data.py",
        "--min", str(minimal),
        "--out", str(full),
        "--report", str(report_dir / "data-derive-report.md"),
    )
    steps.append(("推导完整数据", "PASS" if derive.returncode == 0 else "FAIL", tail(derive.stdout, 2)))
    if derive.returncode != 0:
        print(derive.stdout)
        print(derive.stderr, file=sys.stderr)
        return 1

    validate = run(
        scripts / "validate_qcc_data.py",
        "--data", str(full),
        "--report", str(report_dir / "data-readiness.md"),
    )
    readiness = "就绪" if validate.returncode == 0 else "未就绪"
    steps.append(("数据完整性校验", "PASS" if validate.returncode == 0 else "GAP", f"{readiness}｜{tail(validate.stdout, 1)}"))

    statistics = run(
        scripts / "verify_qcc_statistics.py",
        "--data", str(full),
        "--report", str(report_dir / "qcc-statistics-report.md"),
    )
    steps.append(
        (
            "统计复算",
            "PASS" if statistics.returncode == 0 else "FAIL",
            tail(statistics.stdout, 2),
        )
    )

    compliance_code = None
    if args.deck is not None:
        compliance = run(
            scripts / "check_qcc_method_compliance.py",
            str(args.deck),
            "--data", str(full),
            "--report", str(report_dir / "qcc-method-compliance-report.md"),
        )
        compliance_code = compliance.returncode
        steps.append(
            (
                "方法合规校验",
                "PASS" if compliance.returncode == 0 else "FAIL",
                tail(compliance.stdout, 2),
            )
        )

    lines = [
        "# QCC 数据流水线汇总",
        "",
        f"- 工作目录：`{workspace}`",
        f"- 最小数据：`{minimal}`",
        f"- 完整数据：`{full}`",
        f"- 合规用 pptx：`{args.deck}`" if args.deck else "- 合规用 pptx：（未提供）",
        "",
        "| 阶段 | 状态 | 说明 |",
        "|---|---|---|",
    ]
    for stage, status, detail in steps:
        lines.append(f"| {stage} | {status} | {detail.replace('|', '/')} |")
    if any(status == "GAP" for _, status, _ in steps):
        lines += [
            "",
            "> 数据未就绪：按 `reports/data-readiness.md` 的清单补齐 `qcc-min-data.yaml` 后重跑。",
        ]
    lines.append("")
    summary = "\n".join(lines)
    (report_dir / "pipeline-summary.md").write_text(summary, encoding="utf-8")
    print(summary)

    failed = [
        status
        for _, status, _ in steps
        if status in {"FAIL", "GAP"} or (compliance_code is not None and status == "FAIL")
    ]
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
