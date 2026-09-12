#!/usr/bin/env python3
"""Create a qcc-workspace/ scaffold for the visual enhancer.

Layout (per docs/workspace_and_template_boundary.md):

    qcc-workspace/
      input/            baseline deck goes here
      input/render/     baseline screenshots (optional)
      template/         optional company template
      output/           enhanced deck
      reports/          visual review report
      render/           exported PDF / PNG / montage
"""
from __future__ import annotations

import argparse
from pathlib import Path


README = """# qcc-workspace

1. Put the baseline deck at `input/qcc-baseline.pptx`.
2. Optionally put a company template at `template/company-template.pptx` and baseline
   screenshots under `input/render/`.
3. Run the enhancer:

```bash
python <skill>/scripts/enhance_qcc_ppt.py \\
  --input input/qcc-baseline.pptx \\
  --output output/qcc-review-ready.pptx \\
  --report reports/visual-review-report.md
python <skill>/scripts/render_check.py output/qcc-review-ready.pptx --out render
```

Real project data stays in this workspace; never copy it into the Skill directory.
"""


def main() -> int:
    parser = argparse.ArgumentParser(description="Scaffold a QCC enhancer workspace.")
    parser.add_argument("--workspace", type=Path, default=Path("qcc-workspace"))
    args = parser.parse_args()

    for relative in ("input", "input/render", "template", "output", "reports", "render"):
        (args.workspace / relative).mkdir(parents=True, exist_ok=True)
    readme = args.workspace / "README.md"
    if not readme.exists():
        readme.write_text(README, encoding="utf-8")
    print(f"workspace ready: {args.workspace.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
