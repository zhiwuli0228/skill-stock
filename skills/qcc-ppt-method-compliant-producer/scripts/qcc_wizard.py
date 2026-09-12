#!/usr/bin/env python3
"""Interactive wizard for the minimal QCC data file.

Only raw facts are asked (about 20 questions). Everything that can be computed
(shares, cumulative %, Pareto focus, target value, attainment, progress, p-value)
is derived later by `derive_qcc_data.py`.

Prefer the folder-scan path (`qcc_scan_inputs.py`) when the user already has the
records in files; this wizard is for the case where the facts are only in
people's heads.

    python scripts/qcc_wizard.py --out qcc-workspace/input/qcc-min-data.yaml
    python scripts/qcc_wizard.py --out demo.yaml --defaults     # fill with the sample
    python scripts/qcc_wizard.py --out data.yaml --answers answers.yaml  # non-interactive
"""
from __future__ import annotations

import argparse
from pathlib import Path

import yaml


DEFAULTS = {
    "topic": "降低处理异常率",
    "team": "精益圈",
    "lead": "张三",
    "period": "2026-01-01..2026-03-31",
    "metric": "处理异常率",
    "direction": "lower",
    "current_period": "2026-01-01..2026-01-31",
    "sample": "300",
    "categories": "校验异常:126, 记录缺失:70, 流程等待:60, 标注错误:30, 其他:14",
    "strata": "A 班:46, B 班:38, C 班:41",
    "criteria": "上级政策, 重要性, 迫切性, 可行性, 圈能力",
    "candidates": "降低处理异常率, 缩短处理时长, 减少返工次数",
    "scores": "5,5,4,5,4; 4,4,3,4,4; 3,4,3,3,3",
    "plan_progress": "8@8@第 5 周延期 2 天，已调整顺序",
    "capability": "80",
    "after_period": "2026-03-01..2026-03-31",
    "after_defects": "41",
    "causes": (
        "校验规则缺失:法:14:查检表 300 例:关联异常 98 例（77.8%）；"
        "字段定义不统一:料:12:查检表 300 例:关联异常 36 例（28.6%）；"
        "培训不到位:人:11:访谈 20 人次:8 人次未受训（40%）；"
        "校验工具版本旧:机:10:工具清单核对:3 个环节仍用旧版本；"
        "抽样标准不明确:测:9:抽检记录 60 例:差异不显著"
    ),
    "measures": (
        "补齐校验规则@校验规则缺失@李四@结果校验环节@第 4 周@新增 12 条规则并回归验证@5@5@4@5；"
        "统一字段定义@字段定义不统一@王五@数据录入环节@第 4 周@发布字段字典并培训@5@4@5@4；"
        "优化校验工具@校验工具版本旧@李四@工具链@第 5 周@升级工具版本并配置规则@4@4@4@4"
    ),
    "standard_doc": "结果校验作业标准书@作业标准书@QCC-STD-001@V1.0@2026-04-01@张三@每月@按检查表逐项稽核@新员工入职培训@连续 3 个月复查达标",
    "review": "数据驱动定位改善重点; 工具兼容性评估不足; 抽样标准仍未统一; 降低记录缺失率",
    "intangible": "1-5 分制@问题意识,数据分析,团队协作,表达沟通,工具应用@3.0@4.2",
    "benefit": "24@0.4@312@5.2@1 个月内",
}

