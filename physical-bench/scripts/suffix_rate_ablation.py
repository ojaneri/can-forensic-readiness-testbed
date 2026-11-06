#!/usr/bin/env python3
"""Ablation: does the 100 % spoofing recovery of the augmented forest come from the payload suffix or from the rate?

The augmentation (S2 recipe) adds 50 injected ID 0x100 frames per selected synthetic window. Their payload is
speed + 00 + 94 11 5F 5B 46 00 (the 6-byte suffix). This script varies two factors in a 2 x 2 design:
  suffix: yes (as in S2) / no (the 6 tail bytes are random per frame)
  rate:   fixed 50 Hz (as in S2) / mixed (each augmented window uses 5, 20 or 50 injected frames per second)
Each variant is trained on synthetic + augmentation and evaluated on the six run-C attackers and their recovery
windows. Three seeds per variant. Speeds of injected frames are 180-200 km/h, as in S2.

usage: suffix_rate_ablation.py   (reads physical-bench/runs/2026-11-05_runC and dataset/all_frames_normalized.csv)
writes: physical-bench/runs/2026-11-05_runC/derived_suffix_ablation.json
The run C normalization is written to a temporary directory; no deposited file except the JSON is changed.
"""
import sys, json, re, csv, math, random, hashlib, tempfile
from pathlib import Path
from collections import defaultdict, Counter
import numpy as np
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "analysis/scripts"))
import rf_baseline as rb
from sklearn.ensemble import RandomForestClassifier

RUN_C = ROOT / "physical-bench/runs/2026-11-05_runC"
PC = "bench006C_20261105_203622"
SYN = ROOT / "dataset/all_frames_normalized.csv"
OUT = RUN_C / "derived_suffix_ablation.json"
SEEDS = [2026, 2027, 2028]
SUFFIX = "94115F5B4600"
pat = re.compile(r"\(([\d.]+)\)\s+\S+\s+([0-9A-F]+)#([0-9A-F]*)")


def load(p, src):
    out = []
    for ln in open(p):
        m = pat.match(ln.strip())
        if m:
            out.append((float(m.group(1)), int(m.group(2), 16), m.group(3), src))
    return out


meta = json.loads((RUN_C / f"{PC}_phases.json").read_text())
phases = meta["phases"]
rates = {p["variant"]: p["rate_hz"] for p in phases if p["injected_frames"]}
print("variant -> rate_hz:", rates)
frames = load(RUN_C / f"{PC}_rx.log", "ecu") + load(RUN_C / f"{PC}_tx.log", "injected")
frames.sort(key=lambda x: x[0])
t0 = phases[0]["start_epoch_s"]


def phase_of(t):
    for ph in phases:
        if ph["start_epoch_s"] <= t < ph["end_epoch_s"]:
            return ph["phase"]
    return None


SCHEMA = ["experiment_id", "timestamp_epoch_s", "relative_time_s", "attack_label", "arbitration_id", "dlc",
          "payload_hex", "semantic_label", "source_component", "decoded_speed_kmh", "notes"]
