# Changelog

## v2.9.0 - Mandatory QCC Method Format Baseline

### Added

- Mandatory QCC method chain for baseline decks:
  - 主题评审：头脑风暴 -> 亲和图 -> 检查表
  - 把握现状：SIPOC -> 柏拉图（关键 80%） -> 子流程图
  - 根因分析：鱼骨图 + 矩阵图 -> 根因验证
  - 拟定对策 / 实施：5W
  - 成果固化：标准化清单 / 列表
- Formal-review-safe brainstorming layout: left topic anchor + 2×3 candidate cards, no loose radial connectors.
- Formal-review-safe ranking summary card to prevent two-digit scores from wrapping vertically.
- SIPOC, Pareto, subprocess, root-cause matrix, root-cause validation, 5W and standardization checklist slide builders.
- `scripts/check_qcc_method_compliance.py` for mandatory method keyword coverage.
- `scripts/audit_qcc_visual_heuristics.py` for connector clutter and ranking-card risks.
- Additional method docs:
  - `docs/qcc_method_compliance_protocol.md`
  - `docs/qcc_page_contract.md`
  - `docs/qcc_method_visual_patterns.md`
  - `docs/qcc_method_acceptance_checklist.md`
  - `docs/qcc_format_diagnosis_and_repair.md`
  - `docs/qcc_screenshot_feedback_gate.md`

### Changed

- `build_qcc_ppt.py` now generates a method-compliant baseline deck instead of a generic QCC structure only.
- Agenda now explicitly references QCC method chain.
- Topic selection now splits into brainstorming, affinity diagram and checklist/matrix scoring pages.
- Current-state investigation now splits into SIPOC, Pareto and subprocess flow pages.
- Cause analysis now splits into fishbone, matrix and validation pages.
- Countermeasure and implementation now include 5W pages.
- Standardization now includes a dedicated standardization checklist page.
- `examples/qcc-data.example.yaml` now includes optional `qcc_methods` fields.

### Preserved

- Original baseline package boundary.
- `templates/template_light_16_9.pptx`.
- `templates/qcc-empty-template.pptx`.
- `workspace-template/` structure.
- Existing validation, layout lint, placeholder lint and render scripts.

## v2.8.0 - Baseline Template Boundary

### Added

- Clear separation between Skill capability assets and task workspace assets.
- Built-in `templates/qcc-empty-template.pptx` for no-data usage.
- `workspace-template/` skeleton for new users.
- Generic `qcc-data.example.yaml` and `evidence-index.example.yaml`.
- `docs/workspace_and_template_boundary.md`.

### Changed

- Real task data is no longer stored under `input/` in the Skill package.
- `build_qcc_ppt.py` now supports no-data empty-template mode.
- `--template` is optional; the bundled default template is used when no custom template is provided.

### Removed

- Maintainer/self-evolution materials from the low-capability baseline package.
- Project-specific sample input files from the runtime input directory.

### Boundary

This version is for baseline generation only. Advanced visual enhancement and Skill self-evolution are not part of normal usage.
