---
name: qcc-ppt-method-compliant-producer
description: Produce or enhance QCC (品管圈) PPT decks that must satisfy the standard ten-step QCC method with real analysis chains, not just method names. Use when a QCC presentation must include theme evaluation, activity plan, current-state data collection with check sheet and Pareto, target setting, cause analysis with true-cause verification, countermeasure evaluation with 5W1H, effect confirmation (tangible and intangible), standardization, and review/improvement — with data-completeness gates that block "method theater" decks.
version: "5.2"
license: MIT
---

# QCC PPT Method-Compliant Producer

> v5.0 重做方法链：从「方法名词在场」升级为「标准品管圈十步法的分析链成立」。
> v5.1 补上逻辑门：数据一致性、公式复算、指标方向、真因样本量、改善前后可比性；
> 缺数据判 `INCOMPLETE`，逻辑错误判 `WEAK`，不再放行「术语齐全但算法错误」的稿子。

## 1. Role

You are the QCC PPT production and enhancement agent.

Output must satisfy two goals at the same time:

1. **Method compliance** — the deck must carry the standard QCC ten-step analysis chain
   (input → analysis → data/evidence → output → consumed by the next step).
2. **Presentation quality** — visually consistent, readable, editable, render-clean, template-aligned.

A deck that shows method names but has no data, no analysis logic, or no conclusions is a failed output.

## 2. Mandatory QCC Method Chain (standard ten steps)

```text
1  主题选定     选题背景 + 主题评价矩阵（维度/权重/评分/排序/选定理由）
2  活动计划拟定 甘特图 + PDCA 阶段 + 负责人
3  现状把握     现状流程图 + 查检表（判定标准/期间/样本量）+ 数据汇总 + 层别分析 + 柏拉图（累计% / 80% 改善重点）
4  目标设定     现况值 -（现况值 × 改善重点 × 圈能力）= 目标值 + 目标柱状图 + 合理性说明
5  解析         特性要因图（5M1E / 6M）→ 要因评价 → 真因验证（数据验证，未通过回退）
6  对策拟定     对策评价矩阵 + 对策群组/系统图 + 5W1H + 对策↔真因映射
7  对策实施与检讨 PDCA 实施记录 + 过程数据跟踪 + 困难与调整
8  效果确认     有形成果（改善前后 / 目标达成率 / 进步率）+ 无形成果（雷达图）
9  标准化       标准化文件（作业标准书/流程图/制度/表单）+ 日常稽核 + 教育训练与推广
10 检讨与改进   优点 / 不足 / 残余问题 / 下期主题
```

Methodology reference (authoritative): `docs/qcc_methodology.md`.

The old v4.x chain — brainstorming → affinity → checklist / SIPOC → Pareto → subprocess /
fishbone + matrix → root-cause verification / 5W / list — is superseded. In particular:

- **查检表（检查表）属于现状把握**，不是主题评审；
- **SIPOC 不再替代现状把握**，只可作为业务背景参考；
- 鱼骨图只是候选要因，必须经过要因评价与**数据真因验证**；
- 5W 升级为**5W1H + 对策评价矩阵 + 对策↔真因映射**；
- 效果确认、标准化文件、检讨与改进是必选步骤。

## 3. Capability Boundary

### 3.1 Production mode

Generate a complete deck from project information, following:

- `docs/qcc_page_contract.md`
- `docs/qcc_methodology.md`
- `docs/qcc_method_compliance_protocol.md`
- `docs/qcc_method_visual_patterns.md`

### 3.2 Enhancement mode

Given an existing baseline PPT, first build a method/evidence coverage table. Add or rebuild
missing or weak steps. Visual polishing alone is not acceptable.

## 4. Required Inputs

```text
qcc-workspace/input/qcc-baseline.pptx        # optional (enhancement mode)
qcc-workspace/input/render/montage.png       # optional but recommended
qcc-workspace/template/company-template.pptx # optional
```

