# QCC PPT Baseline Producer v2.9

本 Skill 面向能力较弱的 Agent，用于稳定生成 **QCC PPT 基线版**。v2.9 在 v2.8 的模板边界基础上，补齐了 QCC 常用方法页和正式评审版式门禁。

核心原则：

```text
Skill 放能力，不放真实项目数据。
用户提供内容；Skill 提供默认模板、空白 QCC 模板、脚本、方法页格式和验收规则。
```

## 一、什么时候用

| 场景 | 输出 |
|---|---|
| 有 QCC 数据 + 有自定义模板 | 使用用户模板生成方法合规基线 PPT |
| 有 QCC 数据 + 无自定义模板 | 使用 Skill 默认模板生成方法合规基线 PPT |
| 无 QCC 数据 | 输出完整 QCC 空白模板 |

## 二、v2.9 新增能力

强制生成/检查以下方法页：

```text
主题评审：头脑风暴 -> 亲和图 -> 检查表
把握现状：SIPOC -> 柏拉图（关键 80%） -> 子流程图
根因分析：鱼骨图 + 矩阵图 -> 根因验证
拟定对策 / 实施：5W
成果固化：标准化清单 / 列表
```

特别修复：

- 头脑风暴页不再使用松散放射连线，改为左侧主题锚点 + 右侧 2×3 候选方向卡片。
- 检查表 / 矩阵评分页的 TOP 摘要卡避免 `24`、`20`、`18` 等分数纵向换行。
- 5W、矩阵图、标准化清单等方法页默认采用正式评审更安全的紧凑结构。

## 三、不要这样做

不要把真实数据放进 Skill 目录：

```text
skills/qcc-ppt/input/qcc-data.yaml      # 不推荐
skills/qcc-ppt/output/final.pptx        # 不推荐
```

不要只生成“漂亮页面”而缺少方法形式：

```text
标题写了头脑风暴，但正文是普通段落        # 不合格
标题写了柏拉图，但没有柱形 + 累计/80%     # 不合格
标题写了5W，但没有 What/Why/Who/When/Where # 不合格
```

## 四、推荐工作区

在项目目录创建：

```text
qcc-workspace/
├── input/
│   ├── qcc-data.yaml
│   ├── evidence-index.yaml
│   └── source-materials/
├── template/
│   └── company-template.pptx        # 可选
├── output/
└── reports/
```

## 五、常用命令

### 1. 无数据：生成 QCC 空白模板

```bash
python scripts/build_qcc_ppt.py \
  --empty-template \
  --output qcc-workspace/output/qcc-empty-template.pptx
```

### 2. 有数据：使用默认模板

```bash
python scripts/build_qcc_ppt.py \
  qcc-workspace/input/qcc-data.yaml \
  --output qcc-workspace/output/qcc-baseline.pptx
```

### 3. 有数据：使用用户模板

```bash
python scripts/build_qcc_ppt.py \
  qcc-workspace/input/qcc-data.yaml \
  --template qcc-workspace/template/company-template.pptx \
  --output qcc-workspace/output/qcc-baseline.pptx
```

### 4. 方法覆盖检查

```bash
python scripts/check_qcc_method_compliance.py \
  qcc-workspace/output/qcc-baseline.pptx \
  --report qcc-workspace/reports/qcc-method-compliance-report.md
```

### 5. 视觉启发式检查 + 渲染

```bash
python scripts/audit_qcc_visual_heuristics.py \
  qcc-workspace/output/qcc-baseline.pptx \
  --report qcc-workspace/reports/qcc-visual-heuristics-report.md

python scripts/render_check.py \
  qcc-workspace/output/qcc-baseline.pptx \
  --out qcc-workspace/output/render
```

## 六、交付物

低能力 Agent 至少输出：

```text
qcc-workspace/output/qcc-baseline.pptx
qcc-workspace/output/render/montage.png
qcc-workspace/reports/data-quality-report.md
qcc-workspace/reports/qcc-method-compliance-report.md
qcc-workspace/reports/qcc-visual-heuristics-report.md
```

## 七、边界

本 Skill 只负责生成 **方法合规的基线版**。高级视觉优化、精细排版和审美增强仍应交给更强 Agent 或人工复核。
