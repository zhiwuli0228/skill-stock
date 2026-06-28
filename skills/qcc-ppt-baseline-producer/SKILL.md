---
name: qcc-ppt-baseline-producer
version: "2.9.0"
description: Produce a baseline QCC PPT from user-provided QCC data and an optional PPT template. If no data is provided, output a complete empty QCC presentation template with placeholders. Designed for lower-capability agents that need a strict, low-freedom workflow, now with mandatory QCC method pages and formal-review-safe visual patterns.
license: MIT
compatibility: Requires Python 3.10+, python-pptx, PyYAML, LibreOffice for render checks.
metadata:
  author: qcc-ppt-production
  baseline_role: low-capability-agent
  template_mode: default-template-with-user-override
  method_mode: mandatory-qcc-method-pages
---

# QCC PPT Baseline Producer Skill

## 1. Positioning

This Skill is a **baseline QCC PPT production capability package**. It is not a project-data container and not a free-form PPT beautifier.

It provides:

- default PPT template;
- complete QCC empty presentation template;
- QCC page structure;
- mandatory QCC method pages;
- formal-review-safe method visual patterns;
- page-type rules;
- validation, build, lint, method-compliance and render scripts.

The user provides:

- real project content;
- QCC data;
- evidence files;
- optional custom PPT template.

If the user provides no QCC data, the Skill must **only generate an empty QCC PPT template with placeholders**. It must not invent business content.

## 2. Directory Boundary

### Skill directory stores capability assets only

```text
qcc-ppt-baseline-producer/
├── SKILL.md
├── README.md
├── docs/
├── config/
├── scripts/
├── templates/
│   ├── template_light_16_9.pptx
│   └── qcc-empty-template.pptx
├── examples/
└── workspace-template/
```

### Workspace stores task assets

Create a workspace outside the Skill directory:

```text
qcc-workspace/
├── input/
│   ├── qcc-data.yaml
│   ├── evidence-index.yaml
│   └── source-materials/
├── template/
│   └── company-template.pptx        # optional
├── output/
└── reports/
```

Do not put real project data into the Skill directory.

## 3. Mandatory QCC Method Chain

For formal QCC decks, the generated PPT must include recognizable method pages, not only attractive generic pages.

Required chain:

```text
主题评审：头脑风暴 -> 亲和图 -> 检查表
把握现状：SIPOC -> 柏拉图（改进关键的 80%） -> 子流程图
根因分析：鱼骨图 + 矩阵图 -> 根因验证
拟定对策 / 实施：5W
成果固化：标准化清单 / 列表
```

Method title and visual form are both required. A title such as `主题评审｜头脑风暴` is insufficient if the slide is only paragraph text.

Read before generation:

```text
docs/qcc_method_compliance_protocol.md
docs/qcc_page_contract.md
docs/qcc_method_visual_patterns.md
docs/qcc_format_diagnosis_and_repair.md
```

## 4. Formal-Review-Safe Method Formats

### 4.1 Head brainstorming page

Use the v2.9 safe layout:

```text
[left topic anchor]    [idea card 1] [idea card 2] [idea card 3]
                       [idea card 4] [idea card 5] [idea card 6]
[bottom divergence conclusion]
```

Do not use loose radial lines or connector-heavy mind maps for ordinary agents. Rendered screenshots often show line clutter and weak alignment.

### 4.2 Ranking summary card

For right-side TOP summary cards:

- score text must include suffix such as `24分`;
- score box must be wide enough for two digits;
- explanatory notes must not sit inside the row stack;
- if space is insufficient, remove the note rather than shrinking fonts.

### 4.3 Dense method pages

- 5W pages should prefer compact action cards or short tables.
- Matrix pages should keep top causes only; full detail goes to reports/appendix.
- Standardization pages should use a checklist/list, not prose-only summary.

## 5. Template Rules

Template priority:

```text
user custom template > Skill default template
```

Rules:

1. If the user provides `qcc-workspace/template/company-template.pptx`, use it.
2. If the user does not provide a template, use `templates/template_light_16_9.pptx`.
3. If the user does not provide QCC data, output `templates/qcc-empty-template.pptx` to the requested output path.
4. Do not generate duplicate footer, logo, or brand elements on a branded template.

## 6. Input Modes

### Mode A: Data + custom template

```bash
python scripts/build_qcc_ppt.py \
  qcc-workspace/input/qcc-data.yaml \
  --template qcc-workspace/template/company-template.pptx \
  --output qcc-workspace/output/qcc-baseline.pptx
```

### Mode B: Data + default template

```bash
python scripts/build_qcc_ppt.py \
  qcc-workspace/input/qcc-data.yaml \
  --output qcc-workspace/output/qcc-baseline.pptx
```

### Mode C: No data

```bash
python scripts/build_qcc_ppt.py \
  --empty-template \
  --output qcc-workspace/output/qcc-empty-template.pptx
```

Equivalent shortcut:

```bash
python scripts/build_qcc_ppt.py \
  --output qcc-workspace/output/qcc-empty-template.pptx
```

## 7. Required Workflow for Lower-Capability Agents

Follow these steps exactly.

### Step 1. Prepare workspace

Create or use `qcc-workspace/`.

Put real files here:

```text
qcc-workspace/input/qcc-data.yaml
qcc-workspace/input/evidence-index.yaml
qcc-workspace/input/source-materials/
qcc-workspace/template/company-template.pptx    # optional
```

### Step 2. Validate data if data exists

```bash
python scripts/validate_qcc_data.py \
  qcc-workspace/input/qcc-data.yaml \
  --evidence qcc-workspace/input/evidence-index.yaml \
  --report qcc-workspace/reports/data-quality-report.md
```

If the user has not provided data, skip validation and generate the empty template.

### Step 3. Build PPT

With data:

```bash
python scripts/build_qcc_ppt.py \
  qcc-workspace/input/qcc-data.yaml \
  --template qcc-workspace/template/company-template.pptx \
  --output qcc-workspace/output/qcc-baseline.pptx
```

Without custom template, remove the `--template` line.

Without data:

```bash
python scripts/build_qcc_ppt.py \
  --empty-template \
  --output qcc-workspace/output/qcc-empty-template.pptx
```

### Step 4. Run structural checks

```bash
python scripts/layout_lint.py qcc-workspace/output/qcc-baseline.pptx --mode formal
python scripts/placeholder_lint.py qcc-workspace/output/qcc-baseline.pptx --mode formal
python scripts/check_qcc_method_compliance.py \
  qcc-workspace/output/qcc-baseline.pptx \
  --report qcc-workspace/reports/qcc-method-compliance-report.md
```

### Step 5. Run visual heuristics and render check

```bash
python scripts/audit_qcc_visual_heuristics.py \
  qcc-workspace/output/qcc-baseline.pptx \
  --report qcc-workspace/reports/qcc-visual-heuristics-report.md

python scripts/render_check.py \
  qcc-workspace/output/qcc-baseline.pptx \
  --out qcc-workspace/output/render
```

Open the rendered montage before delivery.

## 8. Baseline Acceptance Standard

The lower-capability agent must ensure:

- QCC structure is complete;
- mandatory QCC methods are visible in titles and recognizable in page format;
- no business data is invented;
- user data is used only from workspace input;
- default template is used when no custom template is given;
- empty template is output when no data is given;
- generated PPT has no obvious overlap, out-of-page shapes, unintentional placeholders, connector clutter, or ranking card score wrapping;
- rendered preview is produced for the next stronger agent or human reviewer.

This Skill produces a **method-compliant baseline deck**, not the final advanced visual design.