Prefer a user-provided template; otherwise use `templates/qcc-empty-template.pptx` or
`templates/template_light_16_9.pptx`.

## 5. Mandatory Execution Steps

### Step 1 — Determine mode

- Baseline PPT provided → enhancement mode.
- Project content only → production mode.
- Incomplete data → keep the step structure and mark `待补充`, but never invent facts
  (a step with placeholders is `INCOMPLETE`, not compliant).

### Step 2 — Build the ten-step evidence map

| # | Step | Required visible method | Required evidence (minimum) |
|---:|---|---|---|
| 1 | 主题选定 | 主题评价矩阵 | candidates ≥2, criteria ≥3, scores, ranking/decision |
| 2 | 活动计划 | 甘特图 | phases ≥4, timeline, owners |
| 3 | 现状把握 | 流程图 + 查检表 + 层别 + 柏拉图 | as-is steps ≥3, criteria/period/sample, categories ≥3 with counts, stratification, cumulative %, 80% vital-few |
| 4 | 目标设定 | 参数 + 目标柱状图 | current, improvement focus %, circle capability %, target, calculation |
| 5 | 解析 | 鱼骨图 + 要因评价 + 真因验证 | 5M1E/6M ≥4 branches, cause scoring, validation data source + result |
| 6 | 对策拟定 | 对策评价矩阵 + 5W1H | measures ≥3, criteria ≥3, scores, 5W1H, measure↔verified cause |
| 7 | 实施与检讨 | PDCA 实施跟踪 | phase/time/owner/progress, tracking data, difficulties |
| 8 | 效果确认 | 有形成果 + 无形成果 | before/after, target attainment %, progress rate, radar chart |
| 9 | 标准化 | 标准化文件 + 稽核 | document name/type, auditor/frequency/method, training |
| 10 | 检讨与改进 | 检讨 | strengths, weaknesses, residual issues, next theme |

### Step 3 — Enforce the page-title contract

Use `阶段｜方法` titles from `docs/qcc_page_contract.md`, e.g.
`主题选定｜主题评价`, `现状把握｜查检表`, `解析｜真因验证`, `对策拟定｜5W1H`,
`效果确认｜有形成果`, `检讨与改进`.

Generic titles (`问题分析`, `原因分析`, `改进措施`, `成果展示`) may not replace method pages.

### Step 4 — Apply visual rules

- `docs/qcc_method_visual_patterns.md`
- `docs/visual_enhancement_protocol.md`
- `docs/slide_review_checklist.md`
- `docs/badge_alignment_rules.md`
- `docs/common_failures.md`
- `docs/qcc_format_diagnosis_and_repair.md`
- `docs/qcc_screenshot_feedback_gate.md`

### Step 5 — Render and inspect

Render PPTX → PDF → PNG screenshots. A deliverable is incomplete without rendered verification.

### Step 5A — Format diagnosis and local repair

```bash
python scripts/audit_qcc_ppt_format.py \
  qcc-workspace/output/qcc-review-ready.pptx \
  --report qcc-workspace/reports/qcc-format-audit-report.md
```

Repair only the defective pages; do not rebuild an accepted framework.

### Step 5B — Screenshot-feedback gate

A user screenshot or marked slide is a hard defect even if programmable audits pass.
Classify it (sparse canvas, connector clutter, overlap, table density, wrap, ranking-card
collision, footer collision, template drift, method-form ambiguity), repair locally, record
the pattern in the Skill, and re-render.

### Step 6 — Run the structural compliance check

```bash
python scripts/check_qcc_method_compliance.py \
  qcc-workspace/output/qcc-review-ready.pptx \
  --report qcc-workspace/reports/qcc-method-compliance-report.md
```

The report must show every step as `FOUND`; any `WEAK` / `MISSING` / `INCOMPLETE` blocks delivery.

### Step 7 — Output

```text
qcc-workspace/output/qcc-review-ready.pptx
qcc-workspace/output/qcc-review-ready.pdf
qcc-workspace/output/render/
qcc-workspace/reports/visual-review-report.md
qcc-workspace/reports/qcc-method-compliance-report.md
qcc-workspace/reports/qcc-format-audit-report.md
```

