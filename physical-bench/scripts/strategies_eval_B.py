#!/usr/bin/env python3
"""Independent run-B evaluation with the strategies FROZEN before run B was captured.
usage: strategies_eval_B.py <runB_dir> <runB_prefix>
Frozen: rule, S0 (RF on synthetic), S2 (RF on synthetic + injection-style augmentation, same recipe and seed as run A),
S3 (IsolationForest on 120 baseline windows), S3b (floor-scaled z-score detector, thr = 2 x max training score).
"""
import sys, json, re, csv, math, random, hashlib
from pathlib import Path
from collections import defaultdict, Counter
import numpy as np
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "analysis/scripts"))
import rf_baseline as rb
from sklearn.ensemble import RandomForestClassifier, IsolationForest
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, confusion_matrix

RUN_A = ROOT / "physical-bench/runs/2026-11-05_runA"
RUN_B = Path(sys.argv[1]); PB = sys.argv[2]
SYN = ROOT / "dataset/all_frames_normalized.csv"
pat = re.compile(r"\(([\d.]+)\)\s+\S+\s+([0-9A-F]+)#([0-9A-F]*)")


def load(p, src):
    out = []
    for ln in open(p):
        m = pat.match(ln.strip())
        if m:
            out.append((float(m.group(1)), int(m.group(2), 16), m.group(3), src))
    return out


meta = json.loads((RUN_B / f"{PB}_phases.json").read_text())
phases = meta["phases"]
ser = [l for l in open(RUN_B / f"{PB}_nucleo_serial.txt") if "rx=" in l]
g = lambda l, k: int(re.search(k + r"=(\d+)", l).group(1))
delivered = g(ser[-1], "rx") - g(ser[0], "rx")
injected = sum(p["injected_frames"] for p in phases)
print(f"[delivery run B] injected={injected} received_by_nucleo={delivered}")

frames = load(RUN_B / f"{PB}_rx.log", "ecu_nucleo_observed_on_bus") + load(RUN_B / f"{PB}_tx.log", "canable_injected")
frames.sort(key=lambda x: x[0])
t0 = phases[0]["start_epoch_s"]


def phase_of(t):
    for ph in phases:
        if ph["start_epoch_s"] <= t < ph["end_epoch_s"]:
            return ph["phase"]
    return None


SCHEMA = ["experiment_id", "timestamp_epoch_s", "relative_time_s", "attack_label", "arbitration_id", "dlc",
          "payload_hex", "semantic_label", "source_component", "decoded_speed_kmh", "notes"]
