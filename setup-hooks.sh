#!/usr/bin/env bash
# ──────────────────────────────────────────────────
# Setup script – configures git to use .githooks/
# Run once after cloning:   bash setup-hooks.sh
# ──────────────────────────────────────────────────

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

echo "🔧 Configuring git to use .githooks/ directory…"
git config core.hooksPath .githooks

# Ensure the hook is executable (matters on macOS / Linux)
chmod +x .githooks/pre-commit 2>/dev/null || true

echo "✅ Done! The pre-commit hook will now run tests before every commit."
echo "   To skip tests for a WIP commit:  git commit --no-verify"
