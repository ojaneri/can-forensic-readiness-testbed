#!/usr/bin/env python3
"""Validate the SHA-256 hashes recorded in dataset/manifest.json.

Checks three groups:
  1. per-experiment files under dataset/experiments/ (manifest 'experiments');
  2. the combined normalized dataset (manifest 'combined_dataset');
  3. derived files listed in manifest 'derived_files' (paths relative to the repository root).
Exit status is 1 if any file is missing or differs from its recorded hash.
"""
from __future__ import annotations
import hashlib, json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]      # dataset/
REPO = ROOT.parent                              # repository root
manifest = json.loads((ROOT / 'manifest.json').read_text(encoding='utf-8'))


def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with p.open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


ok = True
checked = 0


def check(label: str, path: Path, expected: str) -> None:
    global ok, checked
    checked += 1
    if not path.is_file():
        print(f'FAIL {label}: missing')
        ok = False
        return
    got = sha256(path)
    if got != expected:
        print(f'FAIL {label}: {got} != {expected}')
        ok = False
    else:
        print(f'OK   {label}')


for exp, meta in manifest['experiments'].items():
    for name, info in meta['files'].items():
        check(f'{exp}/{name}', ROOT / 'experiments' / exp / name, info['sha256'])

combined = manifest.get('combined_dataset')
if combined:
    check(combined['path'], REPO / combined['path'], combined['sha256'])

for rel, info in manifest.get('derived_files', {}).items():
    check(rel, REPO / rel, info['sha256'])

print(f'checked {checked} files')
sys.exit(0 if ok else 1)