QUESTIONS = [
    ("topic", "课题名称"),
    ("team", "圈组名称"),
    ("lead", "圈长"),
    ("period", "活动周期（如 2026-01-01..2026-03-31）"),
    ("metric", "指标名称"),
    ("direction", "指标方向 lower=越低越好 / higher=越高越好"),
    ("current_period", "现状收集期间"),
    ("sample", "现状样本量"),
    ("categories", "问题类别与频次（名称:频次，逗号分隔）"),
    ("strata", "层别数据（班别:数值，逗号分隔）"),
    ("criteria", "主题评价维度（逗号分隔）"),
    ("candidates", "候选主题（逗号分隔）"),
    ("scores", "主题评分（每个候选一行，维度分用逗号，行间用分号）"),
    ("plan_progress", "计划 vs 实际（计划周数@实际周数@说明）"),
    ("capability", "圈能力（%）"),
    ("after_period", "改善后收集期间"),
    ("after_defects", "改善后异常例数"),
    ("causes", "已验证真因（名称:维度:评分:数据来源:验证结果，逗号分隔）"),
    ("measures", "对策（名称@真因@责任人@范围@时间@做法@可行性@效益性@经济性@圈能力，逗号分隔）"),
    ("standard_doc", "标准化文件（名称@类型@编号@版本@生效@责任人@稽核频率@稽核方式@训练@维持）"),
    ("review", "检讨与改进（优点; 不足; 残余问题; 下期主题）"),
    ("intangible", "无形成果（量表@维度,逗号分隔@活动前均值@活动后均值）"),
    ("benefit", "效益（投入人时@投入费用@年化节省工时@年化节省费用@回收期）"),
]


def split_items(value: str) -> list[str]:
    """Split a packed answer into items.

    ``；`` / ``;`` win when present, so a value may itself contain Chinese commas
    (for example "关联异常 98 例（77.8%），占比较高").
    """
    text = str(value)
    for separator in ("；", ";"):
        if separator in text:
            return [chunk.strip() for chunk in text.split(separator) if chunk.strip()]
    return [chunk.strip() for chunk in text.split(",") if chunk.strip()]


