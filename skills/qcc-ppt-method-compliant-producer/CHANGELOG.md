# Changelog

## v5.7.1 - 使用者指南 + 渲染脚本进 skill

- 新增 `docs/qcc_usage_guide.md`：面向使用者的完整指南——三种给资料的方式（给目录 /
  给数据 / 向导）、三段可直接复制的 Prompt（目录自动探索、只给数据文件、只有口头事实）、
  命令清单、验收清单、七条常见问题（保密、缺数据、公司模板、页数、口径写反、图片数据、
  改哪里）。
- 新增 `scripts/render_qcc_deck.py`：PPTX → PDF（PowerPoint COM）→ 逐页 PNG（poppler）→
  总览拼图（Pillow），缺依赖时给出明确的手动兜底，不再依赖工作区里的临时脚本。
- `qcc_pipeline.py` 新增 `--render`：一条命令走完 推导 → 校验 → 统计 → 出稿 → 合规 → 渲染。
- SKILL.md / README 指向使用者指南，并明确"把指南里的 Prompt A / B 交给使用者"。

## v5.7.0 - 出稿器进 skill：把"标准形态"变成生成器而不是人工排版

前几轮的修复只改了那一份 PPT；本轮把修好的形态固化成 skill 内的**生成器**，
让后续出稿天然合规、缺陷不会再悄悄回来。

- 新增 `scripts/qcc_deck_lib.py`：版式库（模板配色/微软雅黑/统一网格）+ **硬性护栏**：
  表格 ≤6 行 × 6 列、文本溢出、形状重叠、越界、形状数与字数上限；`add_kpi` 自动缩字号与截断。
- 新增 `scripts/build_qcc_deck.py`：从 `qcc-data.yaml` 生成 22 页标准稿，每页都是标准形态
  （评价矩阵逐维度、工作项目甘特图、含判定分支的流程图、5M1E 鱼骨图、逐维度要因/对策评价、
  逐条对策实施、有形成果含效益、圈员能力无形成果、标准化与检讨）。缺数据渲染为 `待补充`
  并写入 `reports/deck-build-report.md` 的违规清单，绝不编造。
- `qcc_pipeline.py` 新增 `--template` / `--deck-out`：一条命令完成
  **推导 → 校验 → 统计复算 → 生成 PPT → 方法合规**。
- 数据侧补齐：`derive` 透传 `narrative`（背景/流程图/结论条/证据清单）、`plan.schedule`
  与 `plan.axis`（逐项排程）、要因逐维度子分、实施记录的 `measure`，并在 `effect` 写入
  `attainment` / `progress_rate`；真因结论推断新增「不显著」判据。
- 新增 `scripts/selftest_qcc_build.py`：用完整最小数据出稿，断言 **出稿器 0 违规 + 22 页 +
  合规 PASS + 格式审计 0 风险**。
- 出稿器自检顺带修掉 4 个真实缺陷：真因验证页只渲染前 3 条导致「对策↔真因映射」失败、
  流程图多节点重叠、数据汇总截断导致累计不收敛、甘特图文本框超审计阈值；合规判据
  「工作项目 ≥6」不再依赖 P/D/C/A 字母（中文页判定更稳）。

## v5.6.3 - 全部方法的标准形态固化（举一反三）

甘特图被指出后，对**十步法每一个方法**做了形态检视，把「方法名词在场」升级为
「方法结构可读」，并逐条落成机器判据（回归样例同步升级为符合新标准的写法）：

- **评价类矩阵**（主题评价 / 要因评价 / 对策评价）：新增「逐维度可见（维度成列或成行）」，
  把「5 / 5 / 4 / 5」这种压成一格的写法判 `WEAK`。
- **现状流程图**：新增「含判定/分支」，直线流程（开始 → … → 结束）不再算现状流程图。
- **鱼骨图**：维度要求由 ≥4 提升为 **≥5（5M1E 完整为佳）**。
- **对策实施与检讨**：新增「逐条对策实施记录」——实施页必须有对策列（对策/时间/责任人/
  实施内容/过程数据/困难与调整），只按阶段写进展不再通过。
- **无形成果**：新增「圈员能力维度 ≥5」——用项目指标（如自动化水平、维护成本）代替
  圈员能力成长会被判 `WEAK`。
- `docs/qcc_page_contract.md` 新增「各方法的最低形态要求」对照表（18 行，含反例/正确形态/
  对应规则），并保留甘特图专项要求。
- `make_qcc_method_fixtures.py`：`data-complete` 样例同步升级（流程图加判定分支、要因评价
  改为逐维度矩阵、对策实施改为逐条对策表），保证回归样例本身就是"标准形态"的范本。
- 回归：`data-complete` PASS，`keyword-only` / `method-theater` 仍 NON-COMPLIANT；
  真实项目交付稿在全部新规则下仍 `overall=PASS`（12/12）。

## v5.6.2 - 甘特图必须是工作项目排程

验收反馈：「甘特图真的是这样的吗？」——原稿只有 4 条 PDCA 阶段横条，属于里程碑条，
不是活动计划甘特图。修正：

- `docs/qcc_page_contract.md`：第 06 页要求由「阶段 ≥4」升级为
  **行＝十步法工作项目（≥6 行）＋ 周次/日期轴 ＋ 负责人 ＋ 计划条 + 实际条 ＋ 进度偏差**，
  并写明反例（四条阶段横条判 `WEAK`）与「实际条须可指回证据」。
