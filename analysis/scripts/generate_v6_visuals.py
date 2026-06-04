#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
ROOT=Path(__file__).resolve().parents[2]; FIG=ROOT/'analysis/figures'; EXP=ROOT/'dataset/experiments'
plt.rcParams.update({'font.family':'DejaVu Sans','figure.dpi':180,'savefig.dpi':320,'axes.spines.top':False,'axes.spines.right':False,'axes.titlesize':12,'axes.labelsize':9,'xtick.labelsize':8,'ytick.labelsize':8})
C={'navy':'#0f172a','muted':'#64748b','blue':'#2563eb','cyan':'#0891b2','green':'#16a34a','amber':'#d97706','red':'#dc2626','purple':'#7c3aed','orange':'#f97316','line':'#cbd5e1'}
def save(fig,name):
 for ext in ['png','pdf','svg']: fig.savefig(FIG/f'{name}.{ext}',bbox_inches='tight',facecolor='white')
 plt.close(fig)
def box(ax,x,y,w,h,title,sub,color):
 ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle='round,pad=.02,rounding_size=.035',ec=color,fc=color+'18',lw=2.2))
 ax.text(x+w/2,y+h*.62,title,ha='center',va='center',fontsize=11,fontweight='bold',color=C['navy'])
 ax.text(x+w/2,y+h*.36,sub,ha='center',va='center',fontsize=8,color=C['muted'])
def arr(ax,a,b,color=None,rad=0):
 ax.add_patch(FancyArrowPatch(a,b,arrowstyle='-|>',mutation_scale=15,lw=2,color=color or C['navy'],connectionstyle=f'arc3,rad={rad}'))
def pipeline():
 fig,ax=plt.subplots(figsize=(11,6)); ax.set_xlim(0,1); ax.set_ylim(0,1); ax.axis('off')
 fig.suptitle('Reproducible CAN Evidence Pipeline — v6',fontsize=18,fontweight='bold',color=C['navy'])
 ax.text(.5,.91,'Internal generation, external replay and python-can virtual-bus captures produce auditable evidence packages',ha='center',fontsize=10,color=C['muted'])
 box(ax,.04,.66,.21,.14,'Internal Matrix','005–007 · 477,738 frames',C['blue'])
 box(ax,.04,.47,.21,.14,'External ICSim','008–009 · ingestion + injection',C['cyan'])
 box(ax,.04,.28,.21,.14,'Wall-clock','010 · 1,167 frames / 20s',C['amber'])
 box(ax,.04,.09,.21,.14,'python-can Bus','011/012 · virtual-bus replay',C['purple'])
 box(ax,.36,.42,.25,.20,'Common Schema','normalized CSV · labels · timestamps',C['navy'])
 box(ax,.70,.57,.24,.17,'Evidence Pack','SHA-256 · metadata · DOI',C['green'])
 box(ax,.70,.28,.24,.17,'Review Surface','paper · demos · CI · release',C['orange'])
 for y,col in [(.73,C['blue']),(.54,C['cyan']),(.35,C['amber']),(.16,C['purple'])]: arr(ax,(.25,y),(.36,.52),col,0.05)
 arr(ax,(.61,.52),(.70,.64),C['green']); arr(ax,(.61,.48),(.70,.36),C['orange']); arr(ax,(.82,.28),(.82,.20),C['orange'])
 ax.text(.5,.035,'Boundary: reproducibility and forensic-readiness workflow — no physical CAN fidelity or operational IDS claim',ha='center',fontsize=9.5,color=C['red'],fontweight='bold')
 save(fig,'reproducible_evidence_pipeline_v6')
