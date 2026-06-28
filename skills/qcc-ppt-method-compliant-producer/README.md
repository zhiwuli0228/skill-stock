# qcc-ppt-production-skill v4.3

This Skill produces or enhances QCC PPT decks with three gates:

1. **QCC method compliance**: mandatory QCC methods must be visible in page titles and visual forms.
2. **Rendered format quality**: PPT must be rendered to screenshots and reviewed.
3. **Screenshot feedback loop**: user-marked screenshot defects must be repaired locally and written back into the Skill as reusable defect patterns.

## Typical flow

```bash
python scripts/check_qcc_method_compliance.py qcc-workspace/output/qcc-review-ready.pptx \
  --report qcc-workspace/reports/qcc-method-compliance-report.md

python scripts/audit_qcc_ppt_format.py qcc-workspace/output/qcc-review-ready.pptx \
  --report qcc-workspace/reports/qcc-format-audit-report.md

python scripts/audit_qcc_visual_heuristics.py qcc-workspace/output/qcc-review-ready.pptx \
  --report qcc-workspace/reports/qcc-visual-heuristics-report.md
```

Then render to PNG and inspect the montage. If the user provides a screenshot, use `docs/qcc_screenshot_feedback_gate.md` as the repair authority.

## v4.3 defect pattern added

For `主题评审｜头脑风暴`, avoid loose radial connector pages when the screenshot shows connector clutter or uncontrolled whitespace. Prefer:

```text
[发散主题 anchor]    [候选方向 1] [候选方向 2] [候选方向 3]
                    [候选方向 4] [候选方向 5] [候选方向 6]
[发散输出 conclusion]
```

This keeps the page method-compliant, readable, editable, and stable in formal review screenshots.


## v4.3 ranking-card gate

v4.3 adds a rendered-screenshot rule for compact TOP summary cards. Ranking side cards must use fixed rank/topic/score zones, avoid vertical score wrapping, and keep explanatory notes outside ranked-item rows.
