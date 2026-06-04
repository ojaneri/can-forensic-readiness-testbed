#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import statistics
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SRC_EXP = ROOT / 'dataset' / 'experiments' / '008_external_icsim_replay'
OUT = ROOT / 'dataset' / 'experiments' / '009_icsim_spoof_injection'
FIELDNAMES = [
    'experiment_id', 'timestamp_epoch_s', 'relative_time_s', 'attack_label',
    'arbitration_id', 'dlc', 'payload_hex', 'semantic_label',
    'source_component', 'decoded_speed_kmh', 'notes'
]

# ICSim defaults from upstream source:
# speed ID 0x244, speed bytes 3 and 4; door ID 0x19B byte 2;
# turn signal ID 0x188 byte 0. We intentionally inject values matching
# this didactic mapping, not any production vehicle.
SPEED_ID = '244'
DOOR_ID = '19B'
SIGNAL_ID = '188'


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def speed_payload(speed: int, marker: int = 0xE9) -> str:
    # ICSim speed uses bytes 3 and 4 in little-endian-ish placement for default model.
    data = [0, 0, marker, speed & 0xFF, (speed >> 8) & 0xFF, 0xAA, 0x55, marker]
    return bytes(data).hex().upper()


def decode_icsim_speed(payload: str) -> int | None:
    try:
        b = bytes.fromhex(payload)
    except Exception:
        return None
    if len(b) >= 5:
        return b[3] | (b[4] << 8)
    return None


def door_payload(state: int, marker: int = 0xD9) -> str:
    data = [marker, 0, state & 0x0F, 0, 0, 0, 0, marker]
    return bytes(data).hex().upper()


def signal_payload(state: int, marker: int = 0xC9) -> str:
    data = [state & 0x03, marker, 0, 0, 0, 0, 0, marker]
    return bytes(data).hex().upper()


def load_external_rows(path: Path) -> list[dict]:
    with path.open(newline='', encoding='utf-8') as f:
        return list(csv.DictReader(f))


def inject_rows(base_rows: list[dict], intensity: str) -> tuple[list[dict], list[dict]]:
    config = {
        'low': {'start': 0.95, 'end': 1.65, 'period': 0.08, 'speed': 140},
        'medium': {'start': 0.85, 'end': 2.15, 'period': 0.04, 'speed': 190},
        'high': {'start': 0.75, 'end': 2.45, 'period': 0.02, 'speed': 230},
    }[intensity]
    out = []
    injected = []
    first_epoch = float(base_rows[0]['timestamp_epoch_s']) if base_rows else 0.0
    duration = float(base_rows[-1]['relative_time_s']) if base_rows else 0.0
    base_iter = iter(base_rows)
    pending = next(base_iter, None)
    inj_times = []
    t = config['start']
    tick = 0
    while t <= min(config['end'], duration):
        speed = config['speed'] + (tick % 5) * 3
        inj_times.append(('speed', t, speed))
        if tick % 5 == 0:
            inj_times.append(('door', t + 0.003, 0x00))  # doors unlocked marker in ICSim terms
        if tick % 7 == 0:
            inj_times.append(('signal', t + 0.006, 0x03))  # both turn signals marker
        t += config['period']
        tick += 1
    inj_times.sort(key=lambda x: x[1])

    def make_inj(kind: str, rel: float, value: int, seq: int) -> dict:
        if kind == 'speed':
            arb, payload, sem, dec = SPEED_ID, speed_payload(value), 'spoofed_icsim_speed', str(value)
            note = f'ATTACK spoofed ICSim speed={value}km/h intensity={intensity}'
        elif kind == 'door':
            arb, payload, sem, dec = DOOR_ID, door_payload(value), 'spoofed_icsim_doors', ''
            note = f'ATTACK spoofed ICSim doors_state=0x{value:X} intensity={intensity}'
        else:
            arb, payload, sem, dec = SIGNAL_ID, signal_payload(value), 'spoofed_icsim_turn_signals', ''
            note = f'ATTACK spoofed ICSim turn_signal_state=0x{value:X} intensity={intensity}'
        return {
            'experiment_id': '009_icsim_spoof_injection',
            'timestamp_epoch_s': f'{first_epoch + rel:.6f}',
            'relative_time_s': f'{rel:.6f}',
            'attack_label': 'spoofed_injection',
            'arbitration_id': arb,
            'dlc': '8',
            'payload_hex': payload,
            'semantic_label': sem,
            'source_component': f'icsim_spoof_injector_{intensity}',
            'decoded_speed_kmh': dec,
            'notes': note,
        }

    seq = 0
    for kind, rel, value in inj_times:
        while pending is not None and float(pending['relative_time_s']) <= rel:
            r = dict(pending)
            r['experiment_id'] = '009_icsim_spoof_injection'
            if r.get('attack_label') == 'external_replay':
                r['attack_label'] = 'external_replay_baseline'
            out.append(r)
            pending = next(base_iter, None)
        row = make_inj(kind, rel, value, seq)
        out.append(row)
        injected.append(row)
        seq += 1
    while pending is not None:
        r = dict(pending)
        r['experiment_id'] = '009_icsim_spoof_injection'
        if r.get('attack_label') == 'external_replay':
            r['attack_label'] = 'external_replay_baseline'
        out.append(r)
        pending = next(base_iter, None)
    out.sort(key=lambda r: (float(r['relative_time_s']), 0 if r['attack_label'] != 'spoofed_injection' else 1))
    return out, injected