def dashboard():
 ds=json.loads((ROOT/'dataset/dataset_summary.json').read_text()); e8=json.loads((EXP/'008_external_icsim_replay/summary.json').read_text()); e9=json.loads((EXP/'009_icsim_spoof_injection/summary.json').read_text()); e10=json.loads((EXP/'010_realtime_wallclock_capture/summary.json').read_text()); e11=json.loads((EXP/'011_python_can_virtual_bus/summary.json').read_text()); e12=json.loads((EXP/'012_python_can_icsim_replay/summary.json').read_text())
 fig,axs=plt.subplots(2,2,figsize=(11,6.6)); fig.suptitle('v6 Evidence and Reproducibility Dashboard',fontsize=17,fontweight='bold',color=C['navy'])
 ax=axs[0,0]; phases=list(ds['phase_counts']); vals=list(ds['phase_counts'].values()); bars=ax.bar(phases,vals,color=[C['blue'],C['purple'],C['red'],C['green']],edgecolor='white'); ax.set_title('Internal labeled frames'); ax.set_ylabel('frames'); ax.tick_params(axis='x',rotation=20); ax.grid(axis='y',alpha=.2)
 for b,v in zip(bars,vals): ax.text(b.get_x()+b.get_width()/2,v,f'{v:,}',ha='center',va='bottom',fontsize=7)
 ax=axs[0,1]; names=['Internal\n005–007','ICSim\n008','Spoof\n009','Clock\n010','py-can\n011','Replay\n012']; vals=[ds['total_frames'],e8['total_frames'],e9['spoofed_frames'],e10['total_frames'],e11['total_frames'],e12['replayed_frames']]
 ax.bar(names,vals,color=[C['blue'],C['cyan'],C['orange'],C['amber'],C['purple'],C['green']],edgecolor='white'); ax.set_yscale('log'); ax.set_title('Package scale (log)'); ax.set_ylabel('frames'); ax.grid(axis='y',which='both',alpha=.2)
 for i,v in enumerate(vals): ax.text(i,v*1.12,f'{v:,}',ha='center',fontsize=7)
 ax=axs[1,0]; labs=['010 wall-clock','011 py-can','012 ICSim replay']; means=[e10['inter_arrival_s']['mean'],e11['inter_arrival_s']['mean'],e12['inter_arrival_s']['mean']]; med=[e10['inter_arrival_s']['median'],e11['inter_arrival_s']['median'],e12['inter_arrival_s']['median']]
 x=np.arange(len(labs)); ax.bar(x-.18,means,.36,label='mean',color=C['blue']); ax.bar(x+.18,med,.36,label='median',color=C['cyan']); ax.set_xticks(x,labs,rotation=15,ha='right'); ax.set_ylabel('seconds'); ax.set_title('Wall-clock timing evidence'); ax.grid(axis='y',alpha=.2); ax.legend(frameon=False,fontsize=8)
 ax=axs[1,1]; rows=['Proposed v6','ICSim','ROAD','can-train']; cols=['DOI','Hashes','Schema','Demo','CI','py-can']; mat=np.array([[1,1,1,1,1,1],[0,0,.5,1,0,0],[1,0,1,0,0,0],[1,0,1,0,0,0]])
 ax.imshow(mat,cmap='YlGnBu',vmin=0,vmax=1); ax.set_xticks(range(len(cols)),cols,rotation=25,ha='right'); ax.set_yticks(range(len(rows)),rows); ax.set_title('Artifact-review posture')
 for r in range(mat.shape[0]):
  for c in range(mat.shape[1]): ax.text(c,r,'✓' if mat[r,c]==1 else ('partial' if mat[r,c] else '—'),ha='center',va='center',fontsize=8,color=C['navy'])
 fig.tight_layout(rect=[0,0,1,.94]); save(fig,'evidence_coverage_dashboard_v6')
def pycan_timing():
 e11=pd.read_csv(EXP/'011_python_can_virtual_bus/frames_normalized.csv'); e12=pd.read_csv(EXP/'012_python_can_icsim_replay/frames_normalized.csv')
 fig,axs=plt.subplots(1,2,figsize=(11,3.9)); fig.suptitle('python-can Virtual Bus Evidence — Experiments 011/012',fontsize=16,fontweight='bold',color=C['navy'])
 for ax,df,title in [(axs[0],e11,'011 generated virtual traffic'),(axs[1],e12,'012 external ICSim replay')]:
  ts=df['timestamp_s'].astype(float).to_numpy(); inter=np.diff(ts); lat=df['send_to_recv_latency_s'].astype(float).to_numpy()
  ax.hist(inter,bins=40,alpha=.75,color=C['blue'],label='inter-arrival',edgecolor='white'); ax.axvline(inter.mean(),color=C['red'],lw=2,label=f'inter mean {inter.mean():.4f}s')
  ax2=ax.twinx(); ax2.plot(np.linspace(0,1,min(300,len(lat))),lat[:min(300,len(lat))]*1000,color=C['green'],alpha=.55,lw=1,label='latency ms')
  ax.set_title(title); ax.set_xlabel('seconds'); ax.set_ylabel('inter-arrival count'); ax2.set_ylabel('send→recv latency (ms)'); ax.grid(axis='y',alpha=.2)
  lines=[Line for Line in ax.get_legend_handles_labels()[0]+ax2.get_legend_handles_labels()[0]]; labels=ax.get_legend_handles_labels()[1]+ax2.get_legend_handles_labels()[1]
  ax.legend(lines,labels,frameon=False,fontsize=7,loc='upper right')
 fig.tight_layout(rect=[0,0,1,.88]); save(fig,'python_can_virtual_bus_timing_v6')
pipeline(); dashboard(); pycan_timing(); print('v6 visuals generated')
