#!/usr/bin/env bash
# ============================================================
# run.sh — Start the Research Update Bot
# ============================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

VENV_DIR="$SCRIPT_DIR/.venv"
PYTHON="${VENV_DIR}/bin/python"
PIP="${VENV_DIR}/bin/pip"

# ------------------------------------------------------------
# 1. Create virtualenv if it doesn't exist
# ------------------------------------------------------------
if [ ! -f "$PYTHON" ]; then
    echo "[setup] Creating virtual environment at $VENV_DIR ..."
    python3 -m venv "$VENV_DIR"
fi

# ------------------------------------------------------------
# 2. Install / upgrade dependencies
# ------------------------------------------------------------
echo "[setup] Installing dependencies from requirements.txt ..."
"$PIP" install --quiet --upgrade pip
"$PIP" install --quiet -r requirements.txt

# ------------------------------------------------------------
# 3. Launch the bot
# ------------------------------------------------------------
echo "[bot] Starting Research Update Bot ..."
exec "$PYTHON" research_bot.py "$@"