def summarize(rows: list[dict], injected: list[dict], intensity: str, src_sha: str) -> dict:
    ids = Counter(r['arbitration_id'] for r in rows)
    labels = Counter(r['attack_label'] for r in rows)
    inj_ids = Counter(r['arbitration_id'] for r in injected)
    speeds = [float(r['decoded_speed_kmh']) for r in injected if r['semantic_label'] == 'spoofed_icsim_speed' and r['decoded_speed_kmh']]
    rel = [float(r['relative_time_s']) for r in rows]
    return {
        'experiment_id': '009_icsim_spoof_injection',
        'created_utc': now_iso(),
        'base_experiment': '008_external_icsim_replay',
        'base_source': 'ICSim/data/sample-can.log',
        'base_source_sha256': src_sha,
        'injection_intensity': intensity,
        'purpose': 'Visual and forensic-readiness demonstration of labeled spoof packet injection into an external ICSim trace; not a real vehicle attack.',
        'total_frames': len(rows),
        'base_frames': labels.get('external_replay_baseline', 0),
        'spoofed_frames': labels.get('spoofed_injection', 0),
        'duration_s': round(max(rel) - min(rel), 6) if rel else 0,
        'unique_arbitration_ids': len(ids),
        'label_counts': dict(labels),
        'top_arbitration_ids': ids.most_common(25),
        'injected_id_counts': dict(inj_ids),
        'injected_speed_stats': {
            'count': len(speeds),
            'min': min(speeds) if speeds else None,
            'max': max(speeds) if speeds else None,
            'mean': round(statistics.mean(speeds), 3) if speeds else None,
        },
        'icsim_semantics_used': {
            'speed': 'ID 0x244, bytes 3-4',
            'doors': 'ID 0x19B, byte 2',
            'turn_signals': 'ID 0x188, byte 0',
        },
        'boundary': 'Spoofed packets are controlled didactic injections into an external ICSim trace. They are labeled for visualization and workflow validation only.',
    }


