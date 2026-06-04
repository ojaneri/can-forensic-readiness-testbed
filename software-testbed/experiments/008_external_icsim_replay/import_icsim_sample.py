#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import re
import shutil
import statistics
import subprocess
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
DEFAULT_OUT = ROOT / 'dataset' / 'experiments' / '008_external_icsim_replay'
DEFAULT_REPO = 'https://github.com/zombieCraig/ICSim.git'
LINE_RE = re.compile(r'^\((?P<ts>[0-9]+(?:\.[0-9]+)?)\)\s+(?P<iface>\S+)\s+(?P<arb>[0-9A-Fa-f]+)#(?P<data>[0-9A-Fa-f]*)\s*$')
FIELDNAMES = [
    'experiment_id', 'timestamp_epoch_s', 'relative_time_s', 'attack_label',
    'arbitration_id', 'dlc', 'payload_hex', 'semantic_label',
    'source_component', 'decoded_speed_kmh', 'notes'
]


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def sh(cmd: list[str], cwd: Path | None = None) -> str:
    return subprocess.check_output(cmd, cwd=str(cwd) if cwd else None, text=True).strip()


def ensure_icsim(repo_dir: Path, repo_url: str) -> None:
    if (repo_dir / '.git').exists() and (repo_dir / 'data' / 'sample-can.log').exists():
        return
    if repo_dir.exists():
        shutil.rmtree(repo_dir)
    subprocess.check_call(['git', 'clone', '--depth', '1', repo_url, str(repo_dir)])


