# skill-stock

Claude Code 自定义 Skill 仓库。集中管理、版本控制、批量安装 skills。

## 项目结构

```
skills/<skill-name>/SKILL.md   — skill 定义（每个 skill 一个目录）
scripts/install.sh             — 安装 skills 到 ~/.claude/skills/
scripts/list.sh                — 列出所有可用 skills
templates/SKILL.md.template    — 新 skill 模板
```

## Skill 规范

### 命名
- 目录名：小写字母 + 连字符（如 `my-cool-skill`）
- SKILL.md frontmatter `name` 字段必须与目录名一致

### Frontmatter 字段

| 字段 | 必填 | 说明 |
|------|------|------|
| `name` | 是 | skill 标识，即斜杠命令名 |
| `description` | 是 | 触发条件描述，以 "Use when..." 开头 |
| `allowed-tools` | 否 | 允许使用的工具列表，逗号分隔 |
| `argument-hint` | 否 | 参数提示（如 `[dry-run\|commit]`） |

### 新增 Skill
1. 复制模板：`cp templates/SKILL.md.template skills/<name>/SKILL.md`
2. 填写 frontmatter 和正文
3. 运行 `scripts/install.sh <name>` 安装到本地
4. 在 Claude Code 中用 `/<name>` 测试

## 常用命令

```bash
# 列出所有 skills
bash scripts/list.sh

# 安装所有 skills 到 ~/.claude/skills/
bash scripts/install.sh

# 安装单个 skill
bash scripts/install.sh <skill-name>

# 预览安装（不实际复制）
bash scripts/install.sh --dry-run
```
