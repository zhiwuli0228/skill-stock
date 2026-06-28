# QCC Data Contract

The PPT generator consumes `qcc-data.yaml`. Core data must be structured and evidence-backed.

## Required top-level sections

```yaml
meta: {}
circle: {}
qcc_process: {}
results: {}
standardization: {}
promotion: {}
```

## Evidence rules

Every core number must include one of:

- `evidence_ids: [E001]`
- `evidence_ref: docs/09-reports/...`
- `evidence_status: missing`

If evidence is missing, the data may be shown as 待补充 or excluded from formal slides.

## Required QCC data

### Circle

```yaml
circle:
  name: 自适应线程池探索圈
  topic: 提升线程池动态治理能力
  activity_period: 2026.05 - 2026.06
  department: 待补充
  leader: 待补充
  facilitator: 待补充
  members:
    - name: 待补充
      role: 架构设计
      responsibility: 负责治理闭环方案设计
```

### Topic selection

Must include selected topic and at least two candidates with scores.

### Current state

Each problem must include scenario, symptom, current response, and impact.

### Targets

Each target must include metric, baseline, target, and rationale.

### Key factor confirmation

Each confirmed factor must include cause, verification method, evidence, and conclusion.

### Countermeasures

Each countermeasure must map to one key factor.

### Results

Effect confirmation requires before, after, improvement, and evidence.

### Risk closure

Each risk closure item must include exactly four elements:

```yaml
concern: 会不会振荡？
experiment: 40步交替负载
result: 0次方向反转
conclusion: 关闭
```

## Data quality gates

- No baseline, no effect-confirmation page.
- No evidence, no formal claim.
- No target rationale, target is invalid.
- No key-factor mapping, countermeasure is invalid.
- Risk closure without four elements is invalid.

## Formal-mode hard gates added in v2.1

Formal QCC delivery must fail when the data is structurally complete but not evidence-complete. A PPT must not be generated as a formal outcome when any core field uses placeholder or oral-only evidence.

### Placeholder ban

The following values are allowed only in draft data-gap mode and must fail formal validation:

- `待补充`
- `待确认`
- `TBD`
- `TODO`
- `未知`
- `未提供`
- `用户口述`

### Evidence quality levels

| Level | Evidence type | Formal PPT allowed |
|---|---|---|
| L0 | no evidence / missing | No |
| L1 | user oral summary / conversation summary | No |
| L2 | source-code or configuration reference | Conditional |
| L3 | test report / experiment report / performance report | Yes |
| L4 | production monitoring / operation log / release record / incident record / audit record | Yes |

For production claims such as “已生产运行半年”, formal mode requires L4 evidence. User statements are useful for drafting but cannot be treated as final QCC proof.

### Quantitative effect rule

The `results.before_after` section must provide numeric or countable before/after values. Qualitative-only wording is insufficient.

Bad:

```yaml
before: 依赖人工发现与重启
after: 框架自检、卡死检测和重建
improvement: 恢复动作标准化
```

Good:

```yaml
before: 半年内人工重启 6 次，平均发现时长 20min
after: 半年内人工重启 0 次，自检重建 11 次，平均恢复 30s
improvement: 人工重启次数降低 100%，平均恢复时长降低 97.5%
evidence_ids: [OPS_LOG_001, MONITOR_002]
```

### Draft mode behavior

When formal evidence is unavailable, run validation with `--allow-draft`. The output is a `data-quality-report.md`, not a formal deliverable PPT.

## Optional v2.9 method-data extension

The generator can derive method pages from existing `qcc_process` fields. For better output, users or upstream agents may provide optional `qcc_methods` fields.

```yaml
qcc_methods:
  affinity_groups:
    - label: 稳定性治理
      ideas:
        - 提升线程池动态治理能力
        - 运行风险自动识别
    - label: 效率优化
      ideas:
        - 优化日志异常检索效率
        - 降低资源空转
    - label: 过程治理
      ideas:
        - 降低AI辅助设计返工率
        - 沉淀需求设计模板

  sipoc:
    supplier: 业务流量 / 运维配置
    input: 线程池参数 / 运行指标
    process: [采样, 诊断, 决策, 安全门, 执行, 审计]
    output: 治理建议 / 调整结果 / Evidence记录
    customer: 服务运行团队 / 运维人员 / 业务系统

  pareto_items:
    - name: 突发流量拒绝
      value: 12
    - name: 下游阻塞等待
      value: 8
    - name: 低峰资源空转
      value: 5

  subprocess_steps:
    - 配置输入
    - 运行采样
    - 问题识别
    - 人工判断
    - 调整执行
    - 结果复盘

  subprocess_pain_points:
    - 发现滞后
    - 经验依赖
    - 缺少审计
```

### v2.9 fallback behavior

If optional method data is absent:

- brainstorming and checklist derive from `topic_selection.candidates`;
- affinity diagram derives three generic clusters from candidates;
- SIPOC uses a safe default flow based on governance loop;
- Pareto derives from `current_state.problems` with placeholder values;
- subprocess flow uses a generic observe-diagnose-act-review chain;
- root-cause matrix derives from `key_factor_confirmation.factors` or cause-analysis dimensions;
- 5W derives from `countermeasures.items`.

Fallback content is for baseline draft generation only. Formal delivery still requires evidence-backed real data.
