#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Circle
from matplotlib.lines import Line2D

ROOT = Path(__file__).resolve().parents[2]
FIG = ROOT / "analysis" / "figures"
EXP = ROOT / "dataset" / "experiments"
plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "axes.titlesize": 13,
    "axes.labelsize": 10,
    "xtick.labelsize": 9,
    "ytick.labelsize": 9,
    "figure.dpi": 180,
    "savefig.dpi": 300,
    "axes.spines.top": False,
    "axes.spines.right": False,
})
COL = {
    "navy":"#0f172a", "slate":"#334155", "muted":"#64748b", "blue":"#2563eb",
    "cyan":"#0891b2", "green":"#16a34a", "amber":"#d97706", "red":"#dc2626",
    "bg":"#f8fafc", "line":"#cbd5e1", "purple":"#7c3aed", "orange":"#f97316"
}

def save(fig, name):
    for ext in ["png", "pdf", "svg"]:
        fig.savefig(FIG / f"{name}.{ext}", bbox_inches="tight", facecolor="white")
    plt.close(fig)

def rounded(ax, xy, w, h, text, sub, color, icon=None):
    x,y=xy
    box=FancyBboxPatch((x,y), w,h, boxstyle="round,pad=0.02,rounding_size=0.035",
                       ec=color, fc=color+"18", lw=2.2)
    ax.add_patch(box)
    if icon:
        ax.text(x+w*0.12, y+h*0.68, icon, ha="center", va="center", fontsize=22)
        tx=x+w*0.55
    else:
        tx=x+w/2
    ax.text(tx, y+h*0.62, text, ha="center", va="center", fontsize=12, fontweight="bold", color=COL['navy'])
    ax.text(tx, y+h*0.36, sub, ha="center", va="center", fontsize=8.5, color=COL['slate'])

def arrow(ax, start, end, color=None, rad=0.0):
    ax.add_patch(FancyArrowPatch(start, end, arrowstyle="-|>", mutation_scale=15,
                                 lw=2.0, color=color or COL['navy'],
                                 connectionstyle=f"arc3,rad={rad}"))

def pipeline():
    fig, ax = plt.subplots(figsize=(10.8,5.8))
    ax.set_xlim(0,1); ax.set_ylim(0,1); ax.axis('off')
    fig.suptitle("Reproducible CAN Evidence Pipeline", x=.5, y=.98, fontsize=18, fontweight="bold", color=COL['navy'])
    ax.text(.5,.91,"Software-defined runs, external traces and wall-clock capture converge into auditable evidence packages", ha='center', color=COL['muted'], fontsize=10)
    rounded(ax,(.04,.64),.22,.17,"Internal Matrix","005–007 · 477,738 frames",COL['blue'],"▦")
    rounded(ax,(.04,.40),.22,.17,"External ICSim","008–009 · trace + injection",COL['cyan'],"↻")
    rounded(ax,(.04,.16),.22,.17,"Wall-clock Capture","010 · 1,167 frames / 20s",COL['amber'],"⏱")
    rounded(ax,(.38,.50),.24,.20,"Normalize + Annotate","CSV schema · labels · timestamps",COL['purple'],"◇")
    rounded(ax,(.72,.50),.24,.20,"Evidence Package","SHA-256 · metadata · DOI",COL['green'],"✓")
    rounded(ax,(.72,.20),.24,.18,"Observer-safe Review","browser demos · no live CAN",COL['orange'],"◉")
    arrow(ax,(.26,.725),(.38,.61),COL['blue'],.05)
    arrow(ax,(.26,.485),(.38,.59),COL['cyan'],0)
    arrow(ax,(.26,.245),(.38,.55),COL['amber'],-.08)
    arrow(ax,(.62,.60),(.72,.60),COL['navy'])
    arrow(ax,(.84,.50),(.84,.38),COL['green'])
    arrow(ax,(.72,.28),(.62,.50),COL['orange'],-.25)
    ax.text(.5,.06,"Claim boundary: reproducibility and forensic-readiness workflow — not physical CAN fidelity or IDS benchmarking", ha='center', fontsize=9.5, color=COL['red'], fontweight='bold')
    save(fig,"reproducible_evidence_pipeline_v5")

