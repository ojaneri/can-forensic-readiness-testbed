#!/usr/bin/env python3
from __future__ import annotations
import hashlib, json, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def sha256(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for chunk in iter(lambda:f.read(1024*1024), b''): h.update(chunk)
 return h.hexdigest()
manifest=json.loads((ROOT/'manifest.json').read_text())
ok=True
for exp,meta in manifest['experiments'].items():
 for name,info in meta['files'].items():
  p=ROOT/'experiments'/exp/name
  got=sha256(p)
  if got != info['sha256']:
   print(f'FAIL {exp}/{name}: {got} != {info["sha256"]}')
   ok=False
  else:
   print(f'OK   {exp}/{name}')
sys.exit(0 if ok else 1)
