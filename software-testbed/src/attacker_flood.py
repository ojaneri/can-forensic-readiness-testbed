#!/usr/bin/env python3
from __future__ import annotations

import argparse
import random
import time
import can


def main() -> int:
    p = argparse.ArgumentParser(description='Controlled flooding on vcan/SocketCAN for an availability experiment.')
    p.add_argument('--iface', default='vcan0')
    p.add_argument('--gap-ms', type=float, default=5.0, help='intervalo entre frames')
    p.add_argument('--duration', type=float, default=10.0)
    p.add_argument('--fixed-id', default='', help='opcional: ID fixo hex, ex 080')
    args = p.parse_args()

    end = time.time() + args.duration
    sent = 0
    fixed = int(args.fixed_id, 16) if args.fixed_id else None
    print(f'[flood] iface={args.iface} duration={args.duration}s gap={args.gap_ms}ms')
    with can.Bus(interface='socketcan', channel=args.iface, receive_own_messages=False) as bus:
        while time.time() < end:
            arb_id = fixed if fixed is not None else random.randrange(0x001, 0x7FF)
            data = bytes(random.randrange(256) for _ in range(8))
            bus.send(can.Message(arbitration_id=arb_id, is_extended_id=False, data=data), timeout=0.2)
            sent += 1
            time.sleep(args.gap_ms / 1000.0)
    print(f'[flood] frames_enviados={sent}')
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
