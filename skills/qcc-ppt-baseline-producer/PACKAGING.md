# Packaging Notes - v2.9

This package is based on `qcc-ppt-production-skill-v2.8-baseline-template-boundary`.

## What changed

Only capability assets were updated. The baseline template boundary is preserved.

- `templates/` preserved.
- `workspace-template/` preserved.
- Existing scripts preserved.
- QCC method-format docs and checks added.
- `build_qcc_ppt.py` upgraded to generate mandatory QCC method pages.

## Local smoke test

The packaged generator was smoke-tested with `examples/qcc-data.example.yaml`.

```bash
python scripts/build_qcc_ppt.py examples/qcc-data.example.yaml --output /tmp/test.pptx
python scripts/layout_lint.py /tmp/test.pptx --mode formal
python scripts/placeholder_lint.py /tmp/test.pptx --mode formal
python scripts/check_qcc_method_compliance.py /tmp/test.pptx --report /tmp/qcc-method-compliance-report.md
python scripts/audit_qcc_visual_heuristics.py /tmp/test.pptx --report /tmp/qcc-visual-heuristics-report.md
python scripts/render_check.py /tmp/test.pptx --out /tmp/render
```

Expected result:

- Method compliance: PASS.
- Visual heuristic risks: 0.
- Layout lint: 0 errors, 0 warnings.
- Placeholder lint: 0 errors.

## Archive Naming

Canonical archive package: `qcc-ppt-baseline-producer.zip`

Canonical top-level directory: `qcc-ppt-baseline-producer/`

The package preserves the complete baseline Skill assets: `docs/`, `config/`, `scripts/`, `templates/`, `examples/`, and `workspace-template/`.
