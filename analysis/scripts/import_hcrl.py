#!/usr/bin/env python3
"""Import HCRL Car-Hacking Dataset into the canonical evidence pipeline.

Creates Experiment 013 (normal run) and Experiment 014 (DoS attack) with
the same schema, manifest, and summary format as internal experiments.
The HCRL dataset contains real OBD-II CAN traffic from a Hyundai vehicle.

Usage:
    python3 analysis/scripts/import_hcrl.py
"""

import csv, hashlib, json, math, sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / 'raw'
OUT = ROOT / 'dataset' / 'experiments'
HCRL_LICENSE = """HCRL Car-Hacking Dataset (c) Korea University, Hacking and Countermeasure Research Lab.
Used for academic purposes per original terms.
Source: https://ocslab.hksecurity.net/Datasets/car-hacking-dataset
Reference: H. M. Song, J. Woo, H. K. Kim, "In-vehicle network intrusion detection using deep convolutional neural network," Vehicular Communications 21, 100198, 2020."""

SCHEMA = [
    'experiment_id', 'timestamp_epoch_s', 'relative_time_s', 'attack_label',
    'arbitration_id', 'dlc', 'payload_hex', 'semantic_label',
    'source_component', 'decoded_speed_kmh', 'notes'
]

HCRL_LABEL_MAP = {
    'normal': 'normal',
    'dos': 'flooding',
    'fuzzy': 'fuzzy',
    'gear': 'spoofing',  # Spoofing the drive gear
    'rpm': 'spoofing',   # Spoofing RPM gauge
}

# Row counts published on the HCRL page (used only to report the import is complete).
OFFICIAL_ROWS = {
    'dos': 3665771,
    'fuzzy': 3838860,
    'gear': 4443142,
    'rpm': 4621702,
}

EXP_IDS = {
    'normal': '013_hcrl_normal',
    'dos': '014_hcrl_dos',
    'fuzzy': '015_hcrl_fuzzy',
    'gear': '016_hcrl_gear_spoof',
    'rpm': '017_hcrl_rpm_spoof',
}

SOURCE_FILES = {
    'normal': 'normal_run_data.7z',  # downloaded separately
    'dos': 'DoS_dataset.csv',
    'fuzzy': 'Fuzzy_dataset.csv',
    'gear': 'gear_dataset.csv',
    'rpm': 'RPM_dataset.csv',
}


def parse_hcrl_value(raw: str):
    """HCRL CSV rows are comma-separated values without header.
    Fields: Timestamp, CAN ID, DLC, DATA[0..DLC-1], Flag.
    Frames with DLC < 8 carry only DLC data fields (for example DLC 2 or 5),
    so the payload is taken as exactly DLC bytes and the flag follows them.
    """
    parts = raw.strip().split(',')
    if len(parts) < 4:
        return None
    try:
        ts = float(parts[0])
        can_id = parts[1].strip().upper()
        dlc = int(parts[2])
        if not 0 <= dlc <= 8 or len(parts) < 3 + dlc:
            return None
        data_bytes = parts[3:3 + dlc]
        payload = ''.join(b.strip().zfill(2) for b in data_bytes)
        flag = parts[3 + dlc].strip().upper() if len(parts) > 3 + dlc else 'R'
        return {
            'timestamp': ts,
            'arbitration_id': can_id,
            'dlc': dlc,
            'payload_hex': payload,
            'flag': flag,
        }
    except (ValueError, IndexError):
        return None


