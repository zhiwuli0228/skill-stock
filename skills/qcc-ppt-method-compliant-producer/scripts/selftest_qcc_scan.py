#!/usr/bin/env python3
"""Self-test for the folder-scan intake path.

Builds a messy raw-data folder, scans it, and asserts that

- the records that ARE in the folder are found (categories, strata, before/after
  defects, measure table, cause verification, theme matrix, cost-benefit sheet);
- the fields that are NOT in the folder stay missing (no invented values);
- a draft that is still incomplete does not silently pass the pipeline.
"""
from __future__ import annotations

import json
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


def names(items: list[dict]) -> list[str]:
    return [str(item.get("name")) for item in items]


def main() -> int:
    scripts = Path(__file__).resolve().parent
    failures: list[str] = []

    with tempfile.TemporaryDirectory(prefix="qcc-scan-") as tmp:
        root = Path(tmp)
        raw = root / "raw"
        workspace = root / "ws"

        build = run(scripts / "make_qcc_scan_fixture.py", "--outdir", str(raw))
        if build.returncode != 0:
            print(build.stderr)
            return 1

        scan = run(scripts / "qcc_scan_inputs.py", "--dir", str(raw), "--workspace", str(workspace))
        if scan.returncode != 0:
            failures.append(f"scan exited {scan.returncode}")
            print(scan.stdout)
            print(scan.stderr)

        evidence_path = workspace / "reports" / "data-scan-evidence.json"
        draft_path = workspace / "input" / "qcc-min-data.draft.yaml"
        if not evidence_path.exists() or not draft_path.exists():
            print("SELFTEST FAILED: scan did not write the evidence index / draft")
            return 1

        evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
        resolved = {target: item["value"] for target, item in evidence["resolved"].items()}

        def expect(target: str, predicate, hint: str) -> None:
            value = resolved.get(target)
            if not predicate(value):
                failures.append(f"{target} not detected as expected ({hint}); got {value!r}")

        expect(
            "current.categories",
            lambda value: value is not None and names(value)
            == ["校验异常", "记录缺失", "流程等待", "标注错误", "其他"],
            "类别表按原顺序读取，含合计行剔除",
        )
        expect(
            "current.strata",
            lambda value: value is not None and names(value) == ["A 班", "B 班", "C 班"],
            "层别表",
        )
        expect("current.before_defects", lambda value: value == 126, "改善前异常例数")
        expect("after.defects", lambda value: value == 41, "改善后异常例数")
        expect("after.total", lambda value: value == 300, "改善后样本量")
        expect("current.sample", lambda value: value == 300, "现状样本量")
        expect("target.capability", lambda value: value == 80, "圈能力")
        expect("theme.criteria", lambda value: value is not None and len(value) == 5, "主题评价维度")
        expect("theme.scores", lambda value: value is not None and len(value) == 3, "评分矩阵")
        expect("measures", lambda value: value is not None and len(value) == 3, "对策表")
        expect("causes", lambda value: value is not None and len(value) == 4, "真因验证表")
        expect("benefit.input_cost", lambda value: value == 0.4, "投入费用（万元）")
        expect("benefit.annual_saving", lambda value: value == 5.2, "年化节省费用（万元）")
        expect("meta.topic", lambda value: value == "降低处理异常率", "Word 里的课题")
        expect("meta.lead", lambda value: value == "张三", "Word 里的圈长")
        expect("meta.direction", lambda value: value == "lower", "指标方向")
        expect("review.next_topic", lambda value: value == "降低记录缺失率", "下期主题")

        for absent in ("standardization", "intangible.scale", "plan.planned_weeks"):
            if absent in resolved:
                failures.append(f"{absent} was filled without evidence: {resolved[absent]!r}")

        if not any(item["path"] == "standardization" for item in evidence["missing"]):
            failures.append("missing list does not flag standardization")

        draft = yaml.safe_load(draft_path.read_text(encoding="utf-8"))
        if draft["review"]["strengths"] != ["数据驱动定位改善重点"]:
            failures.append(f"draft review.strengths wrong: {draft['review']['strengths']!r}")
        if draft["benefit"]["payback"] != "1 个月内":
            failures.append(f"draft benefit.payback wrong: {draft['benefit']['payback']!r}")
        if draft["intangible"]["scale"] is not None:
            failures.append("draft invented the intangible scale")

        pipeline = run(
            scripts / "qcc_pipeline.py",
            "--min", str(draft_path),
            "--workspace", str(root / "ws-pipeline"),
        )
        if pipeline.returncode == 0:
            failures.append("pipeline accepted an incomplete draft")
        readiness = (root / "ws-pipeline" / "reports" / "data-readiness.md")
        if not readiness.exists() or "未就绪" not in readiness.read_text(encoding="utf-8"):
            failures.append("readiness report does not report the draft as incomplete")

    if failures:
        print("SELFTEST FAILED:")
        for item in failures:
            print(f"- {item}")
        return 1
    print(
        "SELFTEST PASSED: folder scan finds the records that exist, leaves the rest "
        "missing, and an incomplete draft does not pass the pipeline."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
