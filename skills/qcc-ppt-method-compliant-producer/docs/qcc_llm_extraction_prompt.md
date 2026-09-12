# 数据抽取提示模板（交给模型执行）

用途：使用者只给了**一个数据文件夹**时，由模型读扫描证据、填最小数据。
使用者不需要填 YAML，也不需要回答问卷。把下面整段发给执行模型即可。

```text
你要为一份品管圈（QCC）汇报 PPT 准备数据。使用者只提供了原始资料目录，
没有填报任何表格，所以由你负责"读证据、抽事实、留缺口"。

【输入】
1. 扫描报告：qcc-workspace/reports/data-scan-report.md
2. 证据索引：qcc-workspace/reports/data-scan-evidence.json   ← 主要依据
3. 待填草稿：qcc-workspace/input/qcc-min-data.draft.yaml
4. 字段说明：docs/qcc_data_requirements.md

【任务】
通读证据索引里的每一个表格块（blocks[].rows）与文本块（blocks[].text），
把 docs/qcc_data_requirements.md 里列出的字段尽量补齐，写回草稿 YAML。

【硬性纪律】
1. 不得编造：证据里没有的值留 null，不要用估计值、行业经验值或示例值顶替。
2. 可追溯：每个填入的值都要记录来源（文件名 + 工作表/页/幻灯片 + 行号或单元格）。
3. 矛盾数据：同一指标两个不同数值时，两处都列出，标注"需人工裁决"，不要取平均。
4. 合计/小计/平均行不是事实数据，跳过。
5. 计算类字段一律不填（占比、累计%、改善重点、目标值、达成率、进步率、p 值），
   这些由 scripts/derive_qcc_data.py 计算。
6. 图片/照片里的数字需视觉识别才可引用，并在报告中标注"来自图片，需人工确认"。
7. 旧格式 .xls/.doc/.ppt 读不了，在报告里写成"需另存为新格式后重扫"。

【输出】
1. 更新后的 qcc-workspace/input/qcc-min-data.yaml
2. qcc-workspace/reports/data-extraction-notes.md，逐字段写明：
   | 字段 | 值 | 来源（文件 + 位置） | 置信度（高/中/低） |
3. 缺失清单：字段 → 这个字段支撑哪一步 → 建议向使用者索要什么材料

【完成后的动作】
运行：
  python scripts/qcc_pipeline.py --min qcc-workspace/input/qcc-min-data.yaml \
    --workspace qcc-workspace
若 reports/data-readiness.md 仍报未就绪，把缺失清单交给使用者，
逐项索取；补齐后重跑，直到"就绪"。
```

## 抽取示例（正确 / 错误）

证据（`查检表-1月汇总.csv` 工作表 `Sheet1` 第 2–6 行）：

```text
类别 | 频次 | 判定标准 | 收集期间 | 样本量 | 责任人
校验异常 | 60 | 结果校验不通过 | 2026-01-01..2026-01-31 | 300 | 张三
...
合计 | 300 | | | |
```

| 字段 | 正确 | 错误 |
|---|---|---|
| `current.categories` | `[{name: 校验异常, count: 60}, ...]`（按文件顺序，剔除"合计"行） | 自己按频次排序后填（应由脚本排序）；把"合计 300"当成一个类别 |
| `current.sample` | `300`（来源：同表"样本量"列） | 由类别频次相加推断并当作事实 |
| 目标值（`target.value`） | 留空（由脚本计算） | 用公式自己先算一遍填进去 |
| 缺失的 `standardization` | `[]` + 列入缺失清单 | 编一个"作业标准书 QCC-STD-001" |

## 与校验器的关系

- 草稿未补齐时：`validate_qcc_data.py` 退出码 1，输出"未就绪 + 待补清单"；
  `qcc_pipeline.py` 汇总里该阶段显示 `GAP`，不会静默出片。
- 补齐后：`derive` → `validate` → `verify_qcc_statistics` → 出片 → `check_qcc_method_compliance --data`，
  每一步都基于**同一份原始数据**，避免"文稿数字与来源对不上"。