def build_document(answers: dict[str, str]) -> dict:
    def pairs(value: str, cast=str) -> list[dict]:
        items = []
        for chunk in split_items(value):
            chunk = chunk.strip()
            if not chunk or ":" not in chunk:
                continue
            name, raw = chunk.split(":", 1)
            items.append({"name": name.strip(), "value": cast(raw.strip())})
        return items

    categories = [
        {"name": item["name"], "count": int(item["value"])} for item in pairs(answers["categories"], float)
    ]
    strata = [{"name": item["name"], "value": float(item["value"])} for item in pairs(answers["strata"], float)]

    criteria = split_items(answers["criteria"].replace("，", ","))
    candidates = split_items(answers["candidates"].replace("，", ","))
    score_rows = []
    for row in answers["scores"].split(";"):
        row = row.strip()
        if row:
            score_rows.append([int(v.strip()) for v in row.replace("，", ",").split(",") if v.strip()])
    progress_parts = [p.strip() for p in answers["plan_progress"].split("@")]

    causes = []
    for chunk in split_items(answers["causes"]):
        parts = [p.strip() for p in chunk.split(":")]
        if len(parts) >= 5:
            causes.append(
                {
                    "name": parts[0],
                    "dimension": parts[1],
                    "score": int(parts[2]),
                    "source": parts[3],
                    "method": "分类统计",
                    "result": parts[4],
                }
            )

    measures = []
    for chunk in split_items(answers["measures"]):
        parts = [p.strip() for p in chunk.split("@")]
        if len(parts) >= 10:
            measures.append(
                {
                    "name": parts[0], "cause": parts[1], "who": parts[2],
                    "where": parts[3], "when": parts[4], "how": parts[5],
                    "scores": {
                        "可行性": int(parts[6]), "效益性": int(parts[7]),
                        "经济性": int(parts[8]), "圈能力": int(parts[9]),
                    },
                }
            )

    standard = []
    std_parts = [p.strip() for p in answers["standard_doc"].split("@")]
    if len(std_parts) >= 10:
        standard.append(
            {
                "name": std_parts[0], "type": std_parts[1], "number": std_parts[2],
                "version": std_parts[3], "effective": std_parts[4], "owner": std_parts[5],
                "audit_frequency": std_parts[6], "audit_method": std_parts[7],
                "training": std_parts[8], "maintenance": std_parts[9],
            }
        )

    raw_review = answers["review"]
    review_parts = [
        p.strip() for p in (raw_review.split(";") if ";" in raw_review else raw_review.split("；"))
    ]
    while len(review_parts) < 4:
        review_parts.append("")

    intangible_parts = [p.strip() for p in answers["intangible"].split("@")]
    benefit_parts = [p.strip() for p in answers["benefit"].split("@")]

    return {
        "meta": {
            "topic": answers["topic"], "team": answers["team"], "lead": answers["lead"],
            "period": answers["period"], "direction": answers["direction"],
        },
        "metric": answers["metric"],
        "current": {
            "period": answers["current_period"],
            "sample": int(answers["sample"]),
            "categories": categories,
            "strata": strata,
            "check_sheet": {
                "criteria": "按判定标准逐例记录异常",
                "method": "查检表逐例记录",
                "owner": answers["lead"],
            },
        },
        "target": {"capability": float(answers["capability"])},
        "after": {"period": answers["after_period"], "defects": int(answers["after_defects"])},
        "theme": {"candidates": candidates, "criteria": criteria, "scores": score_rows},
        "plan": {
            "planned_weeks": float(progress_parts[0]) if progress_parts and progress_parts[0] else None,
            "actual_weeks": float(progress_parts[1]) if len(progress_parts) > 1 and progress_parts[1] else None,
            "note": progress_parts[2] if len(progress_parts) > 2 else "",
        },
        "causes": causes,
        "measures": measures,
        "quality": {"data_type": "计数值", "tools": ["查检表", "柏拉图", "层别"]},
        "statistics": {"test": "chi-square", "comparison": "<", "p": 0.05},
        "standardization": standard,
        "review": {
            "strengths": [review_parts[0]] if review_parts[0] else [],
            "weaknesses": [review_parts[1]] if review_parts[1] else [],
            "residual": [review_parts[2]] if review_parts[2] else [],
            "next_topic": review_parts[3],
        },
        "intangible": {
            "scale": intangible_parts[0] if intangible_parts else "",
            "dimensions": [d.strip() for d in intangible_parts[1].split(",")] if len(intangible_parts) > 1 and intangible_parts[1] else [],
            "before_mean": float(intangible_parts[2]) if len(intangible_parts) > 2 and intangible_parts[2] else None,
            "after_mean": float(intangible_parts[3]) if len(intangible_parts) > 3 and intangible_parts[3] else None,
        },
        "benefit": {
            "input_hours": float(benefit_parts[0]) if len(benefit_parts) > 0 and benefit_parts[0] else None,
            "input_cost": float(benefit_parts[1]) if len(benefit_parts) > 1 and benefit_parts[1] else None,
            "annual_saving_hours": float(benefit_parts[2]) if len(benefit_parts) > 2 and benefit_parts[2] else None,
            "annual_saving": float(benefit_parts[3]) if len(benefit_parts) > 3 and benefit_parts[3] else None,
            "payback": benefit_parts[4] if len(benefit_parts) > 4 else "",
        },
    }


def collect_answers(answers_file: Path | None, use_defaults: bool) -> dict[str, str]:
    if answers_file is not None:
        data = yaml.safe_load(answers_file.read_text(encoding="utf-8")) or {}
        return {key: str(data.get(key, DEFAULTS[key])) for key, _ in QUESTIONS}
    answers: dict[str, str] = {}
    for key, label in QUESTIONS:
        default = DEFAULTS[key]
        if use_defaults:
            answers[key] = default
            continue
        value = input(f"{label} [{default}]: ").strip()
        answers[key] = value or default
    return answers


def main() -> int:
    parser = argparse.ArgumentParser(description="Minimal QCC data wizard.")
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--answers", type=Path, default=None)
    parser.add_argument("--defaults", action="store_true")
    args = parser.parse_args()

    if args.out.exists():
        print(f"refusing to overwrite existing file: {args.out}")
        return 1
    answers = collect_answers(args.answers, args.defaults)
    document = build_document(answers)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(
        "# 最小数据文件（由 qcc_wizard 生成）：只包含原始事实，派生值由 derive_qcc_data.py 计算\n"
        + yaml.safe_dump(document, allow_unicode=True, sort_keys=False),
        encoding="utf-8",
    )
    print(f"written: {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
