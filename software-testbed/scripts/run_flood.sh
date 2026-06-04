#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PYTHON_BIN="$ROOT/.venv/bin/python3"
[[ -x "$PYTHON_BIN" ]] || PYTHON_BIN="python3"
IFACE="${1:-vcan0}"
shift || true
"$PYTHON_BIN" "$ROOT/src/attacker_flood.py" --iface "$IFACE" "$@"
