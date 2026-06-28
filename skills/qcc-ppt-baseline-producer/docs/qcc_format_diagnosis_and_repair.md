# QCC Format Diagnosis and Repair Rules

## 1. Render-first rule

Always render the PPTX to PDF/PNG before final delivery.

Minimum verification artifacts:

```text
qcc-workspace/output/qcc-review-ready.pptx
qcc-workspace/output/qcc-review-ready.pdf
qcc-workspace/render/png/slide-*.png
qcc-workspace/render/montage.png
qcc-workspace/reports/qcc-format-audit-report.md
```

Do not rely only on PowerPoint object inspection. Some problems only appear after rendering, especially chart labels, bottom callouts, footer collisions, and table compression.

## 2. Formal review readability gate

A QCC formal review page must pass these practical checks:

| Item | Gate |
|---|---|
| Method title | Must be visible and not wrapped into two title lines. |
| Body text | Prefer >= 10pt; labels below 9pt require visual justification. |
| Main table | Prefer <= 5 columns and <= 4 content rows on formal pages. |
| 5W page | Prefer action cards or compact table; avoid large empty grid tables. |
| Matrix page | Keep key causes only; move full scoring detail to appendix/report. |
| Bottom callout | Must not collide with notes, legends, footer, or logo. |
| Screenshot readability | Must be readable in 120dpi slide screenshot. |

## 3. Dense-table breaker

If a method page is technically compliant but visually weak, use the following transformation:

| Dense object | Repair pattern |
|---|---|
| 5W table with many rows | Convert to 2×2 or 3×2 action cards; each card keeps What/Why/Who/When/Where. |
| Matrix scoring table | Keep top 4 causes in a compact scoring table and add ranking bars. |
| Verification evidence table | Convert each root cause into an evidence card. |
| Standardization table | Convert to checklist/list with numbered rows. |
| Value map with multiple small tables | Convert to KPI cards + PDCA chain. |

## 4. Local repair rule

When the overall deck framework is accepted, do not rebuild the whole PPT.

Use local repair:

1. Render and identify bad pages.
2. Rebuild only the defective pages.
3. Preserve page order, template style, title system, footer, and logo.
4. Re-run method compliance and render review.
5. Update the Skill with the defect pattern and repair rule.

## 5. Anti-patterns

- Making the deck beautiful but not QCC-method compliant.
- Adding mandatory QCC methods as text only without recognizable method visual form.
- Keeping a page as a dense table because it is “editable”.
- Creating full-width 5W tables with many blank or low-value cells.
- Letting bottom notes overlap with conclusion callouts.
- Using long titles that dominate the slide and compress content.
- Fixing by globally shrinking fonts.

## 6. v4.2 screenshot-defect repair pattern: loose brainstorming page

Observed defect:

- Page title is correct: `主题评审｜头脑风暴`.
- Method is technically present.
- Rendered screenshot still looks weak because candidate cards are scattered, connector lines cross the center area, and the page has uncontrolled whitespace.

Repair rule:

1. Remove free-form connector lines.
2. Keep the central problem as a left-side topic anchor, not as a crossing hub.
3. Place candidate ideas in a strict 2×3 grid.
4. Keep `不评分 / 不排序 / 先发散` as small boundary chips.
5. Use bottom `发散输出` to hand off to affinity diagram and checklist pages.

This pattern must be used before delivery when the user reports the same visual defect.


## 7. v4.3 screenshot-defect repair pattern: crowded TOP ranking summary

Observed defect:

- Page title is correct, e.g. `主题评审｜检查表：矩阵评分选择改善课题`.
- Main checklist / matrix table is readable.
- The right-side `TOP 课题摘要` card fails in rendered screenshot because two-digit scores wrap vertically (`2
4`, `2
0`, `1
8`) and the explanatory note collides with the third row.

Repair rule:

1. Rebuild the ranking card as a structured list, not a mini table.
2. Each row must have three fixed zones: rank badge, topic text, score text.
3. Score zone width must be large enough for `24分` without wrapping; use no less than 0.45 in where possible.
4. Row height must be no less than 0.45 in for Chinese text.
5. Explanatory notes must sit outside the row stack with at least 0.08 in vertical clearance.
6. If the side card cannot fit all content, remove the note or move it into the bottom conclusion; do not shrink fonts below readable size.

This pattern must be used for checklist, matrix scoring, Pareto, and any slide that uses a compact side ranking summary.
