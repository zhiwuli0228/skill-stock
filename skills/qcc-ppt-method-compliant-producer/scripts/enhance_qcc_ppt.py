#!/usr/bin/env python3
"""Minimal visual-enhancer entry point.

This script intentionally performs deterministic baseline-safe operations only:
1. copy input PPTX to output;
2. optionally run badge-centering logic if center_badge_text.py is available;
3. write a small visual review report placeholder.

Advanced slide redesign should be performed by the visual agent using the rules in docs/.
"""
from __future__ import annotations
import argparse
from pathlib import Path
import shutil
import subprocess
import sys


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', required=True, help='Baseline PPTX path')
    parser.add_argument('--output', required=True, help='Enhanced PPTX output path')
    parser.add_argument('--template', required=False, help='Optional custom template path')
    parser.add_argument('--report', required=False, help='Optional visual review report path')
    args = parser.parse_args()

    inp = Path(args.input)
    out = Path(args.output)
    if not inp.exists():
        raise FileNotFoundError(f'Input PPTX not found: {inp}')
    out.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(inp, out)

    script = Path(__file__).with_name('center_badge_text.py')
    if script.exists():
        try:
            subprocess.run([sys.executable, str(script), str(out), '--output', str(out)], check=False)
        except Exception:
            # Do not fail the pipeline; the visual agent should inspect render output.
            pass

    report = Path(args.report) if args.report else out.parent.parent / 'reports' / 'visual-review-report.md'
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text(
        '# Visual Review Report

'
        '- Input: ' + str(inp) + '
'
        '- Output: ' + str(out) + '
'
        '- Custom template: ' + (str(args.template) if args.template else 'not provided; use default visual reference') + '

'
        'Render the output PPTX and inspect screenshots before delivery.
',
        encoding='utf-8'
    )
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
