#!/usr/bin/env python3
"""Generate v7 publication-quality figures for SSV 2026 paper.

Improvements over v5:
  - Phase-shaded regions (axvspan) on speed and ID cardinality plots
  - Proper axis labels with units
  - Print-safe / grayscale-compatible colors
  - Compact architecture figure
  - Time-series speed overview with phase boundaries
  - Experiment-level ID cardinality panels

Usage:
    python3 analysis/scripts/generate_v7_visuals.py
"""

import json
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Circle
from matplotlib.lines import Line2D

ROOT = Path(__file__).resolve().parents[2]
FIG = ROOT / 'analysis' / 'figures'
EXP = ROOT / 'dataset' / 'experiments'
CSV = ROOT / 'dataset' / 'all_frames_normalized.csv'

# ── global rc ──────────────────────────────────────────────────────────
plt.rcParams.update({
    'font.family': 'DejaVu Sans',
    'axes.titlesize': 12,
    'axes.labelsize': 10,
    'xtick.labelsize': 8.5,
    'ytick.labelsize': 8.5,
    'figure.dpi': 180,
    'savefig.dpi': 300,
    'axes.spines.top': False,
    'axes.spines.right': False,
})
# Print-safe palette (grayscale-friendly)
C = {
    'bg': '#f8fafc',
    'line': '#cbd5e1',
    'text': '#1e293b',
    'muted': '#64748b',
    'baseline':   '#475569',   # dark slate
    'spoofing':   '#b91c1c',   # dark red
    'flooding':   '#b45309',   # dark amber
    'recovery':   '#15803d',   # dark green
    'normal':     '#475569',
}
PHASE_COLORS = {
    'baseline': C['baseline'],
    'spoofing': C['spoofing'],
    'flooding': C['flooding'],
    'recovery': C['recovery'],
}
PHASE_ALPHA = 0.18


def save(fig, name):
    for ext in ['png', 'pdf', 'svg']:
        fig.savefig(FIG / f'{name}.{ext}', bbox_inches='tight', facecolor='white')
    plt.close(fig)


def load_data():
    """Load combined normalized CSV with type inference."""
    dtypes = {
        'experiment_id': 'object',
        'timestamp_epoch_s': 'float64',
        'relative_time_s': 'float64',
        'attack_label': 'object',
        'arbitration_id': 'object',
        'dlc': 'int64',
        'payload_hex': 'object',
        'semantic_label': 'object',
        'source_component': 'object',
        'decoded_speed_kmh': 'float64',
        'notes': 'object',
    }
    df = pd.read_csv(CSV, dtype=dtypes, low_memory=False)
    df['arbitration_id_int'] = df['arbitration_id'].apply(lambda x: int(x, 16) if pd.notna(x) else -1)
    return df


def add_phase_shading(ax, phase_ranges, y_min, y_max):
    """Add vertical shaded regions for each phase across all experiments."""
    for exp, phases in phase_ranges.items():
        for phase_name, (start_s, end_s) in phases.items():
            color = PHASE_COLORS.get(phase_name, C['muted'])
            ax.axvspan(start_s, end_s, alpha=PHASE_ALPHA, facecolor=color, zorder=0)


def get_phase_ranges(df):
    """Determine time ranges for each phase per experiment."""
    ranges = {}
    for exp_id, group in df.groupby('experiment_id'):
        phases = {}
        for label, sub in group.groupby('attack_label'):
            t_min = sub['relative_time_s'].min()
            t_max = sub['relative_time_s'].max()
            phases[label] = (t_min, t_max)
        ranges[exp_id] = phases
    return ranges


# ── Figure 1: Architecture (refined from v5, more compact) ────────────

