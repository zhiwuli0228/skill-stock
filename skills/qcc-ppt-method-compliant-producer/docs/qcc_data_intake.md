# QCC 原始数据获取与交接规范（Data Intake）

目标：让使用者用**最低成本**提供数据，并保证数据足以支撑标准十步法的 PPT 与合规判定。

## 1. 三种提供方式

| 方式 | 适用场景 | 交接物 |
|---|---|---|
| A. YAML 数据文件 | 首选；一次填完十步所需数据 | `qcc-workspace/input/qcc-data.yaml` |
| B. 表格（CSV/Excel） | 已有查检表/评分表/前后对比数据 | 每张表按下方列名导出，交给智能体合并进 YAML |
| C. 现有材料 | 已有旧 PPT、Word 报告、纸质查检表照片 | 由智能体抽取为 YAML，**人工确认后再出片** |

无论哪种方式，最终都会归一成同一份 `qcc-data.yaml`，再经校验后生成 PPT。

## 2. 标准流程（4 步）

```bash
# 1. 生成填写模板（或带示例的样例）
python scripts/init_qcc_data.py --out qcc-workspace/input/qcc-data.yaml
python scripts/init_qcc_data.py --out qcc-workspace/input/qcc-data.yaml --sample

# 2. 填写之后先校验完整性（会列出缺哪些字段）
python scripts/validate_qcc_data.py --data qcc-workspace/input/qcc-data.yaml \
  --report qcc-workspace/reports/data-readiness.md

# 3. 复算统计量（原始数据 → χ² / Welch t → p 值）
python scripts/verify_qcc_statistics.py --data qcc-workspace/input/qcc-data.yaml \
  --report qcc-workspace/reports/qcc-statistics-report.md

# 4. 出片后做合规校验（把原始数据一起交给检查器）
python scripts/check_qcc_method_compliance.py qcc-workspace/output/qcc-review-ready.pptx \
  --data qcc-workspace/input/qcc-data.yaml
```

## 3. 需要提供哪些数据（按十步法）

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

## 4. 表格（CSV）列名约定

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

把 CSV 交给智能体（或人工）合并进 `qcc-data.yaml` 的对应字段即可。

## 5. 数据质量红线

1. **不得编造**：缺失项写 `null`，由校验器报为待补；不得用估计值冒充实测值。
2. **口径一致**：改善前后必须是同一指标、同一判定标准、同样的样本统计方式。
3. **可复算**：目标值、达成率、进步率、χ²/t 检验的 p 值都必须能由原始数据复算。
4. **可追溯**：查检表要有收集期间、样本量、收集方法与责任人；真因验证要有数据来源。
5. **人工确认**：由旧材料自动抽取的数据，出片前必须由使用者确认。

## 6. 交付物对照

| 使用者提供 | 脚本产出 | 用途 |
|---|---|---|
| `qcc-data.yaml` | `reports/data-readiness.md` | 数据是否齐备、还差什么 |
| `qcc-data.yaml`（effect） | `reports/qcc-statistics-report.md` | 复算的统计量与 p 值 |
| 上述两者 + deck | `reports/qcc-method-compliance-report.md` | 结构与逻辑合规判定（含第 12 项统计复算） |
