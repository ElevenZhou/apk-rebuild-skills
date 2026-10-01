#!/usr/bin/env bash
# Install apk-rebuild-skills via symlinks. Usage: bash install/install.sh [workbuddy] [claude] [codex]
set -euo pipefail
REPO="$(cd "$(dirname "$0")/.." && pwd)"
TARGETS=("${@:-workbuddy}")
for t in "${TARGETS[@]}"; do
  case "$t" in
    workbuddy) DST="$HOME/.workbuddy/skills" ;;
    claude)    DST="$HOME/.claude/skills" ;;
    codex)     DST="$HOME/.codex/skills" ;;
    *) echo "unknown target: $t"; continue ;;
  esac
  mkdir -p "$DST"
  for s in "$REPO"/skills/*/; do
    name="$(basename "$s")"
    link="$DST/$name"
    if [ -L "$link" ]; then rm "$link"
    elif [ -e "$link" ]; then mv "$link" "$link.bak-$(date +%Y%m%d%H%M%S)"; fi
    ln -s "${s%/}" "$link"
    echo "[$t] $name -> $link"
  done
done
echo "Done. Restart your agent tool. Update later with: git pull"
