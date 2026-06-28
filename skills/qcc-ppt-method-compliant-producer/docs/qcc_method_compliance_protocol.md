# QCC Method Compliance Protocol

## 1. Core principle

QCC PPT delivery is not judged only by visual quality. It must also expose the required QCC methods in a form that reviewers can see immediately.

Therefore, every required method must satisfy three conditions:

1. **Title-visible**: method name appears in the slide title or subtitle.
2. **Form-visible**: the page uses the recognizable visual form of that method.
3. **Content-bounded**: business facts come from user input or evidence; unknown data is marked as `待补充`, not invented.

## 2. Mandatory method chain

```text
主题评审：头脑风暴 -> 亲和图 -> 检查表
把握现状：SIPOC -> 柏拉图（改进关键的 80%） -> 子流程图
根因分析：鱼骨图 + 矩阵图 -> 根因验证
拟定对策 / 实施：5W
成果固化：列表
```

## 3. Method-to-slide requirements

| Phase | Method | Slide title must include | Required visual form | Minimum content |
|---|---|---|---|---|
| 主题评审 | 头脑风暴 | `头脑风暴` | idea cards or idea list | >= 6 candidate ideas or placeholders |
| 主题评审 | 亲和图 | `亲和图` | clustered cards with group labels | >= 3 groups |
| 主题评审 | 检查表 | `检查表` | checklist / scoring table | criteria, score/pass state, conclusion |
| 把握现状 | SIPOC | `SIPOC` | 5-column SIPOC table | S/I/P/O/C columns |
| 把握现状 | 柏拉图 | `柏拉图` and `80%` | descending bar chart + cumulative line or 80% marker | issue category, count/impact, cumulative rate |
| 把握现状 | 子流程图 | `子流程图` | subprocess flowchart or swimlane | start, process steps, handoff, risk point |
| 根因分析 | 鱼骨图 | `鱼骨图` | fishbone diagram | main problem + cause branches |
| 根因分析 | 矩阵图 | `矩阵图` | cause evaluation matrix | cause rows + evaluation criteria columns |
| 根因分析 | 根因验证 | `根因验证` | evidence table | suspected cause, validation method, result |
| 拟定对策 | 5W | `5W` | action table | What/Why/Who/When/Where |
| 实施 | 5W | `5W` | execution tracking table | action, owner, date, status, evidence |
| 成果固化 | 列表 | `成果固化` or `标准化清单` | checklist/list | standard item, owner, effective date, tracking method |

## 4. Production rule

When generating a new deck, create all mandatory method pages first, then apply visual polish.

Recommended order:

1. Topic and background pages
2. 主题评审 method pages
3. Current-state method pages
4. Root-cause method pages
5. Countermeasure and implementation pages
6. Effect confirmation pages
7. Standardization and summary pages

## 5. Enhancement rule

When enhancing an existing deck:

1. Extract all slide titles.
2. Build a method coverage table.
3. Mark each required method as `FOUND`, `WEAK`, or `MISSING`.
4. For `MISSING`, add a new method page using the required visual form.
5. For `WEAK`, rebuild the page title and visual form.
6. Only after method coverage is complete, polish layout and visual details.

## 6. Missing data rule

If data is missing, do not remove the method page.

Use one of these patterns:

- `待补充：需要用户提供问题类别及频次数据`
- `待验证：需要补充验证样本或截图证据`
- `示例结构：仅保留方法框架，不填充业务结论`

This preserves audit form compliance while avoiding fabricated business facts.

## 7. Failure definition

The output is non-compliant if any of the following is true:

- Required method name does not appear in a visible slide title or subtitle.
- Required method appears only as a sentence, not as a recognizable method form.
- The deck has generic pages such as `问题分析` or `改进方案` but lacks the required QCC tool names.
- The deck is visually polished but fails the method coverage table.
