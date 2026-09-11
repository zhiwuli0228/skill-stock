# skill-stock

Claude Code 自定义 Skill 仓库 — 集中管理、版本控制、批量安装。

## 快速开始

```bash
# 查看所有可用 skills
bash scripts/list.sh

# 安装全部 skills 到 ~/.claude/skills/
bash scripts/install.sh

# 安装单个 skill
bash scripts/install.sh <skill-name>

# 创建新 skill
bash scripts/create.sh <skill-name>
```

## 添加新 Skill

1. 运行 `bash scripts/create.sh my-skill` 生成模板
2. 编辑 `skills/my-skill/SKILL.md` 填写内容
3. 运行 `bash scripts/install.sh my-skill` 安装
4. 在 Claude Code 中用 `/my-skill` 测试

## 目录结构

```
skills/                        — 所有 skill 定义
  └── <skill-name>/SKILL.md   — 单个 skill
scripts/                       — 管理脚本
templates/                     — 新 skill 模板
CLAUDE.md                      — 项目规范
```

## 已收录 Skill

| Skill | 说明 |
|---|---|
| `explain-code` | 代码讲解类 skill |
| `qcc-ppt-baseline-producer` | QCC PPT 基线生产 skill（模板、版式、渲染与格式修复） |
| `qcc-ppt-method-compliant-producer` | **v5.0**：按标准品管圈十步法生产/增强 PPT；合规检查为结构化分析链校验（主题评价、查检表、柏拉图、目标设定、真因验证、对策评价、效果确认、标准化、检讨与改进），只有方法名词、没有数据的 PPT 会被判 `NON-COMPLIANT` |

## Skill 规范

每个 skill 是一个包含 `SKILL.md` 的目录，使用 YAML frontmatter：

```yaml
---
name: my-skill
description: Use when <触发条件>
allowed-tools: Bash, Read, Grep, Glob
argument-hint: <参数提示>
---
```
