#!/usr/bin/env bash
# Copy skills from this repository into an agent's skill directory.
#
#   ./scripts/install-skills.sh <target-dir> [skill ...]
#
# Examples:
#   ./scripts/install-skills.sh .agents/skills react-best-practices
#   ./scripts/install-skills.sh ~/.claude/skills brainstorming systematic-debugging
#   ./scripts/install-skills.sh .opencode/skills --all
set -euo pipefail

root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

if [ "$#" -lt 2 ]; then
  echo "usage: $0 <target-dir> <skill ...> | --all" >&2
  echo "example: $0 .agents/skills react-best-practices" >&2
  exit 1
fi

target="$1"
shift
mkdir -p "$target"

if [ "$1" = "--all" ]; then
  count=0
  for dir in "$root"/*/; do
    name="$(basename "$dir")"
    case "$name" in
      scripts|node_modules) continue ;;
    esac
    cp -r "$dir" "$target/"
    count=$((count + 1))
  done
  echo "copied $count skills to $target"
  exit 0
fi

for name in "$@"; do
  if [ ! -f "$root/$name/SKILL.md" ]; then
    echo "skip: $name (no SKILL.md)" >&2
    continue
  fi
  cp -r "$root/$name" "$target/"
  echo "copied $name"
done
