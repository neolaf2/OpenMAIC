#!/usr/bin/env bash
set -euo pipefail

REPO_DIR="$(cd "$(dirname "$0")/../../.." && pwd)"
HARNESS_DIR="$REPO_DIR/agent-harness"
VENV_BIN="$HARNESS_DIR/.venv/bin"
CLI="$VENV_BIN/cli-anything-openmaic"

if [[ ! -x "$CLI" ]]; then
  echo "ERROR: cli-anything-openmaic is not installed at $CLI" >&2
  echo "Hint: cd $HARNESS_DIR && python3 -m venv .venv && . .venv/bin/activate && python -m pip install -U pip && python -m pip install -e . pytest" >&2
  exit 1
fi

exec "$CLI" --repo "$REPO_DIR" "$@"
