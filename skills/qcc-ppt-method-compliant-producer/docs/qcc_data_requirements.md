# QCC 必备数据字段说明（Minimal Schema）

这份清单是**交给模型抽取数据时的唯一依据**：模型只填这些字段，其余一律留 `null`。
最小数据（`qcc-min-data.yaml`）只放**原始事实**；占比、累计百分比、改善重点、目标值、
达成率、进步率、χ²/t 的 p 值全部由 `derive_qcc_data.py` 计算，模型**不要**自己填。

约定：`null` / `[]` = 证据里没有 → 由校验器报为待补；**禁止**用估计值、示例值、行业经验值填充。

## 1. 字段表

| 最小数据字段 | 含义 | 常见来源 | 格式 / 单位 | 缺失后果 |
|---|---|---|---|---|
| `meta.topic` | 课题名称 | 立项书、圈会记录 | 文本 | 主题选定无法闭环 |
| `meta.team` | 圈组名称 | 立项书 | 文本 | 页眉/封面缺项 |
| `meta.lead` | 圈长 | 立项书、圈会记录 | 文本 | 责任人缺失 |
| `meta.period` | 活动周期 | 活动计划表 | `2026-01-01..2026-03-31` | 计划步骤无法核对 |
| `meta.direction` | 指标方向 | 指标定义 | `lower`（越低越好）/ `higher` | 效果方向判反 |
| `metric` | 指标名称 | 指标定义 | 文本 | 效果确认口径不明 |
| `theme.candidates` | 候选主题 | 主题评价表 | 列表，≥2 | 主题选定缺矩阵 |
| `theme.criteria` | 评价维度 | 主题评价表 | 列表，≥3（如上级政策/重要性/迫切性/可行性/圈能力） | 评价规则不成立 |
| `theme.scores` | 评分矩阵 | 主题评价表 | 二维数字数组，行=候选主题 | 选题无依据 |
| `plan.planned_weeks` | 计划周数 | 甘特图 | 数字（周） | 计划 vs 实际缺一半 |
| `plan.actual_weeks` | 实际周数 | 甘特图、进度记录 | 数字（周） | 计划 vs 实际缺一半 |
| `current.period` | 现状收集期间 | 查检表 | 日期区间 | 现状把握不可追溯 |
| `current.sample` | 现状样本量（**检查总数**） | 查检表 | 数字（例） | 现况值无法计算 |
| `current.categories` | 缺陷类别与频次 | 查检表汇总 | `[{name, count}]`，≥3；合计＝**缺陷合计**，须 ≤ 检查总数 | 柏拉图无法生成 |
| `current.strata` | 层别数据 | 层别表 | `[{name, value}]` | 层别分析缺失 |
| `current.before_defects` | 改善前缺陷例数（默认取缺陷类别合计，查检表另有口径时显式覆盖） | 查检表、效果对比表 | 数字（例） | 效果确认缺基线 |
| `target.capability` | 圈能力 | 圈会评价记录 | 数字（%） | 目标值无法计算 |
| `after.period` | 改善后收集期间 | 改善后查检表 | 日期区间 | 前后可比性不明 |
| `after.defects` | 改善后异常例数 | 改善后查检表 | 数字（例） | 效果确认缺失 |
| `after.total` | 改善后样本量 | 改善后查检表 | 数字（例） | 改善后比率无法计算 |
| `causes` | 已验证真因 | 要因评价表 + 真因验证记录 | `[{name, dimension, score, source, method, result}]` | 对策没有真因支撑 |
| `measures` | 对策 | 对策评价矩阵、实施表 | `[{name, cause, who, where, when, how, scores{可行性,效益性,经济性,圈能力}}]` | 对策拟定/5W1H 缺失 |
| `standardization` | 标准化文件 | 作业标准书、制度文件 | `[{name, type, number, version, effective, owner, audit_frequency, audit_method, training, maintenance}]` | 标准化步骤缺失 |
| `review.strengths` | 检讨-优点 | 圈会检讨记录 | 列表 | 检讨与改进缺失 |
| `review.weaknesses` | 检讨-不足 | 圈会检讨记录 | 列表 | 同上 |
| `review.residual` | 残余问题 | 圈会检讨记录 | 列表 | 同上 |
| `review.next_topic` | 下期主题 | 圈会检讨记录 | 文本 | 同上 |
| `intangible.scale` | 无形成果量表 | 圈员评价表 | 如 `1-5分制` | 无形成果无法判定 |
| `intangible.dimensions` | 无形成果维度 | 圈员评价表 | 列表，≥3 | 雷达图无维度 |
| `intangible.before_mean` | 活动前均值 | 圈员评价表 | 数字 | 前后对比缺失 |
| `intangible.after_mean` | 活动后均值 | 圈员评价表 | 数字 | 前后对比缺失 |
| `benefit.input_hours` | 投入人时 | 效益核算表 | 数字（小时） | 效益核算不成立 |
| `benefit.input_cost` | 投入费用 | 效益核算表 | 数字（万元） | 同上 |
| `benefit.annual_saving_hours` | 年化节省工时 | 效益核算表 | 数字（小时） | 收益侧只有钱没有工时不完整（建议填） |
| `benefit.annual_saving` | 年化节省费用 | 效益核算表 | 数字（万元） | 效益核算不成立 |
| `benefit.payback` | 回收期 | 效益核算表 | 文本，如 `1 个月内` | 效益核算不成立 |

## 2. 每个值的来源必须可追溯

抽取时每个填入的值都要记录：`文件名 + 工作表/页/幻灯片 + 行号或单元格`。
报告中输出为：`字段 → 值 → 来源 → 置信度（高/中/低）`。

## 3. 约束

1. **合计/小计/平均行不是事实数据**，不要当类别频次或前后值。
1.1 **两个分母要分清**：柏拉图占比的分母是**缺陷合计**（各类别频次之和）；
   现况值的分母是**检查总数**（`current.sample`）。缺陷合计可以小于检查总数
   （例如 197 个用例里 194 个失败），但不能大于它。
2. **同一指标出现两个不同数值**（例如两个文件的改善前例数不同）→ 两处都列出，交人工裁决，不要自行取平均。
3. **图表截图里的数字**（图片文件）需要视觉识别后才能引用，并在报告中标注“来自图片，需人工确认”。
4. **旧格式 `.xls/.doc/.ppt`** 需先另存为 `xlsx/docx/pptx`，扫描器无法读取二进制老格式。
5. 计算类字段（占比、累计%、目标值、达成率、进步率、p 值）**一律留空**，由脚本推导。

## 4. 推导与校验

```bash
python scripts/qcc_scan_inputs.py --dir <原始数据目录> --workspace qcc-workspace   # 扫描取证
python scripts/qcc_pipeline.py --min qcc-workspace/input/qcc-min-data.yaml         # 推导 + 校验 + 统计
```

`derive_qcc_data.py` 会计算并在 `reports/data-derive-report.md` 中列出每一步算式：
频次降序重排、占比与累计%、80% 改善重点、目标值、目标达成率、进步率、χ²（Yates）或 Welch t 的 p 值。
