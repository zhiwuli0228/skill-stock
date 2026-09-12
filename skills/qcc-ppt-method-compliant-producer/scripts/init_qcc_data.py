#!/usr/bin/env python3
"""Create a QCC data file for the user to fill in.

    python scripts/init_qcc_data.py --out qcc-workspace/input/qcc-data.yaml
    python scripts/init_qcc_data.py --out demo.yaml --sample

The template covers every field the ten-step method needs, so the user only has
to fill values (or replace the sample numbers with real ones).
"""
from __future__ import annotations

import argparse
from pathlib import Path


TEMPLATE = """# QCC 数据文件（十步法）— 填写后即可用于生成 PPT
# 说明：
# 1. 未知项可写 null，但对应步骤会判定为 INCOMPLETE；
# 2. 计数值数据填 defects/total，连续型数据填 n/mean/sd；
# 3. 填写完成后运行：
#      python scripts/validate_qcc_data.py --data <本文件>
#      python scripts/verify_qcc_statistics.py --data <本文件>
#      python scripts/check_qcc_method_compliance.py <deck.pptx> --data <本文件>

meta:
  topic: ""            # 课题名称
  team: ""             # 圈组名称
  lead: ""             # 圈长
  period: ""           # 活动周期，如 2026-01-01..2026-03-31
  direction: lower     # lower = 指标越低越好；higher = 越高越好

# 1 主题选定
theme:
  candidates: []       # 候选主题，≥2 个
  criteria: []         # 评价维度，≥3 项（如 上级政策/重要性/迫切性/可行性/圈能力）
  scores: []           # 每个候选主题在各维度上的评分
  decision_rule: ""    # 评分规则（权重/评分方式）
  selected: ""         # 选定主题

# 2 活动计划拟定
plan:
  phases: []           # 阶段（P/D/C/A 或十步法阶段），≥4
  weeks: null          # 活动周数
  owners: []           # 负责人
  progress:            # 计划 vs 实际
    planned: null
    actual: null
    note: ""

# 3 现状把握
current_state:
  data_type: ""        # 计数值 / 计量值
  tools: []            # 选用手法（查检表/柏拉图/层别/直方图/散布图/管制图...）
  check_sheet:
    criteria: ""       # 判定标准
    period: ""         # 收集期间
    sample: null       # 样本量
    method: ""         # 收集方法/记录方式
    owner: ""          # 责任人
  categories: []       # [{name: 校验异常, count: 126}, ...] 按频次降序
  strata: []           # [{name: A班, value: 46.0}, ...]
  pareto_focus:
    count: null        # 改善重点类别数
    cumulative: null   # 累计占比（%）

# 4 目标设定
target:
  current: null        # 现况值（%）
  focus: null          # 改善重点（%）
  capability: null     # 圈能力（%）
  formula: ""          # 计算公式
  value: null          # 目标值（%）

# 5 解析
analysis:
  fishbone:
    problem: ""        # 主干问题
    dimensions: {}     # {人: [...], 机: [...], 料: [...], 法: [...], 测: [...]}
  cause_scores: []     # [{cause: 校验规则缺失, score: 14, selected: true}, ...]
  verification: []     # [{cause, source, method, result, conclusion}, ...] conclusion: 成立/不成立

# 6 对策拟定（含 5W1H 与真因映射）
countermeasures: []    # [{measure, cause, scores: {可行性: 5, 效益性: 5, 圈能力: 5},
                       #   total, adopted, who, where, when, how}, ...]

# 7 对策实施与检讨
implementation: []     # [{stage, time, owner, progress, data, difficulty}, ...]

# 8 效果确认
effect:
  before: {}           # 计数型 {period, defects, total} 或连续型 {period, n, mean, sd}
  after: {}            # 同上（必须与 before 同口径）
  target: null         # 目标值
  statistics:          # 检验或豁免
    test: ""           # chi-square / welch-t / 不做检验
    p: null            # p 值（或 confidential interval）
    comparison: ""     # "<" / "="
    waiver_reason: ""  # 不做检验时的理由
  intangible:
    scale: ""          # 如 1-5 分制
    dimensions: []     # 评价维度
    before_mean: null
    after_mean: null
  benefit:
    input_hours: null
    input_cost: null
    annual_saving_hours: null
    annual_saving: null
    payback: ""

# 9 标准化
standardization:
  documents: []        # [{name, type, number, version, effective, owner,
                       #   audit_frequency, audit_method, training, maintenance}, ...]

# 10 检讨与改进
review:
  strengths: []
  weaknesses: []
  residual: []
  next_topic: ""
"""


