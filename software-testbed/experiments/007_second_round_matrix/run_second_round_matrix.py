#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import random
import statistics
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
DATASET_ROOT = ROOT / 'dataset'
OUT_DIR = DATASET_ROOT / 'experiments' / '007_second_round_matrix'

FIELDNAMES = [
    'experiment_id', 'timestamp_epoch_s', 'relative_time_s', 'attack_label',
    'arbitration_id', 'dlc', 'payload_hex', 'semantic_label',
    'source_component', 'decoded_speed_kmh', 'notes'
]

EXPECTED_NORMAL_IDS = {'100', '120', '188', '300'}

SPOOF_PROFILES = {
    'low': {'period_s': 0.08, 'speed_min': 145, 'speed_max': 165, 'rpm': 3600, 'throttle': 72},
    'medium': {'period_s': 0.04, 'speed_min': 180, 'speed_max': 200, 'rpm': 4500, 'throttle': 90},
    'high': {'period_s': 0.02, 'speed_min': 210, 'speed_max': 240, 'rpm': 5200, 'throttle': 98},
}

FLOOD_PROFILES = {
    'low': {'period_s': 0.020},     # approx. 50 fps
    'medium': {'period_s': 0.010},  # approx. 100 fps
    'high': {'period_s': 0.005},    # approx. 200 fps
}

# Balanced 10-run matrix over the 3x3 intensity combinations, with one repeated
# medium/medium scenario for seed variability.
DEFAULT_MATRIX = [
    ('run_01', 'low', 'low'),
    ('run_02', 'low', 'medium'),
    ('run_03', 'low', 'high'),
    ('run_04', 'medium', 'low'),
    ('run_05', 'medium', 'medium'),
    ('run_06', 'medium', 'high'),
    ('run_07', 'high', 'low'),
    ('run_08', 'high', 'medium'),
    ('run_09', 'high', 'high'),
    ('run_10', 'medium', 'medium'),
]


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def payload_hex(data: list[int]) -> str:
    return bytes(data).hex().upper()


def speed_payload(speed: int, rpm: int = 1800, throttle: int = 30, temp: int = 86, fuel: int = 75) -> str:
    data = [speed & 0xFF, (speed >> 8) & 0xFF, rpm & 0xFF, (rpm >> 8) & 0xFF, throttle, temp, fuel, 0]
    return payload_hex(data)


def display_payload(speed: int, marker: int = 0) -> str:
    return payload_hex([0, 0, speed & 0xFF, (speed >> 8) & 0xFF, marker, 0, 0, 0])


def decode_speed_from_payload(hex_payload: str) -> int | None:
    if len(hex_payload) < 4:
        return None
    b = bytes.fromhex(hex_payload)
    return b[0] | (b[1] << 8)


def write_row(writer: csv.DictWriter, rows_for_summary: list[dict], row: dict) -> None:
    writer.writerow(row)
    rows_for_summary.append(row)


def add_normal_phase(writer: csv.DictWriter, rows: list[dict], *, exp_id: str, start_epoch: float, start_rel: float, duration_s: float, phase: str, rng: random.Random, normal_period_s: float) -> float:
    t = start_rel
    tick = 0
    while t < start_rel + duration_s - 1e-9:
        speed = int(60 + 25 * math.sin(t / 13) + 8 * math.sin(t / 3))
        rpm = int(1700 + 600 * math.sin(t / 7))
        throttle = int(max(0, min(100, 38 + 25 * math.sin(t / 9))))
        base = {
            'experiment_id': exp_id,
            'timestamp_epoch_s': f'{start_epoch + t:.6f}',
            'relative_time_s': f'{t:.6f}',
            'attack_label': phase,
            'dlc': '8',
        }
        write_row(writer, rows, {**base, 'arbitration_id': '100', 'payload_hex': speed_payload(speed, rpm, throttle), 'semantic_label': 'engine_cluster_state', 'source_component': 'simulated_engine_cluster', 'decoded_speed_kmh': str(speed), 'notes': 'engine_cluster_state'})
        write_row(writer, rows, {**base, 'arbitration_id': '120', 'payload_hex': '0000000000000000', 'semantic_label': 'body_status', 'source_component': 'simulated_body_status', 'decoded_speed_kmh': '', 'notes': 'body_status'})
        write_row(writer, rows, {**base, 'arbitration_id': '188', 'payload_hex': display_payload(speed), 'semantic_label': 'display_speed', 'source_component': 'simulated_dashboard_display', 'decoded_speed_kmh': '', 'notes': 'display_speed'})
        if tick % 8 == 0:
            write_row(writer, rows, {**base, 'arbitration_id': '300', 'payload_hex': payload_hex([rng.randrange(256) for _ in range(8)]), 'semantic_label': 'background_noise', 'source_component': 'background_noise_generator', 'decoded_speed_kmh': '', 'notes': 'background_noise'})
        tick += 1
        t += normal_period_s
    return start_rel + duration_s


