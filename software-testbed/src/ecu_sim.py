#!/usr/bin/env python3
from __future__ import annotations

import argparse
import math
import random
import signal
import time

import can

RUN = True

def stop(*_):
    global RUN
    RUN = False


def frame(arbitration_id: int, data: list[int]) -> can.Message:
    return can.Message(arbitration_id=arbitration_id, is_extended_id=False, data=bytearray(data))


def main() -> int:
    parser = argparse.ArgumentParser(description='Simulated ECUs generating plausible automotive traffic on SocketCAN/vcan.')
    parser.add_argument('--iface', default='vcan0')
    parser.add_argument('--period', type=float, default=0.05, help='base period in seconds')
    parser.add_argument('--duration', type=float, default=0, help='0 = until Ctrl+C')
    args = parser.parse_args()

    signal.signal(signal.SIGINT, stop)
    signal.signal(signal.SIGTERM, stop)

    start = time.time()
    tick = 0
    print(f'[ecu_sim] enviando em {args.iface}; Ctrl+C para parar')
    with can.Bus(interface='socketcan', channel=args.iface, receive_own_messages=False) as bus:
        while RUN:
            elapsed = time.time() - start
            if args.duration and elapsed >= args.duration:
                break

            speed = int(max(0, 60 + 40 * math.sin(elapsed / 6)))  # plausible km/h
            rpm = int(max(800, 1800 + 900 * math.sin(elapsed / 3)))
            throttle = int(max(0, min(100, 40 + 30 * math.sin(elapsed / 4))))
            temp = int(85 + 5 * math.sin(elapsed / 20))
            fuel = int(max(0, 80 - elapsed / 180))
            doors = 0x00 if int(elapsed) % 17 else 0x01

            messages = [
                frame(0x100, [speed & 0xFF, (speed >> 8) & 0xFF, rpm & 0xFF, (rpm >> 8) & 0xFF, throttle, temp, fuel, 0]),
                frame(0x120, [doors, 0, 0, 0, 0, 0, 0, 0]),
                frame(0x188, [0, 0, speed & 0xFF, (speed >> 8) & 0xFF, 0, 0, 0, 0]),
            ]
            if tick % 10 == 0:
                messages.append(frame(0x300, [random.randrange(256) for _ in range(8)]))
            for msg in messages:
                bus.send(msg, timeout=0.2)
            tick += 1
            time.sleep(args.period)
    print('[ecu_sim] encerrado')
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
