#!/usr/bin/env python3
"""Import SocketCAN vcan candump capture into canonical evidence pipeline.

Creates Experiment 018 demonstrating kernel-level SocketCAN compatibility.
The candump log is parsed, normalized to the same CSV schema, and packaged
with manifest + summary + metadata.

Usage:
    python3 analysis/scripts/import_candump.py
"""

import csv, hashlib, json, re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EXP_DIR = ROOT / 'dataset' / 'experiments' / '018_vcan_socketcan_capture'
RAW_LOG = EXP_DIR / 'raw_candump.log'

SCHEMA = [
    'experiment_id', 'timestamp_epoch_s', 'relative_time_s', 'attack_label',
    'arbitration_id', 'dlc', 'payload_hex', 'semantic_label',
    'source_component', 'decoded_speed_kmh', 'notes'
]

# Pattern: (timestamp) interface can_id#payload
CANDUMP_PATTERN = re.compile(
    r'\((\d+\.\d+)\)\s+\S+\s+([0-9a-fA-F]+)#([0-9a-fA-F]+)'
)


def parse_candump_line(line: str):
    m = CANDUMP_PATTERN.match(line.strip())
    if not m:
        return None
    ts = float(m.group(1))
    can_id = m.group(2).upper()
    payload = m.group(3).upper()
    if not payload:
        return None
    dlc = len(payload) // 2
    payload_padded = payload.ljust(16, '0')[:16]  # pad to 8 bytes
    return {
        'timestamp': ts,
        'arbitration_id': can_id.lstrip('0') or '0',
        'dlc': min(dlc, 8),
        'payload_hex': payload_padded,
    }


def main():
    EXP_DIR.mkdir(parents=True, exist_ok=True)

    if not RAW_LOG.exists():
        print(f'[ERROR] {RAW_LOG} not found. Run candump capture first.')
        return

    print(f'Parsing {RAW_LOG}...')
    rows = []
    t0 = None
    skipped = 0

    with RAW_LOG.open() as f:
        for line in f:
            parsed = parse_candump_line(line)
            if parsed is None:
                skipped += 1
                continue
            if t0 is None:
                t0 = parsed['timestamp']

            rows.append({
                'experiment_id': '018_vcan_socketcan_capture',
                'timestamp_epoch_s': round(parsed['timestamp'], 6),
                'relative_time_s': round(parsed['timestamp'] - t0, 6),
                'attack_label': 'baseline',
                'arbitration_id': parsed['arbitration_id'],
                'dlc': parsed['dlc'],
                'payload_hex': parsed['payload_hex'],
                'semantic_label': 'SocketCAN kernel-level CAN traffic',
                'source_component': 'socketcan_vcan0',
                'decoded_speed_kmh': '',
                'notes': 'vcan0 via SocketCAN kernel module (candump)',
            })

    print(f'Parsed {len(rows)} frames ({skipped} skipped)')

    # Write normalized CSV
    csv_path = EXP_DIR / 'frames_normalized.csv'
    with csv_path.open('w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=SCHEMA)
        w.writeheader()
        w.writerows(rows)
    print(f'Written: {csv_path}')

    # Write annotated log
    ann_path = EXP_DIR / 'output_candump_annotated.log'
    with ann_path.open('w', encoding='utf-8') as f:
        for r in rows:
            f.write(f'{r["relative_time_s"]}\t{r["arbitration_id"]}\t{r["payload_hex"]}\t{r["attack_label"]}\n')
    print(f'Written: {ann_path}')

    # Summary
    ids = [r['arbitration_id'] for r in rows]
    unique_ids = len(set(ids))
    id_counts = Counter(ids).most_common(10)
    payload_lens = [r['dlc'] for r in rows]
    mean_dlc = sum(payload_lens) / len(payload_lens) if payload_lens else 0

    timestamps = sorted([r['relative_time_s'] for r in rows])
    iats = [timestamps[i+1] - timestamps[i] for i in range(len(timestamps)-1)]
    mean_iat = sum(iats) / len(iats) if iats else 0
    max_iat = max(iats) if iats else 0
    min_iat = min(iats) if iats else 0
    neg_iats = sum(1 for x in iats if x < 0)
    duration = timestamps[-1] - timestamps[0] if len(timestamps) > 1 else 0
    frame_rate = len(rows) / duration if duration > 0 else 0

    summary = {
        'experiment_id': '018_vcan_socketcan_capture',
        'total_frames': len(rows),
        'unique_arbitration_ids': unique_ids,
        'top_arbitration_ids': [{'id': k, 'count': v} for k, v in id_counts],
        'duration_s': round(duration, 6),
        'mean_inter_arrival_s': round(mean_iat, 6),
        'min_inter_arrival_s': round(min_iat, 6),
        'max_inter_arrival_s': round(max_iat, 6),
        'negative_inter_arrivals': neg_iats,
        'mean_dlc': round(mean_dlc, 4),
        'mean_frame_rate_fps': round(frame_rate, 3),
        'interface': 'vcan0',
        'driver': 'SocketCAN kernel module (can/vcan)',
        'capture_tool': 'candump (can-utils)',
        'notes': 'Kernel-level CAN traffic via SocketCAN vcan interface. Confirms pipeline works with real socket CAN, not just python-can virtual bus.',
    }
    (EXP_DIR / 'summary.json').write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + '\n')
    print(f'Written: {EXP_DIR / "summary.json"}')

    # Source metadata
    with RAW_LOG.open('rb') as f:
        sha256 = hashlib.sha256(f.read()).hexdigest()
    meta = {
        'source_file': 'raw_candump.log',
        'capture_command': 'candump vcan0 -n 2000',
        'generator_command': 'cangen vcan0 -g 10 -I 100 -D 1122334455667788 -L 8',
        'interface': 'vcan0',
        'source_sha256': sha256,
        'experiment_id': '018_vcan_socketcan_capture',
        'date': '2026-07-06',
    }
    (EXP_DIR / 'external_source_metadata.json').write_text(
        json.dumps(meta, indent=2, ensure_ascii=False) + '\n')

    # Manifest
    manifest = {}
    for fpath in sorted(EXP_DIR.iterdir()):
        if fpath.is_file() and fpath.name not in ('manifest.json',):
            h = hashlib.sha256(fpath.read_bytes()).hexdigest()
            manifest[fpath.name] = h
    manifest['_comment'] = 'SHA-256 hashes of experiment output files'
    (EXP_DIR / 'manifest.json').write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + '\n')

    print(f'\n=== Done ===')
    print(f'{len(rows)} frames, {unique_ids} unique IDs, {duration:.3f}s, {frame_rate:.0f} fps')
    print(f'Negative IATs: {neg_iats}')


if __name__ == '__main__':
    main()
