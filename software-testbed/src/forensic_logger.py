#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import signal
import subprocess
import time
from pathlib import Path

import can
from can_common import host_info, run_cmd, sha256_file, utc_now_iso, write_manifest

RUN = True

def stop(*_):
    global RUN
    RUN = False


def main() -> int:
    p = argparse.ArgumentParser(description='Logger forense CAN para vcan/SocketCAN.')
    p.add_argument('--iface', default='vcan0')
    p.add_argument('--outdir', required=True)
    p.add_argument('--duration', type=float, default=0, help='0 = until Ctrl+C')
    args = p.parse_args()

    signal.signal(signal.SIGINT, stop)
    signal.signal(signal.SIGTERM, stop)

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    csv_path = outdir / 'frames.csv'
    raw_path = outdir / 'candump.log'
    manifest_path = outdir / 'manifest.json'

    started = utc_now_iso()
    start_ts = time.time()
    frames = 0

    print(f'[logger] capturando {args.iface} em {outdir}; Ctrl+C para parar')
    with can.Bus(interface='socketcan', channel=args.iface, receive_own_messages=True) as bus, \
         csv_path.open('w', newline='', encoding='utf-8') as csv_f, \
         raw_path.open('w', encoding='utf-8') as raw_f:
        writer = csv.DictWriter(csv_f, fieldnames=['timestamp','relative_s','iface','arbitration_id_hex','dlc','data_hex','is_extended_id','is_error_frame','is_remote_frame'])
        writer.writeheader()
        while RUN:
            if args.duration and (time.time() - start_ts) >= args.duration:
                break
            msg = bus.recv(timeout=0.5)
            if msg is None:
                continue
            rel = time.time() - start_ts
            data_hex = msg.data.hex().upper()
            line = f'({msg.timestamp:.6f}) {args.iface} {msg.arbitration_id:03X}#{data_hex}\n'
            raw_f.write(line)
            writer.writerow({
                'timestamp': f'{msg.timestamp:.6f}',
                'relative_s': f'{rel:.6f}',
                'iface': args.iface,
                'arbitration_id_hex': f'{msg.arbitration_id:X}',
                'dlc': msg.dlc,
                'data_hex': data_hex,
                'is_extended_id': int(msg.is_extended_id),
                'is_error_frame': int(msg.is_error_frame),
                'is_remote_frame': int(msg.is_remote_frame),
            })
            frames += 1
            if frames % 100 == 0:
                csv_f.flush(); raw_f.flush()

    ended = utc_now_iso()
    manifest = {
        'schema': 'software-can-testbed.manifest.v1',
        'started_utc': started,
        'ended_utc': ended,
        'iface': args.iface,
        'outdir': str(outdir),
        'frames': frames,
        'host': host_info(),
        'interface_details': run_cmd(['ip', '-details', 'link', 'show', args.iface]),
        'files': {
            'candump.log': {'sha256': sha256_file(raw_path), 'bytes': raw_path.stat().st_size},
            'frames.csv': {'sha256': sha256_file(csv_path), 'bytes': csv_path.stat().st_size},
        },
        'notes': 'Capture performed in a SocketCAN/vcan environment unless otherwise stated.',
    }
    write_manifest(manifest_path, manifest)
    print(f'[logger] frames={frames}; manifest={manifest_path}')
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