def evidence_dashboard():
    ds=json.loads((ROOT/'dataset/dataset_summary.json').read_text())
    e8=json.loads((EXP/'008_external_icsim_replay/summary.json').read_text())
    e9=json.loads((EXP/'009_icsim_spoof_injection/summary.json').read_text())
    e10=json.loads((EXP/'010_realtime_wallclock_capture/summary.json').read_text())
    fig, axs = plt.subplots(2,2,figsize=(10.8,6.4), gridspec_kw={'height_ratios':[1,1.05]})
    fig.suptitle("Evidence Coverage Summary", fontsize=17, fontweight='bold', color=COL['navy'])
    # phase counts
    phases=list(ds['phase_counts'].keys()); vals=list(ds['phase_counts'].values())
    colors=[COL['blue'],COL['purple'],COL['red'],COL['green']]
    ax=axs[0,0]
    bars=ax.bar(phases, vals, color=colors, edgecolor='white', lw=1.2)
    ax.set_title("Internal labeled frames by phase")
    ax.set_ylabel("frames")
    ax.tick_params(axis='x', rotation=20)
    ax.grid(axis='y', alpha=.2)
    for b,v in zip(bars,vals): ax.text(b.get_x()+b.get_width()/2, v, f"{v:,}", ha='center', va='bottom', fontsize=8)
    # package frames
    ax=axs[0,1]
    names=['Internal\n005–007','ICSim\n008','Spoof\n009','Wall-clock\n010']
    vals=[ds['total_frames'], e8['total_frames'], e9['spoofed_frames'], e10['total_frames']]
    ax.bar(names, vals, color=[COL['blue'],COL['cyan'],COL['orange'],COL['amber']], edgecolor='white')
    ax.set_yscale('log')
    ax.set_title("Evidence package scale (log)")
    ax.set_ylabel("frames")
    ax.grid(axis='y', which='both', alpha=.2)
    for i,v in enumerate(vals): ax.text(i, v*1.15, f"{v:,}", ha='center', fontsize=8)
    # speed stats
    ax=axs[1,0]
    stats=ds['speed_stats_by_phase_for_id_0x100']
    labs=['baseline','spoofing','recovery']
    means=[stats[k]['mean'] for k in labs]
    mins=[stats[k]['min'] for k in labs]; maxs=[stats[k]['max'] for k in labs]
    yerr=np.array([[m-mi for m,mi in zip(means,mins)],[ma-m for m,ma in zip(means,maxs)]])
    ax.errorbar(labs, means, yerr=yerr, fmt='o', color=COL['navy'], ecolor=COL['muted'], elinewidth=4, capsize=5, markersize=8)
    ax.set_title("Decoded speed contrast on ID 0x100")
    ax.set_ylabel("km/h (didactic decode)")
    ax.grid(axis='y', alpha=.2)
    # checklist heatmap
    ax=axs[1,1]
    rows=['Proposed','ICSim','ROAD','can-train']
    cols=['DOI','Hashes','Schema','Demo','Wall-clock']
    mat=np.array([[1,1,1,1,1],[0,0,.5,1,0],[1,0,1,0,0],[1,0,1,0,0]],float)
    im=ax.imshow(mat, cmap='YlGnBu', vmin=0, vmax=1)
    ax.set_xticks(range(len(cols)), cols, rotation=25, ha='right')
    ax.set_yticks(range(len(rows)), rows)
    ax.set_title("Artifact-review posture")
    for r in range(mat.shape[0]):
        for c in range(mat.shape[1]):
            txt='✓' if mat[r,c]==1 else ('partial' if mat[r,c] else '—')
            ax.text(c,r,txt,ha='center',va='center',fontsize=8,color=COL['navy'])
    fig.tight_layout(rect=[0,0,1,.94])
    save(fig,"evidence_coverage_dashboard_v5")

