#!/usr/bin/env python3
"""Detect unfilled placeholders, inherited prompt text, and duplicate template text.

This is an edit-mode structural check. PDF rendering can hide PowerPoint/WPS
placeholder prompts and inherited layout text. Formal decks must not contain:
- slide-level editable placeholders;
- inherited layout/master placeholder prompt text;
- generated text that duplicates template-owned static text, especially end-page
  Thank-you/legal content or agenda title text.
"""
from __future__ import annotations
import argparse
from collections import Counter
from pathlib import Path
from pptx import Presentation

PROMPT_FRAGMENTS = [
    "单击此处添加标题",
    "单击此处添加文本",
    "Click to add title",
    "Click to add text",
    "Click to add subtitle",
    "添加标题",
    "添加文本",
]

END_TEMPLATE_TEXT_FRAGMENTS = [
    "Thank you.",
    "Copyright©2021 Huawei Technologies",
    "Bring digital to every person",
    "把数字世界带入每个人",
]


def normalize(text: str) -> str:
    return " ".join((text or "").split()).strip()


def shape_text(shp) -> str:
    if not getattr(shp, "has_text_frame", False):
        return ""
    try:
        return "\n".join(p.text for p in shp.text_frame.paragraphs).strip()
    except Exception:
        return ""


def iter_layout_shapes(slide):
    layout = slide.slide_layout
    for shp in getattr(layout, "shapes", []):
        yield "layout", shp
    master = getattr(layout, "slide_master", None)
    if master is not None:
        for shp in getattr(master, "shapes", []):
            yield "master", shp


def contains_prompt(txt: str) -> bool:
    return bool(txt and any(frag in txt for frag in PROMPT_FRAGMENTS))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("pptx", type=Path)
    ap.add_argument("--mode", choices=["draft", "formal"], default="formal")
    args = ap.parse_args()

    prs = Presentation(str(args.pptx))
    errors: list[str] = []
    warnings: list[str] = []

    for idx, slide in enumerate(prs.slides, 1):
        slide_texts: list[str] = []
        inherited_texts: list[str] = []

        for shp in slide.shapes:
            txt = normalize(shape_text(shp))
            if txt:
                slide_texts.append(txt)
            is_ph = False
            try:
                is_ph = bool(getattr(shp, "is_placeholder", False))
            except Exception:
                is_ph = False
            if is_ph:
                msg = f"slide {idx}: slide-level editable placeholder remains (shape_id={getattr(shp, 'shape_id', '?')}, text={txt!r})"
                (errors if args.mode == "formal" else warnings).append(msg)
            if contains_prompt(txt):
                msg = f"slide {idx}: slide-level placeholder prompt text remains: {txt!r}"
                (errors if args.mode == "formal" else warnings).append(msg)

        for scope, shp in iter_layout_shapes(slide):
            txt = normalize(shape_text(shp))
            if txt:
                inherited_texts.append(txt)
            is_ph = False
            try:
                is_ph = bool(getattr(shp, "is_placeholder", False))
            except Exception:
                is_ph = False
            if is_ph or contains_prompt(txt):
                msg = f"slide {idx}: inherited {scope} placeholder/prompt remains (shape={getattr(shp, 'name', '?')}, text={txt!r})"
                (errors if args.mode == "formal" else warnings).append(msg)

        inherited_counter = Counter(inherited_texts)
        for txt in slide_texts:
            if txt in inherited_counter:
                msg = f"slide {idx}: generated text duplicates inherited template text: {txt!r}"
                (errors if args.mode == "formal" else warnings).append(msg)

        # End page guard: if the end layout owns Thank-you/legal content, the
        # concrete slide must not add another copy.
        if idx == len(prs.slides):
            for txt in slide_texts:
                if any(frag in txt for frag in END_TEMPLATE_TEXT_FRAGMENTS):
                    msg = f"slide {idx}: generated end-page text duplicates template-owned ending content: {txt!r}"
                    (errors if args.mode == "formal" else warnings).append(msg)

    print(f"PLACEHOLDER LINT: {len(errors)} errors, {len(warnings)} warnings")
    for e in errors:
        print("ERROR:", e)
    for w in warnings:
        print("WARNING:", w)
    if errors:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
