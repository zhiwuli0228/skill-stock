# Changelog

## v5.0 - Standard QCC ten-step analysis chain

- **Breaking**: compliance is no longer "method keywords appear in slide text".
  The checker now validates the standard ten-step QCC chain structurally.
- Added `docs/qcc_methodology.md` (ten-step methodology, tool placement, per-step criteria).
- Rewrote `docs/qcc_method_compliance_protocol.md` with `FOUND / WEAK / MISSING / INCOMPLETE`
  statuses and per-step evidence requirements.
- Rewrote `docs/qcc_page_contract.md` and `docs/qcc_method_acceptance_checklist.md` for the
  ten-step page set and required fields.
- Added visual patterns for 主题评价、甘特图、现状流程图、查检表、层别、目标设定、要因评价、
  真因验证、对策评价矩阵、5W1H、有形成果/无形成果、标准化、检讨与改进.
- Rewrote `scripts/check_qcc_method_compliance.py` to read tables/charts and evaluate
  step-level evidence; placeholders now produce `INCOMPLETE` instead of `PASS`.
- Added `scripts/make_qcc_method_fixtures.py` plus keyword-only / data-complete fixtures and
  `scripts/selftest_qcc_method_compliance.py` as a regression guard.
- Tool placement fixes: 查检表 belongs to 现状把握; SIPOC is background-only; 5W becomes 5W1H
  with a countermeasure evaluation matrix and verified-cause mapping.

## v4.3

- Added ranking-card gate for `TOP` / `TOP 课题摘要` side summaries.
- Added repair rule for vertical score wrapping and note-over-row collisions.
- Added checklist/matrix page local repair pattern based on screenshot feedback.


## v4.2 - Screenshot feedback gate

- Added `docs/qcc_screenshot_feedback_gate.md`.
- Added a hard rule: user-provided rendered screenshots override object-level audit results.
- Added brainstorming-page repair pattern: replace loose radial connector diagrams with a left topic anchor plus 2×3 idea-card grid.
- Added `scripts/audit_qcc_visual_heuristics.py` to flag connector clutter on brainstorming pages.
- Updated method visual patterns and format repair rules with the v4.2 defect pattern.

## v4.1 - Format gate

- Added format diagnosis and local repair workflow.
- Added programmable format audit for dense tables, small fonts, and shape overload.
- Hardened matrix and 5W pages.
