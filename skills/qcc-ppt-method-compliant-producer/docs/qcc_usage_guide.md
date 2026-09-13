# QCC 汇报 PPT：使用者指南

这份文档写给"要出一份品管圈（QCC）汇报 PPT 的人"，不是给开发者的。
你只需要做两件事：**把资料给我**，**在缺口清单上确认**。其余（占比、柏拉图、
目标值、统计检验、22 页排版、合规自查、渲染出图）由 skill 自动完成。

---

## 1. 30 秒上手（最短路径）

```bash
# 一条命令：扫描资料 → 推导 → 校验 → 统计复算 → 生成 22 页 PPT → 合规自查 → 渲染
python <skill>/scripts/qcc_pipeline.py \
  --dir "<你的资料目录>" \
  --template <skill>/templates/qcc-empty-template.pptx \
  --workspace qcc-workspace --render
```

跑完你会得到：

| 交付物 | 位置 |
|---|---|
| 汇报 PPT（22 页，可编辑） | `qcc-workspace/output/qcc-review-ready.pptx` |
| PDF / 逐页 PNG / 总览拼图 | `qcc-workspace/render/`（先看 `montage.png`） |
| 数据扫描报告（找到什么、还缺什么） | `qcc-workspace/reports/data-scan-report.md` |
| 缺口清单（需要你补的字段） | `qcc-workspace/reports/data-readiness.md` |
| 出稿自检（版式/文本/重叠/密度） | `qcc-workspace/reports/deck-build-report.md` |
| 十步法合规报告（12 项判定） | `qcc-workspace/reports/qcc-method-compliance-report.md` |
| 一次流水线的总账 | `qcc-workspace/reports/pipeline-summary.md` |

判断"能不能交"只看两处：`pipeline-summary.md` 全 PASS，且
`deck-build-report.md` 显示"PASS（无违规）"。

> **数据没补全时不会出稿**：流水线会在「生成 PPT」一栏显示 `SKIP`，并指向
> `reports/data-readiness.md` 的待补清单。补齐后重跑同一条命令即可。
> 只想先看一份"缺口预览稿"，加 `--allow-incomplete`。

---

## 2. 三种给资料的方式（按推荐顺序）

| 方式 | 什么时候用 | 你要做什么 | 产出 |
|---|---|---|---|
| **A. 给目录（推荐）** | 资料散落在 Excel / Word / PPT / PDF / 截图 / 导出文件里 | 只给一个文件夹路径 | 扫描报告 + 证据索引 + 待补草稿（`input/qcc-min-data.draft.yaml`） |
| **B. 给数据（表/文件）** | 你手上已有查检表、评分表、前后对比数据 | 给文件或直接贴表格，说明口径 | 最小数据 + 完整数据 |
| **C. 什么都没有** | 数据在脑子里、没有电子文件 | 回答向导的约 20 个问题 | 最小数据 |

三条路最后都会归一成同一份 `qcc-data.yaml`，再生成同一套 22 页标准稿。

### A. 给目录：让模型自己探索（最适合"资料我也说不清在哪"）

把资料目录原样放着就行，**不要**先整理、不要改名、不要放进 `qcc-workspace`。
skill 会逐个文件读，能读的包括：

`xlsx / xlsm`（按工作表）、`csv / tsv`、`docx`（段落 + 表格）、`pptx`（文本框 + 表格）、
`pdf`（逐页文本）、`html`（表格 + 可见文本）、`json`（键值 + 嵌套数组）、
`txt / md / yaml`（含 Markdown 表格）。

读不了的会明确告诉你怎么办：`.xls / .doc / .ppt` 旧格式请另存为新格式；
图片（照片、白板、截图）需要视觉识别，会标注"来自图片，需人工确认"。

### B. 给数据：一份表就够

只要你能给出这四样，就能出稿：

1. **指标口径**：指标名、方向（越低越好 / 越高越好）、检查总数、缺陷合计；
2. **缺陷分类与频次**（查检表汇总）；
3. **改善前 / 改善后**两组数据；
4. **对策与责任人**（有就填，没有会在缺口清单里问你）。

里面**只有原始事实**，"占比 / 累计百分比 / 80% 改善重点 / 目标值 / 达成率 / 进步率 /
p 值"全部由脚本计算——不要自己算，也不要让模型替你算。

### C. 什么都没有：跑向导

```bash
python <skill>/scripts/qcc_wizard.py --out qcc-workspace/input/qcc-min-data.yaml
```

一问一答，只问原始事实（约 20 项）。答完接第 1 节的一条命令即可。

---

## 3. 可直接复制的 Prompt

### Prompt A｜给目录，让模型自动探索（推荐）

