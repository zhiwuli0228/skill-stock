#!/usr/bin/env python3
"""Recompute the effect-confirmation statistics from raw QCC data.

Input: a YAML/JSON dataset, e.g.

    metric: 处理异常率
    direction: lower          # lower | higher
    before: {period: 2026-01-01..2026-01-31, defects: 126, total: 300}
    after:  {period: 2026-03-01..2026-03-31, defects: 41,  total: 300}
    claimed: {test: chi-square, p: 0.05}

or a continuous dataset:

    before: {period: ..., n: 30, mean: 12.4, sd: 2.1}
    after:  {period: ..., n: 30, mean: 9.8,  sd: 1.9}

Exit codes: 0 = computed (and claimed value consistent when provided),
            1 = claimed value inconsistent with the raw data,
            2 = invalid input.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from qcc_statistics import evaluate_dataset


def load_dataset(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    if path.suffix.lower() in {".yaml", ".yml"}:
        try:
            import yaml
        except ImportError as error:  # pragma: no cover
            raise SystemExit("PyYAML is required to read YAML datasets") from error
        data = yaml.safe_load(text)
    else:
        data = json.loads(text)
    if not isinstance(data, dict):
        raise SystemExit("dataset must be a mapping")
    return data


def claimed_consistency(result: dict, claimed: dict | None) -> tuple[bool, str]:
    if not claimed:
        return True, "no claimed value"
    claimed_p = claimed.get("p")
    if claimed_p is None:
        return True, "no claimed p-value"
    claimed_p = float(claimed_p)
    computed_p = float(result["p"])
    bound = str(claimed.get("comparison", ""))
    if bound in {"<", "<="} or claimed_p <= 0.05:
        ok = computed_p <= claimed_p + 1e-9
        return ok, f"claimed p {bound or '<='} {claimed_p} vs computed {computed_p:.4g}"
    ok = abs(computed_p - claimed_p) <= 0.01
    return ok, f"claimed p = {claimed_p} vs computed {computed_p:.4g}"


def build_report(data: dict, result: dict, consistency: tuple[bool, str]) -> str:
    lines = [
        "# QCC 统计数据复算报告",
        "",
        f"- 指标：{result.get('metric')}（方向：{result.get('direction')}）",
        f"- 检验方法：{result['test']}"
        + ("（Yates 校正）" if result.get("yates") else ""),
        f"- 统计量：{result['statistic']:.4f}，df = {result['df']:.2f}",
        f"- p 值：{result['p']:.6g}",
        f"- 结论：{result['conclusion']}",
    ]
    if "before_rate" in result:
        lines.append(
            f"- 改善前 {result['before_rate']:.2f}% → 改善后 {result['after_rate']:.2f}%"
        )
    else:
        lines.append(
            f"- 改善前均值 {result['before_mean']:.3f} → 改善后均值 {result['after_mean']:.3f}"
        )
    ok, detail = consistency
    lines += ["", f"- 文稿声明一致性：{'PASS' if ok else 'MISMATCH'}（{detail}）", ""]
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Recompute QCC effect statistics.")
    parser.add_argument("--data", type=Path, required=True)
    parser.add_argument("--report", type=Path, default=None)
    parser.add_argument("--json", dest="json_path", type=Path, default=None)
    args = parser.parse_args()

    if not args.data.exists():
        print(f"data file not found: {args.data}", file=sys.stderr)
        return 2
    try:
        data = load_dataset(args.data)
        result = evaluate_dataset(data)
    except (ValueError, KeyError, TypeError) as error:
        print(f"invalid dataset: {error}", file=sys.stderr)
        return 2

    consistency = claimed_consistency(result, data.get("claimed"))
    report = build_report(data, result, consistency)
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(report, encoding="utf-8")
    if args.json_path:
        args.json_path.parent.mkdir(parents=True, exist_ok=True)
        args.json_path.write_text(
            json.dumps({**result, "claimed_consistent": consistency[0], "claimed_detail": consistency[1]},
                       ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    print(f"test={result['test']} statistic={result['statistic']:.4f} df={result['df']:.2f} p={result['p']:.6g}")
    print(result["conclusion"])
    return 0 if consistency[0] else 1


if __name__ == "__main__":
    raise SystemExit(main())
