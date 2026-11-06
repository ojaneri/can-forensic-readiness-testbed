#!/usr/bin/env python3
"""Exploratory (post hoc, after seeing run B): RF trained on one physical run, tested on the other."""
import sys, json
from pathlib import Path
import numpy as np
ROOT = Path("/var/lib/article-docs/tenants/u1/artigo-sdv-no-brasil")
sys.path.insert(0, str(ROOT / "uploads/can-testbed/estudo/analysis/scripts"))
import rf_baseline as rb
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, confusion_matrix
F = rb.FEATURE_NAMES

def win(p):
    w = rb.build_features(rb.load_rows(p), 1.0)
    X = np.nan_to_num(np.array([[x["features"][f] for f in F] for x in w], dtype=float))
    return X, np.array([x["label"] for x in w])

XA, yA = win(ROOT / "data/physical_bench/2026-11-05/frames_normalized.csv")
XB, yB = win(ROOT / "data/physical_bench/2026-11-05_runB/frames_normalized.csv")
RF = lambda: RandomForestClassifier(n_estimators=200, max_depth=12, random_state=42, class_weight="balanced", n_jobs=-1)
out = {}
for tag, (Xt, yt, Xe, ye) in {"train_A_test_B": (XA, yA, XB, yB), "train_B_test_A": (XB, yB, XA, yA)}.items():
    p = RF().fit(Xt, yt).predict(Xe)
    cm = confusion_matrix(ye, p, labels=[0, 1, 2])
    print(tag, "accuracy=%.4f" % accuracy_score(ye, p))
    print(cm)
    out[tag] = {"accuracy": round(float(accuracy_score(ye, p)), 4), "cm": cm.tolist()}
(ROOT / "data/physical_bench/2026-11-05_runB/derived_cross_run_rf.json").write_text(json.dumps(out, indent=2))
