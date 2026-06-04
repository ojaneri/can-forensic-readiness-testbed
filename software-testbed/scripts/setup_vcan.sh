#!/usr/bin/env bash
set -euo pipefail
IFACE="${1:-vcan0}"
if [[ ! "$IFACE" =~ ^vcan[0-9]+$ ]]; then
  echo "Error: for safety, this script only creates vcan* interfaces. Received: $IFACE" >&2
  exit 2
fi
if ip link show "$IFACE" >/dev/null 2>&1; then
  sudo ip link set "$IFACE" up
  echo "$IFACE already exists and is up"
  exit 0
fi
sudo modprobe vcan
sudo ip link add dev "$IFACE" type vcan
sudo ip link set up "$IFACE"
echo "Created $IFACE"
