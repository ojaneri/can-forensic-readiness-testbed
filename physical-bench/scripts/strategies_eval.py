#!/usr/bin/env python3
"""Other detection strategies, evaluated on physical-bench run A (600 one-second windows).
S0 RF trained on the synthetic corpus (baseline already reported: 0.80)
S1 RF on synthetic with speed features that assume spoofing REPLACES the legitimate value removed
S2 RF on synthetic + synthetic windows augmented with INJECTION-style spoofing (legit frames kept)
S3 one-class IsolationForest fitted on the first 120 s of physical baseline only
S4 in-domain RF on physical (first half of each phase -> second half), an in-domain ceiling
Rule-based triage for reference. NOTE: S2 was designed after seeing S0 fail on this same run, so it
needs an independent run to count as validated.
"""
import sys, json, math, random, hashlib
from pathlib import Path
from collections import defaultdict, Counter
import numpy as np
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "analysis/scripts"))
import rf_baseline as rb
from sklearn.ensemble import RandomForestClassifier, IsolationForest
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, confusion_matrix

D = ROOT / "physical-bench/runs/2026-11-05_runA"
SYN = ROOT / "dataset/all_frames_normalized.csv"
F = rb.FEATURE_NAMES; fi = {n: i for i, n in enumerate(F)}; names = rb.LABEL_NAMES
def arr(ws, cols=None):
    cols = cols or F
    X = np.nan_to_num(np.array([[w["features"][f] for f in cols] for w in ws], dtype=float))
    y = np.array([w["label"] for w in ws]); return X, y
def RF(): return RandomForestClassifier(n_estimators=200, max_depth=12, random_state=42, class_weight="balanced", n_jobs=-1)
def rep(tag, y, p):
    cm = confusion_matrix(y, p, labels=[0, 1, 2])
    print(f"[{tag}] accuracy={accuracy_score(y, p):.4f}  per-class recall (normal/spoofing/flooding)=" +
          "/".join(f"{cm[i, i] / max(cm[i].sum(), 1):.2f}" for i in range(3))); print(cm)
    return {"accuracy": round(float(accuracy_score(y, p)), 4), "cm": cm.tolist()}

pw = rb.build_features(rb.load_rows(D / "frames_normalized.csv"), 1.0)
Xp, yp = arr(pw); assert len(pw) == 600, len(pw)
print("physical windows:", len(pw), Counter(yp.tolist()))
srows = rb.load_rows(SYN)
sw = rb.build_features(srows, 1.0); Xs, ys = arr(sw)
res = {}

# rule reference
rule = lambda x: 2 if (x[fi["n_unique_ids"]] >= 20 or x[fi["unknown_id_ratio"]] >= 0.35) else (1 if x[fi["max_speed"]] >= 130 else 0)
res["rule"] = rep("rule", yp, np.array([rule(x) for x in Xp]))
# S0
res["S0_rf_synth"] = rep("S0 RF synthetic", yp, RF().fit(Xs, ys).predict(Xp))
# S1 drop speed-average features
drop = {"mean_speed", "min_speed", "std_speed", "speed_count"}
cols1 = [f for f in F if f not in drop]
X1s, y1s = arr(sw, cols1); X1p, _ = arr(pw, cols1)
res["S1_rf_no_speed_avg"] = rep("S1 RF without mean/min/std speed", yp, RF().fit(X1s, y1s).predict(X1p))
# S2 augmentation: injection-style spoofing windows built from synthetic NORMAL windows
rng = random.Random(2026)
by = defaultdict(list)
for r in srows:
    if not math.isnan(r["_t"]): by[(r["experiment_id"], int(r["_t"] // 1.0))].append(r)
aug = []
for (exp, idx), wr in sorted(by.items()):
    lab = Counter(r["attack_label"] for r in wr).most_common(1)[0][0]
    if rb.LABEL_MAP.get(lab, 0) != 0 or rng.random() > 0.25: continue
    key = f"{exp}__inj{idx}"
    for r in wr:
        r2 = dict(r); r2["experiment_id"] = key; r2["_t"] = r["_t"] - idx; r2["attack_label"] = "spoofing"; aug.append(r2)
    for i in range(50):
        t = (i + rng.random() * 0.5) / 50; spd = rng.randint(180, 200)
        aug.append({"experiment_id": key, "_t": t, "_speed": float(spd), "_id": "100", "_payload": f"{spd:02X}0094115F5B4600",
                    "attack_label": "spoofing", "relative_time_s": str(t)})
aw = rb.build_features(aug, 1.0); Xa, ya = arr(aw)
print("augmented injection-style spoofing windows:", len(aw))
res["S2_rf_synth_plus_injection_aug"] = rep("S2 RF synthetic + injection-style augmentation", yp, RF().fit(np.vstack([Xs, Xa]), np.concatenate([ys, ya])).predict(Xp))
res["S2_aug_windows"] = len(aw)
# S3 one-class on first 120 baseline windows
sc = StandardScaler().fit(Xp[:120]); iso = IsolationForest(n_estimators=200, contamination=0.01, random_state=42).fit(sc.transform(Xp[:120]))
flag = iso.predict(sc.transform(Xp)) == -1
held_norm = np.r_[120:180, 420:600]
res["S3_oneclass"] = {"false_positive_rate_heldout_normal": round(float(flag[held_norm].mean()), 4),
                      "detection_rate_spoofing": round(float(flag[180:300].mean()), 4),
                      "detection_rate_flooding": round(float(flag[300:420].mean()), 4)}
print("[S3 one-class IsolationForest, fitted on 120 baseline windows]", res["S3_oneclass"])
# S4 in-domain: first half of each phase -> second half
rng_ph = [(0, 180), (180, 300), (300, 420), (420, 600)]
tr = np.concatenate([np.arange(a, a + (b - a) // 2) for a, b in rng_ph]); te = np.concatenate([np.arange(a + (b - a) // 2, b) for a, b in rng_ph])
res["S4_in_domain_rf"] = rep("S4 in-domain RF (first half -> second half of each phase)", yp[te], RF().fit(Xp[tr], yp[tr]).predict(Xp[te]))
(D / "derived_strategies_eval.json").write_text(json.dumps(res, indent=2))
man = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(D.iterdir()) if p.name != "MANIFEST.sha256.json"}
(D / "MANIFEST.sha256.json").write_text(json.dumps(man, indent=2)); print("manifest:", len(man), "files")