def add_spoof_phase(writer: csv.DictWriter, rows: list[dict], *, exp_id: str, start_epoch: float, start_rel: float, duration_s: float, rng: random.Random, profile_name: str) -> float:
    profile = SPOOF_PROFILES[profile_name]
    t = start_rel
    tick = 0
    while t < start_rel + duration_s - 1e-9:
        speed = rng.randint(profile['speed_min'], profile['speed_max'])
        base = {
            'experiment_id': exp_id,
            'timestamp_epoch_s': f'{start_epoch + t:.6f}',
            'relative_time_s': f'{t:.6f}',
            'attack_label': 'spoofing',
            'dlc': '8',
        }
        write_row(writer, rows, {**base, 'arbitration_id': '100', 'payload_hex': speed_payload(speed, profile['rpm'], profile['throttle'], 91, 70), 'semantic_label': 'fabricated_engine_cluster_state', 'source_component': f'spoof_module_{profile_name}', 'decoded_speed_kmh': str(speed), 'notes': f'ATTACK spoof intensity={profile_name}'})
        write_row(writer, rows, {**base, 'arbitration_id': '188', 'payload_hex': display_payload(speed, 0xAA), 'semantic_label': 'fabricated_display_speed', 'source_component': f'spoof_module_{profile_name}', 'decoded_speed_kmh': '', 'notes': f'ATTACK display spoof intensity={profile_name}'})
        if tick % 10 == 0:
            write_row(writer, rows, {**base, 'arbitration_id': '120', 'payload_hex': '0100000000000000', 'semantic_label': 'fabricated_body_status', 'source_component': f'spoof_module_{profile_name}', 'decoded_speed_kmh': '', 'notes': f'ATTACK body marker intensity={profile_name}'})
        tick += 1
        t += profile['period_s']
    return start_rel + duration_s


def add_flood_phase(writer: csv.DictWriter, rows: list[dict], *, exp_id: str, start_epoch: float, start_rel: float, duration_s: float, rng: random.Random, profile_name: str) -> float:
    profile = FLOOD_PROFILES[profile_name]
    t = start_rel
    while t < start_rel + duration_s - 1e-9:
        arb = rng.randrange(0x001, 0x7FE)
        row = {
            'experiment_id': exp_id,
            'timestamp_epoch_s': f'{start_epoch + t:.6f}',
            'relative_time_s': f'{t:.6f}',
            'attack_label': 'flooding',
            'arbitration_id': f'{arb:X}',
            'dlc': '8',
            'payload_hex': payload_hex([rng.randrange(256) for _ in range(8)]),
            'semantic_label': 'high_cardinality_noise',
            'source_component': f'flood_module_{profile_name}',
            'decoded_speed_kmh': '',
            'notes': f'ATTACK controlled flooding intensity={profile_name}'
        }
        write_row(writer, rows, row)
        t += profile['period_s']
    return start_rel + duration_s


