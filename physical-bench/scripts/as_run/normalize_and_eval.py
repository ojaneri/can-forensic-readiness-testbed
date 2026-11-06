#!/usr/bin/env python3
"""Normalize the physical-bench capture into the evidence-pipeline schema and evaluate
(a) delivery of injected frames, (b) the rule-based triage, (c) the synthetic-trained RF.
Merges _rx.log (frames seen on the bus by the CANable) and _tx.log (frames the CANable injected;
a CAN node does not receive its own frames). Phase labels come from _phases.json.
"""
import sys, json, csv, re, hashlib
from pathlib import Path
import numpy as np
ROOT = Path("/var/lib/article-docs/tenants/u1/artigo-sdv-no-brasil")
sys.path.insert(0, str(ROOT / "uploads/can-testbed/estudo/analysis/scripts"))
import rf_baseline as rb
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, confusion_matrix

D = ROOT / "data/physical_bench/2026-11-05"
PREFIX = "bench006_20261105_195436"
SYN = ROOT / "uploads/can-testbed/estudo/dataset/all_frames_normalized.csv"
meta = json.loads((D / f"{PREFIX}_phases.json").read_text())
phases = meta["phases"]
pat = re.compile(r"\(([\d.]+)\)\s+\S+\s+([0-9A-F]+)#([0-9A-F]*)")

def load(p, src):
    out = []
    for ln in open(p):
        m = pat.match(ln.strip())
        if m:
            out.append((float(m.group(1)), int(m.group(2), 16), m.group(3), src))
    return out

# ---- (a) delivery check from the Nucleo (victim ECU) counters -------------------------------
ser = [l for l in open(D / f"{PREFIX}_nucleo_serial.txt") if "rx=" in l]
def grab(l, k): return int(re.search(k + r"=(\d+)", l).group(1))
first, last = ser[0], ser[-1]
delta_rx = grab(last, "rx") - grab(first, "rx")
injected = sum(p["injected_frames"] for p in phases)
print(f"[delivery] injected by CANable = {injected}; received by the Nucleo = {delta_rx} (delta of its counter during the capture)")

# ---- normalize -------------------------------------------------------------------------------
frames = load(D / f"{PREFIX}_rx.log", "ecu_nucleo_observed_on_bus") + load(D / f"{PREFIX}_tx.log", "canable_injected")
frames.sort(key=lambda x: x[0])
t0 = phases[0]["start_epoch_s"]
def phase_of(t):
    for ph in phases:
        if ph["start_epoch_s"] <= t < ph["end_epoch_s"]:
            return ph["phase"]
    return None
SCHEMA = ["experiment_id", "timestamp_epoch_s", "relative_time_s", "attack_label", "arbitration_id",
          "dlc", "payload_hex", "semantic_label", "source_component", "decoded_speed_kmh", "notes"]
EXP = "020_physical_bench_006"
out_csv = D / "frames_normalized.csv"
n_rows = 0
with open(out_csv, "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=SCHEMA); w.writeheader()
    for t, aid, pl, src in frames:
        ph = phase_of(t)
        if ph is None:
            continue
        pl8 = pl.ljust(16, "0")[:16]
        spd = str(int(pl[:2], 16)) if (aid == 0x100 and len(pl) >= 2) else ""
        w.writerow({"experiment_id": EXP, "timestamp_epoch_s": f"{t:.6f}", "relative_time_s": f"{t - t0:.6f}",
                    "attack_label": ph, "arbitration_id": f"{aid:X}", "dlc": 8, "payload_hex": pl8,
                    "semantic_label": f"physical_bench_{ph}", "source_component": src,
                    "decoded_speed_kmh": spd, "notes": "physical CAN bench, CANable V2.0 Pro slcan, 500 kbit/s"})
        n_rows += 1
print(f"[normalize] {n_rows} frames -> {out_csv.name}")

# ---- windows on the physical capture -----------------------------------------------------------
rows = rb.load_rows(out_csv)
pw = rb.build_features(rows, 1.0)
F = rb.FEATURE_NAMES
def arr(ws):
    X = np.nan_to_num(np.array([[w["features"][f] for f in F] for w in ws], dtype=float))
    y = np.array([w["label"] for w in ws]); return X, y
Xp, yp = arr(pw)
names = rb.LABEL_NAMES
print("[windows] physical:", len(pw), {names[k]: int((yp == k).sum()) for k in (0, 1, 2)})

# per-phase descriptive stats
import collections
for ph in phases:
    sel = [w for w in pw if ph["start_epoch_s"] - t0 <= w["window_start_s"] < ph["end_epoch_s"] - t0] if "window_start_s" in pw[0] else []
print("[phases]", [(p["phase"], p["planned_s"], p["injected_frames"]) for p in phases])

# ---- (b) rule-based triage on physical windows -------------------------------------------------
fi = {n: i for i, n in enumerate(F)}
def rule(x):
    if x[fi["n_unique_ids"]] >= 20 or x[fi["unknown_id_ratio"]] >= 0.35: return 2
    if x[fi["max_speed"]] >= 130: return 1
    return 0
pr = np.array([rule(x) for x in Xp])
cm_r = confusion_matrix(yp, pr, labels=[0, 1, 2])
print(f"[rule-based] accuracy={accuracy_score(yp, pr):.4f}"); print(cm_r)

# ---- (c) RF trained on the synthetic corpus, tested on the physical bench ----------------------
sw = rb.build_features(rb.load_rows(SYN), 1.0)
Xs, ys = arr(sw)
rf = RandomForestClassifier(n_estimators=200, max_depth=12, random_state=42, class_weight="balanced", n_jobs=-1).fit(Xs, ys)
pp = rf.predict(Xp)
cm_rf = confusion_matrix(yp, pp, labels=[0, 1, 2])
print(f"[RF synthetic->physical] accuracy={accuracy_score(yp, pp):.4f}"); print(cm_rf)

# key physical-vs-synthetic descriptors
def stats(mask_cls, X):
    return {"mean_speed": round(float(np.mean(X[:, fi["mean_speed"]])), 1), "max_speed": round(float(np.max(X[:, fi["max_speed"]])), 1),
            "n_unique_ids": round(float(np.mean(X[:, fi["n_unique_ids"]])), 1), "frame_rate": round(float(np.mean(X[:, fi["frame_rate"]])), 1)}
desc = {}
for k in (0, 1, 2):
    desc[names[k]] = {"physical": stats(k, Xp[yp == k]) if (yp == k).any() else None,
                      "synthetic": stats(k, Xs[ys == k]) if (ys == k).any() else None}
print("[descriptors per class: physical vs synthetic]"); print(json.dumps(desc, indent=1))

res = {"delivery": {"injected": injected, "received_by_nucleo": delta_rx},
       "frames_normalized": n_rows, "windows_physical": len(pw),
       "rule_based": {"accuracy": float(accuracy_score(yp, pr)), "cm": cm_r.tolist()},
       "rf_synthetic_to_physical": {"accuracy": float(accuracy_score(yp, pp)), "cm": cm_rf.tolist()},
       "descriptors": desc, "labels": names}
(D / "eval_physical_bench.json").write_text(json.dumps(res, indent=2))

# ---- SHA-256 manifest ---------------------------------------------------------------------------
man = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(D.iterdir()) if p.name != "MANIFEST.sha256.json"}
(D / "MANIFEST.sha256.json").write_text(json.dumps(man, indent=2))
print("[manifest]", len(man), "files hashed")
