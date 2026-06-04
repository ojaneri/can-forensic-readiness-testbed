#!/usr/bin/env bash
set -euo pipefail
cat <<'TXT'
This script installs dependencies for the software-defined CAN testbed:
- can-utils
- python3/pip/venv
- optional build dependencies for ICSim
TXT
sudo apt update
sudo apt install -y can-utils python3 python3-pip python3-venv git build-essential libsdl2-dev libsdl2-image-dev
python3 -m venv .venv
. .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
cat <<'TXT'
Python dependencies installed in .venv.
To activate:
  source .venv/bin/activate
TXT
