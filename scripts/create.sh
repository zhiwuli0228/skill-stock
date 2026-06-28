#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(dirname "$SCRIPT_DIR")"
TEMPLATE="$REPO_ROOT/templates/SKILL.md.template"

if [ $# -lt 1 ]; then
  echo "Usage: bash scripts/create.sh <skill-name>"
  exit 1
fi

SKILL_NAME="$1"
SKILL_DIR="$REPO_ROOT/skills/$SKILL_NAME"

if [ -d "$SKILL_DIR" ]; then
  echo "Error: skill '$SKILL_NAME' already exists"
  exit 1
fi

mkdir -p "$SKILL_DIR"
sed "s/<skill-name>/$SKILL_NAME/g" "$TEMPLATE" > "$SKILL_DIR/SKILL.md"

echo "Created: skills/$SKILL_NAME/SKILL.md"
echo "Edit the file to fill in your skill definition."
