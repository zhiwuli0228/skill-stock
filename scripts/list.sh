#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(dirname "$SCRIPT_DIR")"
SKILLS_DIR="$REPO_ROOT/skills"

echo "Available skills in skill-stock:"
echo "================================"

count=0
for skill_dir in "$SKILLS_DIR"/*/; do
  [ -d "$skill_dir" ] || continue
  skill_file="$skill_dir/SKILL.md"
  name="$(basename "$skill_dir")"

  if [ -f "$skill_file" ]; then
    desc="$(sed -n '/^description:/s/^description: *//p' "$skill_file" | head -1)"
    printf "  %-30s %s\n" "$name" "$desc"
  else
    printf "  %-30s %s\n" "$name" "(no SKILL.md found)"
  fi
  count=$((count + 1))
done

if [ "$count" -eq 0 ]; then
  echo "  (none)"
fi

echo ""
echo "Total: $count skills"
