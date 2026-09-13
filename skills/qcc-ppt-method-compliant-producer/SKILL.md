---
name: qcc-ppt-method-compliant-producer
description: Produce or enhance QCC (品管圈) PPT decks that must satisfy the standard ten-step QCC method with real analysis chains, not just method names. Use when a QCC presentation must include theme evaluation, activity plan, current-state data collection with check sheet and Pareto, target setting, cause analysis with true-cause verification, countermeasure evaluation with 5W1H, effect confirmation (tangible and intangible), standardization, and review/improvement — with data-completeness gates that block "method theater" decks.
version: "5.7.0"
license: MIT
---

# QCC PPT Method-Compliant Producer

> v5.0 重做方法链：从「方法名词在场」升级为「标准品管圈十步法的分析链成立」。
> v5.1 补上逻辑门：数据一致性、公式复算、指标方向、真因样本量、改善前后可比性；
> 缺数据判 `INCOMPLETE`，逻辑错误判 `WEAK`，不再放行「术语齐全但算法错误」的稿子。
> v5.6 把「要使用者填表」换成「要使用者给一个文件夹」：扫描 → 取证 → 模型抽取 → 推导 → 校验。

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
DATA-DIR/                                     # ★ preferred: the user's own folder of records
                                              #   (xlsx/csv/docx/pptx/pdf/txt); the Skill scans it
qcc-workspace/input/qcc-min-data.yaml         # raw facts only (wizard path, when no files exist)
qcc-workspace/input/qcc-data.yaml             # structured ten-step data (already prepared)
qcc-workspace/input/qcc-baseline.pptx         # optional (enhancement mode)
qcc-workspace/input/render/montage.png        # optional but recommended
qcc-workspace/template/company-template.pptx  # optional
```

Prefer the data folder: the user provides records, not answers. Ask for a folder path before
ever handing over a questionnaire or a template.

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

### Step 4A — Generate the deck from data (never hand-roll layouts)

Pages are produced by the bundled builder, so every method appears in its standard form
and the layout defects acceptance review already rejected cannot come back:

```bash
python scripts/qcc_pipeline.py --min qcc-workspace/input/qcc-min-data.yaml \
  --template <skill>/templates/qcc-empty-template.pptx --workspace qcc-workspace