SAMPLE = """# QCC 数据文件（示例：降低处理异常率）
meta:
  topic: 降低处理异常率
  team: 精益圈
  lead: 张三
  period: 2026-01-01..2026-03-31
  direction: lower

theme:
  candidates: [降低处理异常率, 缩短处理时长, 减少返工次数]
  criteria: [上级政策, 重要性, 迫切性, 可行性, 圈能力]
  scores:
    - [5, 5, 4, 5, 4]
    - [4, 4, 3, 4, 4]
    - [3, 4, 3, 3, 3]
  decision_rule: 5 分制，圈员独立打分取平均，权重相同
  selected: 降低处理异常率

plan:
  phases: [P 计划, D 实施, C 检查, A 处理]
  weeks: 8
  owners: [张三, 李四, 王五]
  progress: {planned: 8, actual: 8, note: 第 5 周延期 2 天，已调整顺序}

current_state:
  data_type: 计数值
  tools: [查检表, 柏拉图, 层别]
  check_sheet:
    criteria: 结果校验不通过即判定为异常
    period: 2026-01-01..2026-01-31
    sample: 300
    method: 查检表逐例记录
    owner: 张三
  categories:
    - {name: 校验异常, count: 126}
    - {name: 记录缺失, count: 70}
    - {name: 流程等待, count: 60}
    - {name: 标注错误, count: 30}
    - {name: 其他, count: 14}
  strata:
    - {name: A 班, value: 46.0}
    - {name: B 班, value: 38.0}
    - {name: C 班, value: 41.0}
  pareto_focus: {count: 3, cumulative: 85.3}

target: {current: 42.0, focus: 85.3, capability: 80, formula: 目标值 = 现况值 - (现况值 × 改善重点 × 圈能力), value: 13.3}

analysis:
  fishbone:
    problem: 结果校验异常率高
    dimensions:
      人: [新人操作不熟练]
      机: [校验工具版本旧]
      料: [字段定义不统一]
      法: [校验规则缺失]
      测: [抽样标准不明确]
  cause_scores:
    - {cause: 校验规则缺失, score: 14, selected: true}
    - {cause: 字段定义不统一, score: 12, selected: true}
    - {cause: 抽样标准不明确, score: 9, selected: false}
  verification:
    - {cause: 校验规则缺失, source: 查检表 300 例 + 现场记录, method: 按规则缺失分类统计, result: 关联异常 98 例（77.8%）, conclusion: 成立}
    - {cause: 字段定义不统一, source: 查检表 300 例 + 字段字典, method: 对比字段口径差异, result: 关联异常 36 例（28.6%）, conclusion: 成立}
    - {cause: 抽样标准不明确, source: 抽检记录 60 例, method: 重抽对比判定差异, result: 差异 < 5%，不显著, conclusion: 不成立}

countermeasures:
  - {measure: 补齐校验规则, cause: 校验规则缺失, scores: {可行性: 5, 效益性: 5, 圈能力: 5}, total: 19, adopted: true, who: 李四, where: 结果校验环节, when: 第 4 周, how: 新增 12 条规则并回归验证}
  - {measure: 统一字段定义, cause: 字段定义不统一, scores: {可行性: 5, 效益性: 4, 圈能力: 4}, total: 18, adopted: true, who: 王五, where: 数据录入环节, when: 第 4 周, how: 发布字段字典并培训}
  - {measure: 优化校验工具, cause: 校验规则缺失, scores: {可行性: 4, 效益性: 4, 圈能力: 4}, total: 15, adopted: true, who: 李四, where: 工具链, when: 第 5 周, how: 升级工具版本并配置规则}

implementation:
  - {stage: D, time: 第 4 周, owner: 李四, progress: 完成 12 条校验规则上线, data: 异常率 42.0% → 18.0%, difficulty: 工具兼容性延期 2 天，已调整顺序}
  - {stage: C, time: 第 6-7 周, owner: 张三, progress: 效果确认与目标对比, data: 异常率降至 13.6%, difficulty: 抽样复核发现 2 例边界问题，已修订}

effect:
  before: {period: 2026-01-01..2026-01-31, defects: 126, total: 300}
  after: {period: 2026-03-01..2026-03-31, defects: 41, total: 300}
  target: 13.3
  statistics: {test: chi-square, p: 0.05, comparison: "<"}
  intangible: {scale: 1-5 分制, dimensions: [问题意识, 数据分析, 团队协作, 表达沟通, 工具应用], before_mean: 3.0, after_mean: 4.2}
  benefit: {input_hours: 24, input_cost: 0.4, annual_saving_hours: 312, annual_saving: 5.2, payback: 1 个月内}

standardization:
  documents:
    - {name: 结果校验作业标准书, type: 作业标准书, number: QCC-STD-001, version: V1.0, effective: 2026-04-01, owner: 张三, audit_frequency: 每月, audit_method: 按检查表逐项稽核, training: 新员工入职培训, maintenance: 连续 3 个月复查达标}

review:
  strengths: [数据驱动定位改善重点, 对策与真因一一对应]
  weaknesses: [工具兼容性评估不足, 培训与生产高峰冲突]
  residual: [抽样标准仍未统一]
  next_topic: 降低记录缺失率
"""


def main() -> int:
    parser = argparse.ArgumentParser(description="Create a QCC data file.")
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--sample", action="store_true", help="write a filled sample instead of a blank template")
    args = parser.parse_args()

    if args.out.exists():
        print(f"refusing to overwrite existing file: {args.out}")
        return 1
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(SAMPLE if args.sample else TEMPLATE, encoding="utf-8")
    print(f"written: {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