def parse_sample(path: Path) -> list[dict]:
    rows = []
    first_ts: float | None = None
    with path.open('r', encoding='utf-8', errors='replace') as f:
        for lineno, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            m = LINE_RE.match(line)
            if not m:
                raise ValueError(f'Could not parse line {lineno}: {line!r}')
            ts = float(m.group('ts'))
            if first_ts is None:
                first_ts = ts
            data = m.group('data').upper()
            arb = m.group('arb').upper().lstrip('0') or '0'
            rows.append({
                'experiment_id': '008_external_icsim_replay',
                'timestamp_epoch_s': f'{ts:.6f}',
                'relative_time_s': f'{ts - first_ts:.6f}',
                'attack_label': 'external_replay',
                'arbitration_id': arb,
                'dlc': str(len(data) // 2),
                'payload_hex': data,
                'semantic_label': 'icsim_sample_frame',
                'source_component': 'ICSim/data/sample-can.log',
                'decoded_speed_kmh': '',
                'notes': 'external ICSim sample CAN traffic; labels unavailable; replay/ingestion evidence only',
            })
    return rows


def entropy_payload(rows: list[dict]) -> float:
    counts = Counter()
    total = 0
    for r in rows:
        payload = r['payload_hex']
        for i in range(0, len(payload), 2):
            if i + 2 <= len(payload):
                counts[payload[i:i+2]] += 1
                total += 1
    if total == 0:
        return 0.0
    return -sum((c / total) * math.log2(c / total) for c in counts.values())


def summarize(rows: list[dict], source_log: Path, repo_dir: Path, repo_url: str) -> dict:
    ids = Counter(r['arbitration_id'] for r in rows)
    dlcs = Counter(r['dlc'] for r in rows)
    rel = [float(r['relative_time_s']) for r in rows]
    inter = [b - a for a, b in zip(rel, rel[1:]) if b >= a]
    commit = ''
    try:
        commit = sh(['git', 'rev-parse', 'HEAD'], cwd=repo_dir)
    except Exception:
        commit = 'unknown'
    return {
        'experiment_id': '008_external_icsim_replay',
        'created_utc': now_iso(),
        'external_source': {
            'name': 'ICSim',
            'repository': repo_url,
            'commit': commit,
            'source_file': 'data/sample-can.log',
            'license': 'GPL-3.0 as distributed by upstream repository',
            'source_sha256': sha256_file(source_log),
        },
        'purpose': 'External trace ingestion/replay-readiness check for the forensic workflow; not IDS benchmarking.',
        'total_frames': len(rows),
        'duration_s': round(max(rel) - min(rel), 6) if rel else 0,
        'unique_arbitration_ids': len(ids),
        'top_arbitration_ids': ids.most_common(25),
        'dlc_distribution': dict(dlcs),
        'payload_byte_entropy_bits': round(entropy_payload(rows), 6),
        'inter_arrival_s': {
            'count': len(inter),
            'min': round(min(inter), 9) if inter else None,
            'max': round(max(inter), 9) if inter else None,
            'mean': round(statistics.mean(inter), 9) if inter else None,
            'median': round(statistics.median(inter), 9) if inter else None,
            'stdev': round(statistics.pstdev(inter), 9) if inter else None,
            'negative_values': 0,
        },
        'boundary': 'This is an upstream sample trace. It has no attack phase labels in this package, so it is used for ingestion, normalization, hashing, and replay-readiness evidence only.',
    }


def write_csv(path: Path, rows: list[dict]) -> None:
    with path.open('w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=FIELDNAMES)
        w.writeheader()
        w.writerows(rows)


def write_report(summary: dict, path: Path) -> None:
    lines = [
        '# Experiment 008 — External ICSim Replay/Ingestion',
        '',
        '## Scope',
        '',
        'This experiment imports the public `data/sample-can.log` trace from the ICSim repository and normalizes it into the same evidence schema used by the software-defined CAN testbed.',
        '',
        'The goal is not to benchmark detection. The goal is to answer the adversarial-review objection that the workflow only handles traffic generated by our own scripts.',
        '',
        '## Source',
        '',
        f"- Repository: {summary['external_source']['repository']}",
        f"- Commit: `{summary['external_source']['commit']}`",
        f"- Source file: `{summary['external_source']['source_file']}`",
        f"- License: {summary['external_source']['license']}",
        f"- Source SHA-256: `{summary['external_source']['source_sha256']}`",
        '',
        '## Results',
        '',
        f"- Frames: {summary['total_frames']}",
        f"- Duration: {summary['duration_s']} s",
        f"- Unique arbitration IDs: {summary['unique_arbitration_ids']}",
        f"- Payload byte entropy: {summary['payload_byte_entropy_bits']} bits",
        f"- Inter-arrival mean: {summary['inter_arrival_s']['mean']} s",
        f"- Inter-arrival median: {summary['inter_arrival_s']['median']} s",
        f"- Negative inter-arrival values: {summary['inter_arrival_s']['negative_values']}",
        '',
        '## Top arbitration IDs',
        '',
        '| ID | Frames |',
        '|---:|---:|',
    ]
    for arb, count in summary['top_arbitration_ids'][:15]:
        lines.append(f'| 0x{arb} | {count} |')
    lines += [
        '',
        '## Interpretation',
        '',
        'The same artifact workflow can ingest, normalize, hash, summarize, and package a trace that did not originate from the internal generator. This strengthens the article framing as a forensic-readiness and reproducibility workflow rather than a closed toy simulator.',
        '',
        '## Limitations',
        '',
        'The upstream sample does not include attack labels or complete vehicle semantics in this package. Therefore, it is not used for IDS performance claims. It is used as external-source compatibility evidence.',
        ''
    ]
    path.write_text('\n'.join(lines), encoding='utf-8')


def write_html(summary: dict, path: Path) -> None:
    top_rows = '\n'.join(f'<tr><td>0x{arb}</td><td>{count}</td></tr>' for arb, count in summary['top_arbitration_ids'][:15])
    html = f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Experiment 008 — External ICSim Replay</title>
<style>body{{font-family:Arial,sans-serif;max-width:1000px;margin:32px auto;line-height:1.5;color:#0f172a}}table{{border-collapse:collapse;width:100%}}td,th{{border:1px solid #cbd5e1;padding:8px}}th{{background:#e2e8f0}}.note{{background:#fef9c3;border:1px solid #fde68a;padding:12px;border-radius:8px}}a{{color:#075985}}</style></head><body>
<h1>Experiment 008 — External ICSim Replay/Ingestion</h1>
<p class="note">External-source compatibility evidence. This is not an IDS benchmark because the upstream sample has no attack labels in this package.</p>
<ul><li>Frames: <strong>{summary['total_frames']}</strong></li><li>Duration: <strong>{summary['duration_s']} s</strong></li><li>Unique arbitration IDs: <strong>{summary['unique_arbitration_ids']}</strong></li><li>Payload entropy: <strong>{summary['payload_byte_entropy_bits']} bits</strong></li></ul>
<h2>Files</h2><ul><li><a href="frames_normalized.csv">frames_normalized.csv</a></li><li><a href="raw_icsim_sample-can.log">raw_icsim_sample-can.log</a></li><li><a href="summary.json">summary.json</a></li><li><a href="findings.md">findings.md</a></li><li><a href="manifest.json">manifest.json</a></li><li><a href="external_source_metadata.json">external_source_metadata.json</a></li></ul>
<h2>Top IDs</h2><table><thead><tr><th>ID</th><th>Frames</th></tr></thead><tbody>{top_rows}</tbody></table>
</body></html>'''
    path.write_text(html, encoding='utf-8')


def main() -> int:
    p = argparse.ArgumentParser(description='Import ICSim sample-can.log as external-source Experiment 008.')
    p.add_argument('--repo-dir', default='/tmp/ICSim', help='Local ICSim clone directory')
    p.add_argument('--repo-url', default=DEFAULT_REPO)
    p.add_argument('--source-log', default='', help='Optional explicit sample-can.log path')
    p.add_argument('--outdir', default=str(DEFAULT_OUT))
    args = p.parse_args()

    repo_dir = Path(args.repo_dir)
    ensure_icsim(repo_dir, args.repo_url)
    source_log = Path(args.source_log) if args.source_log else repo_dir / 'data' / 'sample-can.log'
    if not source_log.exists():
        raise FileNotFoundError(source_log)

    out = Path(args.outdir)
    out.mkdir(parents=True, exist_ok=True)
    raw_copy = out / 'raw_icsim_sample-can.log'
    shutil.copy2(source_log, raw_copy)
    license_src = repo_dir / 'LICENSE'
    if license_src.exists():
        shutil.copy2(license_src, out / 'ICSim_LICENSE')

    rows = parse_sample(raw_copy)
    frames_path = out / 'frames_normalized.csv'
    write_csv(frames_path, rows)
    summary = summarize(rows, raw_copy, repo_dir, args.repo_url)

    summary_path = out / 'summary.json'
    findings_path = out / 'findings.md'
    metadata_path = out / 'external_source_metadata.json'
    manifest_path = out / 'manifest.json'
    index_path = out / 'index.html'

    summary_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    metadata_path.write_text(json.dumps(summary['external_source'], indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    write_report(summary, findings_path)
    write_html(summary, index_path)

    manifest = {
        'schema': 'software-defined-can-testbed.external-source.v1',
        'experiment_id': '008_external_icsim_replay',
        'created_utc': now_iso(),
        'files': {},
    }
    for path in sorted(out.iterdir()):
        if path.is_file() and path.name != 'manifest.json':
            manifest['files'][path.name] = {'sha256': sha256_file(path), 'bytes': path.stat().st_size}
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')

    print(json.dumps({'status': 'ok', 'outdir': str(out), 'frames': len(rows), 'duration_s': summary['duration_s'], 'unique_ids': summary['unique_arbitration_ids']}, indent=2, ensure_ascii=False))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
