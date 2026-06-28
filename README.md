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
