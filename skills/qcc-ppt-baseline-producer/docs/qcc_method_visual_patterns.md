# QCC Method Visual Patterns

## 1. 主题评审｜头脑风暴

Use idea cards or a radial idea board.

Required elements:

- Center topic or problem statement
- Candidate ideas around it
- No scoring in this page; scoring belongs to checklist or matrix

Avoid:

- Turning this page into generic paragraph text
- Hiding all ideas in a dense table

## 2. 主题评审｜亲和图

Use clustered sticky-card groups.

Required elements:

- Multiple idea cards
- Group labels
- Clear grouping logic

Recommended layout:

```text
Group A        Group B        Group C
[idea]         [idea]         [idea]
[idea]         [idea]         [idea]
```

## 3. 主题评审｜检查表

Use a criteria table.

Required columns:

- Candidate topic
- Importance
- Feasibility
- Urgency
- Data availability
- Final decision / score

## 4. 把握现状｜SIPOC

Use a five-column table.

Required columns:

- Supplier
- Input
- Process
- Output
- Customer

The process column may contain 3-6 high-level process steps.

## 5. 把握现状｜柏拉图：识别关键 80% 改进项

Use a Pareto visual.

Required elements:

- Issue categories sorted descending by count, impact, or loss
- Bars for count / impact
- Cumulative percentage line or cumulative percentage labels
- 80% reference marker
- Conclusion naming the vital few problems

If actual data is unavailable, keep a placeholder Pareto frame and state what data is missing.

## 6. 把握现状｜子流程图

Use a subprocess flowchart or swimlane.

Required elements:

- Start and end
- Process steps
- Decision / branch if applicable
- Pain points or abnormal points marked clearly

## 7. 根因分析｜鱼骨图

Use a fishbone diagram.

Recommended branch categories:

- 人 / People
- 机 / Machine or tool
- 料 / Material or input
- 法 / Method
- 环 / Environment
- 测 / Measurement

Use the user project context to rename categories when more appropriate.

## 8. 根因分析｜矩阵图

Use a scoring matrix.

Required columns:

- Suspected cause
- Impact
- Frequency
- Controllability
- Evidence availability
- Score / priority
- Keep or discard

The matrix must connect to the fishbone causes.

## 9. 根因验证

Use an evidence table.

Required columns:

- Suspected root cause
- Validation method
- Evidence / sample
- Result
- Conclusion

Do not claim a cause is verified without evidence or a clearly marked placeholder.

## 10. 拟定对策｜5W

Use a 5W action table.

Required columns:

- What: action
- Why: reason / linked root cause
- Who: owner
- When: deadline
- Where: scope / affected process

## 11. 实施跟踪｜5W

Use a 5W execution tracking table.

Required columns:

- What
- Who
- When
- Where
- Status / evidence

## 12. 成果固化｜标准化清单

Use a standardization list or checklist.

Required columns:

- Standardized item
- Document / rule / script / process
- Owner
- Effective date
- Follow-up check method

Avoid:

- Only writing `持续优化`
- Only showing a final achievement number without standardization actions

## 13. v4.2 formal-review hardening for brainstorming

For `主题评审｜头脑风暴`, visual elegance is not enough. In rendered screenshots, free-form radial diagrams often create hidden defects:

- diagonal connector clutter;
- center-card overlap with surrounding cards;
- excessive white space;
- weak alignment with the company template;
- awkward perception that the page is a mind-map rather than a QCC brainstorming output.

Preferred repair pattern:

```text
[发散主题 anchor]    [候选方向 1] [候选方向 2] [候选方向 3]
                    [候选方向 4] [候选方向 5] [候选方向 6]
[发散输出 conclusion]
```

Use this pattern when the user screenshot indicates visual looseness or connector-line defects.


## Ranking summary side-card pattern

When a QCC method page uses a right-side TOP ranking summary, use this formal-review-safe structure:

```text
TOP 课题摘要
[rank]  topic text                  24分
[rank]  topic text                  20分
[rank]  topic text                  18分

small note outside row stack
```

Rules:

- Rank badge: fixed color block, centered number.
- Topic text: one to two lines, no clipping.
- Score text: suffix with `分`, never vertical wrapping.
- Notes: outside the row stack; no overlap with any row.
- If the card is narrow, remove the note rather than reducing row readability.