```text
用 qcc-ppt-method-compliant-producer 这个 skill，帮我做一份 QCC 汇报 PPT。

原始资料都在这个目录：
<粘贴资料目录的绝对路径>

我先说明现状：
- 里面格式很杂（可能有 Excel / Word / PPT / PDF / CSV / 图片 / 导出文件），
  我自己也不确定哪些有用；
- 我不知道该给你哪些字段，请你先探索再告诉我缺什么。

请按这个顺序做：
1. 扫描目录（scripts/qcc_scan_inputs.py），把「找到了什么证据」「还缺什么」列给我看；
2. 读证据补最小数据（qcc-min-data.yaml）：每个值都注明来源
   （文件名 + 工作表/页/幻灯片 + 行号或单元格）；
   找不到的留空，列成「需要我补的清单」，不要猜、不要用示例数据顶替；
3. 把「需要我补的清单」先发我确认，我说 OK 再出片；
4. 出片后给我：output/qcc-review-ready.pptx、render/montage.png、
   reports/deck-build-report.md 里剩余的违规项、合规报告的结论。

主命令（<skill> 换成 skill 的实际路径）：
python <skill>/scripts/qcc_pipeline.py --dir "<资料目录>" \
  --template <skill>/templates/qcc-empty-template.pptx \
  --workspace qcc-workspace --render
```

### Prompt B｜只给数据文件（口径我已经确认过）

```text
用 qcc-ppt-method-compliant-producer 这个 skill，把下面这份数据做成 QCC 汇报 PPT。

数据文件：<粘贴文件路径，或直接把表格贴在下面>
已知口径（没有的写"不知道"）：
- 课题：
- 指标名称 / 方向（越低越好 或 越高越好）：
- 检查总数 / 缺陷合计：
- 收集期间 / 判定标准 / 收集方法 / 责任人：

要求：
1. 先转成最小数据 qcc-min-data.yaml，口径写进 current.check_sheet
   （判定标准 / 期间 / 样本量 / 收集方法 / 责任人 / 记录方式）；
   「占比、累计百分比、80% 改善重点、目标值、达成率、进步率、p 值」不要手算，交给脚本；
2. 缺的字段列成清单问我，不要用示例数据填充；
3. 出片并自检：
   python <skill>/scripts/qcc_pipeline.py --min qcc-workspace/input/qcc-min-data.yaml \
     --template <skill>/templates/qcc-empty-template.pptx \
     --workspace qcc-workspace --render
4. 交付时告诉我：22 页稿在哪、总览图在哪、合规报告结论、出稿自检还剩哪些违规。
```

### Prompt C｜没有电子数据，只有事实

```text
用 qcc-ppt-method-compliant-producer 这个 skill，帮我做 QCC 汇报 PPT。
我手上没有电子表格，只有一些事实（课题、周期、问题类型和数量、改善前后的数）。
请你用向导模式（scripts/qcc_wizard.py）一项一项问我，我问到哪答到哪，
答完直接出片；缺的项列成清单，不要用示例数据填空。
```

---

## 4. 你提供什么 vs 系统算什么

| 必须由你提供（原始事实） | 系统自动计算（不要手填） |
|---|---|
| 课题、圈组、圈长、活动周期、指标与方向 | 各缺陷类别占比、累计百分比 |
| 候选主题与评分矩阵（几选几的打分） | 柏拉图 80% 改善重点（前几类） |
| 活动计划排程（每项的计划与实际情况） | 目标值 = 现况值 −（现况值 × 改善重点 × 圈能力） |
| 查检表：判定标准 / 期间 / 样本量 / 方法 / 责任人 / 记录方式 + 类别频次 | 目标达成率、进步率 |
| 层别数据（按班别、模块、时段等分层） | χ²（Yates）或 Welch t 的 p 值 |
| 改善前 / 改善后两组数据（同口径） | 前后对比图、效益核算的换算 |
| 圈能力（%） | 出稿版式、22 页结构、合规判定 |
| 真因验证记录（要因 / 来源 / 方法 / 结果 / 结论） | |
| 对策（含真因映射、5W1H、可行性/效益性/经济性/圈能力评分） | |
| 实施记录（逐条对策：时间 / 责任人 / 内容 / 过程数据 / 困难） | |
| 无形成果自评（圈员能力维度、前后评分） | |
| 效益核算（投入人时/费用、年化节省、回收期） | |
| 标准化文件（名称/类型/编号/版本/生效/稽核/训练/维持） | |
| 检讨四问（优点 / 不足 / 残余问题 / 下期主题） | |

### 两个口径必须分清（最常被问）

- **柏拉图占比**的分母是**缺陷合计**（各类别频次之和）；
- **现况值**的分母是**检查总数**（`current.sample`）。

例如"197 个用例里 194 个失败"：占比按 194 算，现况值按 194 ÷ 197 = 98.5% 算。
缺陷数可以小于检查数，但不能大于——系统会拦住。

---

## 5. 命令清单（分步执行时用）

