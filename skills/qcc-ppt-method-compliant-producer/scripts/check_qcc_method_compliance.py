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
    title: str = ""

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
        title = ""
        title_size = -1.0
        for shape in slide.shapes:
            for node in _iter_shapes(shape):
                for value in _shape_text(node):
                    # Chrome is not data: page-number badges and the sample-data footer
                    # must not participate in numeric extraction.
                    stripped = value.strip()
                    if re.fullmatch(r"\d{1,2}", stripped):
                        continue
                    if "非真实业务结论" in value:
                        continue
                    texts.append(value)
                if getattr(node, "has_table", False):
                    table = tuple(
                        tuple(cell.text.strip() for cell in row.cells)
                        for row in node.table.rows
                    )
                    tables.append(table)
                if getattr(node, "has_chart", False):
                    has_chart = True
                if getattr(node, "has_text_frame", False):
                    value = node.text_frame.text.strip()
                    sizes = [
                        run.font.size.pt
                        for paragraph in node.text_frame.paragraphs
                        for run in paragraph.runs
                        if run.font.size is not None
                    ]
                    size = max(sizes) if sizes else 0.0
                    if value and size > title_size:
                        title = value
                        title_size = size
        slides.append(
            SlideView(
                index=index,
                text="\n".join(texts),
                tables=tuple(tables),
                has_chart=has_chart,
                title=normalize(title),
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


def title_text(slide: SlideView) -> str:
    """Slide title (largest-font text) or full text when no title is detected."""
    return slide.title or slide.text


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


NUMBER_RE = re.compile(r"-?\d+(?:\.\d+)?")
PERCENT_RE = re.compile(r"-?\d+(?:\.\d+)?\s*%")

LOWER_IS_BETTER = (
    "降低", "减少", "下降", "异常率", "不良率", "缺陷率", "故障率",
    "返工率", "耗时", "时长", "等待", "投诉", "错误率",
)
HIGHER_IS_BETTER = (
    "提高", "提升", "上升", "满意度", "合格率", "达成率",
    "准确率", "覆盖率", "及时率", "成功率",
)
FREQ_HEADERS = ("频次", "次数", "数量", "例数", "件数", "发生次数")
CUMULATIVE_HEADERS = ("累计", "累积")


def numbers_in(text: str) -> list[float]:
    return [float(value) for value in NUMBER_RE.findall(text)]


def percents_in(text: str) -> list[float]:
    return [float(value.rstrip("%")) for value in re.findall(r"-?\d+(?:\.\d+)?\s*%", text)]


def labelled_percent(text: str, *labels: str) -> float | None:
    for label in labels:
        match = re.search(
            re.escape(label) + r"[^0-9%]{0,4}(-?\d+(?:\.\d+)?)\s*%", text
        )
        if match:
            return float(match.group(1))
    return None


def labelled_percent_last(text: str, label: str, window: int = 160) -> float | None:
    """Last percentage within a window after the label (formulas state the result last)."""
    match = re.search(re.escape(label) + r"[\s\S]{0,%d}" % window, text)
    if not match:
        return None
    values = percents_in(match.group(0))
    return values[-1] if values else None


def target_value_percent(text: str) -> float | None:
    """KPI style first ('目标值 13.3%'), then the formula result (last %)."""
    direct = re.findall(r"目标值[^0-9%]{0,10}(\d+(?:\.\d+)?)\s*%", text)
    if direct:
        return float(direct[-1])
    if "目标值" in text:
        window = text[text.find("目标值"):][:200]
        values = percents_in(window)
        if values:
            return values[-1]
    return None


def labelled_number(text: str, *labels: str) -> float | None:
    for label in labels:
        match = re.search(
            re.escape(label) + r"[^0-9]{0,4}(\d+(?:\.\d+)?)", text
        )
        if match:
            return float(match.group(1))
    return None


def detect_direction(text: str) -> str:
    lower = sum(1 for word in LOWER_IS_BETTER if word in text)
    higher = sum(1 for word in HIGHER_IS_BETTER if word in text)
    return "lower" if lower >= higher else "higher"


def column_series(table, headers: Sequence[str]) -> list[float]:
    """Numeric column values for a header match, skipping 合计/总计 rows."""
    if not table:
        return []
    header = [normalize(cell) for cell in table[0]]
    for column, cell in enumerate(header):
        if not any(word in cell for word in headers):
            continue
        values: list[float] = []
        for row in table[1:]:
            if column >= len(row):
                continue
            label = normalize(row[0]) if row else ""
            if any(token in label for token in ("合计", "总计", "小计")):
                continue
            numbers = numbers_in(row[column])
            if numbers:
                values.append(numbers[0])
        if len(values) >= 3:
            return values
    return []


def frequency_series(bundle: "Bundle") -> list[float]:
    for table in bundle.tables:
        series = column_series(table, FREQ_HEADERS)
        if series:
            return series
    return []


def cumulative_series(bundle: "Bundle") -> list[float]:
    for table in bundle.tables:
        series = column_series(table, CUMULATIVE_HEADERS)
        if len(series) >= 3:
            return series
    # an explicit arrow chain states the whole series in order
    for slide in bundle.slides:
        for chain in re.findall(
            r"((?:\d+(?:\.\d+)?\s*%\s*(?:→|->|➜|>)\s*)+\d+(?:\.\d+)?\s*%)", slide.text
        ):
            values = percents_in(chain)
            if (
                len(values) >= 3
                and all(values[index] <= values[index + 1] + 0.05 for index in range(len(values) - 1))
                and abs(values[-1] - 100.0) <= 0.5
            ):
                return values
    # otherwise use the longest non-decreasing run on a page that talks about 累计
    best: list[float] = []
    for slide in bundle.slides:
        if "累计" not in slide.text:
            continue
        run: list[float] = []
        for value in percents_in(slide.text):
            if not run or value >= run[-1] - 0.05:
                run.append(value)
            else:
                run = [value]
            if len(run) > len(best):
                best = list(run)
    return best if len(best) >= 3 else []


CN_DIGITS = {"一": 1, "二": 2, "三": 3, "四": 4, "五": 5, "六": 6, "七": 7, "八": 8, "九": 9, "十": 10}


def declared_focus_count(text: str) -> int | None:
    patterns = (
        r"前\s*([0-9一二三四五六七八九十]+)\s*[类项个]",
        r"(?:改善重点|关键少数)[^0-9一二三四五六七八九十]{0,30}?([0-9一二三四五六七八九十]+)\s*[类项个]",
    )
    for pattern in patterns:
        match = re.search(pattern, text)
        if not match:
            continue
        raw = match.group(1)
        if raw.isdigit():
            return int(raw)
        value = CN_DIGITS.get(raw)
        if value is not None:
            return value
    return None


def pareto_counts_descending(bundle: "Bundle") -> bool:
    series = frequency_series(bundle)
    if len(series) < 3:
        return True  # presence rules already flag missing data
    return all(series[index] >= series[index + 1] for index in range(len(series) - 1))


def pareto_counts_match_sample(bundle: "Bundle") -> bool:
    series = frequency_series(bundle)
    if len(series) < 3:
        return True
    total = sum(series)
    sample = labelled_number(bundle.text, "样本量", "样本", "例数", "n=", "N=")
    if sample is None:
        return True
    # Defects must not exceed the checked population; equality is legitimate when
    # every checked unit carries one defect, so only an excess is an error.
    return total <= sample + max(1.0, sample * 0.01)


def pareto_cumulative_valid(bundle: "Bundle") -> bool:
    series = cumulative_series(bundle)
    if len(series) < 3:
        return True
    monotonic = all(series[index] <= series[index + 1] + 0.05 for index in range(len(series) - 1))
    return monotonic and abs(series[-1] - 100.0) <= 0.5


def pareto_focus_covers_80(bundle: "Bundle") -> bool:
    series = cumulative_series(bundle)
    if len(series) < 3:
        return True
    count = declared_focus_count(bundle.text)
    if count is None or count > len(series):
        count = next((index + 1 for index, value in enumerate(series) if value >= 80), len(series))
    return series[count - 1] >= 80.0 - 0.5


def target_params(bundle: "Bundle") -> dict[str, float | str | None]:
    text = bundle.text
    return {
        "current": labelled_percent(text, "现况值", "现状值"),
        "focus": labelled_percent(text, "改善重点"),
        "capability": labelled_percent(text, "圈能力"),
        "target": target_value_percent(text),
        "standard": labelled_percent(text, "标准值", "理论值", "基准值"),
        "direction": detect_direction(text),
    }


def target_params_in_range(bundle: "Bundle") -> bool:
    params = target_params(bundle)
    values = [params[key] for key in ("current", "focus", "capability", "target")]
    if any(value is None for value in values):
        return True
    return all(0.0 <= float(value) <= 100.0 for value in values)


def target_direction_consistent(bundle: "Bundle") -> bool:
    params = target_params(bundle)
    if params["current"] is None or params["target"] is None:
        return True
    if params["direction"] == "lower":
        return float(params["target"]) < float(params["current"])
    return float(params["target"]) > float(params["current"])


def target_formula_consistent(bundle: "Bundle") -> bool:
    params = target_params(bundle)
    if any(params[key] is None for key in ("current", "focus", "capability", "target")):
        return True
    current = float(params["current"])
    focus = float(params["focus"]) / 100.0
    capability = float(params["capability"]) / 100.0
    target = float(params["target"])
    standard = params["standard"]
    candidates: list[float] = []
    if params["direction"] == "lower":
        candidates.append(current - current * focus * capability)
        if standard is not None:
            candidates.append(current - (current - float(standard)) * focus * capability)
    else:
        candidates.append(current + (100.0 - current) * focus * capability)
        candidates.append(current + current * focus * capability)
        if standard is not None:
            candidates.append(current + (float(standard) - current) * focus * capability)
    return any(abs(target - value) <= 0.5 for value in candidates)


def true_cause_sample_sufficient(bundle: "Bundle") -> bool:
    text = bundle.text
    if any(token in text for token in ("抽样依据", "全量", "普查", "全样本")):
        return True
    samples: list[float] = []
    for match in re.finditer(r"(?:样本量|样本|例数|例|条)\s*[:：]?\s*(\d+(?:\.\d+)?)", text):
        samples.append(float(match.group(1)))
    for match in re.finditer(r"(\d+(?:\.\d+)?)\s*(?:例|条|份)", text):
        samples.append(float(match.group(1)))
    return max(samples) >= 30 if samples else False


def effect_values(bundle: "Bundle") -> dict[str, float | None]:
    text = bundle.text
    return {
        "before": labelled_percent(text, "改善前", "活动前"),
        "after": labelled_percent(text, "改善后", "活动后"),
        "attainment": labelled_percent(text, "目标达成率", "达成率"),
        "progress": labelled_percent(text, "进步率"),
        "target": labelled_percent(text, "目标值"),
        "direction": detect_direction(text),
    }


def effect_direction_improved(bundle: "Bundle") -> bool:
    values = effect_values(bundle)
    if values["before"] is None or values["after"] is None:
        return True
    if values["direction"] == "lower":
        return float(values["after"]) < float(values["before"])
    return float(values["after"]) > float(values["before"])


def effect_attainment_consistent(bundle: "Bundle") -> bool:
    values = effect_values(bundle)
    if any(values[key] is None for key in ("before", "after", "attainment")):
        return True
    before = float(values["before"])
    after = float(values["after"])
    target = float(values["target"]) if values["target"] is not None else None
    if target is None or abs(target - before) < 0.05:
        return True
    computed = (after - before) / (target - before) * 100.0
    declared = float(values["attainment"])
    return abs(computed - declared) <= 1.0 and declared > 0


def effect_progress_consistent(bundle: "Bundle") -> bool:
    values = effect_values(bundle)
    if any(values[key] is None for key in ("before", "after", "progress")):
        return True
    before = float(values["before"])
    after = float(values["after"])
    if before == 0:
        return True
    computed = (before - after) / before * 100.0
    declared = float(values["progress"])
    return abs(computed - declared) <= 1.0


def effect_post_evidence_present(bundle: "Bundle") -> bool:
    text = bundle.text
    post = has_word(text, "改善后", "活动后")
    period = has_word(text, "期间", "日期", "月") or re.search(r"\d{4}[-/]\d{1,2}", text) is not None
    sample = has_word(text, "样本") or re.search(r"\d+\s*例", text) is not None
    return bool(post and period and sample)


def theme_rule_documented(bundle: "Bundle") -> bool:
    return has_word(
        bundle.text, "权重", "评分规则", "评分标准", "评价标准", "评分方式", "评分方法"
    )


def plan_vs_actual_present(bundle: "Bundle") -> bool:
    text = bundle.text
    has_actual = has_word(text, "实际进度", "实际完成", "实际")
    has_progress = has_word(text, "完成率", "进度对照", "偏差", "延期", "按计划")
    return has_actual and has_progress


STEP_NAMES = tuple(word for word in PHASE_WORDS if word not in {"P", "D", "C", "A"})


def plan_work_packages_present(bundle: "Bundle") -> bool:
    """A QCC Gantt lists the work packages (十步法工作项目), not just phase bars.

    Four PDCA phase bars are a milestone strip, not an activity-plan Gantt: the
    plan must name the individual steps so each one can carry an owner, a planned
    window and an actual window.
    """
    steps = count_distinct(bundle.text, STEP_NAMES)
    phases = count_distinct(bundle.text, ("P", "D", "C", "A"))
    return steps >= 6 and phases >= 3


def check_sheet_collection_documented(bundle: "Bundle") -> bool:
    text = bundle.text
    method = has_word(text, "收集方法", "记录方式", "数据来源", "采集方式", "逐例记录")
    owner = has_word(text, "责任人", "负责人", "收集人")
    return method and owner


def intangible_scale_documented(bundle: "Bundle") -> bool:
    text = bundle.text
    scale = has_word(text, "量表", "分制", "评分范围")
    before_after = has_word(text, "活动前", "改善前") and has_word(text, "活动后", "改善后")
    dimensions = has_word(text, "维度", "能力")
    return scale and before_after and dimensions


def standardization_versioned(bundle: "Bundle") -> bool:
    text = bundle.text
    number = has_word(text, "编号")
    version = has_word(text, "版本", "版次", "V1", "v1")
    effective = has_word(text, "生效", "发布日期")
    return number and version and effective


def standardization_audit_loop(bundle: "Bundle") -> bool:
    return has_word(
        bundle.text, "稽核结果", "回写", "效果维持", "复查", "再发防止", "维持"
    )


def verified_causes(slides: Sequence[SlideView]) -> list[str]:
    bundle = Bundle([slide for slide in slides if ANALYSIS.matcher(slide)])
    causes: list[str] = []
    for table in bundle.tables:
        if not table:
            continue
        header = [normalize(cell) for cell in table[0]]
        conclusion_column = next(
            (index for index, cell in enumerate(header) if "结论" in cell), None
        )
        if conclusion_column is None:
            continue
        for row in table[1:]:
            if conclusion_column >= len(row):
                continue
            conclusion = normalize(row[conclusion_column])
            if "成立" in conclusion and "不成立" not in conclusion:
                causes.append(normalize(row[0]))
    return causes


def countermeasure_rows(slides: Sequence[SlideView]) -> list[tuple[str, str, str, bool]]:
    bundle = Bundle([slide for slide in slides if COUNTERMEASURE.matcher(slide)])
    rows: list[tuple[str, str, str, bool]] = []
    for table in bundle.tables:
        if not table:
            continue
        header = [normalize(cell) for cell in table[0]]
        measure_column = next(
            (
                index
                for index, cell in enumerate(header)
                if "对策" in cell or "措施" in cell or "What" in cell
            ),
            None,
        )
        if measure_column is None:
            continue
        cause_column = next(
            (index for index, cell in enumerate(header) if "真因" in cell or "Why" in cell),
            None,
        )
        if cause_column is None:
            # Without a cause-mapping column the table cannot prove the mapping.
            continue
        decision_column = next(
            (
                index
                for index, cell in enumerate(header)
                if "取舍" in cell or "采纳" in cell or "总分" in cell
            ),
            None,
        )
        for row in table[1:]:
            if measure_column >= len(row):
                continue
            measure = normalize(row[measure_column])
            if not measure:
                continue
            mapping = (
                normalize(row[cause_column])
                if cause_column is not None and cause_column < len(row)
                else ""
            )
            decision = (
                normalize(row[decision_column])
                if decision_column is not None and decision_column < len(row)
                else ""
            )
            adopted = "不采纳" not in decision and "放弃" not in decision
            rows.append((measure, mapping, decision, adopted))
    return rows


def countermeasure_mapping_ok(slides: Sequence[SlideView]) -> bool:
    causes = verified_causes(slides)
    rows = countermeasure_rows(slides)
    if not causes or not rows:
        return False
    adopted = [row for row in rows if row[3]]
    if not adopted:
        return False
    for _, mapping, _, _ in adopted:
        if not mapping or mapping in {"—", "-", "–", "待补充"}:
            return False
        if not any(
            cause and (cause in mapping or mapping in cause) for cause in causes
        ):
            return False
    return True


DATA_TYPE_TOKENS = (
    "计数值", "计量值", "计数型", "计量型", "属性值", "连续型", "离散型",
)
TOOL_SELECTION_TOKENS = (
    "查检表", "柏拉图", "直方图", "散布图", "管制图", "层别", "流程图", "矩阵图", "雷达图",
)
STAT_TEST_TOKENS = (
    "卡方", "χ²", "χ2", "t 检验", "t检验", "秩和", "检验", "p 值", "p值",
    "p<", "p <", "显著性", "置信区间",
)
STAT_WAIVER_TOKENS = (
    "不做统计检验", "未做统计检验", "不适用统计", "描述性统计", "描述性",
    "全量数据", "普查", "样本量不足", "豁免",
)


def data_tool_rationale_present(bundle: "Bundle") -> bool:
    """State the data type and why the chosen QC tools fit it."""
    return has_word(bundle.text, *DATA_TYPE_TOKENS) and has_word(
        bundle.text, *TOOL_SELECTION_TOKENS
    )


def effect_statistics_documented(bundle: "Bundle") -> bool:
    text = bundle.text
    if has_word(text, *STAT_TEST_TOKENS):
        if has_word(text, "显著"):
            has_p = re.search(r"p\s*[<＜=＝]\s*0?\.\d+", text) is not None
            return has_p or has_word(text, "置信区间")
        return True
    return has_word(text, *STAT_WAIVER_TOKENS)


def effect_benefit_computed(bundle: "Bundle") -> bool:
    text = bundle.text
    cost = has_word(text, "投入", "成本", "费用", "人时", "工时")
    benefit = has_word(text, "效益", "收益", "节省", "节约", "ROI", "回收期", "年化")
    return cost and benefit and len(numbers_in(text)) >= 4


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

    @property
    def tables(self) -> list[tuple[tuple[str, ...], ...]]:
        return [table for slide in self.slides for table in slide.tables]


def _table_with_rows(bundle: Bundle, minimum_rows: int) -> bool:
    return bundle.max_rows >= minimum_rows


THEME = Step(
    number=1,
    phase="主题选定",
    method="主题评价矩阵",
    matcher=lambda slide: has_word(title_text(slide), "主题选定", "主题评价", "主题评审"),
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
        Rule("主题评价规则（权重/评分标准）", theme_rule_documented),
    ),
)

ACTIVITY_PLAN = Step(
    number=2,
    phase="活动计划拟定",
    method="甘特图",
    matcher=lambda slide: has_word(title_text(slide), "活动计划", "甘特图", "计划拟定"),
    rules=(
        Rule("阶段 ≥4", lambda b: count_distinct(b.text, PHASE_WORDS) >= 4),
        Rule(
            "时间轴（周次/日期）",
            lambda b: has_word(b.text, "周", "月", "日期", "时间")
            or re.search(r"\d+\s*(?:周|月|/\d+)", b.text) is not None,
        ),
        Rule("负责人", lambda b: has_word(b.text, "负责人", "责任人", "圈员")),
        Rule("计划 vs 实际进度对照", plan_vs_actual_present),
        Rule(
            "工作项目 ≥6（逐行排十步法工作项，阶段条不算甘特图）",
            plan_work_packages_present,
        ),
    ),
)

CURRENT_STATE = Step(
    number=3,
    phase="现状把握",
    method="现状流程图 + 查检表 + 层别 + 柏拉图",
    matcher=lambda slide: has_word(
        title_text(slide), "现状把握", "现状流程图", "查检表", "层别", "现状｜柏拉图"
    )
    or (has_word(title_text(slide), "柏拉图") and has_word(title_text(slide), "现状")),
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
        Rule("查检表收集方法与责任人", check_sheet_collection_documented),
        Rule("数据与手法选择说明（数据类型 → 工具）", data_tool_rationale_present),
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
        Rule("柏拉图：频次按降序排列", pareto_counts_descending),
        Rule("柏拉图：缺陷合计不超过检查总数", pareto_counts_match_sample),
        Rule("柏拉图：累计百分比单调且收敛到 100%", pareto_cumulative_valid),
        Rule("柏拉图：80% 改善重点覆盖 ≥80%", pareto_focus_covers_80),
    ),
)

