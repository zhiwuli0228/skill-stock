#!/usr/bin/env python3
"""Heuristic visual-risk audit for QCC PPT pages.

This does not replace rendered screenshot review. It catches patterns that the
basic format audit misses, especially free-form connector clutter on method
pages such as brainstorming, fishbone, and flowcharts.
"""
from __future__ import annotations

import argparse
from pathlib import Path
from pptx import Presentation
from pptx.enum.shapes import MSO_SHAPE_TYPE

EMU_PER_INCH = 914400


def emu_to_in(v: int) -> float:
    return float(v) / EMU_PER_INCH


def first_title(slide) -> str:
    for shape in slide.shapes:
        if getattr(shape, 'has_text_frame', False):
            txt = shape.text.strip().replace('\n', ' ')
            if txt and 'Huawei Confidential' not in txt and not txt.isdigit():
                return txt
    return ''


def bbox(shape):
    return (emu_to_in(shape.left), emu_to_in(shape.top), emu_to_in(shape.left + shape.width), emu_to_in(shape.top + shape.height))


def overlaps(a, b, pad=0.0) -> bool:
    ax1, ay1, ax2, ay2 = a
    bx1, by1, bx2, by2 = b
    return not (ax2 + pad < bx1 or bx2 + pad < ax1 or ay2 + pad < by1 or by2 + pad < ay1)


def audit(pptx: Path):
    prs = Presentation(str(pptx))
    rows = []
    for idx, slide in enumerate(prs.slides, 1):
        title = first_title(slide)
        connectors = []
        text_boxes = []
        card_like = []
        for shape in slide.shapes:
            st = shape.shape_type
            if st == MSO_SHAPE_TYPE.LINE:
                connectors.append(shape)
            if getattr(shape, 'has_text_frame', False) and shape.text.strip():
                text_boxes.append(shape)
            # large rounded/rect objects as card candidates
            try:
                w = emu_to_in(shape.width); h = emu_to_in(shape.height)
                if w > 1.8 and 0.6 < h < 1.8:
                    card_like.append(shape)
            except Exception:
                pass
        risks = []
        if '头脑风暴' in title and len(connectors) >= 4:
            risks.append(f'brainstorm connector clutter: {len(connectors)} connector lines')
        if '头脑风暴' in title and card_like:
            # If connector bbox overlaps many text boxes/card boxes, flag. This is conservative.
            line_hits = 0
            for line in connectors:
                lb = bbox(line)
                for t in text_boxes:
                    if overlaps(lb, bbox(t), pad=0.02):
                        line_hits += 1
                        break
            if line_hits >= 2:
                risks.append(f'connector/text overlap risk: {line_hits} line boxes touch text zones')
        # Ranking side-card risks: narrow two-digit score boxes often wrap after rendering.
        if any(getattr(t, 'has_text_frame', False) and 'TOP' in t.text for t in text_boxes):
            for t in text_boxes:
                txt = t.text.strip().replace(' ', '')
                try:
                    w = emu_to_in(t.width)
                except Exception:
                    w = 99
                if txt in {'24','20','18','16','15','12','10'} and w < 0.42:
                    risks.append(f'ranking score wrap risk: score `{txt}` box width {w:.2f}in')
            note_hits = [t for t in text_boxes if '排序作为' in t.text or '决策摘要' in t.text]
            if note_hits:
                # Flag note texts placed high inside the TOP card area rather than below it.
                for n in note_hits:
                    x1, y1, x2, y2 = bbox(n)
                    if y1 < 3.75:
                        risks.append('ranking note collision risk: explanatory note is inside compact TOP card area')
                        break
        if risks:
            rows.append({'slide': idx, 'title': title, 'risks': risks})
    return rows


def write_report(pptx: Path, report: Path, rows):
    lines = ['# QCC Visual Heuristics Audit Report', '', f'- PPTX: `{pptx}`', f'- Slides with heuristic visual risk: {len(rows)}', '']
    if not rows:
        lines += ['PASS: no heuristic connector-clutter risks found. Rendered screenshot review is still required.']
    else:
        lines += ['| Slide | Title | Risks |', '|---:|---|---|']
        for row in rows:
            lines.append(f"| {row['slide']} | {row['title'].replace('|','/')} | {'<br>'.join(row['risks'])} |")
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text('\n'.join(lines), encoding='utf-8')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('pptx', type=Path)
    ap.add_argument('--report', type=Path, default=Path('qcc-visual-heuristics-report.md'))
    args = ap.parse_args()
    rows = audit(args.pptx)
    write_report(args.pptx, args.report, rows)
    print(f'Wrote {args.report}; visual_risk_slides={len(rows)}')


if __name__ == '__main__':
    main()
