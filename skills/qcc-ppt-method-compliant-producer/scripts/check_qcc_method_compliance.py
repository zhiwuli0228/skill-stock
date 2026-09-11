#!/usr/bin/env python3
"""Structural QCC method-compliance checker (v5.0).

This checker verifies the standard ten-step QCC analysis chain, not just whether
method keywords appear in slide text. Each step must carry its required inputs,
analysis evidence and conclusions; a page that only shows a method name is
reported as WEAK, and a step whose required data is still a placeholder is
reported as INCOMPLETE.

Exit codes:
    0  PASS (all ten steps FOUND)
    1  NON-COMPLIANT (any step WEAK / MISSING / INCOMPLETE)
    2  usage / input error
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, Iterable, Sequence

try:
    from pptx import Presentation
except ImportError:  # pragma: no cover - dependency hint
    print(
        "python-pptx is required: pip install -r requirements.txt",
        file=sys.stderr,
    )
    raise SystemExit(2)


# --------------------------------------------------------------------------- #
# Slide extraction
# --------------------------------------------------------------------------- #


@dataclass(frozen=True)
class SlideView:
    index: int
    text: str
    tables: tuple[tuple[tuple[str, ...], ...], ...]
    has_chart: bool

    @property
    def row_count(self) -> int:
        return max((len(table) for table in self.tables), default=0)

    @property
    def column_count(self) -> int:
        return max((len(row) for table in self.tables for row in table), default=0)


def _iter_shapes(shape) -> Iterable[object]:
    yield shape
    if hasattr(shape, "shapes"):
        for child in shape.shapes:
            yield from _iter_shapes(child)


def _shape_text(shape) -> list[str]:
    chunks: list[str] = []
    if getattr(shape, "has_text_frame", False):
        text = shape.text_frame.text.strip()
        if text:
            chunks.append(text)
    if getattr(shape, "has_table", False):
        for row in shape.table.rows:
            for cell in row.cells:
                value = cell.text.strip()
                if value:
                    chunks.append(value)
    return chunks


def read_slides(pptx_path: Path) -> list[SlideView]:
    presentation = Presentation(str(pptx_path))
    slides: list[SlideView] = []
    for index, slide in enumerate(presentation.slides, start=1):
        texts: list[str] = []
        tables: list[tuple[tuple[str, ...], ...]] = []
        has_chart = False
        for shape in slide.shapes:
            for node in _iter_shapes(shape):
                texts.extend(_shape_text(node))
                if getattr(node, "has_table", False):
                    table = tuple(
                        tuple(cell.text.strip() for cell in row.cells)
                        for row in node.table.rows
                    )
                    tables.append(table)
                if getattr(node, "has_chart", False):
                    has_chart = True
        slides.append(
            SlideView(
                index=index,
                text="\n".join(texts),
                tables=tuple(tables),
                has_chart=has_chart,
            )
        )
    return slides


# --------------------------------------------------------------------------- #
# Text helpers
# --------------------------------------------------------------------------- #


PLACEHOLDERS = ("待补充", "待验证", "示例结构", "TBD", "TODO")

CRITERIA_WORDS = (
    "上级政策",
    "重要性",
    "迫切性",
    "可行性",
    "圈能力",
    "效益性",
    "经济性",
    "可操作性",
    "影响度",
)

PHASE_WORDS = (
    "P",
    "D",
    "C",
    "A",
    "主题选定",
    "活动计划",
    "现状把握",
    "目标设定",
    "解析",
    "对策拟定",
    "对策实施",
    "效果确认",
    "标准化",
    "检讨",
)

CAUSE_DIMENSIONS = ("人", "机", "料", "法", "环", "测")

FIVE_W1H = (
    ("What", ("What", "对策内容", "做什么")),
    ("Why", ("Why", "原因", "真因")),
    ("Who", ("Who", "责任人", "负责人")),
    ("Where", ("Where", "地点", "范围", "环节")),
    ("When", ("When", "时间", "期限", "完成日期")),
    ("How", ("How", "如何", "做法", "判定标准")),
)


def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def has_word(text: str, *words: str) -> bool:
    return any(word and word in text for word in words)


def count_distinct(text: str, words: Sequence[str]) -> int:
    upper = text.upper()
    return sum(1 for word in words if word.upper() in upper)


def has_number(text: str) -> bool:
    return re.search(r"\d", text) is not None


def has_percent(text: str) -> bool:
    return re.search(r"\d+(?:\.\d+)?\s*%", text) is not None


def percent_count(text: str) -> int:
    return len(re.findall(r"\d+(?:\.\d+)?\s*%", text))


def number_count(text: str) -> int:
    return len(re.findall(r"\d+(?:\.\d+)?", text))


def placeholders_in(text: str) -> list[str]:
    return [word for word in PLACEHOLDERS if word in text]


def excerpt(text: str, limit: int = 120) -> str:
    flat = normalize(text)
    return flat if len(flat) <= limit else f"{flat[:limit]}…"


# --------------------------------------------------------------------------- #
# Step definitions
# --------------------------------------------------------------------------- #


@dataclass(frozen=True)
class Rule:
    label: str
    check: Callable[["Bundle"], bool]


@dataclass(frozen=True)
class Step:
    number: int
    phase: str
    method: str
    matcher: Callable[[SlideView], bool]
    rules: tuple[Rule, ...]


@dataclass
class Bundle:
    """Matched slides of one step plus convenience accessors."""

    slides: list[SlideView] = field(default_factory=list)

    @property
    def text(self) -> str:
        return "\n".join(slide.text for slide in self.slides)

    @property
    def page_numbers(self) -> list[int]:
        return [slide.index for slide in self.slides]

    @property
    def max_rows(self) -> int:
        return max((slide.row_count for slide in self.slides), default=0)

    @property
    def max_columns(self) -> int:
        return max((slide.column_count for slide in self.slides), default=0)

    @property
    def has_chart(self) -> bool:
        return any(slide.has_chart for slide in self.slides)


def _table_with_rows(bundle: Bundle, minimum_rows: int) -> bool:
    return bundle.max_rows >= minimum_rows


THEME = Step(
    number=1,
    phase="主题选定",
    method="主题评价矩阵",
    matcher=lambda slide: has_word(slide.text, "主题选定", "主题评价", "主题评审"),
    rules=(
        Rule(
            "候选主题 ≥2",
            lambda b: _table_with_rows(b, 3) or b.text.count("候选") >= 2,
        ),
        Rule(
            "评价维度 ≥3",
            lambda b: count_distinct(b.text, CRITERIA_WORDS) >= 3 or b.max_columns >= 4,
        ),
        Rule("评分数字", lambda b: has_number(b.text)),
        Rule("排序或选定结论", lambda b: has_word(b.text, "排序", "总分", "选定", "采纳", "得分")),
    ),
)

ACTIVITY_PLAN = Step(
    number=2,
    phase="活动计划拟定",
    method="甘特图",
    matcher=lambda slide: has_word(slide.text, "活动计划", "甘特图", "计划拟定"),
    rules=(
        Rule("阶段 ≥4", lambda b: count_distinct(b.text, PHASE_WORDS) >= 4),
        Rule(
            "时间轴（周次/日期）",
            lambda b: has_word(b.text, "周", "月", "日期", "时间")
            or re.search(r"\d+\s*(?:周|月|/\d+)", b.text) is not None,
        ),
        Rule("负责人", lambda b: has_word(b.text, "负责人", "责任人", "圈员")),
    ),
)

CURRENT_STATE = Step(
    number=3,
    phase="现状把握",
    method="现状流程图 + 查检表 + 层别 + 柏拉图",
    matcher=lambda slide: has_word(
        slide.text, "现状把握", "现状流程图", "查检表", "层别", "现状｜柏拉图"
    )
    or (has_word(slide.text, "柏拉图") and has_word(slide.text, "现状")),
    rules=(
        Rule(
            "现状流程图（步骤 ≥3，含起止）",
            lambda b: has_word(b.text, "流程图")
            and (b.text.count("→") >= 3 or has_word(b.text, "开始") and has_word(b.text, "结束")),
        ),
        Rule(
            "查检表判定标准 / 收集期间 / 样本量",
            lambda b: has_word(b.text, "判定标准", "判断标准", "标准")
            and has_word(b.text, "期间", "收集", "日期")
            and has_word(b.text, "样本", "例数", "n=", "N="),
        ),
        Rule(
            "数据汇总（类别 ≥3 且含频次）",
            lambda b: _table_with_rows(b, 4) or number_count(b.text) >= 3,
        ),
        Rule("层别分析维度", lambda b: has_word(b.text, "层别", "分层")),
        Rule(
            "柏拉图累计百分比",
            lambda b: has_word(b.text, "累计") and has_percent(b.text),
        ),
        Rule("80% 改善重点", lambda b: has_word(b.text, "80%", "80 %")),
        Rule(
            "关键少数结论",
            lambda b: has_word(b.text, "改善重点", "关键少数", "关键少数项", "二八"),
        ),
    ),
)

TARGET = Step(
    number=4,
    phase="目标设定",
    method="目标值计算 + 目标柱状图",
    matcher=lambda slide: has_word(slide.text, "目标设定"),
    rules=(
        Rule("现况值", lambda b: has_word(b.text, "现况值", "现状值") and has_number(b.text)),
        Rule("改善重点", lambda b: has_word(b.text, "改善重点") and has_percent(b.text)),
        Rule("圈能力", lambda b: has_word(b.text, "圈能力") and has_percent(b.text)),
        Rule("目标值", lambda b: has_word(b.text, "目标值") and has_number(b.text)),
        Rule(
            "计算关系",
            lambda b: has_word(b.text, "=", "＝", "计算", "公式"),
        ),
        Rule(
            "目标柱状图 / 对比图",
            lambda b: b.has_chart or has_word(b.text, "柱状", "对比图", "目标图"),
        ),
        Rule("合理性说明", lambda b: has_word(b.text, "合理性", "依据", "理由")),
    ),
)

ANALYSIS = Step(
    number=5,
    phase="解析",
    method="鱼骨图 + 要因评价 + 真因验证",
    matcher=lambda slide: has_word(
        slide.text, "解析", "鱼骨图", "特性要因图", "要因评价", "真因验证", "根因验证"
    ),
    rules=(
        Rule(
            "鱼骨图 4M1E ≥4 维",
            lambda b: has_word(b.text, "鱼骨图", "特性要因图")
            and count_distinct(b.text, CAUSE_DIMENSIONS) >= 4,
        ),
        Rule(
            "要因评价（评分/排序）",
            lambda b: has_word(b.text, "要因评价", "要因分析", "矩阵图")
            and has_number(b.text)
            and has_word(b.text, "筛选", "排序", "总分", "评分"),
        ),
        Rule(
            "真因验证数据来源",
            lambda b: has_word(b.text, "真因验证", "根因验证")
            and has_word(b.text, "数据来源", "查检表", "样本", "现场", "验证数据"),
        ),
        Rule(
            "真因验证结果与结论",
            lambda b: has_word(b.text, "结果", "验证结果")
            and has_word(b.text, "结论", "真因", "成立", "不成立"),
        ),
    ),
)

COUNTERMEASURE = Step(
    number=6,
    phase="对策拟定",
    method="对策评价矩阵 + 5W1H + 真因映射",
    matcher=lambda slide: has_word(slide.text, "对策拟定", "对策评价", "5W1H", "5W2H"),
    rules=(
        Rule("对策 ≥3", lambda b: _table_with_rows(b, 4) or number_count(b.text) >= 3),
        Rule(
            "对策评价维度 ≥3",
            lambda b: count_distinct(b.text, CRITERIA_WORDS) >= 3,
        ),
        Rule("对策评分", lambda b: has_number(b.text)),
        Rule(
            "5W1H 六要素",
            lambda b: all(has_word(b.text, *aliases) for _, aliases in FIVE_W1H),
        ),
        Rule("对策↔已验证真因映射", lambda b: has_word(b.text, "真因")),
    ),
)

IMPLEMENTATION = Step(
    number=7,
    phase="对策实施与检讨",
    method="PDCA 实施跟踪",
    matcher=lambda slide: has_word(slide.text, "对策实施", "实施跟踪", "实施与检讨"),
    rules=(
        Rule("阶段 / PDCA", lambda b: count_distinct(b.text, PHASE_WORDS) >= 2 or has_word(b.text, "阶段")),
        Rule("时间 / 责任人", lambda b: has_word(b.text, "时间", "日期") and has_word(b.text, "责任人", "负责人")),
        Rule("进展记录", lambda b: has_word(b.text, "进展", "进度", "状态", "完成")),
        Rule("过程数据跟踪", lambda b: has_number(b.text)),
        Rule("困难与调整", lambda b: has_word(b.text, "困难", "问题", "调整", "改进")),
    ),
)

EFFECT = Step(
    number=8,
    phase="效果确认",
    method="有形成果 + 无形成果",
    matcher=lambda slide: has_word(slide.text, "效果确认", "有形成果", "无形成果"),
    rules=(
        Rule("改善前值", lambda b: has_word(b.text, "改善前", "活动前", "改善前值") and has_number(b.text)),
        Rule("改善后值", lambda b: has_word(b.text, "改善后", "活动后", "改善后值") and has_number(b.text)),
        Rule("目标达成率", lambda b: has_word(b.text, "达成率", "目标达成") and has_percent(b.text)),
        Rule("进步率", lambda b: has_word(b.text, "进步率") and has_percent(b.text)),
        Rule("改善前后对比图", lambda b: has_word(b.text, "对比", "柏拉图", "柱状")),
        Rule(
            "无形成果（雷达图/能力评分）",
            lambda b: has_word(b.text, "雷达图", "无形成果", "能力评分", "成长"),
        ),
    ),
)

STANDARDIZATION = Step(
    number=9,
    phase="标准化",
    method="标准化文件 + 日常稽核",
    matcher=lambda slide: has_word(slide.text, "标准化"),
    rules=(
        Rule(
            "标准化文件名称与类型",
            lambda b: has_word(b.text, "作业标准书", "标准书", "制度", "表单", "流程图", "规范")
            and has_word(b.text, "文件", "编号", "名称", "标准"),
        ),
        Rule(
            "稽核人 / 频率 / 方式",
            lambda b: has_word(b.text, "稽核", "检查", "审核")
            and has_word(b.text, "频率", "周期", "每周", "每月", "每季")
            and has_word(b.text, "责任人", "负责人", "执行人"),
        ),
        Rule("教育训练与推广", lambda b: has_word(b.text, "教育训练", "培训", "训练", "推广")),
    ),
)

REVIEW = Step(
    number=10,
    phase="检讨与改进",
    method="活动检讨 + 下期主题",
    matcher=lambda slide: has_word(slide.text, "检讨与改进", "活动检讨", "检讨"),
    rules=(
        Rule("优点", lambda b: has_word(b.text, "优点", "做得好的", "成效")),
        Rule("不足", lambda b: has_word(b.text, "不足", "待改进", "缺点", "问题点")),
        Rule("残余问题", lambda b: has_word(b.text, "残余", "遗留", "未解决", "持续跟踪")),
        Rule("下期主题", lambda b: has_word(b.text, "下期", "下一期", "后续主题", "持续改进")),
    ),
)


STEPS: tuple[Step, ...] = (
    THEME,
    ACTIVITY_PLAN,
    CURRENT_STATE,
    TARGET,
    ANALYSIS,
    COUNTERMEASURE,
    IMPLEMENTATION,
    EFFECT,
    STANDARDIZATION,
    REVIEW,
)
# --------------------------------------------------------------------------- #
# Evaluation
# --------------------------------------------------------------------------- #


@dataclass
class StepResult:
    step: Step
    status: str
    pages: list[int]
    missing: list[str]
    evidence: list[str]


def evaluate_step(step: Step, slides: Sequence[SlideView]) -> StepResult:
    matched = [slide for slide in slides if step.matcher(slide)]
    bundle = Bundle(matched)
    pages = bundle.page_numbers

    if not matched:
        return StepResult(step, "MISSING", [], [rule.label for rule in step.rules], [])

    missing = [rule.label for rule in step.rules if not rule.check(bundle)]
    placeholders = sorted({word for slide in matched for word in placeholders_in(slide.text)})

    if missing and placeholders:
        status = "INCOMPLETE"
    elif missing:
        status = "WEAK"
    else:
        status = "FOUND"

    evidence = [f"[Slide {slide.index}] {excerpt(slide.text)}" for slide in matched[:4]]
    if placeholders:
        evidence.append("占位符: " + ", ".join(placeholders))
    return StepResult(step, status, pages, missing, evidence)


def evaluate(slides: Sequence[SlideView]) -> list[StepResult]:
    return [evaluate_step(step, slides) for step in STEPS]


def overall_status(results: Sequence[StepResult]) -> str:
    return "PASS" if all(result.status == "FOUND" for result in results) else "NON-COMPLIANT"


def build_report(pptx_path: Path, slides: Sequence[SlideView], results: Sequence[StepResult]) -> str:
    lines: list[str] = []
    lines.append("# QCC Method Compliance Report (v5.0)")
    lines.append("")
    lines.append(f"- PPTX: `{pptx_path}`")
    lines.append(f"- Slides: {len(slides)}")
    lines.append(f"- Checked at: {datetime.now(timezone.utc).isoformat(timespec='seconds')}")
    lines.append(f"- Overall: **{overall_status(results)}**")
    lines.append("")
    lines.append("## Step results")
    lines.append("")
    lines.append("| # | Step | Method | Status | Pages | Missing / notes |")
    lines.append("|---:|---|---|---|---|---|")
    for result in results:
        pages = ", ".join(str(page) for page in result.pages) or "-"
        missing = "; ".join(result.missing) or "-"
        lines.append(
            f"| {result.step.number} | {result.step.phase} | {result.step.method} "
            f"| {result.status} | {pages} | {missing} |"
        )
    lines.append("")
    lines.append("## Details")
    lines.append("")
    for result in results:
        lines.append(f"### {result.step.number}. {result.step.phase} — {result.status}")
        lines.append("")
        if result.missing:
            lines.append("Missing evidence:")
            for item in result.missing:
                lines.append(f"- {item}")
            lines.append("")
        if result.evidence:
            lines.append("Evidence:")
            for item in result.evidence:
                lines.append(f"- {item}")
            lines.append("")
    lines.append("## Notes")
    lines.append("")
    lines.append("- `FOUND` requires inputs, analysis evidence and conclusions for the step.")
    lines.append("- `WEAK` means the step page exists but required evidence is missing.")
    lines.append("- `INCOMPLETE` means required data is still a placeholder.")
    lines.append("- Rendered screenshot review is still required after this check.")
    lines.append("")
    return "\n".join(lines)


def report_to_json(results: Sequence[StepResult]) -> dict[str, object]:
    return {
        "overall": overall_status(results),
        "steps": [
            {
                "number": result.step.number,
                "phase": result.step.phase,
                "method": result.step.method,
                "status": result.status,
                "pages": result.pages,
                "missing": result.missing,
            }
            for result in results
        ],
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Structural QCC ten-step method compliance check (v5.0)."
    )
    parser.add_argument("pptx", type=Path)
    parser.add_argument("--report", type=Path, default=None)
    parser.add_argument("--json", dest="json_path", type=Path, default=None)
    args = parser.parse_args(argv)

    if not args.pptx.exists():
        print(f"PPTX not found: {args.pptx}", file=sys.stderr)
        return 2

    slides = read_slides(args.pptx)
    results = evaluate(slides)
    report = build_report(args.pptx, slides, results)

    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(report, encoding="utf-8")
    if args.json_path:
        args.json_path.parent.mkdir(parents=True, exist_ok=True)
        args.json_path.write_text(
            json.dumps(report_to_json(results), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    print(f"overall={overall_status(results)}")
    for result in results:
        detail = "; ".join(result.missing) if result.missing else "ok"
        print(f"  {result.step.number:>2}. {result.step.phase}: {result.status} ({detail})")

    return 0 if overall_status(results) == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
