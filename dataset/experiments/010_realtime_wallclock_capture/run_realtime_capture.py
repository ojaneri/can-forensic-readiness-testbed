#!/usr/bin/env python3
"""Generate a short wall-clock CAN-like trace for artifact timing validation.

This is intentionally software-only. It does not transmit to a vehicle or CAN
adapter. Frames are emitted according to real sleeps and logged with monotonic
and UTC timestamps to demonstrate the workflow can preserve wall-clock timing
without relying on deterministic fast-run scheduling.
"""
from __future__ import annotations
import csv, hashlib, json, random, statistics, time
from datetime import datetime, timezone
from pathlib import Path

OUT = Path(__file__).resolve().parent
CSV = OUT / "frames_normalized.csv"
RAW = OUT / "realtime_trace.log"
SUMMARY = OUT / "summary.json"
FINDINGS = OUT / "findings.md"
SEED = 2026060411
DURATION_S = 20.0
PERIODS = {
    "100": 0.05,   # engine/speed-like
    "188": 0.05,   # turn/body-like
    "120": 0.07,   # status-like
    "300": 0.25,   # slower background
}
random.seed(SEED)

def payload_for(aid: str, seq: int) -> str:
    if aid == "100":
        speed = 60 + int(12 * random.random())
        return f"{speed:02X} 00 00 00 00 00 00 {seq & 0xff:02X}"
    if aid == "188":
        return f"00 00 00 00 00 00 00 {seq & 0xff:02X}"
    if aid == "120":
        rpm = 1500 + int(400 * random.random())
        return f"{rpm>>8:02X} {rpm&0xff:02X} 00 00 00 00 00 {seq & 0xff:02X}"
    return " ".join(f"{random.randrange(256):02X}" for _ in range(8))

start_mono = time.monotonic()
start_utc = datetime.now(timezone.utc)
next_due = {aid: start_mono for aid in PERIODS}
seq = 0
rows = []
with RAW.open("w") as raw:
    while True:
        now = time.monotonic()
        if now - start_mono >= DURATION_S:
            break
        aid = min(next_due, key=next_due.get)
        sleep_for = next_due[aid] - time.monotonic()
        if sleep_for > 0:
            time.sleep(sleep_for)
        emit_mono = time.monotonic()
        ts_rel = emit_mono - start_mono
        payload = payload_for(aid, seq)
        row = {
            "timestamp_s": f"{ts_rel:.6f}",
            "utc_iso": datetime.now(timezone.utc).isoformat(),
            "arbitration_id": aid,
            "dlc": "8",
            "data_hex": payload,
            "label": "realtime_baseline",
            "source": "010_realtime_wallclock_capture",
            "note": "software_only_wallclock_capture_no_vehicle_no_can_adapter",
        }
        rows.append(row)
        raw.write(f"({ts_rel:.6f}) vcan0 {aid}#" + payload.replace(" ", "") + "\n")
        seq += 1
        next_due[aid] += PERIODS[aid]

with CSV.open("w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
    w.writeheader(); w.writerows(rows)

ts = [float(r["timestamp_s"]) for r in rows]
inter = [b-a for a,b in zip(ts, ts[1:])]
counts = {}
for r in rows:
    counts[r["arbitration_id"]] = counts.get(r["arbitration_id"], 0) + 1
summary = {
    "experiment_id": "010_realtime_wallclock_capture",
    "created_utc": datetime.now(timezone.utc).isoformat(),
    "purpose": "Short software-only wall-clock timing capture for reproducibility evidence; not physical CAN validation.",
    "seed": SEED,
    "requested_duration_s": DURATION_S,
    "measured_duration_s": round(ts[-1] - ts[0], 6),
    "total_frames": len(rows),
    "unique_arbitration_ids": len(counts),
    "id_counts": counts,
    "inter_arrival_s": {
        "count": len(inter),
        "min": round(min(inter), 6),
        "max": round(max(inter), 6),
        "mean": round(statistics.mean(inter), 6),
        "median": round(statistics.median(inter), 6),
        "stdev": round(statistics.pstdev(inter), 6),
        "negative_values": sum(1 for x in inter if x < 0),
    },
    "boundary": "Software-only wall-clock capture. It validates timing/logging workflow, not physical CAN arbitration, electrical behavior, or vehicle realism.",
}
SUMMARY.write_text(json.dumps(summary, indent=2) + "\n")
FINDINGS.write_text(f"""# Experiment 010 — Real-time wall-clock capture\n\nPurpose: short software-only wall-clock timing capture for reproducibility evidence.\n\n- Total frames: {summary['total_frames']}\n- Measured duration: {summary['measured_duration_s']} s\n- Unique arbitration IDs: {summary['unique_arbitration_ids']}\n- Mean inter-arrival: {summary['inter_arrival_s']['mean']} s\n- Negative inter-arrival values: {summary['inter_arrival_s']['negative_values']}\n\nBoundary: this is not physical CAN or vehicle validation. It demonstrates that the artifact workflow can preserve wall-clock timestamps and inter-arrival timing without relying on deterministic fast-run scheduling.\n""")

def sha(p: Path) -> str:
    h=hashlib.sha256(); h.update(p.read_bytes()); return h.hexdigest()
files = ["run_realtime_capture.py", "frames_normalized.csv", "realtime_trace.log", "summary.json", "findings.md"]
manifest = {"experiment_id": "010_realtime_wallclock_capture", "files": {name: {"sha256": sha(OUT/name), "bytes": (OUT/name).stat().st_size} for name in files}}
(OUT/"manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
