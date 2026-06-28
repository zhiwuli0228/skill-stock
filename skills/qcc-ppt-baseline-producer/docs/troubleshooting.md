# Troubleshooting

## The deck looks like a generic technical report

Check whether QCC stages are missing. Rebuild using the required slide structure.

## Cards are floating with too much blank space

Use a denser page type. Increase card height or switch from tiny-card grid to logic-chain or matrix layout.

## Bottom red bars dominate the deck

Delete them. Keep only one short page conclusion where it adds value.

## Text overflows cards

Shorten text first. Increase card height second. Split slides third. Shrinking font below the minimum is not allowed.

## Data looks untrustworthy

Add evidence ids and generate `data-quality-report.md`. Do not use numbers that cannot be traced.

## The template style drifts

Compare with `template_light_16_9.pptx`. Restore cover, agenda, footer, red underline, black title, and restrained white-background style.

## v2.1 common failure cases

### Validation fails because evidence is oral-only

Cause: `evidence-index.yaml` uses types such as `user_statement` or `user_provided_production_summary`.

Fix: convert the statement into formal evidence by adding at least one of: operation log, monitoring export, release record, audit record, incident record, test report, experiment report, or code commit.

### Validation fails because before/after values are qualitative

Cause: effect metrics say “显著提升” or “稳定性较好” without numeric values.

Fix: provide countable before/after values, such as duplicate executions per month, manual restarts, alert count, recovery time, task count, node count, or failure rate.

### Layout lint fails because HUAWEI text is detected

Cause: the generator added logo text while the template already owns the logo layer.

Fix: use `--footer-mode none` or `--footer-mode minimal`. Do not add logo text or logo placeholders in slide code.

### Layout lint fails because of unused vertical space

Cause: dense content is floating near the top and the lower content area is not used.

Fix: enlarge cards, use two-row layouts, increase row height, or merge sparse cards into a stronger main visual block. Do not ignore this warning in formal mode.


## Duplicate Thank-you or placeholder prompt remains

Symptom:

- final page shows two `Thank you.` blocks;
- cover/agenda page shows `单击此处添加标题` or `单击此处添加文本`;
- generated title overlaps a template title.

Cause:

- the generator added content on top of inherited layout/master text;
- the template end page already owns the Thank-you/legal block;
- only slide-level placeholders were deleted, but layout/master placeholders remained.

Required fix:

- run v2.4 or later;
- ensure `sanitize_template_layouts()` is called after template layout mapping and before seed-slide deletion;
- ensure the final slide is created with `slide(prs, role="end")` only, without extra `add_text()` calls;
- run `placeholder_lint.py --mode formal`.
