# qcc-ppt-visual-enhancer v3.9.1

Second-stage visual enhancement skill for QCC presentations: turn an existing baseline
deck into a business-review-ready deck without regenerating business content.

This package is **standalone** — it does not require the baseline producer or the
method-compliant producer to be installed.

## What it contains

| Path | Purpose |
|---|---|
| `SKILL.md` | Agent-facing workflow and hard rules |
| `docs/visual_enhancement_protocol.md` | Enhancement scope and page risk classification |
| `docs/slide_review_checklist.md` | Render-based review checklist |
| `docs/badge_alignment_rules.md` | Circular/rounded badge centering rules |
| `docs/common_failures.md` | Repeatable visual failure patterns |
| `docs/workspace_and_template_boundary.md` | Workspace vs. skill-directory boundary |
| `config/visual_enhancement_profile.yaml` | Enhancement profile |
| `scripts/enhance_qcc_ppt.py` | Deterministic entry: copy + badge centering + report |
| `scripts/center_badge_text.py` | Badge centering repair (`--include-rounded` optional) |
| `scripts/render_check.py` | PPTX → PDF → PNG → montage render gate |
| `scripts/init_workspace.py` | Scaffold `qcc-workspace/` |
| `scripts/selftest_enhancer.py` | Package self-test |
| `templates/` | `qcc-empty-template.pptx`, `template_light_16_9.pptx` |

## Standalone quick start

```bash
pip install -r requirements.txt

python scripts/init_workspace.py --workspace qcc-workspace
# put the baseline deck at qcc-workspace/input/qcc-baseline.pptx

python scripts/enhance_qcc_ppt.py \
  --input qcc-workspace/input/qcc-baseline.pptx \
  --output qcc-workspace/output/qcc-review-ready.pptx \
  --report qcc-workspace/reports/visual-review-report.md

python scripts/render_check.py qcc-workspace/output/qcc-review-ready.pptx \
  --out qcc-workspace/render

python scripts/selftest_enhancer.py
```

## What is automatic vs. agent-driven

- **Automatic (deterministic pass)**: copy the input, center badge text, write a review
  report scaffold, render PDF/PNG.
- **Agent-driven pass**: page risk classification (`PASS` / `REVIEW` / `REDESIGN`) and
  local layout repair, following `docs/visual_enhancement_protocol.md` and
  `docs/slide_review_checklist.md`.

The deterministic pass deliberately never redesigns pages; that keeps it safe to run on
an accepted baseline.

## v3.9.1 fixes

- Repaired the shipped `enhance_qcc_ppt.py` (it raised `SyntaxError` as packaged).
- Added `init_workspace.py`, `selftest_enhancer.py`, `render_check.py`.
- `center_badge_text.py` gained `--include-rounded` for rounded-rectangle badges.
