# Changelog

## v5.4 - Raw-data statistics recomputation

- 新增 `scripts/qcc_statistics.py`：自带 χ²（2×2，Yates 校正）与 Welch t 检验，
  不依赖 scipy（自实现不完全 gamma / 不完全 beta 函数）。
- 新增 `scripts/verify_qcc_statistics.py`：从原始数据文件复算 p 值并生成报告，
  可校验文稿声明的 p 值是否与复算一致。
- 检查脚本新增 `--data`：提供原始数据时追加第 12 项「统计数据复算」，
  文稿 p 值与复算不一致判 `WEAK`。
- 新增 `scripts/selftest_qcc_statistics.py` 覆盖：显著性/非显著性/连续型数据/声明不一致。

## v5.3 - Tool-selection, statistics and cost-benefit gates

- 现状把握：新增「数据与手法选择说明」——须写明数据类型（计数值/计量值）与
  选用查检表/柏拉图/直方图/散布图/管制图等工具的理由（依据 `docs/qcc_methodology.md` 工具选择矩阵）。
- 效果确认：新增「统计检验或豁免说明」——给出检验方法与 p 值/置信区间；
  声称“显著”必须给出 p 值；不做检验须说明理由（全量数据/描述性对比/样本不足）。
- 效果确认：新增「效益核算」——投入（人时/费用）、收益（节省工时/费用）、回收期或 ROI。
- 方法学文档新增「工具选择矩阵」与「统计检验与成本效益」两节。

## v5.2 - Extended method gates

- 主题选定：要求评价规则（权重/评分标准/评分方式）。
- 活动计划：要求「计划 vs 实际」进度对照（完成率/偏差/延期）。
- 查检表：要求收集方法与责任人。
- 无形成果：要求评价量表（分制/评分范围）、维度与前后均值。
- 标准化：要求文件编号、版本、生效日期，以及稽核结果回写/效果维持。
- 新增第 11 项「跨步骤一致性」：每条采纳对策必须映射到一条已验证真因
  （从真因验证表提取结论为“成立”的要因，再与对策表的真因列逐条比对）。

## v5.1 - Method logic gates

- Added numeric/logic verification instead of keyword presence only:
  - Pareto: descending categories, counts sum = sample size, cumulative monotonic to 100%,
    and the 80% improvement focus covering >=80%;
  - target: parameter range, direction consistency, and formula recomputation (tolerance 0.5pt);
  - true-cause verification: sample size >=30 or an explicit sampling basis;
  - effect confirmation: after must beat before, attainment/progress recomputation, and a
    post-improvement period + sample size.
- Step matching now uses the slide title (largest-font text), so roadmap/plan pages no longer
  bleed into other steps' evidence bundles.
- Page-number badges and the sample-data footer are excluded from numeric extraction.
- Terminology fix: fishbone dimensions are 5M1E (Man/Machine/Material/Method/Measurement) or
  6M when Environment is added — not "4M1E (人/机/料/法/环/测)".
- Added the `method-theater.qcc.pptx` fixture (keywords complete, data logic broken) and the
  self-test now asserts it is rejected.

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
