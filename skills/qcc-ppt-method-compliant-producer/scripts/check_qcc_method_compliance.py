#!/usr/bin/env python3
"""Check visible QCC method coverage in a PPTX.

This script is intentionally conservative. It checks whether required method
keywords appear in slide text, especially title-like text. It does not prove
that the visual form is correct; rendered manual inspection is still required.
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from pptx import Presentation


@dataclass(frozen=True)
class RequiredMethod:
    phase: str
    method: str
    keywords: tuple[str, ...]


REQUIRED_METHODS: tuple[RequiredMethod, ...] = (
    RequiredMethod("主题评审", "头脑风暴", ("头脑风暴",)),
    RequiredMethod("主题评审", "亲和图", ("亲和图",)),
    RequiredMethod("主题评审", "检查表", ("检查表",)),
    RequiredMethod("把握现状", "SIPOC", ("SIPOC",)),
    RequiredMethod("把握现状", "柏拉图", ("柏拉图", "80%")),
    RequiredMethod("把握现状", "子流程图", ("子流程图",)),
    RequiredMethod("根因分析", "鱼骨图", ("鱼骨图",)),
    RequiredMethod("根因分析", "矩阵图", ("矩阵图",)),
    RequiredMethod("根因分析", "根因验证", ("根因验证",)),
    RequiredMethod("拟定对策/实施", "5W", ("5W",)),
    RequiredMethod("成果固化", "标准化清单/列表", ("成果固化", "标准化清单", "列表")),
)


def iter_shape_text(shape) -> Iterable[str]:
    if getattr(shape, "has_text_frame", False):
        text = shape.text.strip()
        if text:
            yield text
    if getattr(shape, "has_table", False):
        for row in shape.table.rows:
            for cell in row.cells:
                text = cell.text.strip()
                if text:
                    yield text
    if hasattr(shape, "shapes"):
        for child in shape.shapes:
            yield from iter_shape_text(child)


def slide_texts(prs: Presentation) -> list[str]:
    values: list[str] = []
    for idx, slide in enumerate(prs.slides, start=1):
        chunks: list[str] = []
        for shape in slide.shapes:
            chunks.extend(iter_shape_text(shape))
        values.append(f"[Slide {idx}] " + "\n".join(chunks))
    return values


def keyword_found(slides: list[str], method: RequiredMethod) -> tuple[bool, list[int]]:
    found_pages: list[int] = []
    for idx, text in enumerate(slides, start=1):
        normalized = text.upper()
        if any(keyword.upper() in normalized for keyword in method.keywords):
            found_pages.append(idx)
    return bool(found_pages), found_pages


def build_report(pptx_path: Path, slides: list[str]) -> str:
    lines: list[str] = []
    lines.append("# QCC Method Compliance Report")
    lines.append("")
    lines.append(f"- PPTX: `{pptx_path}`")
    lines.append(f"- Slides: {len(slides)}")
    lines.append("")
    lines.append("## Coverage")
    lines.append("")
    lines.append("| Phase | Method | Status | Slides |")
    lines.append("|---|---|---|---|")

    missing = 0
    for method in REQUIRED_METHODS:
        found, pages = keyword_found(slides, method)
        status = "FOUND" if found else "MISSING"
        if not found:
            missing += 1
        page_text = ", ".join(str(p) for p in pages) if pages else "-"
        lines.append(f"| {method.phase} | {method.method} | {status} | {page_text} |")

    lines.append("")
    lines.append("## Result")
    lines.append("")
    if missing == 0:
        lines.append("PASS: all required QCC method keywords were found in the PPTX text.")
    else:
        lines.append(f"FAIL: {missing} required method item(s) were not found. Add or rebuild the missing method pages before delivery.")

    lines.append("")
    lines.append("## Note")
    lines.append("")
    lines.append("This script checks method keyword coverage only. It does not verify rendered visual form. Render the PPT and inspect the method page shapes before final delivery.")
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("pptx", type=Path)
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()

    if not args.pptx.exists():
        raise FileNotFoundError(f"PPTX not found: {args.pptx}")

    prs = Presentation(str(args.pptx))
    slides = slide_texts(prs)
    report = build_report(args.pptx, slides)

    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(report, encoding="utf-8")
    else:
        print(report)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