## 6. Logic gates (v5.1)

The checker now recomputes the analysis instead of only looking for keywords:

1. **Pareto (现状把握)** — categories sorted descending; counts sum = sample size;
   cumulative percentages monotonic and converging to 100%; the 80% improvement focus
   covers ≥80%.
2. **Target (目标设定)** — parameters within 0–100%; target direction matches the metric
   direction (lower-is-better ⇒ target < current); the target value can be recomputed from
   the stated formula (tolerance 0.5 percentage points).
3. **True-cause verification (解析)** — sample size ≥30, or an explicit sampling basis
   (全量/普查/抽样依据).
4. **Effect confirmation (效果确认)** — after must beat before; attainment and progress
   rates are recomputed from the before/after/target values; the post-improvement period and
   sample size are required.

Page-number badges and the sample-data footer are excluded from numeric extraction.

### 6.1 Extended gates (v5.2)

5. **主题选定** — 评价规则可查：权重 / 评分标准 / 评分方式。
6. **活动计划** — 必须有「计划 vs 实际」进度对照（完成率 / 偏差 / 延期）。
7. **查检表** — 必须写明收集方法与责任人（记录方式 / 数据来源 + 责任人）。
8. **无形成果** — 必须给出评价量表（分制/评分范围）、维度与前后均值。
9. **标准化** — 文件必须有编号、版本、生效日期，并写明稽核结果回写 / 效果维持。
10. **跨步骤一致性（第 11 项）** — 每条采纳对策必须映射到一条已验证真因；
    映射缺失或对不上判 `WEAK`。

## 7. Hard Rules

- Do not deliver a deck whose method pages contain only method names and no data/evidence.
- Do not treat keyword presence as method compliance; every step needs input, analysis, output.
- Do not place 查检表 in 主题选定; it belongs to 现状把握.
- Do not use SIPOC to replace 现状流程图 / 查检表 / 柏拉图 / 层别分析.
- Do not claim root causes from a fishbone diagram or scoring matrix alone; true causes need data verification.
- Do not write countermeasures without evaluation scores and a mapping to verified causes.
- Do not ship 5W without How (5W1H), or without implementation tracking.
- Do not omit 效果确认 (tangible + intangible), 标准化文件, or 检讨与改进.
- Do not mark a step compliant when its data fields are `待补充` / `待验证` / `示例结构`; mark it `INCOMPLETE`.
- Do not invent business data or conclusions.
- Do not deliver without render verification, and do not ignore screenshot feedback.
- Do not fix readability by globally shrinking fonts; reduce content or split/cardize.
- Do not merge mandatory methods into one page unless the title names all merged methods and each keeps its required fields.
- Do not pour body copy into the template's small placeholder boxes (labels/values/short notes).
  Fill each template shape only with content of its intended type, or rebuild the page on the
  template layout using its palette and typography; otherwise the deck renders as a squeezed,
  unreadable mess even though the background is preserved.

## 8. Recommended Commands

Enhancement mode:

```bash
python scripts/enhance_qcc_ppt.py \
  --input qcc-workspace/input/qcc-baseline.pptx \
  --output qcc-workspace/output/qcc-review-ready.pptx \
  --template qcc-workspace/template/company-template.pptx \
  --report qcc-workspace/reports/visual-review-report.md
```

Structural method compliance:

```bash
python scripts/check_qcc_method_compliance.py \
  qcc-workspace/output/qcc-review-ready.pptx \
  --report qcc-workspace/reports/qcc-method-compliance-report.md
```

Fixture self-check (proves the checker rejects keyword-only decks):

```bash
python scripts/make_qcc_method_fixtures.py --outdir examples/fixtures
python scripts/check_qcc_method_compliance.py examples/fixtures/keyword-only.qcc.pptx
python scripts/check_qcc_method_compliance.py examples/fixtures/data-complete.qcc.pptx
```
