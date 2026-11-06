#!/usr/bin/env python3
"""Run C (six unseen attackers) evaluation with strategies FROZEN before the capture.
usage: strategies_eval_C.py <runC_dir> <runC_prefix>
Frozen: rule; S0 RF(synthetic); S2 RF(synthetic + injection-style augmentation, same recipe/seed as runs A and B);
P_AB RF trained on physical runs A and B; S3b z-score detector fit on run C first 60 baseline windows;
S3b_B the same detector fit on run B first 120 baseline windows (cross-run, same ECU profile).
Per-variant rates use only windows fully inside each phase.
"""
import sys, json, re, csv, math, random, hashlib
from pathlib import Path
from collections import defaultdict, Counter
import numpy as np
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "analysis/scripts"))
import rf_baseline as rb
from sklearn.ensemble import RandomForestClassifier

RUN_A = ROOT / "physical-bench/runs/2026-11-05_runA"
RUN_B = ROOT / "physical-bench/runs/2026-11-05_runB"
RUN_C = Path(sys.argv[1]); PC = sys.argv[2]
SYN = ROOT / "dataset/all_frames_normalized.csv"
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
ser = [l for l in open(RUN_C / f"{PC}_nucleo_serial.txt") if "rx=" in l]
g = lambda l, k: int(re.search(k + r"=(\d+)", l).group(1))
delivered = g(ser[-1], "rx") - g(ser[0], "rx")
injected = sum(p["injected_frames"] for p in phases)
print(f"[delivery run C] injected={injected} received_by_nucleo={delivered}")
for p in phases:
    if p["injected_frames"]:
        print(f"   {p['variant']:15s} rate={p['rate_hz']}Hz injected={p['injected_frames']}")

frames = load(RUN_C / f"{PC}_rx.log", "ecu_nucleo_observed_on_bus") + load(RUN_C / f"{PC}_tx.log", "canable_injected")
frames.sort(key=lambda x: x[0])
t0 = phases[0]["start_epoch_s"]


def phase_of(t):
    for ph in phases:
        if ph["start_epoch_s"] <= t < ph["end_epoch_s"]:
            return ph["phase"]
    return None


SCHEMA = ["experiment_id", "timestamp_epoch_s", "relative_time_s", "attack_label", "arbitration_id", "dlc",
          "payload_hex", "semantic_label", "source_component", "decoded_speed_kmh", "notes"]
