# QCC 原始数据获取与交接规范（Data Intake）

目标：让使用者用**最低成本**提供数据，并保证数据足以支撑标准十步法的 PPT 与合规判定。
默认路径不是"让使用者填表"，而是**让使用者给一个文件夹，由模型自己读文件、抽事实**。

## 1. 四种提供方式（A 为默认）

| 方式 | 适用场景 | 使用者只需做 | 交接物 |
|---|---|---|---|
| **A. 数据目录（默认）** | 记录已在 Excel / Word / PPT / PDF / CSV 里 | 给出文件夹路径 | `qcc-workspace/input/qcc-min-data.draft.yaml` + `reports/data-scan-report.md` + `reports/data-scan-evidence.json` |
| B. 最小数据 YAML / 向导 | 数据只在人脑里、没有文件 | 回答约 20 个原始事实问题 | `qcc-workspace/input/qcc-min-data.yaml` |
| C. 单表补充 | 只差查检表/评分表/前后对比 | 按列名导出 CSV | 交给模型，由扫描器读入 |
| D. 完整数据 YAML | 已有现成的十步数据文件 | 直接给文件 | `qcc-workspace/input/qcc-data.yaml` |

四条路径最后都会归一成同一份 `qcc-data.yaml`：A/B/C 先得到**原始事实**，
再由 `derive_qcc_data.py` 计算占比、累计%、改善重点、目标值、达成率、进步率与 p 值。

## 2. A 路径：数据目录自动扫描（推荐）

### 2.1 命令

```bash
# 只扫描取证（模型/人工读证据后再填草稿）
python scripts/qcc_scan_inputs.py --dir "D:/QCC资料" --workspace qcc-workspace

# 一条命令跑完整链路：扫描 → 推导 → 校验 → 统计 →（出片后）合规
python scripts/qcc_pipeline.py --dir "D:/QCC资料" --workspace qcc-workspace
python scripts/qcc_pipeline.py --min qcc-workspace/input/qcc-min-data.yaml \
  --deck qcc-workspace/output/qcc-review-ready.pptx
```

### 2.2 扫描器会做什么

1. **登记清单**：文件名、类型、大小、哈希；
2. **抽取内容**：`.xlsx/.xlsm`（按工作表）、`.csv/.tsv`、`.docx`（段落 + 表格）、
   `.pptx`（文本框 + 表格）、`.pdf`（逐页文本）、`.txt/.md/.json/.yaml`；
3. **匹配字段**：把抽到的表格/文本与十步法必备字段做识别
   （类别频次、层别、主题评分矩阵、对策表、真因验证表、成本效益、检讨等）；
4. **产出三件套**：
   - `input/qcc-min-data.draft.yaml`：**只含证据里确实存在的值**，其余为 `null`；
   - `reports/data-scan-report.md`：文件清单、识别结果、仍缺失清单、给模型的抽取指令；
   - `reports/data-scan-evidence.json`：完整证据索引（表格行、文本块、命中位置），供模型读取。

### 2.3 模型的职责（抽取纪律）

模型读 `data-scan-evidence.json`，把值填进 `qcc-min-data.draft.yaml`，并且：

- 每个值都要能指回来源（文件名 + 工作表/页/幻灯片 + 行号/单元格）；
- 找不到就留 `null`，写进"缺失清单"，**不得编造**；
- 同一指标出现两个数值 → 两处都列出交人工裁决，不要取平均；
- 合计/小计/平均行不算事实数据；
- 计算类字段（占比、累计%、目标值、达成率、进步率、p 值）一律不填，交给脚本。

字段清单见 `docs/qcc_data_requirements.md`；抽取提示模板见 `docs/qcc_llm_extraction_prompt.md`。

### 2.4 扫描器的边界

| 情况 | 处理 |
|---|---|
| `.xls / .doc / .ppt` 旧格式 | 无法读取，报告里提示另存为 `xlsx/docx/pptx` |
| 图片（查检表照片、白板照片） | 只登记清单，需视觉识别后引用，并在报告中标注"来自图片" |
| 未支持类型 | 只登记清单 |
| 目录里没有可用表格/文本 | 退出码 1，提示改用向导或单表补充 |

## 3. B 路径：向导 / 最小数据（数据在人脑里）

```bash
python scripts/qcc_wizard.py --out qcc-workspace/input/qcc-min-data.yaml       # 一问一答
python scripts/qcc_wizard.py --out demo.yaml --defaults                        # 示例（自检/演示用）
python scripts/qcc_wizard.py --out data.yaml --answers answers.yaml            # 非交互
python scripts/qcc_pipeline.py --min qcc-workspace/input/qcc-min-data.yaml
```

向导只问原始事实（约 20 项），不要求使用者算占比或目标值。

## 4. C/D 路径与统一校验

