#!/usr/bin/env bash
set -euo pipefail
IFACE="${1:-vcan0}"
LOGFILE="${2:-}"
if [[ -z "$LOGFILE" || ! -f "$LOGFILE" ]]; then
  echo "Uso: $0 vcan0 caminho/para/candump.log" >&2
  exit 2
fi
canplayer -I "$LOGFILE" "$IFACE=$IFACE"