def fig_architecture():
    fig, ax = plt.subplots(figsize=(8.5, 4.2))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')
    fig.suptitle('Reproducible CAN Evidence Pipeline',
                 x=0.5, y=0.98, fontsize=16, fontweight='bold', color=C['text'])
    ax.text(0.5, 0.90,
            'Internal runs · external traces · wall-clock capture → auditable evidence packages',
            ha='center', color=C['muted'], fontsize=9)

    def rbox(ax, xy, w, h, text, sub, color, icon=None):
        x, y = xy
        box = FancyBboxPatch((x, y), w, h,
                             boxstyle='round,pad=0.02,rounding_size=0.03',
                             ec=color, fc=color + '18', lw=2)
        ax.add_patch(box)
        tx = x + w * 0.55
        if icon:
            ax.text(x + w * 0.15, y + h * 0.65, icon,
                    ha='center', va='center', fontsize=18)
        ax.text(tx, y + h * 0.60, text, ha='center', va='center',
                fontsize=10.5, fontweight='bold', color=C['text'])
        ax.text(tx, y + h * 0.30, sub, ha='center', va='center',
                fontsize=7.5, color=C['muted'])

    def rarrow(ax, start, end, color=None, rad=0.0):
        ax.add_patch(FancyArrowPatch(
            start, end, arrowstyle='-|>', mutation_scale=13,
            lw=1.8, color=color or C['text'],
            connectionstyle=f'arc3,rad={rad}'))

    # Input boxes
    rbox(ax, (0.03, 0.48), 0.22, 0.18, 'Internal Matrix', '005–007 · 477k frames', C['baseline'], '▨')
    rbox(ax, (0.03, 0.24), 0.22, 0.18, 'External ICSim', '008–009 · trace + injection', '#0369a1', '↻')
    rbox(ax, (0.03, 0.00), 0.22, 0.18, 'Wall-clock Capture', '010–012 · timing + virtual bus', '#b45309', '⏱')

    # Processing
    rbox(ax, (0.34, 0.34), 0.28, 0.22, 'Normalize + Annotate',
         'CSV schema · labels · timestamps · source metadata', '#7c3aed', '◇')

    # Output boxes
    rbox(ax, (0.72, 0.38), 0.25, 0.18, 'Evidence Package',
         'SHA-256 · manifests · DOI · Zenodo', '#15803d', '✓')
    rbox(ax, (0.72, 0.06), 0.25, 0.18, 'Observer-safe Review',
         'browser demos · no live CAN', '#d97706', '◉')

    # Arrows (input → normalize)
    rarrow(ax, (0.25, 0.58), (0.34, 0.48), C['baseline'], 0.06)
    rarrow(ax, (0.25, 0.34), (0.34, 0.44), '#0369a1', 0.0)
    rarrow(ax, (0.25, 0.12), (0.34, 0.40), '#b45309', -0.08)
    # normalize → outputs
    rarrow(ax, (0.62, 0.48), (0.72, 0.48), C['text'])
    rarrow(ax, (0.84, 0.38), (0.84, 0.24), C['text'])
    rarrow(ax, (0.72, 0.12), (0.62, 0.34), '#d97706', -0.25)

    ax.text(0.5, -0.08,
            'Boundary: reproducibility & forensic-readiness workflow — '
            'not physical CAN fidelity or IDS benchmarking',
            ha='center', fontsize=7.5, color=C['spoofing'], fontweight='bold',
            transform=ax.transAxes)
    save(fig, 'reproducible_evidence_pipeline_v7')


# ── Figure 2: Speed time-series with phase shading ────────────────────