```bash
S=<skill>/scripts
T=<skill>/templates/qcc-empty-template.pptx

# 1) 扫描资料目录（只取证，不填表）
python $S/qcc_scan_inputs.py --dir "<资料目录>" --workspace qcc-workspace

# 2) 手填最小数据（可选，仅在没有文件时）
python $S/qcc_wizard.py --out qcc-workspace/input/qcc-min-data.yaml

# 3) 推导 + 校验 + 统计复算
python $S/derive_qcc_data.py --min qcc-workspace/input/qcc-min-data.yaml \
  --out qcc-workspace/input/qcc-data.yaml --report qcc-workspace/reports/data-derive-report.md
python $S/validate_qcc_data.py --data qcc-workspace/input/qcc-data.yaml \
  --report qcc-workspace/reports/data-readiness.md
python $S/verify_qcc_statistics.py --data qcc-workspace/input/qcc-data.yaml \
  --report qcc-workspace/reports/qcc-statistics-report.md

# 4) 出稿（标准形态，不要手工排版）
python $S/build_qcc_deck.py --data qcc-workspace/input/qcc-data.yaml --template $T \
  --out qcc-workspace/output/qcc-review-ready.pptx \
  --report qcc-workspace/reports/deck-build-report.md

# 5) 自查与渲染
python $S/check_qcc_method_compliance.py qcc-workspace/output/qcc-review-ready.pptx \
  --data qcc-workspace/input/qcc-data.yaml \
  --report qcc-workspace/reports/qcc-method-compliance-report.md
python $S/audit_qcc_ppt_format.py qcc-workspace/output/qcc-review-ready.pptx \
  --report qcc-workspace/reports/qcc-format-audit-report.md
python $S/render_qcc_deck.py qcc-workspace/output/qcc-review-ready.pptx --outdir qcc-workspace
```

上面 1–5 步等于第 1 节的一条命令。

---

## 6. 验收清单（交付前逐条对照）

- [ ] `reports/pipeline-summary.md` 里 推导 / 校验 / 统计复算 / 生成 PPT / 方法合规 / 渲染 全为 `PASS`
      （出现 `SKIP` 说明数据未就绪：按 `reports/data-readiness.md` 补齐后重跑）
- [ ] `reports/deck-build-report.md` 为 `PASS（无违规）`
- [ ] `reports/qcc-method-compliance-report.md` 十二项全为 `FOUND`
- [ ] `reports/data-readiness.md` 为"就绪"（若显示"未就绪"，把它列的字段补进最小数据后重跑）
- [ ] `render/montage.png` 逐页看过：没有文字溢出、没有遮挡、页数与结构正常
- [ ] 页面上每个数字都能在 `reports/data-derive-report.md` 里找到算式

四种状态的含义：`FOUND` 合规 · `WEAK` 方法形态不对或缺证据 · `MISSING` 缺整页 ·
`INCOMPLETE` 该页还有 `待补充` 占位（**这四种以外才允许交付**）。

---

## 7. 常见问题

**Q：资料里有涉及公司机密的数据，能给我扫描吗？**
A：扫描是本地只读的，不联网、不改你的文件；也可以只给一个子目录，或先导出脱敏后的表格。
真要规避，走方式 B（只给一份整理过的表）。

**Q：缺数据会怎么样？**
A：缺的字段会渲染成 `待补充`，同时出现在 `deck-build-report.md` 的违规清单和
`data-readiness.md` 的待补清单里——**不会**被编造填上。流水线默认在数据未就绪时
**不出稿**（`生成 PPT: SKIP`）；补齐后重跑同一条命令即可。想看缺口预览稿加
`--allow-incomplete`。

**Q：我想用自己的公司模板。**
A：把 `--template` 换成你的模板文件即可；skill 只替换封面文字、沿用模板配色与字体，
不替换母版背景。

**Q：能少几页 / 多加几页吗？**
A：标准结构固定 22 页（十步法每步都有对应页）。要合并页面，改 skill 里的页面契约与
生成器，而不是直接删 PPT 的页——否则合规自查会判 `MISSING`。

**Q：出稿后我发现柏拉图的分母不对。**
A：那是数据口径问题：检查 `current.check_sheet.sample`（检查总数）与类别频次合计
（缺陷合计）是否写反了，改数据后重跑，不要直接改图。

**Q：图片里的数据（查检表照片、白板照）怎么办？**
A：扫描报告会标出"需要视觉识别"。让模型识别后**注明"来自图片，需人工确认"**，
你确认过再写进数据；不要直接当实测值用。

**Q：生成出来的稿子哪里能改？**
A：内容改数据（`qcc-min-data.yaml` / `qcc-data.yaml`），版式改
`scripts/qcc_deck_lib.py` 或 `scripts/build_qcc_deck.py`，然后重跑。
**不要**手工挪 PPT 里的坐标——下次生成会被覆盖，而且版式护栏就失效了。

---

## 8. 一句话总结

给 skill 一个目录（或一份数据）→ 看它列出的缺口 → 补齐 → 重跑一条命令 →
检查 `pipeline-summary.md` 全 PASS、`deck-build-report.md` 无违规、`montage.png` 逐页看过。
数字永远来自你的数据，缺口永远是缺口，不会被"编"上。