```bash
# 已有现成的十步数据文件
python scripts/validate_qcc_data.py --data qcc-workspace/input/qcc-data.yaml \
  --report qcc-workspace/reports/data-readiness.md
python scripts/verify_qcc_statistics.py --data qcc-workspace/input/qcc-data.yaml \
  --report qcc-workspace/reports/qcc-statistics-report.md
python scripts/check_qcc_method_compliance.py qcc-workspace/output/qcc-review-ready.pptx \
  --data qcc-workspace/input/qcc-data.yaml
```

## 5. 需要哪些数据（按十步法）

| 步骤 | 必备数据 | 说明 |
|---|---|---|
| 1 主题选定 | `theme.candidates`（≥2）、`theme.criteria`（≥3）、`theme.scores`、`theme.decision_rule`、`theme.selected` | 评分规则要写清楚（权重/评分方式） |
| 2 活动计划 | `plan.phases`（≥4）、`plan.weeks`、`plan.owners`、`plan.progress.planned/actual` | 必须能看出“计划 vs 实际” |
| 3 现状把握 | `current_state.data_type`、`tools`、`check_sheet.*`（判定标准/期间/样本量/收集方法/责任人）、`categories`（降序频次）、`strata`、`pareto_focus` | `categories` 合计须等于样本量；`pareto_focus.cumulative` ≥80 |
| 4 目标设定 | `target.current/focus/capability/value/formula` | 目标值须能由公式复算 |
| 5 解析 | `analysis.fishbone`（≥4 维）、`cause_scores`、`verification[]`（来源/方法/结果/结论） | 真因验证样本量 ≥30，或写明抽样依据 |
| 6 对策拟定 | `countermeasures[]`：`measure/cause/scores/total/adopted/who/where/when/how` | 每条采纳对策必须映射到一条**已验证真因** |
| 7 对策实施 | `implementation[]`：`stage/time/owner/progress/data/difficulty` | 过程数据必填 |
| 8 效果确认 | `effect.before/after`（计数型 `defects/total` 或连续型 `n/mean/sd`）、`statistics`、`intangible`、`benefit` | 前后必须同口径；统计可复算；效益含投入/收益/回收期 |
| 9 标准化 | `standardization.documents[]`：名称/类型/编号/版本/生效日期/责任人/稽核频率/稽核方式/教育训练 | 另需写明效果维持 |
| 10 检讨与改进 | `review.strengths/weaknesses/residual/next_topic` | 残余问题应与效果确认中的未达标项对应 |

## 6. 表格（CSV）列名约定

**查检表 / 柏拉图数据**（`counts.csv`）：

```csv
类别,频次,判定标准,收集期间,样本量,责任人
校验异常,126,结果校验未通过,2026-01-01..2026-01-31,300,张三
记录缺失,70,关键字段为空,2026-01-01..2026-01-31,300,张三
```

**评分矩阵**（`scores.csv`）：

```csv
候选主题,上级政策,重要性,迫切性,可行性,圈能力
降低处理异常率,5,5,4,5,4
```

**前后对比**（`effect.csv`）：

```csv
阶段,期间,异常例数,样本量
改善前,2026-01-01..2026-01-31,126,300
改善后,2026-03-01..2026-03-31,41,300
```

把 CSV 放进数据目录即可被扫描器自动读入，不必手工合并。

## 7. 数据质量红线

1. **不得编造**：缺失项写 `null`，由校验器报为待补；不得用估计值冒充实测值。
2. **口径一致**：改善前后必须是同一指标、同一判定标准、同样的样本统计方式。
3. **可复算**：目标值、达成率、进步率、χ²/t 检验的 p 值都必须能由原始数据复算。
4. **可追溯**：查检表要有收集期间、样本量、收集方法与责任人；真因验证要有数据来源。
5. **人工确认**：由旧材料自动抽取的数据，出片前必须由使用者确认。

## 8. 交付物对照

| 使用者提供 | 脚本产出 | 用途 |
|---|---|---|
| 原始数据目录 | `reports/data-scan-report.md` + `reports/data-scan-evidence.json` | 目录里找到了什么、还缺什么、证据在哪 |
| 原始数据目录 | `input/qcc-min-data.draft.yaml` | 待填的最小数据（只含已找到的值） |
| 最小数据 | `reports/data-derive-report.md` | 每一步算式（改善重点、目标值、达成率、进步率、p 值） |
| 最小数据 | `reports/data-readiness.md` | 数据是否齐备、还差什么 |
| 完整数据 | `reports/qcc-statistics-report.md` | 复算的统计量与 p 值 |
| 完整数据 + deck | `reports/qcc-method-compliance-report.md` | 结构与逻辑合规判定（含第 12 项统计复算） |
| 任意环节 | `reports/pipeline-summary.md` | 一次流水线各阶段 PASS/FAIL/GAP 汇总 |