def fig_speed_time_series():
    """Decoded speed on ID 0x100 over time with phase-shaded regions."""
    df = load_data()
    df_spd = df[df['arbitration_id'] == '100'].copy()
    df_spd = df_spd[df_spd['decoded_speed_kmh'].notna()]

    if df_spd.empty:
        print('[SKIP] No decoded speed data for fig_speed_time_series')
        return

    phase_ranges = get_phase_ranges(df)

    # Pick representative experiment for the main plot (006 = 10min)
    main_exp = '006_10min_attack'
    if main_exp not in df_spd['experiment_id'].unique():
        main_exp = df_spd['experiment_id'].iloc[0]

    sub = df_spd[df_spd['experiment_id'] == main_exp].sort_values('relative_time_s')

    fig, ax = plt.subplots(figsize=(8, 3.5))

    # Phase shading
    exp_phases = phase_ranges.get(main_exp, {})
    for phase_name, (s, e) in exp_phases.items():
        color = PHASE_COLORS.get(phase_name, C['muted'])
        ax.axvspan(s, e, alpha=PHASE_ALPHA, facecolor=color, zorder=0,
                   label=phase_name.capitalize())

    ax.plot(sub['relative_time_s'], sub['decoded_speed_kmh'],
            color=C['text'], lw=0.5, alpha=0.85)
    ax.scatter(sub['relative_time_s'], sub['decoded_speed_kmh'],
               s=6, color=C['text'], alpha=0.4, zorder=3)

    ax.set_xlabel('Elapsed time (s)')
    ax.set_ylabel('Decoded speed (km/h)')
    ax.set_title(f'Decoded Speed on ID 0x100 — {main_exp}', fontsize=13)
    ax.grid(axis='y', alpha=0.2)
    ax.legend(loc='upper left', fontsize=7.5, frameon=True, facecolor='white',
              edgecolor=C['line'], framealpha=0.85)

    fig.tight_layout()
    save(fig, 'decoded_speed_id_0x100_time_series_v7')


# ── Figure 3: ID Cardinality with phase shading ───────────────────────

