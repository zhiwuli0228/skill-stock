#!/usr/bin/env python3
"""Self-test for the standard deck builder.

Builds a deck from a complete minimal dataset (narrative + schedule + per-dimension
cause scores), then asserts that

* the builder's own layout self-check reports no violations;
* the deck is 22 pages and passes the ten-step compliance check;
* the mechanical format audit reports no risk.

This is the regression guard for "the deck is generated in the method's standard
form" — if a page layout regresses (dense table, overflow, missing decision
branch, phase-bar Gantt…), this test fails.
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


def sample_minimal() -> dict:
    return {
        "meta": {"topic": "降低处理异常率", "team": "精益圈", "lead": "张三",
                 "period": "2026-01-01..2026-03-31", "direction": "lower"},
        "metric": "处理异常率",
        "current": {
            "period": "2026-01-01..2026-01-31",
            "sample": 300,
            "categories": [
                {"name": "校验异常", "count": 60},
                {"name": "记录缺失", "count": 26},
                {"name": "流程等待", "count": 20},
                {"name": "标注错误", "count": 12},
                {"name": "其他", "count": 8},
            ],
            "strata": [{"name": "A 班", "value": 46}, {"name": "B 班", "value": 38},
                       {"name": "C 班", "value": 42}],
            "check_sheet": {"criteria": "结果校验不通过即判定为异常",
                            "method": "查检表逐例记录", "owner": "李四",
                            "record_method": "逐例记录"},
        },
        "target": {"capability": 80},
        "after": {"period": "2026-03-01..2026-03-31", "defects": 41, "total": 300},
        "theme": {
            "candidates": ["降低处理异常率", "缩短处理时长", "减少返工次数"],
            "criteria": ["上级政策", "重要性", "迫切性", "可行性", "圈能力"],
            "scores": [[5, 5, 4, 5, 4], [4, 4, 3, 4, 4], [3, 4, 3, 3, 3]],
            "decision_rule": "5 分制，圈员独立打分取平均，权重相同",
            "selected": "降低处理异常率",
        },
        "plan": {
            "planned_weeks": 8,
            "actual_weeks": 8,
            "note": "第 5 周延期 1 天，完成率 95%",
            "axis": [f"第{i}周" for i in range(1, 9)],
            "schedule": [
                {"step": "1 主题选定", "owner": "张三", "planned": [1, 1], "actual": [1, 1],
                 "deviation": "按计划"},
                {"step": "2 活动计划", "owner": "张三", "planned": [1, 2], "actual": [1, 2],
                 "deviation": "按计划"},
                {"step": "3 现状把握", "owner": "李四", "planned": [2, 3], "actual": [2, 3],
                 "deviation": "按计划"},
                {"step": "4 目标设定", "owner": "李四", "planned": [3, 3], "actual": [3, 3],
                 "deviation": "按计划"},
                {"step": "5 解析", "owner": "王五", "planned": [3, 4], "actual": [3, 5],
                 "deviation": "延期 1 天"},
                {"step": "6 对策拟定", "owner": "王五", "planned": [4, 4], "actual": [5, 5],
                 "deviation": "延期 1 天"},
                {"step": "7 对策实施", "owner": "李四", "planned": [5, 6], "actual": [5, 6],
                 "deviation": "按计划"},
                {"step": "8 效果确认", "owner": "张三", "planned": [6, 7], "actual": [6, 7],
                 "deviation": "按计划"},
                {"step": "9 标准化", "owner": "王五", "planned": [7, 8], "actual": [7, 8],
                 "deviation": "按计划"},
                {"step": "10 检讨与改进", "owner": "张三", "planned": [8, 8], "actual": [8, 8],
                 "deviation": "按计划"},
            ],
        },
        "causes": [
            {"name": "校验规则缺失", "dimension": "法", "score": 14,
             "scores": {"影响度": 5, "发生频次": 5, "可控性": 4},
             "source": "查检表 300 例", "method": "分类统计", "result": "关联异常 98 例（77.8%）",
             "conclusion": "成立"},
            {"name": "字段定义不统一", "dimension": "料", "score": 12,
             "scores": {"影响度": 4, "发生频次": 4, "可控性": 4},
             "source": "查检表 300 例", "method": "口径对比", "result": "关联异常 36 例（28.6%）",
             "conclusion": "成立"},
            {"name": "抽样标准不明确", "dimension": "测", "score": 9,
             "scores": {"影响度": 3, "发生频次": 3, "可控性": 3},
             "source": "抽检记录 60 例", "method": "重抽对比", "result": "差异 < 5%，不显著",
             "conclusion": "不成立"},
            {"name": "培训不到位", "dimension": "人", "score": 11,
             "scores": {"影响度": 4, "发生频次": 4, "可控性": 3},
             "source": "访谈 20 人次", "method": "访谈核查", "result": "8 人次未受训（40%）",
             "conclusion": "成立"},
            {"name": "工具版本旧", "dimension": "机", "score": 8,
             "scores": {"影响度": 3, "发生频次": 2, "可控性": 3},
             "source": "工具清单", "method": "版本核对", "result": "3 个环节仍用旧版本",
             "conclusion": "成立"},
            {"name": "任务高峰集中", "dimension": "环", "score": 7,
             "scores": {"影响度": 3, "发生频次": 2, "可控性": 2},
             "source": "工时记录", "method": "时段统计", "result": "高峰时段异常占比 30%",
             "conclusion": "成立"},
        ],
        "measures": [
            {"name": "补齐校验规则", "cause": "校验规则缺失", "who": "李四",
             "where": "结果校验环节", "when": "第 4 周", "how": "新增 12 条规则并回归验证",
             "scores": {"可行性": 5, "效益性": 5, "经济性": 4, "圈能力": 5}},
            {"name": "统一字段定义", "cause": "字段定义不统一", "who": "王五",
             "where": "数据录入环节", "when": "第 4 周", "how": "发布字段字典并培训",
             "scores": {"可行性": 5, "效益性": 4, "经济性": 5, "圈能力": 4}},
            {"name": "培训到岗", "cause": "培训不到位", "who": "张三",
             "where": "班组培训", "when": "第 5 周", "how": "按岗位清单补训并考核",
             "scores": {"可行性": 4, "效益性": 4, "经济性": 4, "圈能力": 4}},
        ],
        "quality": {"data_type": "计数值", "tools": ["查检表", "柏拉图", "层别"]},
        "statistics": {"test": "chi-square", "comparison": "<", "p": 0.05},
        "standardization": [
            {"name": "结果校验作业标准书", "type": "作业标准书", "number": "QCC-STD-001",
             "version": "V1.0", "effective": "2026-04-01", "owner": "张三",
             "audit_frequency": "每月", "audit_method": "按检查表逐项稽核",
             "training": "新员工入职培训", "maintenance": "连续 3 个月复查达标"},
        ],
        "review": {"strengths": ["数据驱动定位改善重点"], "weaknesses": ["工具兼容性评估不足"],
                   "residual": ["抽样标准仍未统一"], "next_topic": "降低记录缺失率"},
        "intangible": {"scale": "1-5 分制",
                       "dimensions": ["问题意识", "数据分析", "团队协作", "表达沟通",
                                      "工具应用", "责任心"],
                       "before_mean": 3.0, "after_mean": 4.2},
        "benefit": {"input_hours": 24, "input_cost": 0.4, "annual_saving_hours": 312,
                    "annual_saving": 5.2, "payback": "1 个月内"},
        "narrative": {
            "background": {"context": "处理环节近 3 个月出现异常波动。",
                           "problem": "现状抽样 300 例，异常率 42.0%，高于 20% 控制线。",
                           "impact": "异常返工工时损失约占该环节总工时 18%。"},
            "reason": "上级政策要求降低异常率；问题迫切、数据可得、圈能力可支撑。",
            "scope": "处理与结果校验环节（不含上游需求变更）。",
            "flow": {"start": "开始", "process": ["接收任务", "执行处理", "数据记录"],
                     "decision": "结果校验是否通过？", "yes": ["结束"],
                     "no": ["异常处理", "结果校验异常"],
                     "note": "异常点：结果校验环节异常率最高（42.0%）。"},
            "sources": ["查检表 300 例（2026-01）", "改善前后对比记录", "标准化文件清单"],
            "next_step": "下一步：降低记录缺失率。",
        },
    }


def main() -> int:
    scripts = Path(__file__).resolve().parent
    templates = scripts.parent / "templates"
    template = templates / "qcc-empty-template.pptx"
    failures: list[str] = []
    if not template.exists():
        print("SELFTEST SKIPPED: template not found")
        return 0

    with tempfile.TemporaryDirectory(prefix="qcc-build-") as tmp:
        workspace = Path(tmp)
        minimal = workspace / "min.yaml"
        minimal.write_text(
            yaml.safe_dump(sample_minimal(), allow_unicode=True, sort_keys=False),
            encoding="utf-8",
        )
        full = workspace / "qcc-data.yaml"
        if run(scripts / "derive_qcc_data.py", "--min", str(minimal), "--out", str(full)).returncode != 0:
            failures.append("derive failed")
        deck = workspace / "deck.pptx"
        build = run(scripts / "build_qcc_deck.py", "--data", str(full),
                    "--template", str(template), "--out", str(deck), "--strict")
        if build.returncode != 0:
            failures.append("builder reported layout violations")
            print(build.stdout)
        if not deck.exists():
            failures.append("deck was not written")
        else:
            from pptx import Presentation

            slides = len(Presentation(str(deck)).slides)
            if slides != 22:
                failures.append(f"expected 22 slides, got {slides}")

        compliance = run(scripts / "check_qcc_method_compliance.py", str(deck),
                         "--data", str(full), "--json", str(workspace / "compliance.json"))
        if compliance.returncode != 0:
            failures.append("compliance check rejected the generated deck")
            print(compliance.stdout)
        report_path = workspace / "format.md"
        run(scripts / "audit_qcc_ppt_format.py", str(deck), "--report", str(report_path))
        if report_path.exists():
            report_text = report_path.read_text(encoding="utf-8")
            if "Slides with format risk: 0" not in report_text:
                failures.append("format audit reported risk")
                print(report_text)
        else:
            failures.append("format audit report missing")
        if (workspace / "compliance.json").exists():
            payload = json.loads((workspace / "compliance.json").read_text(encoding="utf-8"))
            if payload.get("overall") != "PASS":
                failures.append(f"compliance overall={payload.get('overall')}")

    if failures:
        print("SELFTEST FAILED:")
        for item in failures:
            print(f"- {item}")
        return 1
    print("SELFTEST PASSED: builder emits 22 method-compliant pages with no layout violations.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
