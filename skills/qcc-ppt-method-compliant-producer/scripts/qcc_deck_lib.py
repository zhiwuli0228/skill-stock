#!/usr/bin/env python3
"""Layout library for the standard QCC ten-step deck.

The library exists so that pages are produced the same way every time, and so
that the defects found in real acceptance review cannot silently come back:

* tables are capped at 6 rows × 6 columns (dense tables are the #1 layout defect);
* every page is checked for text overflow, shape overlap and out-of-bounds shapes
  before the deck is written;
* palette / fonts / grid come from one place, so template colours are preserved.

``build_qcc_deck.py`` is the only consumer; pages must not be hand-rolled.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field

from pptx.chart.data import CategoryChartData
from pptx.dml.color import RGBColor
from pptx.enum.chart import XL_LEGEND_POSITION
from pptx.enum.shapes import MSO_CONNECTOR, MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.oxml.ns import qn
from pptx.util import Emu, Inches, Pt

# palette sampled from templates/qcc-empty-template.pptx
INK = RGBColor(0x23, 0x23, 0x23)
PRIMARY = RGBColor(0x1F, 0x4E, 0x79)
ACCENT = RGBColor(0xC8, 0x10, 0x2E)
GREEN = RGBColor(0x00, 0x99, 0x44)
ORANGE = RGBColor(0xEB, 0x5C, 0x01)
RED = RGBColor(0xC8, 0x10, 0x2E)
GRAY = RGBColor(0x66, 0x66, 0x66)
LIGHT = RGBColor(0xFD, 0xEC, 0xEE)
LIGHT2 = RGBColor(0xFF, 0xFF, 0xFF)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
BORDER = RGBColor(0xDD, 0xDD, 0xDD)
FONT = "微软雅黑"

SLIDE_W = 13.333
SLIDE_H = 7.5
CANVAS_LAYOUT = None

MAX_TABLE_ROWS = 6
MAX_TABLE_COLS = 6
MAX_SHAPES = 70
MAX_CHARS = 600
BODY_MIN_FONT = 9.0

CANVAS_LAYOUT_NAME = "1_Chinese text page"
END_LAYOUT_NAME = "End page"


@dataclass
class Violation:
    slide: int
    kind: str
    detail: str


@dataclass
class DeckReport:
    violations: list[Violation] = field(default_factory=list)

    def add(self, slide: int, kind: str, detail: str) -> None:
        self.violations.append(Violation(slide, kind, detail))

    @property
    def ok(self) -> bool:
        return not self.violations


def set_run_font(run, size=14, bold=False, color=INK, name=FONT):
    font = run.font
    font.size = Pt(size)
    font.bold = bold
    font.color.rgb = color
    font.name = name
    rpr = run._r.get_or_add_rPr()
    for tag in ("a:ea", "a:cs"):
        element = rpr.find(qn(tag))
        if element is None:
            element = rpr.makeelement(qn(tag), {})
            rpr.append(element)
        element.set("typeface", name)


def add_text(slide, x, y, w, h, lines, size=14, bold=False, color=INK,
             align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP, line_spacing=1.15):
    box = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    frame = box.text_frame
    frame.word_wrap = True
    frame.vertical_anchor = anchor
    if not isinstance(lines, list):
        lines = [lines]
    for index, item in enumerate(lines):
        paragraph = frame.paragraphs[0] if index == 0 else frame.add_paragraph()
        paragraph.alignment = align
        paragraph.line_spacing = line_spacing
        if isinstance(item, list):
            for chunk, style in item:
                run = paragraph.add_run()
                run.text = str(chunk)
                set_run_font(
                    run,
                    size=style.get("size", size),
                    bold=style.get("bold", bold),
                    color=style.get("color", color),
                    name=style.get("name", FONT),
                )
        else:
            run = paragraph.add_run()
            run.text = str(item)
            set_run_font(run, size=size, bold=bold, color=color)
    return box


def add_rect(slide, x, y, w, h, fill=None, line=None,
             shape=MSO_SHAPE.ROUNDED_RECTANGLE, line_width=1.0, radius=0.08):
    shp = slide.shapes.add_shape(shape, Inches(x), Inches(y), Inches(w), Inches(h))
    if fill is None:
        shp.fill.background()
    else:
        shp.fill.solid()
        shp.fill.fore_color.rgb = fill
    if line is None:
        shp.line.fill.background()
    else:
        shp.line.color.rgb = line
        shp.line.width = Pt(line_width)
    shp.shadow.inherit = False
    if shape == MSO_SHAPE.ROUNDED_RECTANGLE:
        try:
            shp.adjustments[0] = radius
        except (IndexError, ValueError):
            pass
    return shp


def add_line(slide, x1, y1, x2, y2, color=GRAY, width=1.5, dash=False):
    connector = slide.shapes.add_connector(
        MSO_CONNECTOR.STRAIGHT, Inches(x1), Inches(y1), Inches(x2), Inches(y2)
    )
    connector.line.color.rgb = color
    connector.line.width = Pt(width)
    if dash:
        connector.line.dash_style = 4
    return connector


def add_table(slide, x, y, w, h, headers, rows, col_ratio=None, font_size=11,
              row_height=0.34, header_fill=PRIMARY, report: DeckReport | None = None,
              page: int = 0):
    """Add a table, recording a violation when it exceeds the density limits."""
    if report is not None:
        if len(rows) + 1 > MAX_TABLE_ROWS:
            report.add(page, "dense-table", f"{len(rows) + 1} rows > {MAX_TABLE_ROWS}")
        if len(headers) > MAX_TABLE_COLS:
            report.add(page, "dense-table", f"{len(headers)} cols > {MAX_TABLE_COLS}")
    shape = slide.shapes.add_table(
        len(rows) + 1, len(headers), Inches(x), Inches(y), Inches(w), Inches(h)
    )
    table = shape.table
    if col_ratio:
        total = sum(col_ratio)
        for index, ratio in enumerate(col_ratio):
            table.columns[index].width = Emu(int(Inches(w) * ratio / total))
    for row in table.rows:
        row.height = Inches(row_height)
    for column, header in enumerate(headers):
        cell = table.cell(0, column)
        cell.fill.solid()
        cell.fill.fore_color.rgb = header_fill
        cell.margin_left = Inches(0.07)
        cell.margin_right = Inches(0.05)
        cell.vertical_anchor = MSO_ANCHOR.MIDDLE
        frame = cell.text_frame
        frame.word_wrap = True
        paragraph = frame.paragraphs[0]
        paragraph.alignment = PP_ALIGN.CENTER
        run = paragraph.add_run()
        run.text = str(header)
        set_run_font(run, size=font_size, bold=True, color=WHITE)
    for row_index, row in enumerate(rows, start=1):
        for column, value in enumerate(row):
            cell = table.cell(row_index, column)
            cell.fill.solid()
            cell.fill.fore_color.rgb = WHITE if row_index % 2 == 1 else LIGHT
            cell.margin_left = Inches(0.07)
            cell.margin_right = Inches(0.05)
            cell.vertical_anchor = MSO_ANCHOR.MIDDLE
            frame = cell.text_frame
            frame.word_wrap = True
            paragraph = frame.paragraphs[0]
            paragraph.alignment = PP_ALIGN.LEFT if column == 0 else PP_ALIGN.CENTER
            run = paragraph.add_run()
            run.text = str(value)
            set_run_font(run, size=font_size, bold=False, color=INK)
    return table


def add_chart(slide, x, y, w, h, chart_type, categories, series, legend=True):
    data = CategoryChartData()
    data.categories = categories
    for name, values in series:
        data.add_series(name, values)
    frame = slide.shapes.add_chart(chart_type, Inches(x), Inches(y), Inches(w), Inches(h), data)
    chart = frame.chart
    chart.has_legend = legend
    if legend:
        chart.legend.position = XL_LEGEND_POSITION.BOTTOM
        chart.legend.include_in_layout = False
    chart.font.size = Pt(10)
    chart.font.name = FONT
    return chart


def add_kpi(slide, x, y, w, h, label, value, note="", fill=LIGHT,
            value_color=PRIMARY, value_size=18, accent=None):
    """KPI card. Value and note are auto-fitted so long numbers never overflow."""
    accent = accent or value_color
    value_text = str(value)
    if len(value_text) > 11:
        value_size = max(11.0, value_size * 11.0 / len(value_text))
    note_text = str(note)
    if len(note_text) > 26:
        note_text = note_text[:25] + "…"
    add_rect(slide, x, y, w, h, fill=WHITE, line=BORDER, radius=0.05)
    add_rect(slide, x, y, w, 0.07, fill=accent, radius=0.4)
    add_text(slide, x + 0.15, y + 0.16, w - 0.3, 0.26, label, size=9.5, color=GRAY)
    add_text(slide, x + 0.15, y + 0.42, w - 0.3, 0.45, value_text, size=value_size, bold=True,
             color=value_color)
    if note_text:
        add_text(slide, x + 0.15, y + h - 0.32, w - 0.3, 0.28, note_text, size=9, color=GRAY)


def page(prs, title, number, subtitle=None, footer=""):
    slide = prs.slides.add_slide(CANVAS_LAYOUT)
    add_text(slide, 0.62, 0.40, 11.5, 0.5, title, size=22, bold=True, color=INK,
             anchor=MSO_ANCHOR.MIDDLE)
    add_rect(slide, 0.64, 0.94, 0.9, 0.05, fill=RED, shape=MSO_SHAPE.RECTANGLE)
    if subtitle:
        add_text(slide, 0.64, 1.05, 11.6, 0.3, subtitle, size=10, color=GRAY)
    add_rect(slide, 12.18, 0.40, 0.58, 0.42, fill=RED, radius=0.3)
    add_text(slide, 12.18, 0.40, 0.58, 0.42, f"{number:02d}", size=11, bold=True,
             color=WHITE, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
    if footer:
        add_text(slide, 0.62, 7.10, 11.6, 0.28, footer, size=9, color=GRAY)
    return slide


def takeaway(slide, text, fill=LIGHT):
    add_rect(slide, 0.62, 6.32, 12.1, 0.55, fill=fill, radius=0.08)
    add_rect(slide, 0.62, 6.32, 1.3, 0.55, fill=RED, radius=0.08)
    add_text(slide, 0.62, 6.32, 1.3, 0.55, "结论", size=11, bold=True, color=WHITE,
             align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
    add_text(slide, 2.1, 6.32, 10.4, 0.55, text, size=11, bold=True, color=INK,
             anchor=MSO_ANCHOR.MIDDLE)


# --------------------------------------------------------------------------- #
# self-checks
# --------------------------------------------------------------------------- #
def _iter_shapes(shape):
    yield shape
    if hasattr(shape, "shapes"):
        for child in shape.shapes:
            yield from _iter_shapes(child)


def check_slide(slide, page_number: int, report: DeckReport) -> None:
    boxes = []
    shapes = [shape for shape in slide.shapes]
    if len(shapes) > MAX_SHAPES:
        report.add(page_number, "shape-explosion", f"{len(shapes)} shapes > {MAX_SHAPES}")
    total_chars = 0
    for shape in shapes:
        try:
            left, top = shape.left / 914400, shape.top / 914400
            width, height = shape.width / 914400, shape.height / 914400
        except TypeError:
            continue
        text = shape.text_frame.text.strip() if shape.has_text_frame else ""
        is_table = getattr(shape, "has_table", False) and shape.has_table
        total_chars += len(text)
        if left < -0.02 or top < -0.02 or left + width > SLIDE_W + 0.02 or top + height > SLIDE_H + 0.02:
            report.add(page_number, "out-of-bounds", f"{text[:16] or 'shape'} ({left:.2f},{top:.2f})")
        if text and not is_table:
            boxes.append((left, top, width, height, text))
            estimated = 0.0
            max_size = 0.0
            for paragraph in shape.text_frame.paragraphs:
                line = "".join(run.text for run in paragraph.runs)
                if not line:
                    estimated += 0.4 * 0.2
                    continue
                size = max((run.font.size.pt for run in paragraph.runs if run.font.size), default=12.0)
                max_size = max(max_size, size)
                chars_per_line = max(4.0, (width * 72.0) / (size * 1.02))
                estimated += max(1.0, math.ceil(len(line) / chars_per_line))
            if max_size and estimated * max_size * 1.35 / 72.0 > height * 1.18 + 0.06:
                report.add(page_number, "text-overflow", text[:24])
            if max_size and max_size < BODY_MIN_FONT:
                report.add(page_number, "small-font", f"{max_size:.1f}pt :: {text[:20]}")
    if total_chars > MAX_CHARS:
        report.add(page_number, "too-much-text", f"{total_chars} chars > {MAX_CHARS}")
    for index, first in enumerate(boxes):
        for second in boxes[index + 1:]:
            ix = max(0.0, min(first[0] + first[2], second[0] + second[2]) - max(first[0], second[0]))
            iy = max(0.0, min(first[1] + first[3], second[1] + second[3]) - max(first[1], second[1]))
            if ix * iy > 0.30 * min(first[2] * first[3], second[2] * second[3]) and ix * iy > 0.08:
                report.add(page_number, "overlap", f"{first[4][:16]} × {second[4][:16]}")


def check_deck(prs, report: DeckReport) -> DeckReport:
    for index, slide in enumerate(prs.slides, start=1):
        check_slide(slide, index, report)
    return report
