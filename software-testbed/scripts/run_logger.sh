#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PYTHON_BIN="$ROOT/.venv/bin/python3"
[[ -x "$PYTHON_BIN" ]] || PYTHON_BIN="python3"
IFACE="${1:-vcan0}"
OUTDIR="${2:-logs/session-$(date +%Y%m%d-%H%M%S)}"
mkdir -p "$OUTDIR"
"$PYTHON_BIN" "$ROOT/src/forensic_logger.py" --iface "$IFACE" --outdir "$OUTDIR"