def realtime_timing():
    df=pd.read_csv(EXP/'010_realtime_wallclock_capture/frames_normalized.csv')
    ts=df['timestamp_s'].astype(float).to_numpy()
    inter=np.diff(ts)
    fig, axs=plt.subplots(1,2,figsize=(10.8,3.8))
    fig.suptitle("Experiment 010: Wall-clock Timing Capture", fontsize=16, fontweight='bold', color=COL['navy'])
    ax=axs[0]
    for aid,sub in df.groupby('arbitration_id'):
        ax.scatter(sub['timestamp_s'].astype(float), [aid]*len(sub), s=8, alpha=.75, label=f"0x{aid}")
    ax.set_xlabel("elapsed wall-clock time (s)"); ax.set_ylabel("arbitration ID")
    ax.set_title("Frame timeline")
    ax.grid(axis='x', alpha=.2)
    ax.legend(loc='upper right', fontsize=8, frameon=False)
    ax=axs[1]
    ax.hist(inter, bins=35, color=COL['blue'], alpha=.85, edgecolor='white')
    ax.axvline(inter.mean(), color=COL['red'], lw=2, label=f"mean {inter.mean():.4f}s")
    ax.set_title("Inter-arrival distribution")
    ax.set_xlabel("seconds"); ax.set_ylabel("count")
    ax.grid(axis='y', alpha=.2); ax.legend(frameon=False, fontsize=8)
    ax.text(.98,.92,"negative values: 0", transform=ax.transAxes, ha='right', fontsize=9, color=COL['green'], fontweight='bold')
    fig.tight_layout(rect=[0,0,1,.88])
    save(fig,"exp010_wallclock_timing_v5")

def demo_preview_png():
    fig, ax=plt.subplots(figsize=(10.8,5.6)); ax.axis('off'); ax.set_xlim(0,1); ax.set_ylim(0,1)
    ax.set_facecolor('#0f172a'); fig.patch.set_facecolor('#0f172a')
    ax.text(.5,.94,"ICSim Spoof Injection Demo",ha='center',va='center',fontsize=20,fontweight='bold',color='white')
    ax.text(.5,.89,"observer-safe replay · highlighted injected packets · no live CAN traffic",ha='center',color='#94a3b8',fontsize=11)
    # speed card
    rounded(ax,(.06,.16),.38,.64,"Speed / Body State","ID 0x244 · ID 0x19B · ID 0x188",'#38bdf8','')
    circ=Circle((.25,.48),.17,fc='#111827',ec='#38bdf8',lw=4); ax.add_patch(circ)
    ax.text(.25,.51,"196",ha='center',va='center',fontsize=38,fontweight='bold',color='white')
    ax.text(.25,.42,"km/h",ha='center',color='#94a3b8',fontsize=12)
    # event stream
    rounded(ax,(.54,.16),.38,.64,"Injected Frame Review","45 labeled didactic packets",'#f97316','')
    events=[('0x244','speed spoof','33'),('0x19B','door state','7'),('0x188','turn signal','5')]
    y=.58
    for aid,label,count in events:
        ax.text(.60,y,aid,color='#facc15',fontsize=15,fontweight='bold')
        ax.text(.72,y,label,color='white',fontsize=13)
        ax.text(.88,y,count,color='#22c55e',fontsize=15,fontweight='bold',ha='right')
        y-=.12
    ax.text(.73,.24,"safe browser demo",ha='center',color='#94a3b8',fontsize=12)
    fig.savefig(ROOT/'demo-icsim-spoof/demo-icsim-spoof-preview.png', bbox_inches='tight', facecolor=fig.get_facecolor(), dpi=220)
    plt.close(fig)

pipeline(); evidence_dashboard(); realtime_timing(); demo_preview_png()
print('Generated v5 visuals in', FIG)