def write_csv(path: Path, rows: list[dict]) -> None:
    with path.open('w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=FIELDNAMES)
        w.writeheader(); w.writerows(rows)


def write_report(summary: dict, path: Path) -> None:
    lines = [
        '# Experiment 009 — ICSim External Trace with Spoofed Packet Injection', '',
        '## Scope', '',
        'This package starts from the external ICSim sample trace imported in Experiment 008 and injects labeled spoofed packets using ICSim didactic semantics: speed, door status, and turn signals.', '',
        'It is designed for a visual dashboard demo and forensic workflow validation. It is not a real-vehicle attack and not an IDS benchmark.', '',
        '## Results', '',
        f"- Base frames: {summary['base_frames']}",
        f"- Spoofed frames: {summary['spoofed_frames']}",
        f"- Total frames: {summary['total_frames']}",
        f"- Duration: {summary['duration_s']} s",
        f"- Unique arbitration IDs: {summary['unique_arbitration_ids']}",
        f"- Injected ID counts: `{summary['injected_id_counts']}`",
        f"- Injected speed stats: `{summary['injected_speed_stats']}`", '',
        '## ICSim semantics used', '',
        '- Speed: ID `0x244`, bytes 3-4.',
        '- Doors: ID `0x19B`, byte 2.',
        '- Turn signals: ID `0x188`, byte 0.', '',
        '## Interpretation', '',
        'The experiment demonstrates that an external trace can be augmented with labeled didactic events while preserving base-source provenance, normalized evidence records, and SHA-256 manifests.', '',
        '## Boundary', '',
        summary['boundary'], ''
    ]
    path.write_text('\n'.join(lines), encoding='utf-8')


def write_html(summary: dict, path: Path) -> None:
    html = f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Experiment 009 — ICSim Spoof Injection</title><style>body{{font-family:Arial,sans-serif;max-width:980px;margin:32px auto;line-height:1.5;color:#0f172a}}a{{color:#075985}}.note{{background:#fef9c3;border:1px solid #fde68a;padding:12px;border-radius:8px}}</style></head><body><h1>Experiment 009 — ICSim Spoof Injection</h1><p class="note">Controlled didactic spoof injection into external ICSim trace. Not a real-vehicle attack or IDS benchmark.</p><ul><li>Base frames: <strong>{summary['base_frames']}</strong></li><li>Spoofed frames: <strong>{summary['spoofed_frames']}</strong></li><li>Total frames: <strong>{summary['total_frames']}</strong></li><li>Injected IDs: <code>{summary['injected_id_counts']}</code></li></ul><h2>Files</h2><ul><li><a href="frames_normalized.csv">frames_normalized.csv</a></li><li><a href="spoof_injection_plan.json">spoof_injection_plan.json</a></li><li><a href="spoofed_packets.csv">spoofed_packets.csv</a></li><li><a href="summary.json">summary.json</a></li><li><a href="findings.md">findings.md</a></li><li><a href="manifest.json">manifest.json</a></li></ul><p>Visual demo: <a href="../../../demo-icsim-spoof/">demo-icsim-spoof/</a></p></body></html>'''
    path.write_text(html, encoding='utf-8')


def main() -> int:
    ap = argparse.ArgumentParser(description='Create Experiment 009: inject labeled spoofed packets into external ICSim trace.')
    ap.add_argument('--intensity', choices=['low','medium','high'], default='medium')
    ap.add_argument('--outdir', default=str(OUT))
    args = ap.parse_args()
    out = Path(args.outdir); out.mkdir(parents=True, exist_ok=True)
    base_path = SRC_EXP / 'frames_normalized.csv'
    src_meta = json.loads((SRC_EXP / 'external_source_metadata.json').read_text())
    base = load_external_rows(base_path)
    rows, injected = inject_rows(base, args.intensity)
    write_csv(out / 'frames_normalized.csv', rows)
    write_csv(out / 'spoofed_packets.csv', injected)
    plan = {
        'experiment_id': '009_icsim_spoof_injection',
        'created_utc': now_iso(),
        'base_experiment': '008_external_icsim_replay',
        'base_source_metadata': src_meta,
        'intensity': args.intensity,
        'injected_semantics': {'speed_id':'0x244','door_id':'0x19B','turn_signal_id':'0x188'},
        'safety_boundary': 'software-only labeled packet injection for visualization and forensic workflow validation',
    }
    (out / 'spoof_injection_plan.json').write_text(json.dumps(plan, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    summary = summarize(rows, injected, args.intensity, src_meta['source_sha256'])
    (out / 'summary.json').write_text(json.dumps(summary, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    write_report(summary, out / 'findings.md')
    write_html(summary, out / 'index.html')
    manifest = {'schema':'software-defined-can-testbed.spoof-injection.v1','experiment_id':'009_icsim_spoof_injection','created_utc':now_iso(),'files':{}}
    for p in sorted(out.iterdir()):
        if p.is_file() and p.name != 'manifest.json':
            manifest['files'][p.name] = {'sha256': sha256_file(p), 'bytes': p.stat().st_size}
    (out / 'manifest.json').write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    print(json.dumps({'status':'ok','outdir':str(out),'base_frames':summary['base_frames'],'spoofed_frames':summary['spoofed_frames'],'total_frames':summary['total_frames']}, indent=2))
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