tmpdir = Path(tempfile.mkdtemp(prefix="ablation_"))
csvC = tmpdir / "runC_normalized.csv"
with open(csvC, "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=SCHEMA)
    w.writeheader()
    for t, aid, pl, src in frames:
        ph = phase_of(t)
        if ph is None:
            continue
        spd = str(int(pl[:2], 16)) if (aid == 0x100 and len(pl) >= 2) else ""
        w.writerow({"experiment_id": "022_runC", "timestamp_epoch_s": f"{t:.6f}", "relative_time_s": f"{t - t0:.6f}",
                    "attack_label": ph, "arbitration_id": f"{aid:X}", "dlc": 8,
                    "payload_hex": pl.ljust(16, "0")[:16], "semantic_label": f"physical_bench_{ph}",
                    "source_component": src, "decoded_speed_kmh": spd, "notes": "run C"})

F = rb.FEATURE_NAMES
fi = {x: i for i, x in enumerate(F)}


def arr(ws):
    X = np.nan_to_num(np.array([[w["features"][f] for f in F] for w in ws], dtype=float))
    return X, np.array([w["label"] for w in ws])


def RF(seed):
    return RandomForestClassifier(n_estimators=200, max_depth=12, random_state=seed, class_weight="balanced", n_jobs=-1)


XC, yC = arr(rb.build_features(rb.load_rows(csvC), 1.0))
sets = defaultdict(list)
for ph in phases:
    a0 = ph["start_epoch_s"] - t0
    b0 = ph["end_epoch_s"] - t0
    for k in range(int(math.ceil(a0)), int(math.floor(b0))):
        if k < len(XC):
            sets[ph["variant"]].append(k)
expected = {"spoof_low_rate": 1, "spoof_stealth": 1, "spoof_mid": 1, "flood_slow": 2, "flood_targeted": 2, "dos_id0": 2}
recov = np.array(sets["recovery"])

srows = rb.load_rows(SYN)
Xs, ys = arr(rb.build_features(srows, 1.0))
by = defaultdict(list)
for r in srows:
    if not math.isnan(r["_t"]):
        by[(r["experiment_id"], int(r["_t"] // 1.0))].append(r)


def augment(seed, suffix, mixed):
    """Same selection rule as S2 (25 % of attack-free windows, sorted keys); injection draws use a separate RNG."""
    sel = random.Random(seed)
    inj = random.Random(seed + 1000)
    aug = []
    for (exp, idx), wr in sorted(by.items()):
        lab = Counter(r["attack_label"] for r in wr).most_common(1)[0][0]
        if rb.LABEL_MAP.get(lab, 0) != 0 or sel.random() > 0.25:
            continue
        key = f"{exp}__inj{idx}"
        for r in wr:
            r2 = dict(r)
            r2["experiment_id"] = key
            r2["_t"] = r["_t"] - idx
            r2["attack_label"] = "spoofing"
            aug.append(r2)
        n = inj.choice([5, 20, 50]) if mixed else 50
        for i in range(n):
            t = (i + inj.random() * 0.5) / n
            spd = inj.randint(180, 200)
            tail = SUFFIX if suffix else "".join(f"{inj.randrange(256):02X}" for _ in range(6))
            aug.append({"experiment_id": key, "_t": t, "_speed": float(spd), "_id": "100",
                        "_payload": f"{spd:02X}00{tail}", "attack_label": "spoofing", "relative_time_s": str(t)})
    return aug


def score(p):
    row = {"fp_recovery": round(float((p[recov] != 0).mean()), 3)}
    for v, cls in expected.items():
        idx = np.array(sets[v])
        row[v] = round(float((p[idx] == cls).mean()), 3)
    return row


VARIANTS = {"V1_suffix_50Hz (S2 recipe)": (True, False), "V2_nosuffix_50Hz": (False, False),
            "V3_suffix_mixedrate": (True, True), "V4_nosuffix_mixedrate": (False, True)}
results = {}
for name, (suffix, mixed) in VARIANTS.items():
    per_seed = []
    for seed in SEEDS:
        Xa, ya = arr(rb.build_features(augment(seed, suffix, mixed), 1.0))
        clf = RF(seed).fit(np.vstack([Xs, Xa]), np.concatenate([ys, ya]))
        per_seed.append(score(clf.predict(XC)))
        print(name, seed, per_seed[-1], flush=True)
    agg = {}
    for k in per_seed[0]:
        vals = [s[k] for s in per_seed]
        agg[k] = {"mean": round(float(np.mean(vals)), 3), "min": min(vals), "max": max(vals)}
    results[name] = {"per_seed": per_seed, "aggregate": agg}

out = {"script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(), "seeds": SEEDS,
       "attack_phases_rate_hz": rates, "windows_run_C": len(XC), "variants": results}
OUT.write_text(json.dumps(out, indent=2))
print("wrote", OUT)