# 等价于：derive → validate → verify statistics → build_qcc_deck → method compliance
```

`scripts/build_qcc_deck.py` + `scripts/qcc_deck_lib.py` render the 22 pages from
`qcc-data.yaml`: 主题评价/要因评价/对策评价 matrices read dimension by dimension, the plan is
a work-package Gantt with plan and actual bars, the as-is flow has a decision branch, the
fishbone carries 5M1E, effects show before/after plus benefit, intangible results use
circle-ability dimensions. The library enforces the guards (≤6×6 tables, text fit, overlap,
out-of-bounds, shape/char ceilings) and writes `reports/deck-build-report.md`.

Rules:

- **Do not hand-roll page layouts.** If a page looks wrong, fix the data or the library —
  not the individual deck.
- Missing data becomes `待补充` **and** a violation line in the build report; read it before
  delivering.
- Re-run `scripts/selftest_qcc_build.py` after touching the library or the builder.

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

### 6.2 Analysis-quality gates (v5.3)

11. **数据与手法选择说明** — 现状把握必须写明数据类型（计数值/计量值）与选用该手法的理由
    （见 `docs/qcc_methodology.md` 工具选择矩阵）。
12. **统计检验或豁免说明** — 效果确认须给出检验方法与 p 值/置信区间；
    声称“显著”必须给出 p 值；不做检验须说明理由（全量/描述性/样本不足）。
13. **效益核算** — 有形成果须给出投入（人时/费用）、收益（节省工时/费用）与回收期/ROI。

### 6.3 Raw-data statistics recomputation (v5.4)

14. **统计数据复算（第 12 项）** — 当提供原始数据文件时，脚本用自带的
    χ²（2×2，Yates 校正）或 Welch t 检验复算 p 值，并与文稿声明的 p 值比对；
    不一致判 `WEAK`。

数据文件约定（`qcc-workspace/input/qcc-data.yaml`，也接受 JSON）：

```yaml
metric: 处理异常率
direction: lower          # lower | higher
before: {period: 2026-01-01..2026-01-31, defects: 126, total: 300}
after:  {period: 2026-03-01..2026-03-31, defects: 41,  total: 300}
claimed: {test: chi-square, comparison: "<", p: 0.05}
```

连续型数据用 `before/after: {n, mean, sd}`。命令：

```bash
python scripts/verify_qcc_statistics.py --data qcc-workspace/input/qcc-data.yaml
python scripts/check_qcc_method_compliance.py deck.pptx --data qcc-workspace/input/qcc-data.yaml
```

### 6.4 Data intake (v5.5)

Users provide data with the lowest possible effort; the skill normalises it into one
`qcc-data.yaml` and validates it before production:

```bash
python scripts/init_qcc_data.py --out qcc-workspace/input/qcc-data.yaml           # blank template
python scripts/init_qcc_data.py --out qcc-workspace/input/qcc-data.yaml --sample  # filled example
python scripts/validate_qcc_data.py --data qcc-workspace/input/qcc-data.yaml      # lists missing fields
python scripts/verify_qcc_statistics.py --data qcc-workspace/input/qcc-data.yaml  # recompute p-value
```

Intake rules, CSV column conventions and the per-step field checklist live in
`docs/qcc_data_intake.md`. Generated decks must be checked with `--data` so the
statistics step is recomputed from the same source the user supplied.

### 6.5 Folder-scan intake — the default path (v5.6)

Ask the user for **a folder**, not for a filled form. One command scans it, extracts
evidence, and derives everything that can be computed:

```bash
python scripts/qcc_pipeline.py --dir "D:/QCC资料" --workspace qcc-workspace
```

Under the hood:

| 脚本 | 作用 |
|---|---|
| `scripts/qcc_scan_inputs.py` | 扫描目录 → 登记清单 + 抽取表格/文本 + 匹配必备字段 → 写 `qcc-min-data.draft.yaml`、`data-scan-report.md`、`data-scan-evidence.json` |
| `scripts/derive_qcc_data.py` | 原始事实 → 占比/累计%/80% 改善重点/目标值/达成率/进步率/p 值 |
| `scripts/validate_qcc_data.py` | 十步法字段齐备性 + 派生一致性（不合就 `GAP`） |
| `scripts/verify_qcc_statistics.py` | 从原始数据复算统计量 |
| `scripts/check_qcc_method_compliance.py --data` | 出片后合并第 12 项统计复算 |

Extraction discipline (non-negotiable, see `docs/qcc_llm_extraction_prompt.md`):

1. every filled value must point back to a source (file + sheet/page/slide + row/cell);
2. missing data stays `null` and is listed as a gap — never estimated or filled with the sample;
3. contradictory values are both listed for human arbitration, never averaged;
4. total/subtotal/average rows are not facts;
5. computed fields (share, cumulative %, target, attainment, progress, p-value) are never
   filled by the model — `derive_qcc_data.py` computes them;
6. images need visual recognition before their numbers are used, and must be flagged as such.

Field-by-field specification: `docs/qcc_data_requirements.md`.

Two denominators, never mixed (v5.6.1): the Pareto share is computed over the **defect
total** (sum of the category counts), while the current-state rate is computed over the
**checked total** (`current.sample`). Defects may be fewer than the checked units
(194 failures out of 197 cases) but never more; the checker enforces `defects ≤ checked`.

## 7. Hard Rules

- Ask for a **data folder first**; never open with a questionnaire or a blank YAML template.
- Never lay out a deck by hand: generate it with `scripts/build_qcc_deck.py`, then fix the
  data (or the library) rather than editing slide coordinates.
- Never deliver while `reports/deck-build-report.md` still lists violations.
- Never treat a scanned value as a fact without a source pointer; never estimate a gap.
- Never let the model fill computed fields (share / cumulative % / target / attainment /
  progress / p-value); the scripts compute them, and the checker recomputes them.
- Report contradictions instead of smoothing them: two conflicting values are two facts to arbitrate.
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

Folder-scan intake (default):

```bash
python scripts/qcc_scan_inputs.py --dir "D:/QCC资料" --workspace qcc-workspace
python scripts/qcc_pipeline.py --dir "D:/QCC资料" --workspace qcc-workspace \
  --template <skill>/templates/qcc-empty-template.pptx
python scripts/qcc_pipeline.py --min qcc-workspace/input/qcc-min-data.yaml \
  --template <skill>/templates/qcc-empty-template.pptx --workspace qcc-workspace
python scripts/qcc_pipeline.py --min qcc-workspace/input/qcc-min-data.yaml --deck output/deck.pptx
python scripts/build_qcc_deck.py --data qcc-workspace/input/qcc-data.yaml \
  --template <skill>/templates/qcc-empty-template.pptx \
  --out qcc-workspace/output/qcc-review-ready.pptx \
  --report qcc-workspace/reports/deck-build-report.md
python scripts/selftest_qcc_build.py                                       # 出稿回归自测
python scripts/make_qcc_scan_fixture.py --outdir examples/scan-fixture      # 造一个乱目录做演练
python scripts/selftest_qcc_scan.py                                        # 扫描路径自检
python scripts/selftest_qcc_minimal.py                                     # 最小数据路径自检
```

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
