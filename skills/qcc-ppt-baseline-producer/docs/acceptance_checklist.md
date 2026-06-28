# Acceptance Checklist

## QCC completeness

- [ ] Circle profile is present and explains roles, evidence responsibility, and activity mechanism.
- [ ] Topic selection includes rationale and candidate comparison.
- [ ] Current-state investigation has baseline data or explicit evidence status.
- [ ] Targets are measurable and have rationale.
- [ ] Cause analysis separates symptoms from causes.
- [ ] Key factors are confirmed by evidence.
- [ ] Countermeasures map to key factors.
- [ ] Implementation explains how countermeasures were executed.
- [ ] Effect confirmation uses before/after comparison.
- [ ] Risk closure has concern, experiment, result, and conclusion.
- [ ] Standardization outputs are concrete.
- [ ] Promotion plan is staged and realistic.

## Template alignment

- [ ] Cover follows the supplied template style.
- [ ] Agenda follows the supplied template style.
- [ ] Footer is consistent.
- [ ] Red underline and typography are consistent.
- [ ] No custom dark-tech visual identity appears.

## Layout quality

- [ ] No text or shape is outside slide bounds.
- [ ] No text visibly overlaps unrelated elements.
- [ ] Card text stays inside cards.
- [ ] No slide has two bottom conclusion bars.
- [ ] No conclusion bars appear on cover, agenda, or circle-profile slides.
- [ ] Dense slides do not leave large unused lower space.
- [ ] Body text is readable.
- [ ] KPI cards do not place subtitle/description outside the card.
- [ ] Similar page types use consistent layout rules.

## Data quality

- [ ] Every core number has evidence.
- [ ] Missing evidence is marked, not hidden.
- [ ] Before/after data is complete on effect pages.
- [ ] Risk closure items include four required elements.

## Formal delivery hard gates v2.1

- [ ] `validate_qcc_data.py` passes without `--allow-draft`.
- [ ] No placeholder values remain in formal slide data.
- [ ] No core effect uses qualitative-only wording.
- [ ] Production-running claims are backed by production logs, monitoring exports, release records, audit records, or incident records.
- [ ] User oral summaries are not used as final evidence.
- [ ] `layout_lint.py --mode formal` passes with zero errors and zero warnings.
- [ ] The rendered montage has been visually inspected.
- [ ] No generated `HUAWEI` logo text appears on top of the template.
- [ ] Bottom-right logo safe zone is not occupied by generated text or shapes.


## Placeholder acceptance

- [ ] No slide contains `单击此处添加标题` / `单击此处添加文本` or equivalent prompt text.
- [ ] No editable placeholder remains in the generated PPTX.
- [ ] Generated text does not cover an unused template placeholder.
- [ ] `python scripts/placeholder_lint.py output/qcc_ppt.pptx --mode formal` passes with 0 errors.


## V2.4 edit-mode template checks

Before delivery, open the deck in PowerPoint/WPS and verify:

- no `单击此处添加标题` or `单击此处添加文本` remains;
- no dotted editable placeholder frame remains on generated slides;
- agenda title and items are not duplicated by inherited template text;
- the final page shows the template-owned Thank-you/legal content only once;
- generated content does not duplicate the template logo, footer, copyright or vision statement.

The command `python scripts/placeholder_lint.py output/qcc_ppt.pptx --mode formal` is mandatory and must pass.

## v2.9 QCC method-format hard gates

- [ ] `主题评审｜头脑风暴` exists and uses a recognizable idea-card layout.
- [ ] Brainstorming page does not use loose radial connector clutter.
- [ ] `主题评审｜亲和图` exists and uses clustered cards.
- [ ] `主题评审｜检查表` exists and uses criteria/matrix scoring.
- [ ] TOP ranking summary card scores such as `24分` do not wrap vertically.
- [ ] `把握现状｜SIPOC` exists and uses Supplier/Input/Process/Output/Customer columns.
- [ ] `把握现状｜柏拉图` exists and includes descending bars, cumulative percentage or labels, and 80% marker.
- [ ] `把握现状｜子流程图` exists and marks pain points / abnormal points.
- [ ] `根因分析｜鱼骨图` exists and is visually recognizable as fishbone.
- [ ] `根因分析｜矩阵图` exists and connects to suspected causes.
- [ ] `根因验证` exists and every retained root cause has validation method and evidence field.
- [ ] `拟定对策｜5W` exists and contains What/Why/Who/When/Where.
- [ ] `实施跟踪｜5W` exists and contains What/Why/Who/When/Where or status/evidence.
- [ ] `成果固化｜标准化清单` exists and uses a checklist/list, not prose-only content.
- [ ] `scripts/check_qcc_method_compliance.py` returns PASS.
- [ ] `scripts/audit_qcc_visual_heuristics.py` returns no connector-clutter or ranking-wrap risk.
