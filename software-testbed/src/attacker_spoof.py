#!/usr/bin/env python3
from __future__ import annotations

import argparse
import time
import can
from can_common import parse_hex_data


def main() -> int:
    p = argparse.ArgumentParser(description='Envia frames CAN fabricados/spoofing em ambiente vcan/SocketCAN.')
    p.add_argument('--iface', default='vcan0')
    p.add_argument('--id', default='188', help='arbitration id em hex ou decimal, ex: 188 ou 0x188')
    p.add_argument('--data', default='000000C800000000', help='payload hex up to 8 bytes')
    p.add_argument('--period', type=float, default=0.05)
    p.add_argument('--count', type=int, default=20)
    args = p.parse_args()

    arb_id = int(args.id, 0) if args.id.startswith('0x') else int(args.id, 16)
    data = parse_hex_data(args.data)

    print(f'[spoof] iface={args.iface} id=0x{arb_id:X} data={data.hex()} count={args.count}')
    with can.Bus(interface='socketcan', channel=args.iface, receive_own_messages=False) as bus:
        for i in range(args.count):
            msg = can.Message(arbitration_id=arb_id, is_extended_id=False, data=data)
            bus.send(msg, timeout=0.2)
            time.sleep(args.period)
    print('[spoof] completed')
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