csvC = RUN_C / "frames_normalized.csv"
n = 0
with open(csvC, "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=SCHEMA)
    w.writeheader()
    for t, aid, pl, src in frames:
        ph = phase_of(t)
        if ph is None:
            continue
        spd = str(int(pl[:2], 16)) if (aid == 0x100 and len(pl) >= 2) else ""
        w.writerow({"experiment_id": "022_physical_bench_runC_variants", "timestamp_epoch_s": f"{t:.6f}",
                    "relative_time_s": f"{t - t0:.6f}", "attack_label": ph, "arbitration_id": f"{aid:X}", "dlc": 8,
                    "payload_hex": pl.ljust(16, "0")[:16], "semantic_label": f"physical_bench_{ph}",
                    "source_component": src, "decoded_speed_kmh": spd,
                    "notes": "physical CAN bench run C, six unseen attackers"})
        n += 1
print(f"[normalize run C] {n} frames")

F = rb.FEATURE_NAMES
fi = {x: i for i, x in enumerate(F)}


def arr(ws):
    X = np.nan_to_num(np.array([[w["features"][f] for f in F] for w in ws], dtype=float))
    return X, np.array([w["label"] for w in ws])


def RF():
    return RandomForestClassifier(n_estimators=200, max_depth=12, random_state=42, class_weight="balanced", n_jobs=-1)


def win(p):
    return arr(rb.build_features(rb.load_rows(p), 1.0))


XA, yA = win(RUN_A / "frames_normalized.csv")
XB, yB = win(RUN_B / "frames_normalized.csv")
XC, yC = win(csvC)
print("run C windows:", len(XC), Counter(yC.tolist()))

# window sets (windows fully inside each phase)
sets = defaultdict(list)
for ph in phases:
    a0 = ph["start_epoch_s"] - t0
    b0 = ph["end_epoch_s"] - t0
    for k in range(int(math.ceil(a0)), int(math.floor(b0))):
        if k < len(XC):
            sets[ph["variant"]].append(k)
expected = {"spoof_low_rate": 1, "spoof_stealth": 1, "spoof_mid": 1, "flood_slow": 2, "flood_targeted": 2, "dos_id0": 2}
recov = np.array(sets["recovery"])
base = np.array(sets["baseline"])

srows = rb.load_rows(SYN)
sw = rb.build_features(srows, 1.0)
Xs, ys = arr(sw)
preds = {}
rule = lambda x: 2 if (x[fi["n_unique_ids"]] >= 20 or x[fi["unknown_id_ratio"]] >= 0.35) else (1 if x[fi["max_speed"]] >= 130 else 0)
preds["rule"] = np.array([rule(x) for x in XC])
preds["S0_rf_synthetic"] = RF().fit(Xs, ys).predict(XC)

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
Xa, ya = arr(rb.build_features(aug, 1.0))
preds["S2_rf_synth_plus_injection_aug"] = RF().fit(np.vstack([Xs, Xa]), np.concatenate([ys, ya])).predict(XC)
preds["P_AB_rf_physical_A_plus_B"] = RF().fit(np.vstack([XA, XB]), np.concatenate([yA, yB])).predict(XC)


def zfit(X):
    mu = X.mean(0)
    sd = X.std(0)
    s = np.maximum.reduce([sd, 0.05 * np.abs(mu), np.full_like(sd, 1e-3)])
    return mu, s, 2.0 * np.abs((X - mu) / s).max(1).max()


mu, s, thr = zfit(XC[:60])
flagC = np.abs((XC - mu) / s).max(1) > thr
mu, s, thr = zfit(XB[:120])
flagB = np.abs((XC - mu) / s).max(1) > thr
detectors = {"S3b_zscore_fit_on_C_baseline": flagC, "S3b_zscore_fit_on_B_baseline": flagB}

res = {"delivery": {"injected": injected, "received_by_nucleo": delivered}, "windows": len(XC),
       "window_counts": {k: len(v) for k, v in sets.items()}}
print("\n=== resultado por atacante: fracao de janelas classificadas corretamente (classificadores) / sinalizadas (detectores) ===")
header = f"{'estrategia':36s} {'FP normal':>9s} " + " ".join(f"{v[:13]:>13s}" for v in expected)
print(header)
for name, p in preds.items():
    row = {"false_positive_rate_recovery": round(float((p[recov] != 0).mean()), 4)}
    for v, cls in expected.items():
        idx = np.array(sets[v])
        row[v] = round(float((p[idx] == cls).mean()), 3)
        row[v + "_any_attack"] = round(float((p[idx] != 0).mean()), 3)
    res[name] = row
    print(f"{name:36s} {row['false_positive_rate_recovery']:9.3f} " + " ".join(f"{row[v]:13.3f}" for v in expected))
for name, fl in detectors.items():
    row = {"false_positive_rate_recovery": round(float(fl[recov].mean()), 4)}
    for v in expected:
        row[v] = round(float(fl[np.array(sets[v])].mean()), 3)
    res[name] = row
    print(f"{name:36s} {row['false_positive_rate_recovery']:9.3f} " + " ".join(f"{row[v]:13.3f}" for v in expected))
print("(S3b e detectores: coluna = fracao sinalizada como anomalia, sem distinguir o tipo de ataque)")

(RUN_C / "derived_strategies_eval_C.json").write_text(json.dumps(res, indent=2))
man = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(RUN_C.iterdir()) if p.name != "MANIFEST.sha256.json"}
(RUN_C / "MANIFEST.sha256.json").write_text(json.dumps(man, indent=2))
print("manifest:", len(man), "files")
