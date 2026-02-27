#!/bin/bash
set -euo pipefail

# Only run in remote Claude Code on the web environments
if [ "${CLAUDE_CODE_REMOTE:-}" != "true" ]; then
  exit 0
fi

cd "${CLAUDE_PROJECT_DIR:-$(git rev-parse --show-toplevel)}"

# Install dev dependencies if pyproject.toml exists
if [ -f "pyproject.toml" ]; then
  echo "Installing dev dependencies..."
  pip install -e ".[dev]" --quiet
else
  echo "No pyproject.toml found, skipping dependency install."
fi
