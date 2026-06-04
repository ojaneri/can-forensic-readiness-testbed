#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import os
import platform
import socket
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Iterable, Optional


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode('utf-8')).hexdigest()


def run_cmd(cmd: list[str]) -> Dict[str, object]:
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        return {
            'cmd': cmd,
            'returncode': p.returncode,
            'stdout': p.stdout.strip(),
            'stderr': p.stderr.strip(),
        }
    except Exception as exc:
        return {'cmd': cmd, 'error': repr(exc)}


def host_info() -> Dict[str, object]:
    return {
        'hostname': socket.gethostname(),
        'platform': platform.platform(),
        'python': platform.python_version(),
        'cwd': os.getcwd(),
    }


def write_manifest(path: Path, manifest: Dict[str, object]) -> None:
    path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')


def parse_hex_data(hex_data: str) -> bytes:
    clean = hex_data.replace(' ', '').replace(':', '').replace('-', '')
    if len(clean) % 2:
        raise ValueError('hex data must have an even number of characters')
    if len(clean) > 16:
        raise ValueError('classic CAN allows up to 8 bytes / 16 hex chars')
    return bytes.fromhex(clean)
