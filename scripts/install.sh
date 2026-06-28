#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(dirname "$SCRIPT_DIR")"
SKILLS_DIR="$REPO_ROOT/skills"
TARGET_DIR="$HOME/.claude/skills"

DRY_RUN=false
SINGLE_SKILL=""

for arg in "$@"; do
  case "$arg" in
    --dry-run) DRY_RUN=true ;;
    -*) echo "Unknown option: $arg"; exit 1 ;;
    *) SINGLE_SKILL="$arg" ;;
  esac
done

install_skill() {
  local skill_dir="$1"
  local skill_name="$(basename "$skill_dir")"
  local target="$TARGET_DIR/$skill_name"

  if [ "$DRY_RUN" = true ]; then
    echo "[dry-run] $skill_name -> $target"
    return
  fi

  mkdir -p "$target"
  cp -r "$skill_dir"/* "$target/"
  echo "[installed] $skill_name"
}

if [ -n "$SINGLE_SKILL" ]; then
  skill_path="$SKILLS_DIR/$SINGLE_SKILL"
  if [ ! -d "$skill_path" ]; then
    echo "Error: skill '$SINGLE_SKILL' not found in $SKILLS_DIR"
    exit 1
  fi
  install_skill "$skill_path"
else
  count=0
  for skill_dir in "$SKILLS_DIR"/*/; do
    [ -d "$skill_dir" ] || continue
    install_skill "$skill_dir"
    count=$((count + 1))
  done
  if [ "$DRY_RUN" = false ]; then
    echo ""
    echo "Done. $count skills installed to $TARGET_DIR"
  fi
fi
