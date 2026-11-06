#!/usr/bin/env python3
"""Plot the aggregated LOEO confusion matrix from analysis/tables/rf_ablation_loeo.json
(run analysis/scripts/ablation_loeo.py first). Writes analysis/figures/rf_loeo_confusion_matrix.{pdf,png}.
Fonts are embedded as TrueType (pdf.fonttype 42)."""
import json
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

plt.rcParams["pdf.fonttype"] = 42
plt.rcParams["ps.fonttype"] = 42
ROOT = Path(__file__).resolve().parents[2]
d = json.loads((ROOT / "analysis/tables/rf_ablation_loeo.json").read_text())
cm = np.array(d["loeo_aggregated_cm"])
names = d["labels"]
fig, ax = plt.subplots(figsize=(3.4, 3.0))
ax.imshow(cm, cmap="Blues")
ax.set_xticks(range(3))
ax.set_yticks(range(3))
ax.set_xticklabels(names)
ax.set_yticklabels(names)
ax.set_xlabel("Predicted")
ax.set_ylabel("True (expected)")
thr = cm.max() / 2.0
for i in range(3):
    for j in range(3):
        ax.text(j, i, int(cm[i, j]), ha="center", va="center", color="white" if cm[i, j] > thr else "black", fontsize=10)
fig.tight_layout()
out = ROOT / "analysis" / "figures"
out.mkdir(parents=True, exist_ok=True)
for ext in ("pdf", "png"):
    fig.savefig(out / f"rf_loeo_confusion_matrix.{ext}", bbox_inches="tight")
print("wrote", out)