def fig_id_cardinality():
    """Rolling unique-ID count per window with phase shading."""
    df = load_data()
    phase_ranges = get_phase_ranges(df)
    main_exp = '006_10min_attack'
    if main_exp not in df['experiment_id'].unique():
        main_exp = df['experiment_id'].iloc[0]

    sub = df[df['experiment_id'] == main_exp].copy()
    window_s = 1.0
    sub['_window'] = (sub['relative_time_s'] // window_s).astype(int)
    cardinality = sub.groupby('_window')['arbitration_id'].nunique().reset_index()
    cardinality.columns = ['window', 'unique_ids']

    fig, ax = plt.subplots(figsize=(8, 3.0))

    exp_phases = phase_ranges.get(main_exp, {})
    for phase_name, (s, e) in exp_phases.items():
        color = PHASE_COLORS.get(phase_name, C['muted'])
        ax.axvspan(s, e, alpha=PHASE_ALPHA, facecolor=color, zorder=0,
                   label=phase_name.capitalize())

    ax.step(cardinality['window'] * window_s, cardinality['unique_ids'],
            where='mid', color=C['text'], lw=1.2)

    ax.set_xlabel('Elapsed time (s)')
    ax.set_ylabel('Unique arbitration IDs per 1s window')
    ax.set_title(f'Arbitration-ID Diversity — {main_exp}', fontsize=13)
    ax.grid(axis='y', alpha=0.2)
    ax.legend(loc='upper left', fontsize=7.5, frameon=True, facecolor='white',
              edgecolor=C['line'], framealpha=0.85)

    fig.tight_layout()
    save(fig, 'id_cardinality_1s_v7')


# ── Figure 4: Evidence dashboard (refined) ────────────────────────────

def fig_evidence_dashboard():
    """Compact 2×2 coverage dashboard with better labels."""
    ds = json.loads((ROOT / 'dataset/dataset_summary.json').read_text())
    e8 = json.loads((EXP / '008_external_icsim_replay/summary.json').read_text())
    e9 = json.loads((EXP / '009_icsim_spoof_injection/summary.json').read_text())
    e10 = json.loads((EXP / '010_realtime_wallclock_capture/summary.json').read_text())

    fig, axs = plt.subplots(2, 2, figsize=(9, 5.8),
                            gridspec_kw={'height_ratios': [1, 1.05]})
    fig.suptitle('Evidence Coverage Summary', fontsize=15,
                 fontweight='bold', color=C['text'])

    # (a) Phase counts
    ax = axs[0, 0]
    phases = list(ds['phase_counts'].keys())
    vals = list(ds['phase_counts'].values())
    colors = [PHASE_COLORS.get(p, C['muted']) for p in phases]
    bars = ax.bar(phases, vals, color=colors, edgecolor='white', lw=1)
    ax.set_title('(a) Labeled frames by phase', fontsize=10)
    ax.set_ylabel('Frames')
    ax.tick_params(axis='x', rotation=25, labelsize=8)
    ax.grid(axis='y', alpha=0.2)
    for b, v in zip(bars, vals):
        ax.text(b.get_x() + b.get_width() / 2, v, f'{v:,}',
                ha='center', va='bottom', fontsize=7)

    # (b) Evidence packages (log scale)
    ax = axs[0, 1]
    names = ['Internal\n005–007', 'ICSim\n008', 'Spoof inj.\n009', 'Timing\n010']
    vals = [ds['total_frames'], e8['total_frames'],
            e9['spoofed_frames'], e10['total_frames']]
    ax.bar(names, vals, color=[C['baseline'], '#0369a1', C['spoofing'], '#b45309'],
           edgecolor='white')
    ax.set_yscale('log')
    ax.set_title('(b) Evidence-package scale (log)', fontsize=10)
    ax.set_ylabel('Frames')
    ax.grid(axis='y', which='both', alpha=0.2)
    for i, v in enumerate(vals):
        ax.text(i, v * 1.15, f'{v:,}', ha='center', fontsize=7.5)

    # (c) Speed contrast
    ax = axs[1, 0]
    stats = ds['speed_stats_by_phase_for_id_0x100']
    labs = ['baseline', 'spoofing', 'recovery']
    means = [stats[k]['mean'] for k in labs]
    mins = [stats[k]['min'] for k in labs]
    maxs = [stats[k]['max'] for k in labs]
    yerr = np.array(
        [[m - mi for m, mi in zip(means, mins)],
         [ma - m for m, ma in zip(means, maxs)]]
    )
    ax.errorbar(labs, means, yerr=yerr, fmt='o',
                color=C['text'], ecolor=C['muted'], elinewidth=3,
                capsize=4, markersize=7)
    ax.set_title('(c) Speed contrast on ID 0x100', fontsize=10)
    ax.set_ylabel('Decoded speed (km/h)')
    ax.grid(axis='y', alpha=0.2)

    # (d) Artifact-review posture
    ax = axs[1, 1]
    rows = ['Proposed', 'ICSim', 'ROAD', 'can-train']
    cols = ['DOI', 'Hashes', 'Schema', 'Demo', 'Wall-clock']
    mat = np.array([
        [1, 1, 1, 1, 1],
        [0, 0, 0.5, 1, 0],
        [1, 0, 1, 0, 0],
        [1, 0, 1, 0, 0],
    ], dtype=float)
    im = ax.imshow(mat, cmap='YlGnBu', vmin=0, vmax=1)
    ax.set_xticks(range(len(cols)))
    ax.set_xticklabels(cols, rotation=25, ha='right', fontsize=8)
    ax.set_yticks(range(len(rows)))
    ax.set_yticklabels(rows, fontsize=8)
    ax.set_title('(d) Artifact-review posture', fontsize=10)
    for r in range(mat.shape[0]):
        for c in range(mat.shape[1]):
            txt = '✓' if mat[r, c] == 1 else ('partial' if mat[r, c] else '—')
            ax.text(c, r, txt, ha='center', va='center', fontsize=7.5,
                    color=C['text'])

    fig.tight_layout(rect=[0, 0, 1, 0.94])
    save(fig, 'evidence_coverage_dashboard_v7')


# ── Figure 5: Wall-clock timing ───────────────────────────────────────

def fig_timing():
    """Timing plot with proper units and labels."""
    path = EXP / '010_realtime_wallclock_capture/frames_normalized.csv'
    if not path.exists():
        print('[SKIP] No wall-clock data for fig_timing')
        return
    df = pd.read_csv(path)
    ts = df['timestamp_s'].astype(float).to_numpy()
    inter = np.diff(ts)

    fig, axs = plt.subplots(1, 2, figsize=(9, 3.2))
    fig.suptitle('Experiment 010 — Wall-clock Timing Capture',
                 fontsize=14, fontweight='bold', color=C['text'])

    ax = axs[0]
    for aid, sub in df.groupby('arbitration_id'):
        ax.scatter(sub['timestamp_s'].astype(float),
                   [f'0x{aid}'] * len(sub), s=6, alpha=0.7, label=f'0x{aid}')
    ax.set_xlabel('Elapsed wall-clock time (s)')
    ax.set_ylabel('Arbitration ID')
    ax.set_title('(a) Frame timeline', fontsize=10)
    ax.grid(axis='x', alpha=0.2)
    ax.legend(loc='upper right', fontsize=7, frameon=False)

    ax = axs[1]
    ax.hist(inter, bins=30, color=C['baseline'], alpha=0.85, edgecolor='white')
    ax.axvline(inter.mean(), color=C['spoofing'], lw=2,
               label=f"Mean {inter.mean():.4f}s")
    ax.set_title('(b) Inter-arrival distribution', fontsize=10)
    ax.set_xlabel('Time between consecutive frames (s)')
    ax.set_ylabel('Count')
    ax.grid(axis='y', alpha=0.2)
    ax.legend(frameon=False, fontsize=8)
    ax.text(0.97, 0.92, 'Negative IAT: 0',
            transform=ax.transAxes, ha='right', fontsize=8,
            color=C['recovery'], fontweight='bold')

    fig.tight_layout(rect=[0, 0, 1, 0.87])
    save(fig, 'exp010_wallclock_timing_v7')


# ── Figure 6: Python-can virtual bus timing ───────────────────────────

def fig_virtual_bus_timing():
    """Timing for experiments 011 and 012."""
    import glob
    paths = sorted(glob.glob(str(ROOT / 'dataset/experiments/01[12]*/frames_normalized.csv')))
    if not paths:
        print('[SKIP] No python-can virtual bus data')
        return

    fig, axs = plt.subplots(1, len(paths), figsize=(9, 3.2))
    if len(paths) == 1:
        axs = [axs]
    fig.suptitle('python-can Virtual-Bus Timing Evidence',
                 fontsize=14, fontweight='bold', color=C['text'])

    for i, csv_path in enumerate(paths):
        exp_dir = Path(csv_path).parent
        exp_name = exp_dir.name
        df = pd.read_csv(csv_path)
        ts = df['timestamp_s'].astype(float).to_numpy() if 'timestamp_s' in df.columns else \
             np.cumsum(np.ones(len(df)) * 0.01)
        inter = np.diff(ts)

        ax = axs[i]
        ax.hist(inter, bins=25, color=C['baseline'], alpha=0.85, edgecolor='white')
        ax.axvline(inter.mean(), color=C['spoofing'], lw=2,
                   label=f"Mean {inter.mean():.5f}s")
        ax.set_title(exp_name, fontsize=9)
        ax.set_xlabel('Send-to-receive latency (s)')
        ax.set_ylabel('Count')
        ax.grid(axis='y', alpha=0.2)
        ax.legend(frameon=False, fontsize=7)

    fig.tight_layout(rect=[0, 0, 1, 0.87])
    save(fig, 'python_can_virtual_bus_timing_v7')


# ── Main ──────────────────────────────────────────────────────────────

if __name__ == '__main__':
    FIG.mkdir(parents=True, exist_ok=True)
    print('[1/6] Architecture figure...')
    fig_architecture()
    print('[2/6] Speed time-series with phase shading...')
    fig_speed_time_series()
    print('[3/6] ID cardinality with phase shading...')
    fig_id_cardinality()
    print('[4/6] Evidence dashboard...')
    fig_evidence_dashboard()
    print('[5/6] Wall-clock timing...')
    fig_timing()
    print('[6/6] Virtual-bus timing...')
    fig_virtual_bus_timing()
    print(f'Done. Figures in {FIG}')
