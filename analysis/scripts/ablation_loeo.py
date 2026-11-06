#!/usr/bin/env python3
"""Ablation of the Random Forest baseline on the synthetic corpus.

Leave-one-experiment-out (LOEO) accuracy with all 26 features versus without the 12 features that most
directly encode the generation rule (ID cardinality, unknown-ID ratio, per-ID counts, speed moments),
plus the aggregated LOEO confusion matrix. Deterministic (random_state=42).
Reads dataset/all_frames_normalized.csv; writes analysis/tables/rf_ablation_loeo.json.
"""
import sys, json
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))
import rf_baseline as rb
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, confusion_matrix, f1_score

CSV = ROOT / "dataset" / "all_frames_normalized.csv"
rows = rb.load_rows(CSV)
windows = rb.build_features(rows, 1.0)
FULL = rb.FEATURE_NAMES
GEN = ["n_unique_ids", "unknown_id_ratio", "known_frame_ratio", "cnt_100", "cnt_120", "cnt_188", "cnt_300",
       "mean_speed", "max_speed", "min_speed", "std_speed", "speed_count"]
REDUCED = [f for f in FULL if f not in GEN]
exps = sorted(set(w["experiment_id"] for w in windows))
labs = [0, 1, 2]


def Xy(ws, feats):
    X = np.array([[w["features"][f] for f in feats] for w in ws], dtype=np.float64)
    y = np.array([w["label"] for w in ws], dtype=np.int32)
    return X, y


def loeo(feats, cm=False):
    accs = {}
    f1m = []
    CM = np.zeros((3, 3), dtype=int)
    for held in exps:
        tr = [w for w in windows if w["experiment_id"] != held]
        te = [w for w in windows if w["experiment_id"] == held]
        Xtr, ytr = Xy(tr, feats)
        Xte, yte = Xy(te, feats)
        if len(np.unique(ytr)) < 2 or len(np.unique(yte)) < 2:
            continue
        rf = RandomForestClassifier(n_estimators=200, max_depth=12, random_state=42, class_weight="balanced", n_jobs=-1)
        rf.fit(Xtr, ytr)
        p = rf.predict(Xte)
        accs[held] = round(float(accuracy_score(yte, p)), 4)
        f1m.append(f1_score(yte, p, average="macro", labels=labs, zero_division=0))
        if cm:
            CM += confusion_matrix(yte, p, labels=labs)
    a = np.array(list(accs.values()))
    return accs, float(a.mean()), float(a.std()), float(np.mean(f1m)), CM


accF, mF, sF, f1F, cmF = loeo(FULL, cm=True)
accR, mR, sR, f1R, _ = loeo(REDUCED)
out = {"n_windows": len(windows), "experiments": len(exps), "labels": rb.LABEL_NAMES,
       "full_n": len(FULL), "reduced_n": len(REDUCED), "dropped": GEN,
       "loeo_full_mean": round(mF, 4), "loeo_full_std": round(sF, 4), "loeo_full_macroF1": round(f1F, 4),
       "loeo_reduced_mean": round(mR, 4), "loeo_reduced_std": round(sR, 4), "loeo_reduced_macroF1": round(f1R, 4),
       "per_exp_full": accF, "per_exp_reduced": accR,
       "loeo_aggregated_cm": cmF.tolist()}
dest = ROOT / "analysis" / "tables" / "rf_ablation_loeo.json"
dest.parent.mkdir(parents=True, exist_ok=True)
dest.write_text(json.dumps(out, indent=2))
print(json.dumps({k: out[k] for k in ["loeo_full_mean", "loeo_full_std", "loeo_reduced_mean", "loeo_reduced_std",
                                      "loeo_full_macroF1", "loeo_reduced_macroF1", "loeo_aggregated_cm"]}, indent=2))