def summarize_run(exp_id: str, rows: list[dict], spoof_intensity: str, flood_intensity: str, seed: int, duration_s: float) -> dict:
    phase_counts = Counter(r['attack_label'] for r in rows)
    ids = Counter(r['arbitration_id'].upper() for r in rows)
    speed_by_phase = defaultdict(list)
    for r in rows:
        if r['arbitration_id'].upper() == '100' and r['decoded_speed_kmh']:
            speed_by_phase[r['attack_label']].append(float(r['decoded_speed_kmh']))
    speed_stats = {}
    for phase, values in speed_by_phase.items():
        speed_stats[phase] = {
            'count': len(values),
            'min': min(values),
            'max': max(values),
            'mean': round(statistics.mean(values), 3),
            'stdev': round(statistics.pstdev(values), 3),
        }
    flood_rows = [r for r in rows if r['attack_label'] == 'flooding']
    unknown_flood = sum(1 for r in flood_rows if r['arbitration_id'].upper() not in EXPECTED_NORMAL_IDS)
    return {
        'experiment_id': exp_id,
        'seed': seed,
        'duration_s': duration_s,
        'spoof_intensity': spoof_intensity,
        'flood_intensity': flood_intensity,
        'total_frames': len(rows),
        'phase_counts': dict(phase_counts),
        'top_arbitration_ids': ids.most_common(15),
        'unique_ids_total': len(ids),
        'unique_ids_flooding': len(set(r['arbitration_id'].upper() for r in flood_rows)),
        'unknown_id_ratio_flooding': round(unknown_flood / len(flood_rows), 6) if flood_rows else 0,
        'speed_stats_by_phase_for_id_0x100': speed_stats,
    }


def aggregate_summaries(summaries: list[dict]) -> dict:
    total_frames = sum(s['total_frames'] for s in summaries)
    phase_counts = Counter()
    for s in summaries:
        phase_counts.update(s['phase_counts'])
    by_combo = defaultdict(list)
    for s in summaries:
        by_combo[(s['spoof_intensity'], s['flood_intensity'])].append(s)
    combo_rows = []
    for (spoof, flood), items in sorted(by_combo.items()):
        combo_rows.append({
            'spoof_intensity': spoof,
            'flood_intensity': flood,
            'runs': len(items),
            'mean_total_frames': round(statistics.mean(i['total_frames'] for i in items), 3),
            'mean_flood_frames': round(statistics.mean(i['phase_counts'].get('flooding', 0) for i in items), 3),
            'mean_unique_ids_flooding': round(statistics.mean(i['unique_ids_flooding'] for i in items), 3),
            'mean_unknown_id_ratio_flooding': round(statistics.mean(i['unknown_id_ratio_flooding'] for i in items), 6),
            'mean_spoof_speed': round(statistics.mean(i['speed_stats_by_phase_for_id_0x100']['spoofing']['mean'] for i in items), 3),
        })
    return {
        'batch_id': '007_second_round_matrix',
        'created_utc': now_iso(),
        'method': 'deterministic fast-run event simulation; timestamps and relative timing are generated from the declared experiment schedule rather than real wall-clock waiting',
        'runs': len(summaries),
        'duration_per_run_s': 600,
        'total_synthetic_duration_s': sum(s['duration_s'] for s in summaries),
        'total_frames': total_frames,
        'phase_counts': dict(phase_counts),
        'matrix_summary': combo_rows,
        'run_summaries': summaries,
        'boundary': 'software-only authorized CAN traffic generation; not physical CAN fidelity or operational IDS benchmarking',
    }


