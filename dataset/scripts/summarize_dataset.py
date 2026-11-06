#!/usr/bin/env python3
from __future__ import annotations
import csv, json, statistics
from collections import Counter, defaultdict
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
rows=list(csv.DictReader((ROOT/'all_frames_normalized.csv').open(newline='',encoding='utf-8')))
phase=Counter(r['attack_label'] for r in rows)
ids=Counter(r['arbitration_id'] for r in rows).most_common(20)
speed=defaultdict(list)
for r in rows:
 # Decode speed from ID 0x100 frames outside the flooding phase. Random flooding can collide with
 # arbitration ID 0x100 and yields absurd first-byte values, so flooding-phase frames are excluded;
 # spoofing frames of every experiment, including Matrix 007, are kept.
 if (
  r['arbitration_id'].upper()=='100'
  and r['decoded_speed_kmh']
  and r['attack_label']!='flooding'
 ):
  speed[r['attack_label']].append(float(r['decoded_speed_kmh']))
out={'total_frames':len(rows),'phase_counts':dict(phase),'top_arbitration_ids':ids,'speed_stats_by_phase_for_id_0x100':{k:{'count':len(v),'min':min(v),'max':max(v),'mean':round(statistics.mean(v),2)} for k,v in speed.items()}}
print(json.dumps(out,indent=2))