- `scripts/check_qcc_method_compliance.py`：新增规则「工作项目 ≥6（逐行排十步法工作项，
  阶段条不算甘特图）」——统计计划页出现的十步法工作项名称 ≥6 且 PDCA 阶段 ≥3。
  原「阶段 ≥4」规则保留，两者同时生效。
- 回归确认：`data-complete` 样例仍 PASS，`keyword-only` / `method-theater` 仍
  NON-COMPLIANT；本次真实项目交付稿在新规则下仍 `overall=PASS`。

## v5.6.1 - Defect-total model + real-world scan hardening

真实项目（frontend-skill-forge，197 个用例 / 194 个失败）跑通全链路时暴露并修复：

- **缺陷合计 vs 检查总数**：柏拉图占比的分母改为**缺陷类别合计**，现况值的分母保持
  **检查总数**（`current.sample`）；`derive_qcc_data.py` 默认取缺陷合计作改善前缺陷数，
  可用 `current.before_defects` 覆盖。`validate_qcc_data.py` 的规则由
  「频次合计 = 样本量」改为「缺陷类别合计 ≤ 检查总数」，`check_qcc_method_compliance.py`
  同步改判据（并把规则名改为「缺陷合计不超过检查总数」）。
- **真因验证结论**：`causes[]` 支持显式 `conclusion`（成立/不成立），未提供时按
  验证结果文本推断，不再一律判「成立」。
- **统计复算入口**：`check_qcc_method_compliance.py --data` 现在同时接受 v5.4 原始数据
  文件和**十步完整数据文件**（自动读取 `effect.before/after`），不再报「无法解析」。
- **柏拉图累计序列**：改为按「箭头链」或「最长非递减序列」提取，避免同页其他百分比
  干扰导致的误判。
- **扫描器增强**（真实语料驱动）：支持 **Markdown 表格**、**HTML 表格 + 可见文本**、
  **JSON（标量键值表 + 嵌套数组表）**；新增「运行汇总」识别（总数/通过/失败/跳过 →
  检查总数 + 缺陷数）；低置信度推断不再写入草稿；对文档表格误判加入代码标识与
  规模约束（≥5 行、合计 ≥50、≥3 个不同取值）。
- `selftest_qcc_minimal.py` 期望值随新口径更新（改善重点 84.1%、目标值 13.7%）。

## v5.6 - Folder-scan intake (默认路径：给文件夹，不给表格)

- 新增 `scripts/qcc_scan_inputs.py`：扫描使用者的数据目录，登记清单并抽取
  xlsx/xlsm（按工作表）、csv/tsv、docx（段落+表格）、pptx（文本+表格）、pdf（逐页文本）、
  txt/md/json/yaml；把抽到的块与十步法必备字段匹配，输出
  `qcc-min-data.draft.yaml`（只含证据里确实存在的值）、`reports/data-scan-report.md`、
  `reports/data-scan-evidence.json`（供模型读取的完整证据索引）。
  识别覆盖：类别频次、层别、主题评分矩阵、对策表（含 5W1H/评分列）、真因验证表、
  成本效益、检讨四问、课题/圈组/圈长/周期/方向、圈能力、计划 vs 实际。
- 新增 `scripts/derive_qcc_data.py`：原始事实 → 频次降序重排、占比、累计%、80% 改善重点、
  目标值、目标达成率、进步率、χ²（Yates）/Welch t 的 p 值，输出推导报告。
- 新增 `scripts/qcc_wizard.py`：约 20 项原始事实的交互向导（支持 `--defaults` / `--answers`）。
- 新增 `scripts/qcc_pipeline.py`：一条命令串联 扫描 → 推导 → 校验 → 统计 →（可选）合规校验，
  输出 `reports/pipeline-summary.md`（PASS / FAIL / GAP 汇总），数据未就绪不会静默出片。
- 新增 `scripts/make_qcc_scan_fixture.py`：生成"乱目录"演练素材（含旧格式 .xls 与图片）。
- 新增自测：`selftest_qcc_scan.py`（找到该找的、不编不该有的、未就绪草稿不放行）、
  `selftest_qcc_minimal.py`（示例事实跑通全链路，且推导值与公式一致）。
- 新增 `docs/qcc_data_requirements.md`（字段级说明）与 `docs/qcc_llm_extraction_prompt.md`
  （交给模型的抽取提示与正/反例）。
- `docs/qcc_data_intake.md` 重写为四条路径，A=数据目录扫描（默认），B=向导，C=单表，D=完整 YAML。
- 扫描/抽取纪律：值必须可回溯来源；缺失留 `null` 并报缺口；矛盾数值两处并列交人工裁决；
  合计行不算事实；计算类字段一律由脚本推导，模型不得自行填写。

## v5.5 - Data intake workflow

- 新增 `docs/qcc_data_intake.md`：三种数据提供方式（YAML / CSV 表格 / 现有材料）、
  四步标准流程、按十步法的必备字段清单、CSV 列名约定与五条数据质量红线。
- 新增 `scripts/init_qcc_data.py`：生成空白填写模板或带示例的样例数据。
- 新增 `scripts/validate_qcc_data.py`：逐步骤检查数据完整性并输出待补清单，
  同时做派生校验（频次合计、目标公式、改善方向、统计量）。
- 新增 `scripts/selftest_qcc_data.py`：空白模板必须报缺、样例必须就绪、统计可复算。
- `workspace-template/input/qcc-data.example.yaml` 作为随包示例。

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
