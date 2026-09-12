# Changelog

## v3.9.1 - Standalone package repair

- Fixed the broken `scripts/enhance_qcc_ppt.py` entry point (string literals had been
  mangled into real newlines, so the script raised `SyntaxError` as shipped).
- Added `scripts/init_workspace.py` to scaffold `qcc-workspace/` in one command.
- Added `scripts/selftest_enhancer.py`: builds a minimal sample deck, runs the entry
  point, and asserts slide count, badge centering and report generation.
- Added `scripts/render_check.py` (PowerPoint COM on Windows, LibreOffice fallback,
  poppler for PNG) so the skill can complete its own render gate without the baseline
  producer.
- Added `--include-rounded` to `scripts/center_badge_text.py` for rounded-rectangle
  badges; circle-only remains the default.

## v3.9 - Visual Enhancer Template Boundary

- Reframed this package as the second-stage visual enhancer for stronger agents.
- Clarified that real project data must stay in qcc-workspace, not the Skill directory.
- Added default template and empty QCC template as built-in fallback assets.
- Added workspace/template boundary rules.
- Added visual enhancement protocol and slide review checklist.
- Preserved badge alignment governance from v3.8.
- Added minimal `enhance_qcc_ppt.py` entry point for baseline-safe enhancement.
- Explicitly removed self-evolution from beginner/standard execution flow.
