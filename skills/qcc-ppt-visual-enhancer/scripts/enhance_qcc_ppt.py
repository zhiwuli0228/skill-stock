#!/usr/bin/env python3
"""Minimal visual-enhancer entry point.

Deterministic, baseline-safe operations only:
1. copy the input PPTX to the output path;
2. run badge-centering repair (center_badge_text.py) when available;
3. write a visual-review report scaffold.

Advanced slide redesign is performed by the visual agent using the rules in docs/.
"""
from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path


REPORT_TEMPLATE = """# Visual Review Report

- Input: {input_path}
- Output: {output_path}
- Custom template: {template}

## Deterministic pass

- badge centering: {badge_result}

## Agent pass (manual)

Render the output PPTX and inspect screenshots against
`docs/visual_enhancement_protocol.md`, `docs/slide_review_checklist.md` and
`docs/badge_alignment_rules.md`; repair only the pages with clear defects.
"""


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="Baseline PPTX path")
    parser.add_argument("--output", required=True, help="Enhanced PPTX output path")
    parser.add_argument("--template", required=False, help="Optional custom template path")
    parser.add_argument("--report", required=False, help="Optional visual review report path")
    args = parser.parse_args()

    source = Path(args.input)
    target = Path(args.output)
    if not source.exists():
        raise FileNotFoundError(f"Input PPTX not found: {source}")
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)

    badge_result = "skipped"
    badge_script = Path(__file__).with_name("center_badge_text.py")
    if badge_script.exists():
        completed = subprocess.run(
            [sys.executable, str(badge_script), str(target), "--output", str(target)],
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        badge_result = (completed.stdout or completed.stderr or "").strip().replace("\n", "; ")
        if completed.returncode != 0:
            badge_result = f"failed: {badge_result}"

    report = (
        Path(args.report)
        if args.report
        else target.parent.parent / "reports" / "visual-review-report.md"
    )
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text(
        REPORT_TEMPLATE.format(
            input_path=source,
            output_path=target,
            template=args.template or "not provided; use default visual reference",
            badge_result=badge_result,
        ),
        encoding="utf-8",
    )
    print(f"enhanced: {target}")
    print(f"badge: {badge_result}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
