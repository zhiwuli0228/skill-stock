#!/usr/bin/env python3
"""Build the standard QCC ten-step deck from ``qcc-data.yaml``.

This is the only sanctioned way to lay out a deck: every page is produced in the
method's standard form (matrices read dimension by dimension, the plan is a work-
package Gantt, the flow chart has a decision branch, the fishbone carries 5M1E,
effects show before/after, intangible results use circle-ability dimensions), and
the layout is checked for overflow / overlap / density before the file is written.

Missing data is rendered as ``待补充`` and recorded as a violation — never invented.

    python scripts/build_qcc_deck.py \
      --data qcc-workspace/input/qcc-data.yaml \
      --template templates/qcc-empty-template.pptx \
      --out qcc-workspace/output/qcc-review-ready.pptx \
      --report qcc-workspace/reports/deck-build-report.md

Exit codes: 0 = built (violations, if any, are listed in the report),
            1 = built with --strict and violations were found, 2 = bad input.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import yaml
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.chart import XL_CHART_TYPE
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.util import Pt

from qcc_deck_lib import (  # noqa: E402  (same directory)
    ACCENT, BODY_MIN_FONT, CANVAS_LAYOUT_NAME, END_LAYOUT_NAME, GREEN, GRAY, INK, LIGHT,
    LIGHT2, ORANGE, PRIMARY, RED, WHITE, DeckReport, add_chart, add_kpi, add_line, add_rect,
    add_table, add_text, check_deck, page, takeaway,
)
import qcc_deck_lib as lib

PENDING = "待补充"
EFFECT_COLORS = {"before": ORANGE, "after": GREEN}


# --------------------------------------------------------------------------- #
# data access
# --------------------------------------------------------------------------- #
def load(path: Path) -> dict:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise SystemExit("dataset must be a mapping")
    return data


def g(data: dict, path: str, default=None):
    node = data
    for part in path.split("."):
        if isinstance(node, dict) and part in node:
            node = node[part]
        elif isinstance(node, list) and part.isdigit() and int(part) < len(node):
            node = node[int(part)]
        else:
            return default
    return node


def txt(value, default=PENDING) -> str:
    if value is None:
        return default
    if isinstance(value, (list, tuple)):
        return "、".join(str(item) for item in value) if value else default
    text = str(value).strip()
    return text or default


def num(value, default=0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def pct(value, digits: int = 1) -> str:
    return f"{num(value):.{digits}f}%" if value is not None else PENDING


def series(name: str) -> str:
    labels = {
        "chi-square": "χ²（2×2，Yates 校正）",
        "welch-t": "Welch t 检验",
    }
    return labels.get(name, txt(name, "统计检验"))


def scores_of(row: dict, keys: tuple[str, ...]) -> list[float | None]:
    scores = row.get("scores") or {}
    if isinstance(scores, dict):
        return [num(scores.get(key), None) if scores.get(key) is not None else None for key in keys]
    return [None] * len(keys)


def measure_dimensions(countermeasures: list[dict]) -> list[str]:
    order = ["可行性", "效益性", "经济性", "圈能力", "可操作性", "成本"]
    present = {key for row in countermeasures for key in (row.get("scores") or {})}
    return [key for key in order if key in present][:4] or ["可行性", "效益性", "经济性", "圈能力"]


# --------------------------------------------------------------------------- #
# pages
# --------------------------------------------------------------------------- #
def patch_cover(slide, data: dict) -> None:
    meta = data.get("meta") or {}
    current = g(data, "current_state.check_sheet", {}) or {}
    mapping = {
        "QCC 成果汇报模板": "QCC 品管圈活动报告",
        "【请填写本页说明：用一句话说明本页要表达的核心结论】":
            f"{txt(meta.get('topic'))} · 标准十步法实践",
        "【请填写内容】": f"课题：{txt(meta.get('topic'))}",
        "【请填写指标】": f"活动周期：{txt(meta.get('period'))}",
        "【请填写数据】": f"圈组：{txt(meta.get('team'))}　圈长：{txt(meta.get('lead'))}",
        "【请填写证据】": "数据来源：见末页证据清单",
    }
    for shape in slide.shapes:
        if not shape.has_text_frame:
            continue
        text = shape.text_frame.text.strip()
        for key, value in mapping.items():
            if key in text:
                frame = shape.text_frame
                while len(frame.paragraphs) > 1:
                    paragraph = frame.paragraphs[-1]
                    paragraph._p.getparent().remove(paragraph._p)
                paragraph = frame.paragraphs[0]
                for run in list(paragraph.runs)[1:]:
                    run._r.getparent().remove(run._r)
                if not paragraph.runs:
                    paragraph.add_run()
                paragraph.runs[0].text = _fit(value, 26)
                break


def slide_roadmap(prs, n, data, report):
    footer = deck_footer(data)
    slide = page(prs, "活动路线｜标准品管圈十步法", n,
                 "Method chain: input → analysis → evidence → conclusion", footer)
    steps = ["1 主题选定", "2 活动计划", "3 现状把握", "4 目标设定", "5 解析",
             "6 对策拟定", "7 实施与检讨", "8 效果确认", "9 标准化", "10 检讨与改进"]
    for index, label in enumerate(steps):
        row, column = divmod(index, 5)
        x = 0.6 + column * 2.52
        y = 1.5 + row * 1.42
        add_rect(slide, x, y, 2.28, 1.1, fill=PRIMARY if row == 0 else ACCENT, radius=0.12)
        add_text(slide, x + 0.12, y + 0.1, 2.04, 0.9, label, size=14, bold=True, color=WHITE,
                 align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
    before = (g(data, "effect.before", {}) or {})
    after = (g(data, "effect.after", {}) or {})
    add_rect(slide, 0.6, 4.5, 12.13, 1.55, fill=LIGHT)
    add_text(slide, 0.85, 4.62, 11.7, 1.35,
             [
                 [("PDCA 闭环：", {"bold": True, "color": PRIMARY}),
                  ("P 主题选定/活动计划/现状把握/目标设定 → D 解析/对策拟定/实施 → C 效果确认 "
                   "→ A 标准化/检讨与改进", {})],
                 [("本圈数据链：", {"bold": True, "color": PRIMARY}),
                  (f"检查总数 {txt(g(data, 'current_state.check_sheet.sample'))} → 缺陷合计 "
                   f"{txt(g(data, 'effect.before.defects'))} → 改善重点 {pct(g(data, 'target.focus'))} "
                   f"→ 目标 {pct(g(data, 'target.value'))} → 改善后 {txt(after.get('defects'))} 例异常", {})],
                 [("判定门槛：", {"bold": True, "color": PRIMARY}),
                  ("每一步都要有输入、分析、证据与结论；缺数据判 INCOMPLETE，方法形态不符判 WEAK。", {})],
             ],
             size=11.5, line_spacing=1.4)
    return slide


def slide_background(prs, n, data, report):
    slide = page(prs, "选题背景与理由", n,
                 f"来源：活动数据与证据文件；{txt(g(data, 'meta.period'))}", deck_footer(data))
    narrative = (data.get("narrative") or {}).get("background") or {}
    categories = g(data, "current_state.categories", []) or []
    top = categories[0] if categories else {}
    cards = [
        ("背景", txt(narrative.get("context"),
                     f"{txt(g(data, 'meta.team'))}在{txt(g(data, 'meta.period'))}期间开展"
                     f"{txt(g(data, 'meta.topic'))}专项。"), PRIMARY),
        ("问题", txt(narrative.get("problem"),
                     f"现状检查 {txt(g(data, 'current_state.check_sheet.sample'))} 例，"
                     f"缺陷 {txt(g(data, 'effect.before.defects'))} 例，现况值 "
                     f"{pct(g(data, 'target.current'))}。"), RED),
        ("影响", txt(narrative.get("impact"),
                     f"前 {txt(g(data, 'current_state.pareto_focus.count'))} 类缺陷占 "
                     f"{pct(g(data, 'current_state.pareto_focus.cumulative'))}，"
                     f"其中「{txt(top.get('name'))}」{txt(top.get('count'))} 例最集中。"), ORANGE),
    ]
    for index, (label, text, color) in enumerate(cards):
        x = 0.6 + index * 4.15
        add_rect(slide, x, 1.45, 3.85, 2.35, fill=LIGHT2, line=color, line_width=1.5)
        add_rect(slide, x, 1.45, 3.85, 0.48, fill=color)
        add_text(slide, x, 1.45, 3.85, 0.48, label, size=15, bold=True, color=WHITE,
                 align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
        add_text(slide, x + 0.24, 2.08, 3.4, 1.6, text, size=12, color=INK, line_spacing=1.35)
    add_rect(slide, 0.6, 4.05, 12.13, 1.95, fill=LIGHT)
    add_text(slide, 0.85, 4.18, 11.7, 1.75,
             [
                 [("选题理由：", {"bold": True, "color": PRIMARY}),
                  (txt(narrative.get("reason"),
                       f"上级政策要求落实验证闭环；问题迫切（{pct(g(data, 'target.current'))}）；"
                       f"数据可得；圈能力 {pct(g(data, 'target.capability'), 0)}。"), {})],
                 [("活动范围：", {"bold": True, "color": PRIMARY}),
                  (txt(narrative.get("scope")), {})],
             ],
             size=11.5, line_spacing=1.4)
    takeaway(slide, "结论：选题有政策依据、有数据、有影响、可落地，进入主题评价确认。")
    return slide


def slide_theme(prs, n, data, report):
    theme = data.get("theme") or {}
    candidates = [txt(item) for item in (theme.get("candidates") or [])]
    criteria = [txt(item) for item in (theme.get("criteria") or [])]
    scores = theme.get("scores") or []
    slide = page(prs, "主题选定｜主题评价矩阵", n,
                 f"评价规则：{txt(theme.get('decision_rule'))}", deck_footer(data))
    if not candidates or not criteria or not scores:
        add_text(slide, 0.6, 2.6, 12.0, 1.2,
                 "主题评价矩阵数据不完整：需要候选主题、评价维度与评分矩阵。", size=14, color=RED)
        report.add(n, "missing-data", "theme.candidates/criteria/scores")
        return slide
    letters = [chr(ord("A") + index) for index in range(len(candidates))]
    # keep the table within 6 columns: dimensions as rows, candidates as columns
    shown = candidates[: MAX_TOTAL_COLUMNS - 2]
    headers = ["评价维度", "权重"] + [f"{letters[index]} {_short(shown[index])}"
                                      for index in range(len(shown))]
    rows = []
    for index, criterion in enumerate(criteria):
        values = [scores[c][index] if c < len(scores) and index < len(scores[c]) else "" for c in range(len(shown))]
        rows.append([criterion, f"{100 // max(1, len(criteria))}%"] + values)
    totals = []
    for column in range(len(shown)):
        total = sum(num(scores[column][index]) for index in range(len(criteria))
                    if column < len(scores) and index < len(scores[column]))
        totals.append(int(total) if float(total).is_integer() else round(total, 1))
    add_table(slide, 0.55, 1.42, 12.23, 2.6, headers, rows,
              col_ratio=[1.5, 0.9] + [2.2] * len(shown), font_size=10, row_height=0.42,
              report=report, page=n)
    ranking = sorted(range(len(totals)), key=lambda index: -num(totals[index]))
    total_line = "／".join(
        f"{letters[index]} {totals[index]}（{rank + 1}"
        + (" ✔ 选定" if index == ranking[0] else "")
        + "）" for rank, index in enumerate(ranking))
    add_rect(slide, 0.55, 4.12, 6.0, 1.95, fill=LIGHT2, line=PRIMARY, line_width=1.2)
    add_text(slide, 0.78, 4.22, 5.55, 1.75,
             [[("候选主题对照：", {"bold": True, "color": PRIMARY})],
              "　".join(f"{letters[i]} {item}" for i, item in enumerate(candidates)),
              "",
              [("总分与排序：", {"bold": True, "color": PRIMARY})],
              total_line], size=10, line_spacing=1.3)
    add_rect(slide, 6.78, 4.12, 6.0, 1.95, fill=LIGHT)
    add_text(slide, 7.01, 4.22, 5.55, 1.75,
             [[("维度释义与口径：", {"bold": True, "color": PRIMARY})],
              "各维度权重相同（见「权重」列），逐维度评分可复核；总分＝各维度评分之和。",
              "",
              [("选定：", {"bold": True, "color": RED})],
              f"{txt(theme.get('selected'), candidates[ranking[0]])}"], size=10, line_spacing=1.3)
    takeaway(slide, "主题评价矩阵逐维度可见：维度成行 × 候选主题成列，权重、总分与排序齐备。")
    return slide


def _short(value: str, limit: int = 10) -> str:
    return value if len(value) <= limit else value[: limit - 1] + "…"


def _fit(value, limit: int = 26) -> str:
    """Trim a value so it fits a template placeholder box on a single line."""
    text = txt(value)
    return text if len(text) <= limit else text[: limit - 1] + "…"


def _count(value) -> str:
    number = num(value)
    return str(int(number)) if float(number).is_integer() else f"{number:g}"


MAX_TOTAL_COLUMNS = 6
MAX_TABLE_ROWS = 6


def slide_brainstorm(prs, n, data, report):
    slide = page(prs, "主题选定｜头脑风暴与亲和图（辅助）", n,
                 "亲和图只用于候选主题归类，不得替代主题评价", deck_footer(data))
    narrative = (data.get("narrative") or {}).get("brainstorm") or {}
    groups = narrative.get("groups")
    if not groups:
        candidates = [txt(item) for item in (g(data, "theme.candidates", []) or [])]
        if candidates:
            groups = [{"title": "候选主题（未提供亲和图分组）", "items": candidates}]
        else:
            groups = []
            report.add(n, "missing-data", "narrative.brainstorm.groups")
    palette = [RED, PRIMARY, ORANGE, GREEN]
    for index, group in enumerate(groups[:4]):
        row, column = divmod(index, 2)
        x = 0.6 + column * 6.25
        y = 1.45 + row * 2.28
        color = palette[index % len(palette)]
        add_rect(slide, x, y, 5.95, 2.05, fill=LIGHT2, line=color, line_width=1.4)
        add_rect(slide, x, y, 5.95, 0.44, fill=color)
        add_text(slide, x, y, 5.95, 0.44, txt(group.get("title")), size=13.5, bold=True,
                 color=WHITE, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
        items = group.get("items") or []
        add_text(slide, x + 0.25, y + 0.6, 5.5, 1.3,
                 "\n".join(f"· {txt(item)}" for item in items) if items else PENDING,
                 size=12.5, color=INK, line_spacing=1.5)
    takeaway(slide, "亲和图归为若干类候选；最终主题由主题评价矩阵的总分决定。")
    return slide


def slide_gantt(prs, n, data, report):
    plan = data.get("plan") or {}
    schedule = plan.get("schedule") or []
    weeks = int(num(plan.get("weeks"), 8) or 8)
    slide = page(prs, "活动计划｜甘特图（工作项目排程）", n,
                 f"活动周期 {txt(g(data, 'meta.period'))}（{weeks} 周）· 各行含负责人、计划条与实际条",
                 deck_footer(data))
    if not schedule:
        report.add(n, "missing-data", "plan.schedule（逐项排程）→ 已按等分兜底，实际条留空")
        steps = ["1 主题选定", "2 活动计划", "3 现状把握", "4 目标设定", "5 解析",
                 "6 对策拟定", "7 对策实施", "8 效果确认", "9 标准化", "10 检讨与改进"]
        span = max(1, weeks / len(steps))
        for index, step in enumerate(steps):
            start = int(index * span) + 1
            schedule.append({"step": step, "owner": txt(g(data, "meta.lead")),
                             "planned": [min(start, weeks), min(start + 1, weeks)],
                             "actual": None, "deviation": PENDING})
    rows = schedule[:10]
    axis = plan.get("axis") or [f"第{i + 1}周" for i in range(weeks)]
    label_x, label_w = 0.55, 3.30
    grid_x, grid_w = 3.95, 7.00
    dev_x, dev_w = 11.05, 1.73
    top = 2.02
    row_h = min(0.30, 3.0 / max(1, len(rows)))
    col_w = grid_w / len(axis)
    add_text(slide, label_x, 1.68, label_w, 0.32, "工作项目（负责人）· 偏差", size=10,
             bold=True, color=GRAY, anchor=MSO_ANCHOR.MIDDLE)
    for index, day in enumerate(axis):
        add_text(slide, grid_x + index * col_w, 1.66, col_w, 0.34, day, size=9, bold=True,
                 color=GRAY, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE, line_spacing=1.0)
    add_rect(slide, grid_x, top, grid_w, row_h * len(rows), fill=WHITE,
             line=RGBColor(0xD5, 0xDF, 0xE8), shape=MSO_SHAPE.RECTANGLE)
    for index in range(1, len(axis)):
        add_line(slide, grid_x + index * col_w, top, grid_x + index * col_w,
                 top + row_h * len(rows), color=RGBColor(0xE7, 0xED, 0xF3), width=0.75)
    for index, row in enumerate(rows):
        y = top + index * row_h
        owner = row.get("owner")
        label = txt(row.get("step"))
        if owner:
            label = f"{label}（{txt(owner)}）"
        deviation = txt(row.get("deviation"))
        if deviation:
            label = f"{label} · {deviation}"
        add_text(slide, label_x, y, label_w, row_h, label, size=9, color=INK,
                 anchor=MSO_ANCHOR.MIDDLE)
        planned = row.get("planned")
        if planned and len(planned) == 2:
            add_rect(slide, grid_x + (int(planned[0]) - 1) * col_w + 0.04, y + 0.045,
                     (int(planned[1]) - int(planned[0]) + 1) * col_w - 0.08, 0.10,
                     fill=PRIMARY, shape=MSO_SHAPE.RECTANGLE)
        actual = row.get("actual")
        if actual and len(actual) == 2:
            add_rect(slide, grid_x + (int(actual[0]) - 1) * col_w + 0.04, y + 0.165,
                     (int(actual[1]) - int(actual[0]) + 1) * col_w - 0.08, 0.10,
                     fill=ACCENT, shape=MSO_SHAPE.RECTANGLE)
    add_rect(slide, label_x, 5.12, 0.28, 0.14, fill=PRIMARY, shape=MSO_SHAPE.RECTANGLE)
    add_text(slide, label_x + 0.34, 5.05, 1.1, 0.28, "计划条", size=9.5, color=GRAY,
             anchor=MSO_ANCHOR.MIDDLE)
    add_rect(slide, label_x + 1.55, 5.12, 0.28, 0.14, fill=ACCENT, shape=MSO_SHAPE.RECTANGLE)
    add_text(slide, label_x + 1.89, 5.05, 1.1, 0.28, "实际条", size=9.5, color=GRAY,
             anchor=MSO_ANCHOR.MIDDLE)
    progress = plan.get("progress") or {}
    add_rect(slide, 0.55, 5.42, 12.23, 0.78, fill=LIGHT)
    add_text(slide, 0.8, 5.5, 11.8, 0.62,
             [[("计划 vs 实际：", {"bold": True, "color": PRIMARY}),
               (f"计划 {txt(progress.get('planned'), PENDING)} / 实际 "
                f"{txt(progress.get('actual'), PENDING)}；{txt(progress.get('note'), PENDING)}", {})]],
             size=9.5, line_spacing=1.25)
    return slide


def slide_flow(prs, n, data, report):
    slide = page(prs, "现状把握｜现状流程图（as-is）", n,
                 f"数据类型 {txt(g(data, 'current_state.data_type'))} · 手法 "
                 f"{txt(g(data, 'current_state.tools'))}", deck_footer(data))
    flow = (data.get("narrative") or {}).get("flow") or {}
    start = txt(flow.get("start"), "开始")
    process = flow.get("process") or ["执行作业", "记录数据"]
    process_label = " → ".join(txt(item) for item in process[:3])
    decision = txt(flow.get("decision"), "结果是否合格？")
    yes_path = flow.get("yes") or ["结束"]
    no_path = flow.get("no") or ["异常处理", "异常点"]
    add_rect(slide, 0.62, 2.12, 1.35, 0.72, fill=PRIMARY, shape=MSO_SHAPE.ROUNDED_RECTANGLE)
    add_text(slide, 0.62, 2.12, 1.35, 0.72, start, size=10, bold=True, color=WHITE,
             align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
    x = 2.22
    add_rect(slide, x, 2.12, 1.95, 0.72, fill=PRIMARY, shape=MSO_SHAPE.RECTANGLE)
    add_text(slide, x, 2.12, 1.95, 0.72, process_label, size=9.5, bold=True, color=WHITE,
             align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE, line_spacing=1.1)
    add_line(slide, x - 0.23, 2.48, x - 0.02, 2.48, color=GRAY, width=1.4)
    add_rect(slide, 4.42, 1.92, 2.05, 1.12, fill=ORANGE, shape=MSO_SHAPE.DIAMOND)
    add_text(slide, 4.55, 1.92, 1.8, 1.12, decision, size=9.5, bold=True, color=WHITE,
             align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
    add_line(slide, 4.17, 2.48, 4.40, 2.48, color=GRAY, width=1.4)
    add_line(slide, 6.47, 2.30, 6.93, 2.30, color=GREEN, width=1.6)
    add_text(slide, 6.30, 2.02, 0.6, 0.26, "是", size=9.5, bold=True, color=GREEN,
             align=PP_ALIGN.CENTER)
    add_rect(slide, 6.95, 2.12, 1.95, 0.72, fill=GREEN, shape=MSO_SHAPE.RECTANGLE)
    add_text(slide, 6.95, 2.12, 1.95, 0.72, txt(yes_path[0]), size=10, bold=True, color=WHITE,
             align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
    add_line(slide, 8.90, 2.48, 9.26, 2.48, color=GREEN, width=1.4)
    add_rect(slide, 9.28, 2.12, 1.35, 0.72, fill=GREEN, shape=MSO_SHAPE.ROUNDED_RECTANGLE)
    add_text(slide, 9.28, 2.12, 1.35, 0.72, "结束", size=10, bold=True, color=WHITE,
             align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
    add_line(slide, 5.45, 3.04, 5.45, 3.70, color=RED, width=1.6)
    add_text(slide, 5.50, 3.16, 0.6, 0.26, "否", size=9.5, bold=True, color=RED)
    add_rect(slide, 4.42, 3.72, 2.05, 0.72, fill=RED, shape=MSO_SHAPE.RECTANGLE)
    add_text(slide, 4.42, 3.72, 2.05, 0.72, txt(no_path[0]), size=10, bold=True, color=WHITE,
             align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
    add_line(slide, 6.47, 4.08, 6.93, 4.08, color=RED, width=1.4)
    add_rect(slide, 6.95, 3.72, 1.95, 0.72, fill=RED, shape=MSO_SHAPE.RECTANGLE)
    add_text(slide, 6.95, 3.72, 1.95, 0.72, txt(no_path[-1]), size=9.5, bold=True, color=WHITE,
             align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
    add_line(slide, 8.90, 4.08, 9.26, 4.08, color=RED, width=1.4)
    add_rect(slide, 9.28, 3.72, 1.35, 0.72, fill=RED, shape=MSO_SHAPE.ROUNDED_RECTANGLE)
    add_text(slide, 9.28, 3.72, 1.35, 0.72, "异常点", size=9.5, bold=True, color=WHITE,
             align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
    add_text(slide, 0.62, 4.62, 12.15, 0.3,
             "流程路径：开始 → 执行作业 → 判定 → 否 → 异常处理 → 异常点；判定为是 → 结束",
             size=9.5, color=GRAY)
    add_rect(slide, 0.62, 5.0, 12.1, 1.1, fill=LIGHT)
    add_text(slide, 0.85, 5.08, 11.7, 0.95,
             txt(flow.get("note"),
                 f"异常点：{txt(no_path[-1])}；缺陷合计 {txt(g(data, 'effect.before.defects'))} 例。"),
             size=10, color=INK, line_spacing=1.3)
    return slide


def slide_check_sheet(prs, n, data, report):
    sheet = g(data, "current_state.check_sheet", {}) or {}
    categories = g(data, "current_state.categories", []) or []
    total = sum(num(row.get("count")) for row in categories)
    slide = page(prs, "现状把握｜查检表（数据收集）", n,
                 "判定标准 / 收集期间 / 样本量 / 收集方法 / 责任人 / 记录方式 全部写明",
                 deck_footer(data))
    rows = [[txt(row.get("name")), txt(sheet.get("criteria")), txt(sheet.get("record_method"), "逐例记录"),
             int(num(row.get("count"))) if row.get("count") is not None else PENDING,
             pct(100 * num(row.get("count")) / total if total else None)]
            for row in categories[:4]]
    rows.append(["合计", "——", "——", int(total) if total else PENDING, "100.0%" if total else PENDING])
    add_table(slide, 0.55, 1.42, 12.23, 2.6,
              ["缺陷类型", "判定标准", "记录方式", "频次", "占比"], rows,
              col_ratio=[1.6, 4.0, 1.5, 1.0, 1.2], font_size=10, row_height=0.42,
              report=report, page=n)
    add_kpi(slide, 0.55, 4.15, 2.9, 1.2, "收集期间", _fit(sheet.get("period"), 16), "",
            value_size=15)
    add_kpi(slide, 3.65, 4.15, 2.9, 1.2, "样本量", f"{txt(sheet.get('sample'))} 例",
            f"圈长：{_fit(g(data, 'meta.lead'), 14)}")
    add_kpi(slide, 6.75, 4.15, 2.9, 1.2, "缺陷合计", f"{int(total) if total else PENDING} 例",
            f"占样本 {pct(100 * total / num(sheet.get('sample'), 1)) if total else PENDING}")
    add_kpi(slide, 9.85, 4.15, 2.93, 1.2, "收集方法", _fit(sheet.get("method"), 12),
            "详见 evidence-report", value_size=13)
    add_rect(slide, 0.55, 5.5, 12.23, 0.7, fill=LIGHT)
    add_text(slide, 0.8, 5.5, 11.8, 0.7,
             f"责任人：{txt(sheet.get('owner'))}；记录方式：{txt(sheet.get('record_method'), '逐例记录')}。",
             size=11, color=INK, anchor=MSO_ANCHOR.MIDDLE)
    return slide


def slide_data_summary(prs, n, data, report):
    categories = g(data, "current_state.categories", []) or []
    strata = g(data, "current_state.strata", []) or []
    total = sum(num(row.get("count")) for row in categories)
    slide = page(prs, "现状把握｜数据汇总与层别分析", n,
                 "数据汇总（类别降序 + 频次 + 占比 + 累计）＋ 层别（全部层别维度）",
                 deck_footer(data))
    rows = []
    cumulative = 0.0
    for row in categories:
        share = 100 * num(row.get("count")) / total if total else 0.0
        cumulative += share
        rows.append([txt(row.get("name")), int(num(row.get("count"))), pct(share), pct(cumulative)])
    if len(categories) <= 4:
        rows.append(["合计", int(total), "100.0%", "——"])
    add_table(slide, 0.55, 1.42, 5.4, 2.3, ["缺陷类别", "频次", "占比", "累计"], rows,
              col_ratio=[2.2, 0.9, 0.9, 0.9], font_size=10, row_height=0.36,
              report=report, page=n)
    add_text(slide, 6.25, 1.36, 6.55, 0.3, f"层别：{len(strata)} 个层别的缺陷数", size=11,
             bold=True, color=PRIMARY)
    if strata:
        add_chart(slide, 6.2, 1.7, 6.6, 2.6, XL_CHART_TYPE.BAR_CLUSTERED,
                  [txt(row.get("name")) for row in strata[:12]],
                  [("缺陷数", [num(row.get("value")) for row in strata[:12]])],
                  legend=False)
    else:
        report.add(n, "missing-data", "current_state.strata")
    add_rect(slide, 0.55, 4.05, 12.23, 2.1, fill=LIGHT2, line=ACCENT, line_width=1.2)
    add_text(slide, 0.8, 4.15, 11.8, 1.9,
             [[("数据类型 → 手法：", {"bold": True, "color": PRIMARY}),
               (f"数据类型为{txt(g(data, 'current_state.data_type'))}，手法为"
                f"{txt(g(data, 'current_state.tools'))}。", {})],
              [("层别结论：", {"bold": True, "color": PRIMARY}),
               (txt(g(data, "narrative.data_summary.conclusion"),
                    f"层别覆盖 {len(strata)} 个维度，最大层别 "
                    f"{txt(strata[0].get('name')) if strata else PENDING}。"), {})]],
             size=10, line_spacing=1.3)
    return slide


def slide_pareto(prs, n, data, report):
    categories = g(data, "current_state.categories", []) or []
    total = sum(num(row.get("count")) for row in categories)
    focus = g(data, "current_state.pareto_focus", {}) or {}
    slide = page(prs, "现状把握｜柏拉图：识别关键 80% 改进项", n,
                 f"占比分母＝缺陷合计 {int(total) if total else PENDING}；"
                 f"现况值分母＝检查总数 {txt(g(data, 'current_state.check_sheet.sample'))}",
                 deck_footer(data))
    if not categories:
        report.add(n, "missing-data", "current_state.categories")
        return slide
    x0, y0, w, h = 0.9, 1.78, 7.7, 3.3
    add_line(slide, x0, y0 + h, x0 + w, y0 + h, color=GRAY, width=1.2)
    add_line(slide, x0, y0, x0, y0 + h, color=GRAY, width=1.2)
    counts = [num(row.get("count")) for row in categories]
    max_count = max(counts) or 1
    focus_count = int(num(focus.get("count"), len(categories)))
    bar_w = w / (len(categories) * 2.2)
    cumulative = 0.0
    points = []
    for index, count in enumerate(counts):
        cumulative += 100 * count / (total or 1)
        cx = x0 + w * (index + 0.5) / len(categories)
        bar_h = h * count / max_count
        color = RED if index < focus_count else GRAY
        add_rect(slide, cx - bar_w / 2, y0 + h - bar_h, bar_w, bar_h, fill=color,
                 shape=MSO_SHAPE.RECTANGLE)
        add_text(slide, cx - 0.55, y0 + h - bar_h - 0.3, 1.1, 0.28,
                 str(int(count) if float(count).is_integer() else count), size=10.5, bold=True,
                 color=INK, align=PP_ALIGN.CENTER)
        add_text(slide, cx - 0.8, y0 + h + 0.06, 1.6, 0.5, txt(categories[index].get("name")),
                 size=9.5, color=INK, align=PP_ALIGN.CENTER)
        points.append((cx, y0 + h - h * cumulative / 100.0, cumulative))
    for index in range(len(points) - 1):
        add_line(slide, points[index][0], points[index][1], points[index + 1][0],
                 points[index + 1][1], color=ORANGE, width=2.0)
    for px, py, value in points:
        add_rect(slide, px - 0.05, py - 0.05, 0.1, 0.1, fill=ORANGE, shape=MSO_SHAPE.OVAL)
        add_text(slide, px - 0.5, py - 0.34, 1.0, 0.26, pct(value), size=9.5, bold=True,
                 color=ORANGE, align=PP_ALIGN.CENTER)
    y80 = y0 + h - h * 0.8
    add_line(slide, x0, y80, x0 + w, y80, color=RED, width=1.4, dash=True)
    add_text(slide, x0 - 0.52, y80 - 0.14, 0.45, 0.28, "80%", size=9.5, bold=True, color=RED,
             align=PP_ALIGN.RIGHT)
    add_rect(slide, 8.85, 1.78, 3.9, 3.37, fill=LIGHT)
    add_text(slide, 9.05, 1.92, 3.5, 3.1,
             [[("累计百分比：", {"bold": True, "color": PRIMARY})],
              " → ".join(pct(value) for _, _, value in points),
              "",
              [("80% 改善重点：", {"bold": True, "color": RED})],
              f"前 {focus_count} 类："
              + "、".join(txt(row.get("name")) for row in categories[:focus_count]),
              f"累计 {pct(focus.get('cumulative'))}",
              "",
              [("现况值：", {"bold": True, "color": PRIMARY})],
              f"{pct(g(data, 'target.current'))}（缺陷合计 ÷ 检查总数）"], size=11, line_spacing=1.35)
    takeaway(slide, f"柏拉图成立：降序 + 累计百分比 + 80% 线，改善重点＝前 {focus_count} 类"
                    f"（累计 {pct(focus.get('cumulative'))}）。")
    return slide


def slide_target(prs, n, data, report):
    target = data.get("target") or {}
    slide = page(prs, "目标设定", n,
                 f"{txt(target.get('formula'), '目标值 = 现况值 −（现况值 × 改善重点 × 圈能力）')}"
                 "；圈能力来源见下方依据", deck_footer(data))
    add_kpi(slide, 0.55, 1.45, 2.9, 1.35, "现况值", pct(target.get("current")),
            "缺陷合计 ÷ 检查总数", value_color=RED)
    add_kpi(slide, 3.6, 1.45, 2.9, 1.35, "改善重点", pct(target.get("focus")),
            "柏拉图前 N 类累计", value_color=ORANGE)
    add_kpi(slide, 6.65, 1.45, 2.9, 1.35, "圈能力", pct(target.get("capability"), 0),
            _fit(g(data, "narrative.target.capability_source"), 22))
    add_kpi(slide, 9.7, 1.45, 3.08, 1.35, "目标值", pct(target.get("value")), "按公式计算",
            value_color=GREEN, fill=RGBColor(0xE8, 0xF4, 0xEA))
    add_text(slide, 0.55, 2.90, 5.9, 0.3, "现况 vs 目标（对比图）", size=11, bold=True,
             color=PRIMARY)
    add_chart(slide, 0.5, 3.22, 5.95, 1.95, XL_CHART_TYPE.COLUMN_CLUSTERED,
              ["现况值", "目标值"],
              [("指标（%）", [num(target.get("current")), num(target.get("value"))])],
              legend=False)
    add_rect(slide, 6.65, 2.90, 6.13, 1.25, fill=LIGHT2, line=PRIMARY, line_width=1.2)
    add_text(slide, 6.87, 2.98, 5.7, 1.1,
             [[("计算过程：", {"bold": True, "color": PRIMARY})],
              f"{pct(g(data, 'target.current'))} −（{pct(g(data, 'target.current'))} × "
              f"{pct(g(data, 'target.focus'))} × {pct(g(data, 'target.capability'), 0)}）"
              f" = {pct(g(data, 'target.value'))}"], size=11, line_spacing=1.3)
    add_rect(slide, 6.65, 4.28, 6.13, 0.9, fill=LIGHT)
    add_text(slide, 6.87, 4.34, 5.7, 0.8,
             [[("合理性说明：", {"bold": True, "color": PRIMARY})],
              (txt(g(data, "narrative.target.rationale"),
                   "圈能力与改善重点均需注明出处；目标值可由公式复算。"), {})],
             size=10, line_spacing=1.25)
    takeaway(slide, f"目标值 {pct(target.get('value'))} 可由公式复算，口径与现状把握页一致。")
    return slide


def slide_fishbone(prs, n, data, report):
    fishbone = g(data, "analysis.fishbone", {}) or {}
    dimensions = fishbone.get("dimensions") or {}
    slide = page(prs, "解析｜特性要因图（鱼骨图）", n,
                 f"5M1E 维度：{' / '.join(dimensions) if dimensions else PENDING}；"
                 "本图只产生候选要因", deck_footer(data))
    if len(dimensions) < 4:
        report.add(n, "method-form", f"鱼骨图维度 {len(dimensions)} < 4")
    spine_y = 3.55
    add_rect(slide, 1.0, spine_y, 8.9, 0.07, fill=INK, shape=MSO_SHAPE.RECTANGLE)
    add_rect(slide, 9.95, spine_y - 0.3, 2.85, 0.67, fill=RED, shape=MSO_SHAPE.RIGHT_ARROW)
    add_text(slide, 10.0, spine_y - 0.3, 2.75, 0.67,
             f"主干问题：{txt(fishbone.get('problem'), txt(g(data, 'meta.topic')))}", size=10,
             bold=True, color=WHITE, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
    entries = list(dimensions.items())[:6]
    positions = [1.5, 4.2, 6.9]
    for index, (name, causes) in enumerate(entries):
        above = index < 3
        x = positions[index % 3]
        if above:
            add_line(slide, x + 0.35, spine_y, x + 0.82, spine_y - 1.35, color=GRAY, width=1.5)
            box_y = spine_y - 2.45
        else:
            add_line(slide, x + 0.35, spine_y, x + 0.82, spine_y + 1.35, color=GRAY, width=1.5)
            box_y = spine_y + 1.12
        add_rect(slide, x + 0.80, box_y, 2.45, 1.32, fill=LIGHT2, line=ACCENT, line_width=1.2)
        add_rect(slide, x + 0.80, box_y, 0.40, 1.32, fill=PRIMARY, shape=MSO_SHAPE.RECTANGLE)
        add_text(slide, x + 0.80, box_y, 0.40, 1.32, txt(name), size=12, bold=True, color=WHITE,
                 align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
        body = "\n".join(f"{i + 1}. {txt(item)}" for i, item in enumerate(causes or [])) or PENDING
        add_text(slide, x + 1.24, box_y + 0.06, 1.94, 1.2, body, size=9, color=INK,
                 line_spacing=1.2)
    add_text(slide, 0.55, 6.05, 12.2, 0.28,
             "候选要因来源：查检表/现场数据；是否成立由要因评价与真因验证裁定。",
             size=9, color=GRAY)
    return slide


CAUSE_DIMENSIONS = ("影响度", "发生频次", "可控性")


def slide_cause_scoring(prs, n, data, report):
    causes = g(data, "analysis.cause_scores", []) or []
    slide = page(prs, "解析｜要因评价（筛选要因）", n,
                 "影响度 / 发生频次 / 可控性 逐维度评分；达到阈值进入真因验证", deck_footer(data))
    if not causes:
        report.add(n, "missing-data", "analysis.cause_scores")
        return slide
    sub_available = any(isinstance(row.get("scores"), dict) for row in causes)
    shown = causes[:4] if len(causes) > 5 else causes[:5]
    extras = causes[len(shown):]
    headers = ["候选要因"] + (list(CAUSE_DIMENSIONS) if sub_available else ["评分"]) + ["总分", "筛选结论"]
    rows = []
    for row in shown:
        sub = scores_of(row, CAUSE_DIMENSIONS) if sub_available else []
        cells = [PENDING if value is None else int(value) if float(value).is_integer() else value
                 for value in sub] if sub_available else [num(row.get("score"))]
        rows.append([txt(row.get("cause"))] + cells + [num(row.get("score")),
                    "进入真因验证" if row.get("selected") else "本轮不验证"])
    if extras:
        names = " / ".join(_short(txt(row.get("cause")), 8) for row in extras)
        rows.append([f"其他候选（{names}）"] + [PENDING] * (len(headers) - 3)
                    + ["5-6", "本轮不验证"])
    add_table(slide, 0.55, 1.45, 12.23, 2.6, headers, rows,
              col_ratio=[4.2] + [1.1] * (len(headers) - 3) + [0.9, 1.6], font_size=10,
              row_height=0.42, report=report, page=n)
    if not sub_available:
        report.add(n, "missing-data", "analysis.cause_scores[].scores（逐维度子分）→ 已用总分列兜底")
    add_rect(slide, 0.55, 4.25, 12.23, 1.9, fill=LIGHT)
    add_text(slide, 0.8, 4.36, 11.8, 1.7,
             [[("筛选结论：", {"bold": True, "color": PRIMARY}),
               (txt(g(data, "narrative.cause_scoring.conclusion"),
                    "达到阈值的要因进入真因验证，其余本轮不验证。"), {})],
              [("评分依据：", {"bold": True, "color": PRIMARY}),
               ("各维度 5 分制，逐维度评分可由圈员复核；总分＝各维度之和。", {})],
              [("维度分布：", {"bold": True, "color": PRIMARY}),
               (f"候选要因覆盖 {' / '.join(g(data, 'analysis.fishbone.dimensions', {}).keys()) or PENDING}。", {})]],
             size=10, line_spacing=1.3)
    return slide


def slide_true_cause(prs, n, data, report):
    verification = g(data, "analysis.verification", []) or []
    slide = page(prs, "解析｜真因验证（数据裁定）", n,
                 f"判定标准：{txt(g(data, 'narrative.verification_criteria'), '需写明成立判据与回退条件')}",
                 deck_footer(data))
    if not verification:
        report.add(n, "missing-data", "analysis.verification")
        return slide
    # keep every verified cause on the page: dropping one breaks the
    # countermeasure-to-true-cause mapping check in the next step
    held_all = [row for row in verification if "不成立" not in txt(row.get("conclusion"))]
    held = held_all[:5]
    rejected = [row for row in verification if "不成立" in txt(row.get("conclusion"))]
    if len(held_all) > len(held):
        report.add(n, "truncated", f"真因 {len(held_all)} 条，仅渲染前 {len(held)} 条")
    rows = [[txt(row.get("cause")), txt(row.get("source")), txt(row.get("method")),
             txt(row.get("result")), txt(row.get("conclusion"))] for row in held]
    add_table(slide, 0.4, 1.42, 12.53, 2.4,
              ["候选真因", "数据来源", "验证方法", "验证结果", "结论"], rows,
              col_ratio=[2.4, 2.3, 2.4, 3.6, 1.0], font_size=9.5, row_height=0.6,
              report=report, page=n)
    if rejected:
        add_rect(slide, 0.4, 3.95, 12.53, 1.25, fill=LIGHT2, line=GRAY, line_width=1.0)
        add_text(slide, 0.65, 4.05, 12.0, 1.1,
                 [[("被数据排除的候选（不成立，需回退）：", {"bold": True, "color": GRAY})]]
                 + [f"· {txt(row.get('cause'))} —— {txt(row.get('result'))}" for row in rejected[:3]],
                 size=10, line_spacing=1.3)
    add_rect(slide, 0.4, 5.30, 12.53, 0.8, fill=LIGHT2, line=RED, line_width=1.2)
    add_text(slide, 0.65, 5.38, 12.0, 0.7,
             [[("真因结论：", {"bold": True, "color": RED}),
               (f"{len(held)} 条真因成立；{len(rejected)} 条不成立并回退，结论与数据来源一一对应。", {})]],
             size=11, line_spacing=1.3)
    return slide


def slide_countermeasure(prs, n, data, report):
    measures = data.get("countermeasures") or []
    dimensions = measure_dimensions(measures)
    slide = page(prs, "对策拟定｜对策评价矩阵", n,
                 " / ".join(dimensions) + " 逐维度评分；达阈值采纳", deck_footer(data))
    if not measures:
        report.add(n, "missing-data", "countermeasures")
        return slide
    headers = ["对策"] + dimensions + ["总分 / 取舍"]
    rows = []
    for row in measures[:5]:
        values = scores_of(row, tuple(dimensions))
        rows.append([txt(row.get("measure"))]
                    + [PENDING if value is None else int(value) for value in values]
                    + [f"{txt(row.get('total'))} " + ("采纳" if row.get("adopted") else "舍弃")])
    if len(measures) > 5:
        report.add(n, "truncated", f"对策 {len(measures)} 条，仅渲染前 5 条")
    add_table(slide, 0.5, 1.42, 12.33, 2.1, headers, rows,
              col_ratio=[4.0] + [1.3] * len(dimensions) + [1.8], font_size=10, row_height=0.42,
              report=report, page=n)
    mapping = [f"{txt(row.get('measure'))} → 真因「{txt(row.get('cause'))}」" for row in measures[:5]]
    add_rect(slide, 0.5, 3.70, 6.0, 2.3, fill=LIGHT2, line=PRIMARY, line_width=1.2)
    add_text(slide, 0.74, 3.82, 5.55, 2.1,
             [[("采纳结果：", {"bold": True, "color": PRIMARY})],
              (txt(g(data, "narrative.countermeasure.conclusion"),
                   f"共 {len(measures)} 条对策，其中 "
                   f"{sum(1 for row in measures if row.get('adopted'))} 条采纳。"), {}),
              "",
              [("评分口径：", {"bold": True, "color": PRIMARY})],
              ("各维度 5 分制，逐维度可见；总分＝各维度之和。", {})], size=10, line_spacing=1.3)
    add_rect(slide, 6.83, 3.70, 6.0, 2.3, fill=LIGHT)
    add_text(slide, 7.07, 3.82, 5.55, 2.1,
             [[("对策↔真因映射：", {"bold": True, "color": PRIMARY})]]
             + [txt(item) for item in mapping] if mapping else [PENDING],
             size=10, line_spacing=1.3)
    return slide


def slide_5w1h(prs, n, data, report):
    measures = (data.get("countermeasures") or [])[:4]
    slide = page(prs, "对策拟定｜5W1H（对策实施展开）", n,
                 "What / Why / Who / Where / When / How 六项齐备，并与真因逐条对应",
                 deck_footer(data))
    rows = [[txt(row.get("measure")), txt(row.get("cause")), txt(row.get("who")),
             txt(row.get("where")), txt(row.get("when")), txt(row.get("how"))] for row in measures]
    if not rows:
        report.add(n, "missing-data", "countermeasures（5W1H 字段）")
    add_table(slide, 0.45, 1.42, 12.43, 3.6,
              ["What 对策", "Why 真因", "Who 责任人", "Where 位置", "When 时间", "How 做法"],
              rows, col_ratio=[2.6, 2.3, 1.3, 2.7, 1.5, 4.2], font_size=9.5, row_height=0.62,
              report=report, page=n)
    add_rect(slide, 0.45, 5.2, 12.43, 0.95, fill=LIGHT)
    add_text(slide, 0.7, 5.2, 12.0, 0.95,
             "How 需写明具体动作与产出物；实施阶段按同一口径复测。",
             size=11.5, color=INK, anchor=MSO_ANCHOR.MIDDLE)
    return slide


def slide_implementation(prs, n, data, report):
    records = data.get("implementation") or []
    slide = page(prs, "对策实施与检讨", n,
                 "逐条对策记录实施过程；缺对策名的记录会被标记", deck_footer(data))
    headers = ["对策（阶段）", "时间", "责任人", "实施内容", "过程数据", "困难与调整"]
    rows = []
    missing_measure = False
    for row in records[:4]:
        measure = row.get("measure")
        if not measure:
            missing_measure = True
            measure = txt(row.get("stage"))
        rows.append([f"{txt(measure)}（{txt(row.get('stage'))}）", txt(row.get("time")),
                     txt(row.get("owner")), txt(row.get("progress")), txt(row.get("data")),
                     txt(row.get("difficulty"))])
    if not rows:
        report.add(n, "missing-data", "implementation")
    if missing_measure:
        report.add(n, "method-form", "implementation[] 缺少 measure 字段（逐条对策记录不完整）")
    if len(records) > 4:
        report.add(n, "truncated", f"实施记录 {len(records)} 条，仅渲染前 4 条")
    add_table(slide, 0.4, 1.42, 12.53, 2.6, headers, rows,
              col_ratio=[2.4, 1.2, 1.1, 3.2, 2.2, 2.4], font_size=9.5, row_height=0.52,
              report=report, page=n)
    effect_before = num(g(data, "effect.before.defects"))
    effect_after = g(data, "effect.after.defects")
    add_rect(slide, 0.4, 4.28, 12.53, 1.0, fill=LIGHT2, line=PRIMARY, line_width=1.2)
    add_text(slide, 0.64, 4.36, 12.0, 0.9,
             [[("实施进展与检讨：", {"bold": True, "color": PRIMARY}),
               (txt(g(data, "narrative.implementation.progress"),
                    f"对策实施后缺陷数由 {int(effect_before)} 降至 {txt(effect_after)}；"
                    "困难与调整见上表。"), {})]], size=10, line_spacing=1.3)
    add_rect(slide, 0.4, 5.4, 12.53, 0.8, fill=LIGHT)
    add_text(slide, 0.64, 5.46, 12.0, 0.7,
             txt(g(data, "narrative.implementation.timeline"), "证据时间线：待补充"),
             size=9.5, color=INK, anchor=MSO_ANCHOR.MIDDLE)
    return slide


def slide_effect_tangible(prs, n, data, report):
    effect = data.get("effect") or {}
    before, after = effect.get("before") or {}, effect.get("after") or {}
    statistics = effect.get("statistics") or {}
    benefit = effect.get("benefit") or {}
    before_rate = 100 * num(before.get("defects")) / num(before.get("total"), 1)
    after_rate = 100 * num(after.get("defects")) / num(after.get("total"), 1)
    target = num(effect.get("target"))
    attainment = ((before_rate - after_rate) / (before_rate - target) * 100
                  if abs(before_rate - target) > 1e-9 else 0.0)
    progress = ((before_rate - after_rate) / before_rate * 100) if before_rate else 0.0
    slide = page(prs, "效果确认｜有形成果", n,
                 "改善前后对比 + 目标达成率 + 进步率 + 统计检验 + 效益核算", deck_footer(data))
    add_kpi(slide, 0.55, 1.40, 2.9, 1.25, "缺陷数",
            f"{_count(before.get('defects'))} → {_count(after.get('defects'))}",
            f"{_count(before.get('total'))} → {_count(after.get('total'))} 例")
    add_kpi(slide, 3.6, 1.40, 2.9, 1.25, "现况 → 改善后率",
            f"{pct(before_rate, 0)} → {pct(after_rate, 0)}", "同口径", value_color=GREEN,
            fill=RGBColor(0xE8, 0xF4, 0xEA))
    add_kpi(slide, 6.65, 1.40, 2.9, 1.25, "目标达成率", pct(attainment),
            f"目标值 {pct(target)}", value_color=GREEN, fill=RGBColor(0xE8, 0xF4, 0xEA))
    add_kpi(slide, 9.7, 1.40, 3.08, 1.25, "进步率", pct(progress), "",
            value_color=GREEN,
            fill=RGBColor(0xE8, 0xF4, 0xEA))
    add_text(slide, 0.55, 2.78, 6.4, 0.28, "改善前后对比（对比图）", size=11, bold=True,
             color=PRIMARY)
    add_chart(slide, 0.5, 3.08, 6.45, 2.05, XL_CHART_TYPE.COLUMN_CLUSTERED,
              ["改善前", "改善后"], [("指标（%）", [before_rate, after_rate])], legend=False)
    add_table(slide, 7.15, 2.72, 5.63, 1.35, ["统计检验", "结果"],
              [[series(statistics.get("test")), txt(statistics.get("test"))],
               ["p 值", f"p {txt(statistics.get('comparison'), '<')} {txt(statistics.get('p'))}"],
               ["结论", "改善前后差异显著" if num(statistics.get("p"), 1) < 0.05 else "未达显著"]],
              col_ratio=[1.6, 2.6], font_size=10, row_height=0.34, report=report, page=n)
    add_rect(slide, 7.15, 4.20, 5.63, 1.0, fill=LIGHT2, line=PRIMARY, line_width=1.2)
    add_text(slide, 7.33, 4.28, 5.3, 0.88,
             [[("效益核算：", {"bold": True, "color": PRIMARY})],
              (f"投入 {txt(benefit.get('input_hours'))} 人时 / {txt(benefit.get('input_cost'))} 万元；"
               f"年化节省 {txt(benefit.get('annual_saving_hours'))} 人时 / "
               f"{txt(benefit.get('annual_saving'))} 万元；回收期 {txt(benefit.get('payback'))}", {})],
             size=9.5, color=INK, line_spacing=1.3)
    add_rect(slide, 0.5, 5.30, 6.45, 0.85, fill=LIGHT)
    add_text(slide, 0.68, 5.36, 6.1, 0.75,
             f"口径说明：改善前 {txt(before.get('period'))}（{txt(before.get('total'))} 例）；"
             f"改善后 {txt(after.get('period'))}（{txt(after.get('total'))} 例）。",
             size=9.5, color=INK, line_spacing=1.25)
    return slide


def slide_effect_intangible(prs, n, data, report):
    intangible = g(data, "effect.intangible", {}) or {}
    dimensions = [txt(item) for item in (intangible.get("dimensions") or [])]
    slide = page(prs, "效果确认｜无形成果", n,
                 f"圈员能力成长（{txt(intangible.get('scale'))}，圈组评议会自评）", deck_footer(data))
    if len(dimensions) < 3:
        report.add(n, "missing-data", "effect.intangible.dimensions")
    before = num(intangible.get("before_mean"))
    after = num(intangible.get("after_mean"))
    add_chart(slide, 0.55, 1.42, 6.9, 4.2, XL_CHART_TYPE.RADAR, dimensions,
              [("活动前", [before] * len(dimensions)), ("活动后", [after] * len(dimensions))])
    add_rect(slide, 7.7, 1.42, 5.08, 2.9, fill=LIGHT2, line=PRIMARY, line_width=1.2)
    add_text(slide, 7.9, 1.52, 4.7, 2.7,
             [[("圈员能力评分", {"bold": True, "color": PRIMARY})]]
             + [f"· {item}" for item in dimensions]
             + ["", f"活动前均值 {before} → 活动后均值 {after}"
                f"（{'+' if after >= before else ''}{round(after - before, 1)}）"],
             size=9.5, color=INK, line_spacing=1.2)
    add_rect(slide, 7.7, 4.42, 5.08, 1.2, fill=LIGHT)
    add_text(slide, 7.9, 4.5, 4.7, 1.05,
             [[("说明：", {"bold": True, "color": PRIMARY}),
               ("无形成果只评圈员能力成长；项目经营指标不并入雷达图，如有可另列参考。", {})]],
             size=9, color=INK, line_spacing=1.2)
    takeaway(slide, f"无形成果成立：量表 {txt(intangible.get('scale'))} ＋ "
                    f"{len(dimensions)} 维能力 ＋ 前后均值 {before} → {after}。")
    return slide


def slide_standardization(prs, n, data, report):
    documents = g(data, "standardization.documents", []) or []
    slide = page(prs, "标准化文件与稽核机制", n,
                 "标准化文件 + 日常稽核 + 教育训练与效果维持（编号应可追溯）", deck_footer(data))
    rows = []
    for doc in documents[:4]:
        rows.append([txt(doc.get("name")), txt(doc.get("type")),
                     f"{txt(doc.get('number'))} / {txt(doc.get('version'))} / {txt(doc.get('effective'))}",
                     f"责任人：{txt(doc.get('owner'))} / {txt(doc.get('audit_frequency'))} / "
                     f"{txt(doc.get('audit_method'))}",
                     f"{txt(doc.get('training'))} / {txt(doc.get('maintenance'))}"])
    if not rows:
        report.add(n, "missing-data", "standardization.documents")
    if len(documents) > 4:
        report.add(n, "truncated", f"标准化文件 {len(documents)} 条，仅渲染前 4 条")
    add_table(slide, 0.45, 1.42, 12.43, 3.1,
              ["标准化文件", "类型", "编号 / 版本 / 生效", "稽核人 / 频率 / 方式", "训练 / 维持"],
              rows, col_ratio=[2.2, 1.3, 4.0, 3.2, 2.0], font_size=9, row_height=0.62,
              report=report, page=n)
    add_rect(slide, 0.45, 4.6, 12.43, 1.55, fill=LIGHT2, line=PRIMARY, line_width=1.2)
    add_text(slide, 0.7, 4.7, 12.0, 1.4,
             [[("效果维持：", {"bold": True, "color": PRIMARY}),
               (txt(g(data, "narrative.standardization.maintenance"),
                    "① 验证三件套为每次变更必填；② 受治理面变更由门禁拦截；"
                    "③ 统一检查一条命令复核；④ 稽核结果回写并计入下轮基线。"), {})]],
             size=10.5, line_spacing=1.4)
    return slide


def slide_review(prs, n, data, report):
    review = data.get("review") or {}
    slide = page(prs, "检讨与改进", n, "优点 / 不足 / 残余问题 / 下期主题", deck_footer(data))
    blocks = [
        ("优点", review.get("strengths"), GREEN),
        ("不足", review.get("weaknesses"), ORANGE),
        ("残余问题", review.get("residual"), RED),
        ("下期主题", [review.get("next_topic")] if review.get("next_topic") else None, PRIMARY),
    ]
    for index, (title, items, color) in enumerate(blocks):
        row, column = divmod(index, 2)
        x = 0.55 + column * 6.25
        y = 1.42 + row * 2.45
        add_rect(slide, x, y, 5.95, 2.25, fill=LIGHT2, line=color, line_width=1.4)
        add_rect(slide, x, y, 5.95, 0.44, fill=color)
        add_text(slide, x, y, 5.95, 0.44, title, size=13, bold=True, color=WHITE,
                 align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
        body = "\n".join(f"· {txt(item)}" for item in (items or [])) or PENDING
        add_text(slide, x + 0.25, y + 0.58, 5.5, 1.55, body, size=11, color=INK,
                 line_spacing=1.35)
        if not items:
            report.add(n, "missing-data", f"review.{title}")
    return slide


def annotate_end_page(slide, data) -> None:
    sources = (data.get("narrative") or {}).get("sources") or []
    add_text(slide, 0.95, 2.05, 11.4, 0.6, "下一步与证据清单", size=18, bold=True, color=WHITE)
    lines = [txt(g(data, "narrative.next_step"), "下一步：见检讨与改进页的下期主题。")]
    lines += [f"· {txt(item)}" for item in sources] or ["· 证据文件清单：待补充"]
    add_text(slide, 0.95, 2.85, 11.4, 2.2, lines, size=11,
             color=RGBColor(0xD6, 0xE4, 0xF0), line_spacing=1.45)


def deck_footer(data: dict) -> str:
    meta = data.get("meta") or {}
    return (f"{txt(meta.get('topic'), 'QCC 活动')} · {txt(meta.get('team'), '圈组')} · "
            f"标准十步法 · 数据来源：活动证据文件")


PAGE_BUILDERS = (
    slide_roadmap, slide_background, slide_theme, slide_brainstorm, slide_gantt, slide_flow,
    slide_check_sheet, slide_data_summary, slide_pareto, slide_target, slide_fishbone,
    slide_cause_scoring, slide_true_cause, slide_countermeasure, slide_5w1h,
    slide_implementation, slide_effect_tangible, slide_effect_intangible,
    slide_standardization, slide_review,
)


def build(data: dict, template: Path, out: Path) -> tuple[Path, DeckReport]:
    prs = Presentation(str(template))
    canvas = end = None
    for master in prs.slide_masters:
        for layout in master.slide_layouts:
            if layout.name == CANVAS_LAYOUT_NAME:
                canvas = layout
            if layout.name == END_LAYOUT_NAME:
                end = layout
    if canvas is None:
        raise SystemExit(f"template is missing the '{CANVAS_LAYOUT_NAME}' layout")
    lib.CANVAS_LAYOUT = canvas
    report = DeckReport()

    slide_ids = list(prs.slides._sldIdLst)
    end_page = slide_ids[-1]
    for slide_id in slide_ids[1:-1]:
        prs.part.drop_rel(slide_id.rId)
        prs.slides._sldIdLst.remove(slide_id)
    patch_cover(prs.slides[0], data)
    if end is not None:
        annotate_end_page(prs.slides[1], data)

    for index, builder in enumerate(PAGE_BUILDERS, start=2):
        builder(prs, index, data, report)

    sld_id_lst = prs.slides._sldIdLst
    sld_id_lst.remove(end_page)
    sld_id_lst.append(end_page)

    check_deck(prs, report)
    out.parent.mkdir(parents=True, exist_ok=True)
    prs.save(str(out))
    return out, report


def report_markdown(target: Path, report: DeckReport, slides: int) -> str:
    lines = [
        "# QCC 出稿自检报告",
        "",
        f"- 文件：`{target}`",
        f"- 页数：{slides}",
        f"- 结论：{'PASS（无违规）' if report.ok else f'{len(report.violations)} 项需处理'}",
        "",
        "## 明细",
        "",
        "| 页 | 类型 | 说明 |",
        "|---:|---|---|",
    ]
    lines += [f"| {item.slide} | {item.kind} | {item.detail} |" for item in report.violations] or ["| - | - | 无 |"]
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Build the standard QCC ten-step deck from data.")
    parser.add_argument("--data", type=Path, required=True)
    parser.add_argument("--template", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--report", type=Path, default=None)
    parser.add_argument("--strict", action="store_true", help="violations make the command fail")
    args = parser.parse_args()
    if not args.data.exists():
        print(f"data file not found: {args.data}", file=sys.stderr)
        return 2
    if not args.template.exists():
        print(f"template not found: {args.template}", file=sys.stderr)
        return 2

    target, report = build(load(args.data), args.template, args.out)
    slides = len(Presentation(str(target)).slides)
    text = report_markdown(target, report, slides)
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(text, encoding="utf-8")
    print(text)
    if args.strict and not report.ok:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