csvB = RUN_B / "frames_normalized.csv"
n = 0
with open(csvB, "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=SCHEMA)
    w.writeheader()
    for t, aid, pl, src in frames:
        ph = phase_of(t)
        if ph is None:
            continue
        spd = str(int(pl[:2], 16)) if (aid == 0x100 and len(pl) >= 2) else ""
        w.writerow({"experiment_id": "021_physical_bench_006_runB", "timestamp_epoch_s": f"{t:.6f}",
                    "relative_time_s": f"{t - t0:.6f}", "attack_label": ph, "arbitration_id": f"{aid:X}", "dlc": 8,
                    "payload_hex": pl.ljust(16, "0")[:16], "semantic_label": f"physical_bench_{ph}",
                    "source_component": src, "decoded_speed_kmh": spd,
                    "notes": "physical CAN bench run B, smooth ECU speed profile"})
        n += 1
print(f"[normalize run B] {n} frames")

F = rb.FEATURE_NAMES
fi = {x: i for i, x in enumerate(F)}


def arr(ws):
    X = np.nan_to_num(np.array([[w["features"][f] for f in F] for w in ws], dtype=float))
    return X, np.array([w["label"] for w in ws])


def RF():
    return RandomForestClassifier(n_estimators=200, max_depth=12, random_state=42, class_weight="balanced", n_jobs=-1)


def rep(tag, y, p):
    cm = confusion_matrix(y, p, labels=[0, 1, 2])
    rec = "/".join(f"{cm[i, i] / max(cm[i].sum(), 1):.2f}" for i in range(3))
    print(f"[{tag}] accuracy={accuracy_score(y, p):.4f} recall normal/spoofing/flooding={rec}")
    print(cm)
    return {"accuracy": round(float(accuracy_score(y, p)), 4), "cm": cm.tolist()}


pwB = rb.build_features(rb.load_rows(csvB), 1.0)
XB, yB = arr(pwB)
pwA = rb.build_features(rb.load_rows(RUN_A / "frames_normalized.csv"), 1.0)
XA, yA = arr(pwA)
print("run B windows:", len(pwB), Counter(yB.tolist()))
assert len(pwB) == 600, len(pwB)
srows = rb.load_rows(SYN)
sw = rb.build_features(srows, 1.0)
Xs, ys = arr(sw)
res = {"delivery": {"injected": injected, "received_by_nucleo": delivered}, "windows": len(pwB)}

rule = lambda x: 2 if (x[fi["n_unique_ids"]] >= 20 or x[fi["unknown_id_ratio"]] >= 0.35) else (1 if x[fi["max_speed"]] >= 130 else 0)
res["rule"] = rep("rule", yB, np.array([rule(x) for x in XB]))
res["S0"] = rep("S0 RF synthetic", yB, RF().fit(Xs, ys).predict(XB))

rng = random.Random(2026)
by = defaultdict(list)
for r in srows:
    if not math.isnan(r["_t"]):
        by[(r["experiment_id"], int(r["_t"] // 1.0))].append(r)
aug = []
for (exp, idx), wr in sorted(by.items()):
    lab = Counter(r["attack_label"] for r in wr).most_common(1)[0][0]
    if rb.LABEL_MAP.get(lab, 0) != 0 or rng.random() > 0.25:
        continue
    key = f"{exp}__inj{idx}"
    for r in wr:
        r2 = dict(r)
        r2["experiment_id"] = key
        r2["_t"] = r["_t"] - idx
        r2["attack_label"] = "spoofing"
        aug.append(r2)
    for i in range(50):
        t = (i + rng.random() * 0.5) / 50
        spd = rng.randint(180, 200)
        aug.append({"experiment_id": key, "_t": t, "_speed": float(spd), "_id": "100", "_payload": f"{spd:02X}0094115F5B4600",
                    "attack_label": "spoofing", "relative_time_s": str(t)})
aw = rb.build_features(aug, 1.0)
Xa, ya = arr(aw)
res["S2"] = rep(f"S2 RF synthetic + injection augmentation ({len(aw)} windows)", yB,
                RF().fit(np.vstack([Xs, Xa]), np.concatenate([ys, ya])).predict(XB))

norm_B = np.r_[0:180, 420:600]
held_B = np.r_[120:180, 420:600]


def det(tag, flag, normal_idx):
    r = {"false_positive_rate": round(float(flag[normal_idx].mean()), 4),
         "detect_spoofing": round(float(flag[180:300].mean()), 4),
         "detect_flooding": round(float(flag[300:420].mean()), 4)}
    print(f"[{tag}] {r}")
    return r


sc = StandardScaler().fit(XB[:120])
iso = IsolationForest(n_estimators=200, contamination=0.01, random_state=42).fit(sc.transform(XB[:120]))
res["S3_iforest_fit_on_B_baseline"] = det("S3 IsolationForest fit on B first 120 s", iso.predict(sc.transform(XB)) == -1, held_B)


def zfit(X):
    mu = X.mean(0)
    sd = X.std(0)
    s = np.maximum.reduce([sd, 0.05 * np.abs(mu), np.full_like(sd, 1e-3)])
    return mu, s, 2.0 * np.abs((X - mu) / s).max(1).max()


def zflag(X, mu, s, thr):
    return np.abs((X - mu) / s).max(1) > thr


mu, s, thr = zfit(XB[:120])
res["S3b_zscore_fit_on_B_baseline"] = det("S3b z-score fit on B first 120 s", zflag(XB, mu, s, thr), held_B)
mu, s, thr = zfit(XA[:120])
res["S3b_zscore_fit_on_A_baseline_cross_run"] = det("S3b z-score fit on RUN A baseline -> B (independent)", zflag(XB, mu, s, thr), norm_B)
(RUN_B / "derived_strategies_eval_B.json").write_text(json.dumps(res, indent=2))
man = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(RUN_B.iterdir()) if p.name != "MANIFEST.sha256.json"}
(RUN_B / "MANIFEST.sha256.json").write_text(json.dumps(man, indent=2))
print("manifest:", len(man), "files")