def write_markdown_report(aggregate: dict, path: Path) -> None:
    lines = [
        '# Second Experimental Round — Matrix 007',
        '',
        '## Scope',
        '',
        'Authorized, software-only CAN traffic generation for the article testbed. This round uses deterministic fast-run event simulation: frame timestamps follow the declared schedule, but the script does not wait for ten real minutes per run.',
        '',
        '## Design',
        '',
        '- 10 runs of 600 s each.',
        '- Four phases per run: 180 s baseline, 120 s spoofing, 120 s flooding, 180 s recovery.',
        '- Spoofing intensity levels: low, medium, high.',
        '- Flooding intensity levels: low, medium, high.',
        '- One medium/medium repetition is included to show seed variability.',
        '',
        '## Aggregate results',
        '',
        f"- Total runs: {aggregate['runs']}",
        f"- Total synthetic duration: {aggregate['total_synthetic_duration_s']} s",
        f"- Total frames: {aggregate['total_frames']}",
        f"- Phase counts: `{aggregate['phase_counts']}`",
        '',
        '## Matrix summary',
        '',
        '| Spoof | Flood | Runs | Mean total frames | Mean flood frames | Mean unique flood IDs | Mean unknown-ID ratio | Mean spoof speed |',
        '|---|---:|---:|---:|---:|---:|---:|---:|',
    ]
    for row in aggregate['matrix_summary']:
        lines.append(f"| {row['spoof_intensity']} | {row['flood_intensity']} | {row['runs']} | {row['mean_total_frames']} | {row['mean_flood_frames']} | {row['mean_unique_ids_flooding']} | {row['mean_unknown_id_ratio_flooding']} | {row['mean_spoof_speed']} |")
    lines += [
        '',
        '## Interpretation',
        '',
        'This round strengthens the article by replacing a single demonstrative run with a controlled matrix. The resulting evidence supports discussion of parameter sensitivity, run-to-run reproducibility, and triage consistency under different spoofing and flooding intensities.',
        '',
        '## Limitation',
        '',
        'The data remains synthetic and software-defined. It validates the reproducible workflow, labels, evidence packaging, and preliminary triage logic; it does not validate electrical CAN behavior, ECU timing constraints, or real-vehicle attack performance.',
        ''
    ]
    path.write_text('\n'.join(lines), encoding='utf-8')


def write_index_html(aggregate: dict, path: Path) -> None:
    rows = '\n'.join(
        f"<tr><td>{r['spoof_intensity']}</td><td>{r['flood_intensity']}</td><td>{r['runs']}</td><td>{r['mean_total_frames']}</td><td>{r['mean_flood_frames']}</td><td>{r['mean_unique_ids_flooding']}</td><td>{r['mean_spoof_speed']}</td></tr>"
        for r in aggregate['matrix_summary']
    )
    html = f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Second Experimental Round — Matrix 007</title>
