# Common Visual Failures

## 1. Badge number is too high

Symptom: number in circle is visually close to the upper edge.

Fix: use independent text box overlay and optical y correction.

## 2. Cards float in upper page

Symptom: page bottom has large blank area but cards are small.

Fix: increase card height or use 2x2 dashboard layout.

## 3. Page has no visual focus

Symptom: every element has similar weight.

Fix: enlarge main metric, conclusion, or primary card.

## 4. Template style drift

Symptom: page uses colors or layout unlike the selected enterprise template.

Fix: reuse title, underline, footer, card radius, and accent colors from template.

## 5. Overuse of bottom conclusion bars

Symptom: every page has a red bar and it becomes visual noise.

Fix: keep only when it provides a real page-level conclusion.

## 6. 方法名词在场，但分析链不成立（method theater）

Symptom: 页面标题有“柏拉图”“鱼骨图”“根因验证”等名词，但柏拉图没有类别/频次/
累计百分比，目标设定没有现况值/圈能力/目标值，真因验证没有数据来源，对策没有评价
与真因映射。旧版只做关键词覆盖检查时，这类 PPT 会被判 PASS。

Fix:

- 对照 `docs/qcc_methodology.md` 的十步判定标准，补齐该步的输入、数据与结论；
- 运行 `scripts/check_qcc_method_compliance.py`，任何 `WEAK` / `MISSING` / `INCOMPLETE`
  都不得交付；
- 用 `examples/fixtures/keyword-only.qcc.pptx` 回归验证：只有方法名词的 PPT 必须判
  `NON-COMPLIANT`。