TARGET = Step(
    number=4,
    phase="目标设定",
    method="目标值计算 + 目标柱状图",
    matcher=lambda slide: has_word(title_text(slide), "目标设定"),
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
        Rule("参数取值 0–100%", target_params_in_range),
        Rule("目标值方向与指标方向一致", target_direction_consistent),
        Rule("目标值可由公式复算", target_formula_consistent),
    ),
)

ANALYSIS = Step(
    number=5,
    phase="解析",
    method="鱼骨图 + 要因评价 + 真因验证",
    matcher=lambda slide: has_word(
        title_text(slide), "解析", "鱼骨图", "特性要因图", "要因评价", "真因验证", "根因验证"
    ),
    rules=(
        Rule(
            "鱼骨图 5M1E/6M ≥4 维",
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
        Rule("真因验证样本量 ≥30 或说明抽样依据", true_cause_sample_sufficient),
    ),
)

COUNTERMEASURE = Step(
    number=6,
    phase="对策拟定",
    method="对策评价矩阵 + 5W1H + 真因映射",
    matcher=lambda slide: has_word(title_text(slide), "对策拟定", "对策评价", "5W1H", "5W2H"),
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
    matcher=lambda slide: has_word(title_text(slide), "对策实施", "实施跟踪", "实施与检讨"),
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
    matcher=lambda slide: has_word(title_text(slide), "效果确认", "有形成果", "无形成果"),
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
        Rule("无形成果量表（维度/评分范围/前后均值）", intangible_scale_documented),
        Rule("统计检验或豁免说明", effect_statistics_documented),
        Rule("效益核算（成本/效益/回收期）", effect_benefit_computed),
        Rule("改善后优于改善前（方向一致）", effect_direction_improved),
        Rule("目标达成率可由公式复算", effect_attainment_consistent),
        Rule("进步率可由公式复算", effect_progress_consistent),
        Rule("改善后期间与样本量", effect_post_evidence_present),
    ),
)