<style>body{{font-family:Arial,sans-serif;max-width:1100px;margin:32px auto;line-height:1.45;color:#0f172a}}table{{border-collapse:collapse;width:100%;margin:16px 0}}td,th{{border:1px solid #cbd5e1;padding:8px;text-align:left}}th{{background:#e2e8f0}}code{{background:#f1f5f9;padding:2px 4px;border-radius:4px}}.note{{background:#fef9c3;border:1px solid #fde68a;padding:12px;border-radius:8px}}</style>
</head><body>
<h1>Second Experimental Round — Matrix 007</h1>
<p class="note">Deterministic fast-run event simulation: timestamps follow a declared 10-minute schedule per run, but the generator does not wait for real wall-clock execution.</p>
<ul>
<li>Total runs: <strong>{aggregate['runs']}</strong></li>
<li>Total synthetic duration: <strong>{aggregate['total_synthetic_duration_s']} s</strong></li>
<li>Total frames: <strong>{aggregate['total_frames']}</strong></li>
<li>Boundary: software-only CAN simulation; not physical CAN fidelity.</li>
</ul>
<h2>Files</h2>
<ul>
<li><a href="second_round_frames_normalized.csv">second_round_frames_normalized.csv</a></li>
<li><a href="second_round_summary.json">second_round_summary.json</a></li>
<li><a href="second_round_summary.md">second_round_summary.md</a></li>
<li><a href="experiment_matrix.csv">experiment_matrix.csv</a></li>
<li><a href="manifest.json">manifest.json</a></li>
</ul>
<h2>Matrix summary</h2>
<table><thead><tr><th>Spoof</th><th>Flood</th><th>Runs</th><th>Mean total frames</th><th>Mean flood frames</th><th>Mean unique flood IDs</th><th>Mean spoof speed</th></tr></thead><tbody>
{rows}
</tbody></table>
</body></html>'''
    path.write_text(html, encoding='utf-8')


def main() -> int:
    parser = argparse.ArgumentParser(description='Generate second experimental round for the SSV 2026 software-defined CAN testbed article.')
    parser.add_argument('--outdir', default=str(OUT_DIR), help='Output directory for batch artifacts.')
    parser.add_argument('--seed-base', type=int, default=2026060407)
    parser.add_argument('--duration', type=float, default=600.0, help='Per-run synthetic duration in seconds.')
    args = parser.parse_args()

    out = Path(args.outdir)
    out.mkdir(parents=True, exist_ok=True)

    phase_plan = [('baseline', 180.0), ('spoofing', 120.0), ('flooding', 120.0), ('recovery', 180.0)]
    if args.duration != 600.0:
        scale = args.duration / 600.0
        phase_plan = [(name, dur * scale) for name, dur in phase_plan]

    matrix_path = out / 'experiment_matrix.csv'
    frames_path = out / 'second_round_frames_normalized.csv'
    summary_path = out / 'second_round_summary.json'
    report_path = out / 'second_round_summary.md'
    manifest_path = out / 'manifest.json'
    index_path = out / 'index.html'

    summaries = []
    with matrix_path.open('w', newline='', encoding='utf-8') as mf, frames_path.open('w', newline='', encoding='utf-8') as ff:
        matrix_writer = csv.DictWriter(mf, fieldnames=['experiment_id', 'seed', 'duration_s', 'baseline_s', 'spoofing_s', 'flooding_s', 'recovery_s', 'spoof_intensity', 'spoof_period_s', 'flood_intensity', 'flood_period_s'])
        frame_writer = csv.DictWriter(ff, fieldnames=FIELDNAMES)
        matrix_writer.writeheader()
        frame_writer.writeheader()

        for idx, (run_name, spoof_intensity, flood_intensity) in enumerate(DEFAULT_MATRIX, start=1):
            exp_id = f'007_matrix_{run_name}_{spoof_intensity}_spoof_{flood_intensity}_flood'
            seed = args.seed_base + idx
            rng = random.Random(seed)
            start_epoch = 1780600000.0 + idx * 10000
            rows_for_summary: list[dict] = []
            matrix_writer.writerow({
                'experiment_id': exp_id,
                'seed': seed,
                'duration_s': args.duration,
                'baseline_s': phase_plan[0][1],
                'spoofing_s': phase_plan[1][1],
                'flooding_s': phase_plan[2][1],
                'recovery_s': phase_plan[3][1],
                'spoof_intensity': spoof_intensity,
                'spoof_period_s': SPOOF_PROFILES[spoof_intensity]['period_s'],
                'flood_intensity': flood_intensity,
                'flood_period_s': FLOOD_PROFILES[flood_intensity]['period_s'],
            })
            t = 0.0
            t = add_normal_phase(frame_writer, rows_for_summary, exp_id=exp_id, start_epoch=start_epoch, start_rel=t, duration_s=phase_plan[0][1], phase='baseline', rng=rng, normal_period_s=0.05)
            t = add_spoof_phase(frame_writer, rows_for_summary, exp_id=exp_id, start_epoch=start_epoch, start_rel=t, duration_s=phase_plan[1][1], rng=rng, profile_name=spoof_intensity)
            t = add_flood_phase(frame_writer, rows_for_summary, exp_id=exp_id, start_epoch=start_epoch, start_rel=t, duration_s=phase_plan[2][1], rng=rng, profile_name=flood_intensity)
            t = add_normal_phase(frame_writer, rows_for_summary, exp_id=exp_id, start_epoch=start_epoch, start_rel=t, duration_s=phase_plan[3][1], phase='recovery', rng=rng, normal_period_s=0.05)
            summaries.append(summarize_run(exp_id, rows_for_summary, spoof_intensity, flood_intensity, seed, args.duration))

    aggregate = aggregate_summaries(summaries)
    summary_path.write_text(json.dumps(aggregate, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    write_markdown_report(aggregate, report_path)
    write_index_html(aggregate, index_path)

    manifest = {
        'schema': 'software-defined-can-testbed.second-round.v1',
        'batch_id': '007_second_round_matrix',
        'created_utc': now_iso(),
        'files': {}
    }
    for path in [matrix_path, frames_path, summary_path, report_path, index_path]:
        manifest['files'][path.name] = {'sha256': sha256_file(path), 'bytes': path.stat().st_size}
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')

    print(json.dumps({
        'status': 'ok',
        'outdir': str(out),
        'runs': aggregate['runs'],
        'total_frames': aggregate['total_frames'],
        'total_synthetic_duration_s': aggregate['total_synthetic_duration_s'],
    }, indent=2, ensure_ascii=False))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
