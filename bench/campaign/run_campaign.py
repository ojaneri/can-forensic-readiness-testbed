#!/usr/bin/env python3
"""Multi-run timing campaign for Experiments 010, 011 and 012.

The manuscript's Section VII names this as future work: "The current timing evidence
(Exp. 010-012) is limited to single runs." This driver runs each of them N times and
reports mean +/- sd of the quantities the paper quotes from a single sample.

It never touches estudo/. Each run gets its own directory under runs/, the runner is
copied into it, and the runner writes beside itself -- which is how the archived runners
already behave (a trap if you run them in place: they overwrite the evidence).

The seed is held constant on purpose. It fixes the payload content, so the only thing
varying across runs is OS scheduling -- which is exactly what a timing campaign measures.

Usage:  python3 bench/campaign/run_campaign.py [--runs 10] [--only 010,011]
"""
from __future__ import annotations
import argparse, json, os, shutil, statistics, subprocess, sys, time
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
RUNNERS = HERE / "runners"
RUNS = HERE / "runs"
ICSIM_SRC = (HERE.parents[1] /
             "dataset/experiments/008_external_icsim_replay/frames_normalized.csv")

# The archived runners hash themselves into their own manifest by their original
# filename, so each copy must keep that name.
EXPS = {
    "010": ("run_realtime_capture.py", "wall-clock capture", 20.0),
    "011": ("run_python_can_virtual_bus.py", "python-can virtual bus", 30.0),
    "012": ("run_python_can_icsim_replay.py", "python-can ICSim replay", None),
}

def one_run(exp: str, i: int) -> dict:
    runner, _, _ = EXPS[exp]
    d = RUNS / exp / f"run_{i:02d}"
    if d.exists():
        shutil.rmtree(d)
    d.mkdir(parents=True)
    shutil.copy2(RUNNERS / exp / runner, d / runner)
    env = dict(os.environ)
    env["EXP_CHANNEL"] = f"bench_vcan_{exp}_{i:02d}"   # no cross-talk between runs
    if exp == "012":
        env["EXP_SRC"] = str(ICSIM_SRC)
    t0 = time.monotonic()
    p = subprocess.run([sys.executable, runner], cwd=d, env=env,
                       capture_output=True, text=True)
    wall = time.monotonic() - t0
    if p.returncode != 0:
        return {"run": i, "ok": False, "stderr": p.stderr[-400:]}
    s = json.loads((d / "summary.json").read_text())
    out = {"run": i, "ok": True, "wall_s": round(wall, 3),
           "frames": s.get("total_frames") or s.get("replayed_frames"),
           "duration_s": s.get("measured_duration_s"),
           "unique_ids": s.get("unique_arbitration_ids"),
           "iat_mean": s.get("inter_arrival_s", {}).get("mean"),
           "iat_stdev": s.get("inter_arrival_s", {}).get("stdev"),
           "iat_negative": s.get("inter_arrival_s", {}).get("negative_values")}
    lat = s.get("send_to_recv_latency_s")
    if lat:
        out["lat_mean"] = lat.get("mean")
        out["lat_max"] = lat.get("max")
    return out

def stats(vals):
    vals = [v for v in vals if v is not None]
    if not vals:
        return None
    return {"n": len(vals), "mean": statistics.mean(vals),
            "sd": statistics.stdev(vals) if len(vals) > 1 else 0.0,
            "min": min(vals), "max": max(vals)}

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs", type=int, default=10)
    ap.add_argument("--only", default="010,011,012")
    a = ap.parse_args()
    todo = [e for e in a.only.split(",") if e in EXPS]

    report = {"created_utc": datetime.now(timezone.utc).isoformat(),
              "runs_requested": a.runs, "python": sys.version.split()[0],
              "note": "seed held constant; OS scheduling is the only variable",
              "experiments": {}}
    for exp in todo:
        _, label, _ = EXPS[exp]
        print(f"\n=== Exp. {exp} — {label} — {a.runs} runs ===", flush=True)
        rows = []
        for i in range(1, a.runs + 1):
            r = one_run(exp, i)
            rows.append(r)
            if r["ok"]:
                extra = f" lat={r['lat_mean']}" if "lat_mean" in r else ""
                print(f"  run {i:2d}: {r['frames']} frames  dur={r['duration_s']}"
                      f"  iat={r['iat_mean']}  neg={r['iat_negative']}{extra}", flush=True)
            else:
                print(f"  run {i:2d}: FAILED — {r['stderr']}", flush=True)
        ok = [r for r in rows if r["ok"]]
        report["experiments"][exp] = {
            "label": label, "runs_ok": len(ok), "runs_failed": len(rows) - len(ok),
            "frames": stats([r["frames"] for r in ok]),
            "duration_s": stats([r["duration_s"] for r in ok]),
            "iat_mean_s": stats([r["iat_mean"] for r in ok]),
            "latency_mean_s": stats([r.get("lat_mean") for r in ok]),
            "negative_iat_total": sum(r["iat_negative"] or 0 for r in ok),
            "unique_ids": sorted({r["unique_ids"] for r in ok}),
            "per_run": ok,
        }
    (HERE / "campaign_report.json").write_text(json.dumps(report, indent=2) + "\n")
    print("\n" + "=" * 72)
    for exp, d in report["experiments"].items():
        print(f"Exp. {exp} — {d['label']}  ({d['runs_ok']} ok, {d['runs_failed']} failed)")
        for k in ("frames", "duration_s", "iat_mean_s", "latency_mean_s"):
            st = d[k]
            if st:
                print(f"  {k:15s} mean={st['mean']:.6f}  sd={st['sd']:.6f}"
                      f"  min={st['min']:.6f}  max={st['max']:.6f}  (n={st['n']})")
        print(f"  negative IAT across all runs: {d['negative_iat_total']}")
        print(f"  unique IDs observed: {d['unique_ids']}")
    print(f"\nreport -> {HERE/'campaign_report.json'}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