def import_hcrl(in_path: Path, exp_id: str, label: str, max_frames: int = None):
    """Import one HCRL CSV into canonical experiment format."""
    print(f'  Importing {in_path.name} → {exp_id} ({label})')
    out_dir = OUT / exp_id
    out_dir.mkdir(parents=True, exist_ok=True)

    rows = []
    skipped = 0
    rows_read = 0
    t0 = None

    with in_path.open(newline='', encoding='utf-8', errors='replace') as f:
        for i, line in enumerate(f):
            if max_frames and i >= max_frames:
                break
            rows_read = i + 1
            parsed = parse_hcrl_value(line)
            if parsed is None:
                skipped += 1
                continue
            if t0 is None:
                t0 = parsed['timestamp']
            ts = parsed['timestamp']
            attack = 'normal' if parsed['flag'] == 'R' else label
            semantic_map = {
                'dos': 'DoS attack (ID 0x000 flood)',
                'fuzzy': 'Fuzzy attack (random IDs/data)',
                'gear': 'Gear spoofing attack',
                'rpm': 'RPM gauge spoofing attack',
                'normal': 'Normal driving CAN traffic',
            }
            source_map = {
                'dos': 'hcrl_dos_attack',
                'fuzzy': 'hcrl_fuzzy_attack',
                'gear': 'hcrl_gear_spoof',
                'rpm': 'hcrl_rpm_spoof',
                'normal': 'hcrl_normal_driving',
            }
            rows.append({
                'experiment_id': exp_id,
                'timestamp_epoch_s': round(ts, 6),
                'relative_time_s': round(ts - t0, 6),
                'attack_label': HCRL_LABEL_MAP.get(attack, attack),
                'arbitration_id': parsed['arbitration_id'].lstrip('0').upper() or '0',
                'dlc': parsed['dlc'],
                'payload_hex': parsed['payload_hex'],
                'semantic_label': semantic_map.get(attack, attack),
                'source_component': source_map.get(label, 'hcrl_unknown'),
                'decoded_speed_kmh': '',
                'notes': f'HCRL dataset: {label}',
            })

    if not rows:
        print(f'    [SKIP] No valid rows found')
        return

    # Write normalized CSV
    csv_path = out_dir / 'frames_normalized.csv'
    with csv_path.open('w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=SCHEMA)
        w.writeheader()
        w.writerows(rows)
    print(f'    {len(rows)} rows written to {csv_path}')

    # Write raw log (first 1000 lines as sample)
    raw_sample_path = out_dir / 'raw_sample.log'
    with in_path.open(newline='', encoding='utf-8', errors='replace') as f:
        with raw_sample_path.open('w', encoding='utf-8') as out:
            for _ in range(2000):
                out.write(f.readline())
    print(f'    Raw sample written to {raw_sample_path}')

    # Source metadata
    with in_path.open('rb') as f:
        sha256 = hashlib.sha256()
        while True:
            chunk = f.read(65536)
            if not chunk:
                break
            sha256.update(chunk)
        source_hash = sha256.hexdigest()

    meta = {
        'name': 'HCRL Car-Hacking Dataset',
        'source_file': in_path.name,
        'source_sha256': source_hash,
        'label': label,
        'license': 'Academic use per HCRL terms',
        'reference': 'https://ocslab.hksecurity.net/Datasets/car-hacking-dataset',
        'original_vehicle': 'Hyundai (OBD-II port)',
        'experiment_id': exp_id,
    }
    meta_path = out_dir / 'external_source_metadata.json'
    meta_path.write_text(json.dumps(meta, indent=2, ensure_ascii=False) + '\n')

    # Summary
    ids = [r['arbitration_id'] for r in rows]
    unique_ids = len(set(ids))
    id_counts = Counter(ids).most_common(10)
    payload_lens = [len(r['payload_hex']) // 2 for r in rows if r['payload_hex']]
    mean_dlc = sum(payload_lens) / len(payload_lens) if payload_lens else 0

    # Inter-arrival times
    timestamps = sorted([r['relative_time_s'] for r in rows])
    iats = [timestamps[i+1] - timestamps[i] for i in range(len(timestamps)-1)]
    mean_iat = sum(iats) / len(iats) if iats else 0
    max_iat = max(iats) if iats else 0
    min_iat = min(iats) if iats else 0
    neg_iats = sum(1 for x in iats if x < 0)

    duration = timestamps[-1] - timestamps[0] if len(timestamps) > 1 else 0
    frame_rate = len(rows) / duration if duration > 0 else 0

    summary = {
        'experiment_id': exp_id,
        'label': label,
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
        'attack_frames': sum(1 for r in rows if r['attack_label'] != 'normal'),
        'normal_frames': sum(1 for r in rows if r['attack_label'] == 'normal'),
        'label_type': HCRL_LABEL_MAP.get(label, label),
    }
    summary['rows_read'] = rows_read
    summary['rows_skipped_malformed'] = skipped
    summary['short_dlc_rows'] = sum(1 for r in rows if r['dlc'] < 8)
    summary['official_rows_expected'] = OFFICIAL_ROWS.get(label)
    summary_path = out_dir / 'summary.json'
    summary_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + '\n')

    # Manifest (SHA-256 of each output file)
    manifest = {}
    for fpath in sorted(out_dir.iterdir()):
        if fpath.is_file() and fpath.name != 'manifest.json':
            h = hashlib.sha256(fpath.read_bytes()).hexdigest()
            manifest[fpath.name] = h
    manifest['_comment'] = 'SHA-256 hashes of experiment output files'
    manifest_path = out_dir / 'manifest.json'
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + '\n')

    print(f'    Summary: {len(rows)} frames, {unique_ids} unique IDs, '
          f'{duration:.1f}s duration, {frame_rate:.0f} fps')
    print(f'    Attack frames: {summary["attack_frames"]}')
    print(f'    Manifest: {len(manifest)-1} files hashed')

    return summary


def main():
    print('=== HCRL Car-Hacking Dataset Import ===')
    print(f'Source: {RAW}')
    summaries = []

    # Import each HCRL CSV
    # normal_run_data.7z needs extraction - skip for now, import labeled sets
    for label in ['dos', 'fuzzy', 'gear', 'rpm']:
        src = RAW / SOURCE_FILES[label]
        if not src.exists():
            print(f'  [SKIP] {src} not found')
            continue
        exp_id = EXP_IDS[label]
        summary = import_hcrl(src, exp_id, label)
        if summary:
            summaries.append(summary)

    print(f'\n=== Import Complete ===')
    for s in summaries:
        print(f'  {s["experiment_id"]}: {s["total_frames"]} frames, '
              f'{s["duration_s"]:.0f}s, {s["unique_arbitration_ids"]} IDs')

    # Write combined summary
    all_s = {
        'source': 'HCRL Car-Hacking Dataset',
        'experiments': summaries,
        'total_frames_imported': sum(s['total_frames'] for s in summaries),
        'total_duration_s': round(sum(s['duration_s'] for s in summaries), 1),
    }
    print(f'\nTotal: {all_s["total_frames_imported"]} frames imported')


if __name__ == '__main__':
    main()
