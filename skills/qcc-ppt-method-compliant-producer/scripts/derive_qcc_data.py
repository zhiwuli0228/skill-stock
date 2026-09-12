#!/usr/bin/env python3
"""Derive the full QCC data file from the minimal one.

Input : qcc-min-data.yaml  (only raw facts, produced by qcc_wizard.py)
Output: qcc-data.yaml     (full ten-step schema used by validate/build/check)
        derived-report.md  (what was computed, what still needs input)

Derived values: shares, cumulative %, Pareto focus, target value, attainment,
progress rate, chi-square p-value, plan/analysis/countermeasure structures.
"""
from __future__ import annotations

import argparse
from pathlib import Path

import yaml

from qcc_statistics import evaluate_dataset


def load(path: Path) -> dict:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise SystemExit("minimal data file must be a mapping")
    return data


def derive(minimal: dict) -> tuple[dict, list[str], list[str]]:
    notes: list[str] = []
    missing: list[str] = []

    meta = minimal.get("meta") or {}
    current = minimal.get("current") or {}
    after = minimal.get("after") or {}
    target_in = minimal.get("target") or {}
    theme_in = minimal.get("theme") or {}
    plan_in = minimal.get("plan") or {}

    sample = current.get("sample")
    categories_in = current.get("categories") or []
    categories = sorted(
        ({"name": str(row.get("name", "")), "count": float(row.get("count", 0))} for row in categories_in),
        key=lambda row: row["count"],
        reverse=True,
    )
    if [row.get("count") for row in categories_in] != [row["count"] for row in categories]:
        notes.append("问题类别已按频次降序重排（柏拉图要求降序）")

    total_count = sum(row["count"] for row in categories)
    if sample is None:
        sample = int(total_count)
        notes.append(f"样本量未提供，取缺陷类别合计 {sample}")
    defects_total = total_count if total_count > 0 else float(sample or 0)
    if abs(total_count - float(sample)) > 1.0:
        notes.append(
            f"缺陷类别合计 {total_count:g}，检查总数 {sample:g}："
            "柏拉图占比按缺陷合计计算，现况值 = 缺陷合计 ÷ 检查总数"
        )
    else:
        notes.append(
            f"缺陷类别合计 {total_count:g} = 检查总数 {sample:g}（每个检查单位各计一次缺陷）"
        )

    cumulative = 0.0
    cumulative_rows = []
    for row in categories:
        share = 100.0 * row["count"] / defects_total if defects_total else 0.0
        cumulative += share
        cumulative_rows.append({**row, "share": round(share, 1), "cumulative": round(min(cumulative, 100.0), 1)})
    focus_count = next(
        (index + 1 for index, row in enumerate(cumulative_rows) if row["cumulative"] >= 80.0),
        len(cumulative_rows),
    )
    focus_cumulative = cumulative_rows[focus_count - 1]["cumulative"] if cumulative_rows else 0.0
    notes.append(f"柏拉图改善重点 = 前 {focus_count} 类，累计 {focus_cumulative}%")

    before_defects = current.get("before_defects")
    if before_defects is None:
        before_defects = defects_total
        notes.append(
            f"改善前异常例数取缺陷类别合计 {before_defects:g}"
            "（查检表另有口径时，可用 current.before_defects 覆盖）"
        )
    before_rate = 100.0 * float(before_defects) / float(sample) if sample else 0.0

    capability = float(target_in.get("capability", 80))
    target_value = before_rate - before_rate * focus_cumulative / 100.0 * capability / 100.0
    notes.append(f"目标值 = {before_rate:.1f}% − {before_rate:.1f}%×{focus_cumulative}%×{capability:g}% = {target_value:.1f}%")

    after_total = float(after.get("total") or sample)
    after_defects = float(after.get("defects", 0))
    after_rate = 100.0 * after_defects / after_total if after_total else 0.0
    attainment = (
        (before_rate - after_rate) / (before_rate - target_value) * 100.0
        if abs(before_rate - target_value) > 1e-9 else 0.0
    )
    progress = (before_rate - after_rate) / before_rate * 100.0 if before_rate else 0.0
    notes.append(f"改善后 {after_rate:.1f}%：目标达成率 {attainment:.1f}%，进步率 {progress:.1f}%")

    stats_input = {
        "metric": str(minimal.get("metric", "指标")),
        "direction": str(meta.get("direction", "lower")),
        "before": {"defects": float(before_defects), "total": float(sample)},
        "after": {"defects": after_defects, "total": after_total},
    }
    result = evaluate_dataset(stats_input)
    claimed = minimal.get("statistics") or {}
    statistics = {
        "test": str(claimed.get("test") or result["test"]),
        "p": claimed.get("p", round(float(result["p"]), 6)),
        "comparison": str(claimed.get("comparison", "<")),
    }
    notes.append(
        f"统计复算：{result['test']}，p = {float(result['p']):.4g}（{result['conclusion']}）"
    )

    causes = minimal.get("causes") or []
    dimensions: dict[str, list[str]] = {}
    cause_scores = []
    verification = []
    for row in causes:
        name = str(row.get("name", ""))
        dimension = str(row.get("dimension", "法"))
        score = row.get("score")
        result_text = str(row.get("result", ""))
        conclusion = str(row.get("conclusion") or "").strip()
        if not conclusion:
            if any(word in result_text for word in ("不成立", "无显著", "未发现", "排除", "无关")):
                conclusion = "不成立"
            else:
                conclusion = "成立" if result_text else "待确认"
        dimensions.setdefault(dimension, []).append(name)
        if score is not None:
            cause_scores.append({"cause": name, "score": float(score), "selected": float(score) >= 12})
        verification.append(
            {
                "cause": name,
                "source": str(row.get("source", "查检表")),
                "method": str(row.get("method", "分类统计")),
                "result": result_text,
                "conclusion": conclusion,
            }
        )
    if not causes:
        missing.append("analysis.verification（已验证真因）")

    measures = []
    owners: list[str] = []
    for row in minimal.get("measures") or []:
        scores = row.get("scores") or {}
        total = sum(float(value) for value in scores.values()) if scores else 0.0
        owner = str(row.get("who", ""))
        if owner:
            owners.append(owner)
        measures.append(
            {
                "measure": str(row.get("name", "")),
                "cause": str(row.get("cause", "")),
                "scores": scores,
                "total": total,
                "adopted": total >= 15,
                "who": owner,
                "where": str(row.get("where", "")),
                "when": str(row.get("when", "")),
                "how": str(row.get("how", "")),
            }
        )
    if not measures:
        missing.append("countermeasures（对策）")

    review = minimal.get("review") or {}
    weakness = (review.get("weaknesses") or [""])[0]
    implementation = [
        {
            "stage": "D 实施",
            "time": row["when"],
            "owner": row["who"],
            "progress": f"已实施：{row['measure']}",
            "data": f"异常率 {before_rate:.1f}% → {after_rate:.1f}%",
            "difficulty": weakness or "无重大困难",
        }
        for row in measures
        if row["adopted"]
    ]

    planned = plan_in.get("planned_weeks")
    actual = plan_in.get("actual_weeks")
    if planned is None:
        planned = 8
        notes.append("计划周数未提供，默认 8 周")
    if actual is None:
        actual = planned
        notes.append("实际周数未提供，默认与计划一致（请核对）")

    full = {
        "meta": {
            "topic": str(meta.get("topic", "")),
            "team": str(meta.get("team", "")),
            "lead": str(meta.get("lead", "")),
            "period": str(meta.get("period", "")),
            "direction": str(meta.get("direction", "lower")),
        },
        "theme": {
            "candidates": theme_in.get("candidates") or [],
            "criteria": theme_in.get("criteria") or [],
            "scores": theme_in.get("scores") or [],
            "decision_rule": str(theme_in.get("decision_rule", "5 分制，圈员独立打分取平均，权重相同")),
            "selected": str(meta.get("topic", "")),
        },
        "plan": {
            "phases": ["P 计划", "D 实施", "C 检查", "A 处理"],
            "weeks": planned,
            "owners": [str(meta.get("lead", ""))] + owners,
            "progress": {"planned": planned, "actual": actual, "note": str(plan_in.get("note", ""))},
        },
        "current_state": {
            "data_type": str((minimal.get("quality") or {}).get("data_type", "计数值")),
            "tools": (minimal.get("quality") or {}).get("tools") or ["查检表", "柏拉图", "层别"],
            "check_sheet": {
                "criteria": str((current.get("check_sheet") or {}).get("criteria", "按判定标准逐例记录异常")),
                "period": str(current.get("period", "")),
                "sample": sample,
                "method": str((current.get("check_sheet") or {}).get("method", "查检表逐例记录")),
                "owner": str((current.get("check_sheet") or {}).get("owner", meta.get("lead", ""))),
            },
            "categories": [{"name": row["name"], "count": row["count"]} for row in cumulative_rows],
            "strata": [
                {"name": str(row.get("name", "")), "value": float(row.get("value", 0))}
                for row in current.get("strata") or []
            ],
            "pareto_focus": {"count": focus_count, "cumulative": focus_cumulative},
        },
        "target": {
            "current": round(before_rate, 1),
            "focus": focus_cumulative,
            "capability": capability,
            "formula": "目标值 = 现况值 - (现况值 × 改善重点 × 圈能力)",
            "value": round(target_value, 1),
        },
        "analysis": {
            "fishbone": {"problem": str(meta.get("topic", "")), "dimensions": dimensions},
            "cause_scores": cause_scores,
            "verification": verification,
        },
        "countermeasures": measures,
        "implementation": implementation,
        "effect": {
            "before": {"period": str(current.get("period", "")), "defects": before_defects, "total": sample},
            "after": {"period": str(after.get("period", "")), "defects": after_defects, "total": after_total},
            "target": round(target_value, 1),
            "statistics": statistics,
            "intangible": minimal.get("intangible") or {},
            "benefit": minimal.get("benefit") or {},
        },
        "standardization": {"documents": minimal.get("standardization") or []},
        "review": {
            "strengths": review.get("strengths") or [],
            "weaknesses": review.get("weaknesses") or [],
            "residual": review.get("residual") or [],
            "next_topic": str(review.get("next_topic", "")),
        },
    }
    return full, notes, missing


def main() -> int:
    parser = argparse.ArgumentParser(description="Derive the full QCC data file.")
    parser.add_argument("--min", dest="minimal", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--report", type=Path, default=None)
    args = parser.parse_args()

    if not args.minimal.exists():
        print(f"minimal data file not found: {args.minimal}")
        return 2
    full, notes, missing = derive(load(args.minimal))
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(
        yaml.safe_dump(full, allow_unicode=True, sort_keys=False), encoding="utf-8"
    )

    lines = ["# QCC 数据推导报告", "", f"- 最小数据：`{args.minimal}`", f"- 完整数据：`{args.out}`", "", "## 自动推导", ""]
    lines += [f"- {note}" for note in notes]
    lines += ["", "## 仍需人工确认", ""]
    lines += [f"- {item}" for item in missing] if missing else ["- 无"]
    report = "\n".join(lines) + "\n"
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(report, encoding="utf-8")
    print(report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
