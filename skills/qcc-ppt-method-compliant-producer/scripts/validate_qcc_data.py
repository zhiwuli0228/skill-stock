#!/usr/bin/env python3
"""Validate a QCC data file against the ten-step requirements.

The report tells the user exactly which fields are still missing before the deck
can be generated, and also runs the derived checks (Pareto totals, target
formula, effect direction, chi-square p-value).

Exit codes: 0 = ready, 1 = missing/invalid items, 2 = unusable file.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from qcc_statistics import evaluate_dataset


def load(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    if path.suffix.lower() in {".yaml", ".yml"}:
        import yaml

        data = yaml.safe_load(text)
    else:
        data = json.loads(text)
    if not isinstance(data, dict):
        raise ValueError("dataset must be a mapping")
    return data


def is_filled(value) -> bool:
    if value is None:
        return False
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, (list, tuple, dict)):
        return len(value) > 0
    return True


def check(step: str, label: str, ok: bool, issues: list[str]) -> None:
    if not ok:
        issues.append(f"[{step}] {label}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate a QCC data file.")
    parser.add_argument("--data", type=Path, required=True)
    parser.add_argument("--report", type=Path, default=None)
    args = parser.parse_args()

    if not args.data.exists():
        print(f"data file not found: {args.data}", file=sys.stderr)
        return 2
    try:
        data = load(args.data)
    except Exception as error:  # noqa: BLE001
        print(f"cannot read dataset: {error}", file=sys.stderr)
        return 2

    issues: list[str] = []
    notes: list[str] = []

    # 1 theme
    theme = data.get("theme") or {}
    check("1 主题选定", "候选主题 ≥2", len(theme.get("candidates") or []) >= 2, issues)
    check("1 主题选定", "评价维度 ≥3", len(theme.get("criteria") or []) >= 3, issues)
    check("1 主题选定", "评分矩阵", is_filled(theme.get("scores")), issues)
    check("1 主题选定", "评价规则", is_filled(theme.get("decision_rule")), issues)
    check("1 主题选定", "选定主题", is_filled(theme.get("selected")), issues)

    # 2 plan
    plan = data.get("plan") or {}
    check("2 活动计划", "阶段 ≥4", len(plan.get("phases") or []) >= 4, issues)
    check("2 活动计划", "负责人", is_filled(plan.get("owners")), issues)
    progress = plan.get("progress") or {}
    check("2 活动计划", "计划 vs 实际（planned/actual）", is_filled(progress.get("planned")) and is_filled(progress.get("actual")), issues)

    # 3 current state
    current = data.get("current_state") or {}
    sheet = current.get("check_sheet") or {}
    check("3 现状把握", "数据类型", is_filled(current.get("data_type")), issues)
    check("3 现状把握", "选用手法", is_filled(current.get("tools")), issues)
    check("3 现状把握", "查检表判定标准", is_filled(sheet.get("criteria")), issues)
    check("3 现状把握", "收集期间", is_filled(sheet.get("period")), issues)
    check("3 现状把握", "样本量", is_filled(sheet.get("sample")), issues)
    check("3 现状把握", "收集方法", is_filled(sheet.get("method")), issues)
    check("3 现状把握", "责任人", is_filled(sheet.get("owner")), issues)
    categories = current.get("categories") or []
    check("3 现状把握", "问题类别 ≥3", len(categories) >= 3, issues)
    counts = [row.get("count") for row in categories if isinstance(row, dict)]
    numeric_counts = [float(value) for value in counts if isinstance(value, (int, float))]
    descending = all(numeric_counts[i] >= numeric_counts[i + 1] for i in range(len(numeric_counts) - 1))
    check("3 现状把握", "类别频次降序", descending, issues)
    if sheet.get("sample") and numeric_counts:
        sample_value = float(sheet["sample"])
        defects_total = sum(numeric_counts)
        check(
            "3 现状把握",
            "缺陷类别合计不超过检查总数",
            defects_total <= sample_value + 1.0,
            issues,
        )
        if defects_total < sample_value - 1.0:
            notes.append(
                f"3 现状把握：缺陷类别合计 {defects_total:g} / 检查总数 {sample_value:g}"
                f"（现况值 {100.0 * defects_total / sample_value:.1f}%）"
            )
    focus = current.get("pareto_focus") or {}
    check("3 现状把握", "80% 改善重点覆盖 ≥80%", float(focus.get("cumulative") or 0) >= 80.0, issues)
    check("3 现状把握", "层别数据", is_filled(current.get("strata")), issues)

    # 4 target
    target = data.get("target") or {}
    for field, label in (
        ("current", "现况值"), ("focus", "改善重点"), ("capability", "圈能力"),
        ("value", "目标值"), ("formula", "计算公式"),
    ):
        check("4 目标设定", label, is_filled(target.get(field)), issues)
    try:
        current_v = float(target["current"]); focus_v = float(target["focus"])
        cap_v = float(target["capability"]); value_v = float(target["value"])
        computed = current_v - current_v * focus_v / 100.0 * cap_v / 100.0
        check("4 目标设定", "目标值可由公式复算", abs(computed - value_v) <= 0.5, issues)
    except (KeyError, TypeError, ValueError):
        pass

    # 5 analysis
    analysis = data.get("analysis") or {}
    fishbone = analysis.get("fishbone") or {}
    dims = fishbone.get("dimensions") or {}
    check("5 解析", "鱼骨图维度 ≥4", len(dims) >= 4, issues)
    check("5 解析", "候选要因评分", is_filled(analysis.get("cause_scores")), issues)
    verification = analysis.get("verification") or []
    check("5 解析", "真因验证记录", len(verification) >= 1, issues)
    for row in verification:
        if not isinstance(row, dict):
            continue
        for field, label in (("source", "数据来源"), ("result", "验证结果"), ("conclusion", "结论")):
            check("5 解析", f"真因验证 {label}", is_filled(row.get(field)), issues)
    verified = {
        row.get("cause")
        for row in verification
        if isinstance(row, dict) and "成立" in str(row.get("conclusion", "")) and "不成立" not in str(row.get("conclusion", ""))
    }

    # 6 countermeasures
    measures = data.get("countermeasures") or []
    adopted = [row for row in measures if isinstance(row, dict) and row.get("adopted")]
    check("6 对策拟定", "对策 ≥3", len(measures) >= 3, issues)
    for row in adopted:
        check("6 对策拟定", f"对策「{row.get('measure', '?')}」真因映射", row.get("cause") in verified, issues)
        for field, label in (("who", "Who"), ("where", "Where"), ("when", "When"), ("how", "How")):
            check("6 对策拟定", f"对策「{row.get('measure', '?')}」{label}", is_filled(row.get(field)), issues)

    # 7 implementation
    implementation = data.get("implementation") or []
    check("7 对策实施", "实施记录", len(implementation) >= 1, issues)
    for row in implementation:
        if isinstance(row, dict):
            for field, label in (("stage", "阶段"), ("time", "时间"), ("owner", "责任人"), ("data", "跟踪数据"), ("difficulty", "困难与调整")):
                check("7 对策实施", f"实施记录 {label}", is_filled(row.get(field)), issues)

    # 8 effect
    effect = data.get("effect") or {}
    before = effect.get("before") or {}
    after = effect.get("after") or {}
    check("8 效果确认", "改善前数据", is_filled(before), issues)
    check("8 效果确认", "改善后数据", is_filled(after), issues)
    statistics = effect.get("statistics") or {}
    has_test = is_filled(statistics.get("test")) and statistics.get("test") not in {"不做检验", "none"}
    has_waiver = is_filled(statistics.get("waiver_reason"))
    check("8 效果确认", "统计检验或豁免理由", has_test or has_waiver, issues)
    intangible = effect.get("intangible") or {}
    check("8 效果确认", "无形成果量表", is_filled(intangible.get("scale")), issues)
    check("8 效果确认", "无形成果维度", is_filled(intangible.get("dimensions")), issues)
    check(
        "8 效果确认",
        "无形成果前后均值",
        is_filled(intangible.get("before_mean")) and is_filled(intangible.get("after_mean")),
        issues,
    )
    benefit = effect.get("benefit") or {}
    check("8 效果确认", "效益核算（投入/收益/回收期）", all(is_filled(benefit.get(k)) for k in ("input_hours", "input_cost", "annual_saving", "payback")), issues)
    try:
        result = evaluate_dataset({"metric": "effect", "direction": "lower", "before": before, "after": after})
        notes.append(f"8 效果确认：复算 p = {result['p']:.6g}（{result['conclusion']}）")
        if not result.get("improved"):
            issues.append("[8 效果确认] 改善后未优于改善前")
    except Exception:  # noqa: BLE001
        notes.append("8 效果确认：数据不足以复算统计量（需 defects/total 或 n/mean/sd）")

    # 9 standardization
    standard = data.get("standardization") or {}
    documents = standard.get("documents") or []
    check("9 标准化", "标准化文件", len(documents) >= 1, issues)
    for doc in documents:
        if isinstance(doc, dict):
            for field, label in (("number", "编号"), ("version", "版本"), ("effective", "生效日期"), ("owner", "责任人"), ("audit_frequency", "稽核频率"), ("audit_method", "稽核方式"), ("training", "教育训练")):
                check("9 标准化", f"标准化文件 {label}", is_filled(doc.get(field)), issues)

    # 10 review
    review = data.get("review") or {}
    for field, label in (("strengths", "优点"), ("weaknesses", "不足"), ("residual", "残余问题"), ("next_topic", "下期主题")):
        check("10 检讨与改进", label, is_filled(review.get(field)), issues)

    lines = ["# QCC 数据完整性检查报告", "", f"- 数据文件：`{args.data}`"]
    lines += ["", "## 结果", ""]
    if issues:
        lines.append(f"**未就绪：{len(issues)} 项待补**")
        lines.append("")
        for item in issues:
            lines.append(f"- {item}")
    else:
        lines.append("**就绪：可以用于生成 PPT。**")
    lines += ["", "## 派生校验", ""]
    for note in notes:
        lines.append(f"- {note}")
    lines.append("")
    report_text = "\n".join(lines)

    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(report_text, encoding="utf-8")
    print(report_text)
    return 1 if issues else 0


if __name__ == "__main__":
    raise SystemExit(main())
