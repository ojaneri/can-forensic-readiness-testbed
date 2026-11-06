#!/usr/bin/env python3
"""Import varied SocketCAN vcan capture (Exp. 019) - multi-ID realistic traffic.

Usage:
    python3 analysis/scripts/import_vcan_varied.py
"""
import csv, hashlib, json, re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EXP_DIR = ROOT / 'dataset' / 'experiments' / '019_vcan_varied_traffic'
RAW_LOG = EXP_DIR / 'raw_candump.log'
SCHEMA = ['experiment_id', 'timestamp_epoch_s', 'relative_time_s', 'attack_label',
          'arbitration_id', 'dlc', 'payload_hex', 'semantic_label',
          'source_component', 'decoded_speed_kmh', 'notes']
CANDUMP_PATTERN = re.compile(r'\((\d+\.\d+)\)\s+\S+\s+([0-9a-fA-F]+)#([0-9a-fA-F]*)')

rows = []
t0 = None
with RAW_LOG.open() as f:
    for line in f:
        m = CANDUMP_PATTERN.match(line.strip())
        if not m:
            continue
        ts = float(m.group(1))
        can_id = m.group(2).upper()
        payload = m.group(3).upper()
        if t0 is None: t0 = ts
        dlc = min(len(payload)//2, 8)
        payload_padded = payload.ljust(16, '0')[:16]
        rows.append({'experiment_id': '019_vcan_varied_traffic',
            'timestamp_epoch_s': round(ts, 6),
            'relative_time_s': round(ts - t0, 6),
            'attack_label': 'baseline',
            'arbitration_id': can_id.lstrip('0') or '0',
            'dlc': max(dlc, 1),
            'payload_hex': payload_padded,
            'semantic_label': 'SocketCAN multi-ID kernel traffic',
            'source_component': 'socketcan_vcan0',
            'decoded_speed_kmh': '',
            'notes': 'vcan0 via SocketCAN, varied IDs 0x100-0x3FF'})

# Write CSV
csv_path = EXP_DIR / 'frames_normalized.csv'
with csv_path.open('w', newline='', encoding='utf-8') as f:
    w = csv.DictWriter(f, fieldnames=SCHEMA)
    w.writeheader(); w.writerows(rows)

# Summary
ids = [r['arbitration_id'] for r in rows]
unique_ids = len(set(ids))
id_counts = Counter(ids).most_common(10)
timestamps = sorted([r['relative_time_s'] for r in rows])
iats = [timestamps[i+1]-timestamps[i] for i in range(len(timestamps)-1)]
mean_iat = sum(iats)/len(iats) if iats else 0
duration = timestamps[-1]-timestamps[0] if len(timestamps)>1 else 0
neg_iats = sum(1 for x in iats if x < 0)
summary = {
    'experiment_id': '019_vcan_varied_traffic',
    'total_frames': len(rows),
    'unique_arbitration_ids': unique_ids,
    'top_arbitration_ids': [{'id': k, 'count': v} for k,v in id_counts],
    'duration_s': round(duration, 6),
    'mean_inter_arrival_s': round(mean_iat, 6),
    'negative_inter_arrivals': neg_iats,
    'mean_frame_rate_fps': round(len(rows)/duration, 3) if duration else 0,
    'channels': ['vcan0'],
    'capture_tool': 'candump (can-utils)',
    'generator': 'cangen vcan0 -g 5 -I 100-3FF -D i -L 8',
    'notes': 'Multi-ID SocketCAN traffic. Confirms the pipeline handles kernel-level CAN with varied arbitration IDs.'
}
(EXP_DIR / 'summary.json').write_text(json.dumps(summary, indent=2)+'\n')

# Metadata
with RAW_LOG.open('rb') as f:
    sha256 = hashlib.sha256(f.read()).hexdigest()
(EXP_DIR / 'external_source_metadata.json').write_text(json.dumps({
    'source_file': 'raw_candump.log',
    'source_sha256': sha256,
    'experiment_id': '019_vcan_varied_traffic',
    'interface': 'vcan0',
    'driver': 'SocketCAN kernel module',
}, indent=2)+'\n')

# Manifest
manifest = {}
for fpath in sorted(EXP_DIR.iterdir()):
    if fpath.is_file() and fpath.name != 'manifest.json':
        manifest[fpath.name] = hashlib.sha256(fpath.read_bytes()).hexdigest()
(EXP_DIR / 'manifest.json').write_text(json.dumps(manifest, indent=2)+'\n')

print(f'Done: {len(rows)} frames, {unique_ids} unique IDs, {duration:.2f}s, {neg_iats} negative IAT')