STANDARDIZATION = Step(
    number=9,
    phase="标准化",
    method="标准化文件 + 日常稽核",
    matcher=lambda slide: has_word(title_text(slide), "标准化"),
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
        Rule("标准化文件编号/版本/生效日期", standardization_versioned),
        Rule("稽核结果回写 / 效果维持", standardization_audit_loop),
    ),
)

REVIEW = Step(
    number=10,
    phase="检讨与改进",
    method="活动检讨 + 下期主题",
    matcher=lambda slide: has_word(title_text(slide), "检讨与改进", "活动检讨", "检讨"),
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


CROSS_STEP = Step(
    number=11,
    phase="跨步骤一致性",
    method="对策↔已验证真因",
    matcher=lambda slide: False,
    rules=(Rule("对策↔已验证真因逐条映射", lambda bundle: True),),
)

ALL_STEPS: tuple[Step, ...] = STEPS + (CROSS_STEP,)


STAT_STEP = Step(
    number=12,
    phase="统计数据复算",
    method="χ² / Welch t 检验（原始数据）",
    matcher=lambda slide: False,
    rules=(Rule("文稿 p 值与原始数据复算一致", lambda bundle: True),),
)


def statistics_check_result(slides: Sequence[SlideView], data_path: Path) -> StepResult | None:
    """Recompute the effect statistics from raw data and compare with the deck."""
    try:
        import qcc_statistics  # same directory as this script
    except ImportError:
        return None
    text = "\n".join(slide.text for slide in slides)
    try:
        raw = data_path.read_text(encoding="utf-8")
        if data_path.suffix.lower() in {".yaml", ".yml"}:
            import yaml

            data = yaml.safe_load(raw)
        else:
            data = json.loads(raw)
        if isinstance(data, dict) and "effect" in data:
            effect = data.get("effect") or {}
            meta = data.get("meta") or {}
            data = {
                "metric": str(meta.get("topic") or "effect"),
                "direction": str(meta.get("direction", "lower")),
                "before": effect.get("before") or {},
                "after": effect.get("after") or {},
                "claimed": effect.get("statistics") or {},
            }
        result = qcc_statistics.evaluate_dataset(data)
    except Exception:  # noqa: BLE001 - invalid data must not crash the checker
        return StepResult(
            STAT_STEP, "WEAK", [], ["原始数据文件无法解析或字段不完整"], []
        )

    claimed_match = re.search(r"p\s*[<＜=＝]\s*(0?\.\d+)", text)
    computed = float(result["p"])
    evidence = [
        f"{result['test']} statistic={result['statistic']:.4f} df={result['df']:.2f} p={computed:.6g}",
        result["conclusion"],
    ]
    if claimed_match:
        claimed = float(claimed_match.group(1))
        operator = claimed_match.group(0).split("p")[1].strip()[0]
        if operator in {"<", "＜", "=", "＝"} and operator in {"=", "＝"}:
            ok = abs(computed - claimed) <= 0.01
        else:
            ok = computed <= claimed + 1e-9
        evidence.append(f"文稿声明 p {claimed}，复算 p {computed:.4g} → {'一致' if ok else '不一致'}")
        return StepResult(
            STAT_STEP, "FOUND" if ok else "WEAK", [], [] if ok else ["文稿 p 值与原始数据复算一致"], evidence
        )
    return StepResult(
        STAT_STEP, "WEAK", [], ["文稿 p 值与原始数据复算一致"], evidence + ["文稿未声明 p 值"]
    )


def cross_check_result(slides: Sequence[SlideView]) -> StepResult:
    causes = verified_causes(slides)
    ok = countermeasure_mapping_ok(slides)
    evidence = [f"已验证真因：{', '.join(causes)}"] if causes else []
    return StepResult(
        CROSS_STEP,
        "FOUND" if ok else "WEAK",
        [],
        [] if ok else ["对策↔已验证真因逐条映射"],
        evidence,
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
    results = [evaluate_step(step, slides) for step in STEPS]
    results.append(cross_check_result(slides))
    return results


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
    parser.add_argument(
        "--data",
        type=Path,
        default=None,
        help="optional raw dataset (qcc-data.yaml/json) for statistics recomputation",
    )
    args = parser.parse_args(argv)

    if not args.pptx.exists():
        print(f"PPTX not found: {args.pptx}", file=sys.stderr)
        return 2

    slides = read_slides(args.pptx)
    results = evaluate(slides)
    if args.data is not None:
        statistics_result = statistics_check_result(slides, args.data)
        if statistics_result is not None:
            results.append(statistics_result)
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
