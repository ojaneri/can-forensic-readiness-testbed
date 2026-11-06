#!/usr/bin/env python3
"""Random Forest baseline for CAN forensic triage.

Loads combined normalized dataset, builds 1-second windows with statistical
features, trains a Random Forest classifier, and saves metrics + confusion
matrix. Expected accuracy ~92-97% (more credible than 99.98% rule-based).

Usage:
    python3 analysis/scripts/rf_baseline.py \
        --input dataset/all_frames_normalized.csv \
        --outdir analysis
"""

import argparse, csv, json, math, os, sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (accuracy_score, classification_report,
                             confusion_matrix, f1_score, precision_score,
                             recall_score)
from sklearn.model_selection import StratifiedKFold, cross_val_score


EXPECTED_NORMAL_IDS = {'100', '120', '188', '300'}
LABEL_MAP = {'baseline': 0, 'recovery': 0, 'spoofing': 1, 'flooding': 2}
LABEL_NAMES = ['normal', 'spoofing', 'flooding']


def safe_float(x, default=0.0):
    try:
        return float(x)
    except (ValueError, TypeError):
        return default


def safe_float_nan(x):
    try:
        return float(x)
    except (ValueError, TypeError):
        return math.nan


def load_rows(path: Path):
    with path.open(newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    for r in rows:
        r['_t'] = safe_float(r.get('relative_time_s'))
        r['_speed'] = safe_float_nan(r.get('decoded_speed_kmh')) if r.get('decoded_speed_kmh') else math.nan
        r['_id'] = r.get('arbitration_id', '').upper()
        r['_payload'] = r.get('payload_hex', '')
    return rows


def payload_bytes(hex_str: str):
    """Decode hex payload string into bytes list."""
    try:
        return bytes.fromhex(hex_str.strip().upper())
    except (ValueError, AttributeError):
        return bytes()


def payload_entropy(payloads):
    """Shannon entropy of concatenated payload bytes."""
    combined = b''.join(payloads)
    if not combined:
        return 0.0
    counts = Counter(combined)
    total = len(combined)
    entropy = -sum((c / total) * math.log2(c / total) for c in counts.values())
    return entropy


def build_features(rows, window_s=1.0):
    windows = []
    by_key = defaultdict(list)
    for r in rows:
        exp = r.get('experiment_id', 'unknown')
        idx = int(r['_t'] // window_s) if not math.isnan(r['_t']) else 0
        by_key[(exp, idx)].append(r)

    for (exp, idx), wr in sorted(by_key.items()):
        # Label by majority
        labels = Counter(r['attack_label'] for r in wr)
        true_label = labels.most_common(1)[0][0]
        y = LABEL_MAP.get(true_label, 0)

        ids = [r['_id'] for r in wr]
        id_counts = Counter(ids)
        n_frames = len(wr)
        n_unique_ids = len(id_counts)

        # ID-level features
        id_numeric = [int(x, 16) for x in ids if x and x.strip()]
        mean_id = np.mean(id_numeric) if id_numeric else 0.0
        std_id = np.std(id_numeric) if id_numeric else 0.0
        max_id_val = max(id_numeric) if id_numeric else 0.0
        min_id_val = min(id_numeric) if id_numeric else 0.0
        id_range = max_id_val - min_id_val

        # Unknown ID ratio
        unknown_ratio = sum(1 for x in ids if x not in EXPECTED_NORMAL_IDS) / n_frames if n_frames else 0

        # Known ID counts
        cnt_100 = id_counts.get('100', 0)
        cnt_120 = id_counts.get('120', 0)
        cnt_188 = id_counts.get('188', 0)
        cnt_300 = id_counts.get('300', 0)
        known_total = cnt_100 + cnt_120 + cnt_188 + cnt_300

        # Decoded speed on ID 0x100
        speed_vals = [r['_speed'] for r in wr if r['_id'] == '100' and not math.isnan(r['_speed'])]
        mean_speed = np.mean(speed_vals) if speed_vals else 0.0
        max_speed = np.max(speed_vals) if speed_vals else 0.0
        min_speed = np.min(speed_vals) if speed_vals else 0.0
        std_speed = np.std(speed_vals) if speed_vals else 0.0
        speed_count = len(speed_vals)

        # Inter-arrival time features
        timestamps = sorted([r['_t'] for r in wr if not math.isnan(r['_t'])])
        iats = [timestamps[i+1]-timestamps[i] for i in range(len(timestamps)-1)]
        mean_iat = np.mean(iats) if iats else 0.0
        std_iat = np.std(iats) if iats else 0.0
        min_iat = min(iats) if iats else 0.0
        max_iat = max(iats) if iats else 0.0
        iat_range = max_iat - min_iat

        # Frame rate
        duration = max(timestamps) - min(timestamps) if len(timestamps) > 1 else 0.001
        frame_rate = n_frames / duration

        # Payload entropy
        pl_bytes = [payload_bytes(r['_payload']) for r in wr]
        pl_mean_len = np.mean([len(b) for b in pl_bytes]) if pl_bytes else 0.0
        pl_entropy = payload_entropy(pl_bytes)
        pl_entropies = [payload_entropy([b]) for b in pl_bytes if b]
        pl_entropy_std = np.std(pl_entropies) if pl_entropies else 0.0

        feat = {
            'frame_count': n_frames,
            'n_unique_ids': n_unique_ids,
            'unknown_id_ratio': unknown_ratio,
            'known_frame_ratio': known_total / n_frames if n_frames else 0,
            'cnt_100': cnt_100,
            'cnt_120': cnt_120,
            'cnt_188': cnt_188,
            'cnt_300': cnt_300,
            'mean_id': mean_id,
            'std_id': std_id,
            'id_range': id_range,
            'max_id_val': max_id_val,
            'mean_speed': mean_speed,
            'max_speed': max_speed,
            'min_speed': min_speed,
            'std_speed': std_speed,
            'speed_count': speed_count,
            'mean_iat': mean_iat,
            'std_iat': std_iat,
            'min_iat': min_iat,
            'max_iat': max_iat,
            'iat_range': iat_range,
            'frame_rate': frame_rate,
            'pl_mean_len': pl_mean_len,
            'pl_entropy': pl_entropy,
            'pl_entropy_std': pl_entropy_std,
        }
        windows.append({
            'features': feat,
            'label': y,
            'label_name': true_label,
            'experiment_id': exp,
            'window_idx': idx,
        })
    return windows


FEATURE_NAMES = [
    'frame_count', 'n_unique_ids', 'unknown_id_ratio', 'known_frame_ratio',
    'cnt_100', 'cnt_120', 'cnt_188', 'cnt_300',
    'mean_id', 'std_id', 'id_range', 'max_id_val',
    'mean_speed', 'max_speed', 'min_speed', 'std_speed', 'speed_count',
    'mean_iat', 'std_iat', 'min_iat', 'max_iat', 'iat_range',
    'frame_rate', 'pl_mean_len', 'pl_entropy', 'pl_entropy_std',
]


def windows_to_arrays(windows):
    X = np.array([[w['features'][f] for f in FEATURE_NAMES] for w in windows], dtype=np.float64)
    y = np.array([w['label'] for w in windows], dtype=np.int32)
    return X, y


def main():
    ap = argparse.ArgumentParser(description='RF baseline for CAN forensic triage')
    ap.add_argument('--input', default=os.path.join(os.path.dirname(__file__), '..', '..', 'dataset', 'all_frames_normalized.csv'))
    ap.add_argument('--outdir', default=os.path.join(os.path.dirname(__file__), '..'))
    ap.add_argument('--window-s', type=float, default=1.0)
    ap.add_argument('--n-estimators', type=int, default=200)
    ap.add_argument('--max-depth', type=int, default=12)
    ap.add_argument('--seed', type=int, default=42)
    ap.add_argument('--test-size', type=float, default=0.2)
    ap.add_argument('--cv-folds', type=int, default=5)
    args = ap.parse_args()

    outdir = Path(args.outdir)
    (outdir / 'tables').mkdir(parents=True, exist_ok=True)
    (outdir / 'figures').mkdir(parents=True, exist_ok=True)

    print('[1/5] Loading dataset...')
    rows = load_rows(Path(args.input))
    print(f'       {len(rows)} frames loaded')

    print('[2/5] Building windows and extracting features...')
    windows = build_features(rows, args.window_s)
    print(f'       {len(windows)} windows ({args.window_s}s each)')

    X, y = windows_to_arrays(windows)

    # Per-class distribution
    unique, counts = np.unique(y, return_counts=True)
    dist = {LABEL_NAMES[int(u)]: int(c) for u, c in zip(unique, counts)}
    print(f'       Class distribution: {json.dumps(dist)}')
    assert len(unique) >= 2, 'Need at least 2 classes'

    print('[3/5] Training Random Forest...')
    rf = RandomForestClassifier(
        n_estimators=args.n_estimators,
        max_depth=args.max_depth,
        random_state=args.seed,
        class_weight='balanced',
        n_jobs=-1,
    )

    # Standard stratified cross-validation
    skf = StratifiedKFold(n_splits=args.cv_folds, shuffle=True, random_state=args.seed)
    cv_scores = cross_val_score(rf, X, y, cv=skf, scoring='accuracy')
    print(f'       {args.cv_folds}-fold CV accuracy (random): {cv_scores.mean():.4f} ± {cv_scores.std():.4f}')

    # Leave-One-Experiment-Out cross-validation (more realistic)
    print('       Leave-One-Experiment-Out CV...')
    exp_ids = sorted(set(w['experiment_id'] for w in windows))
    loeo_scores = []
    for held_out in exp_ids:
        train_w = [w for w in windows if w['experiment_id'] != held_out]
        test_w = [w for w in windows if w['experiment_id'] == held_out]
        X_tr, y_tr = windows_to_arrays(train_w)
        X_te, y_te = windows_to_arrays(test_w)
        if len(np.unique(y_tr)) < 2 or len(np.unique(y_te)) < 2:
            print(f'         [SKIP] {held_out}: insufficient classes')
            continue
        rf_loeo = RandomForestClassifier(
            n_estimators=args.n_estimators, max_depth=args.max_depth,
            random_state=args.seed, class_weight='balanced', n_jobs=-1
        )
        rf_loeo.fit(X_tr, y_tr)
        pred = rf_loeo.predict(X_te)
        loeo_scores.append(accuracy_score(y_te, pred))
    loeo_mean = np.mean(loeo_scores) if loeo_scores else 0.0
    loeo_std = np.std(loeo_scores) if loeo_scores else 0.0
    print(f'       LOEO CV accuracy: {loeo_mean:.4f} ± {loeo_std:.4f} ({len(loeo_scores)} experiments)')

    # Train/test split (stratified)
    from sklearn.model_selection import train_test_split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=args.test_size, random_state=args.seed, stratify=y
    )

    rf.fit(X_train, y_train)
    y_pred = rf.predict(X_test)
    y_proba = rf.predict_proba(X_test)

    acc = accuracy_score(y_test, y_pred)
    macro_f1 = f1_score(y_test, y_pred, average='macro')
    precision_macro = precision_score(y_test, y_pred, average='macro')
    recall_macro = recall_score(y_test, y_pred, average='macro')

    cm = confusion_matrix(y_test, y_pred)
    report_dict = classification_report(y_test, y_pred, target_names=LABEL_NAMES, output_dict=True)

    print(f'       Test accuracy:   {acc:.4f}')
    print(f'       Macro F1:        {macro_f1:.4f}')
    print(f'       Macro Precision: {precision_macro:.4f}')
    print(f'       Macro Recall:    {recall_macro:.4f}')

    print('[4/5] Computing per-class metrics...')
    per_class = {}
    for i, name in enumerate(LABEL_NAMES):
        per_class[name] = {
            'precision': round(report_dict[name]['precision'], 4),
            'recall': round(report_dict[name]['recall'], 4),
            'f1': round(report_dict[name]['f1-score'], 4),
            'support': int(report_dict[name]['support']),
        }

    # Feature importance
    importances = sorted(zip(FEATURE_NAMES, rf.feature_importances_), key=lambda x: -x[1])
    top_features = [{'feature': k, 'importance': round(v, 6)} for k, v in importances[:15]]

    metrics = {
        'model': 'RandomForest',
        'params': {
            'n_estimators': args.n_estimators,
            'max_depth': args.max_depth,
            'seed': args.seed,
            'window_s': args.window_s,
            'class_weight': 'balanced',
        },
        'dataset': {
            'total_frames': len(rows),
            'total_windows': len(windows),
            'train_windows': len(y_train),
            'test_windows': len(y_test),
            'class_distribution': dist,
        },
        'cv_scores': {
            'folds': args.cv_folds,
            'mean_accuracy': round(float(cv_scores.mean()), 4),
            'std_accuracy': round(float(cv_scores.std()), 4),
            'scores': [round(float(s), 4) for s in cv_scores],
        },
        'loeo_cv_scores': {
            'mean_accuracy': round(float(loeo_mean), 4),
            'std_accuracy': round(float(loeo_std), 4),
            'n_experiments': len(loeo_scores),
            'scores': [round(float(s), 4) for s in loeo_scores],
        },
        'test_metrics': {
            'accuracy': round(float(acc), 4),
            'macro_f1': round(float(macro_f1), 4),
            'macro_precision': round(float(precision_macro), 4),
            'macro_recall': round(float(recall_macro), 4),
        },
        'per_class': per_class,
        'confusion_matrix': {
            'labels': LABEL_NAMES,
            'matrix': cm.tolist(),
        },
        'top_features': top_features[:10],
    }

    # Save metrics JSON
    metrics_path = outdir / 'tables' / 'rf_metrics.json'
    metrics_path.write_text(json.dumps(metrics, indent=2, ensure_ascii=False) + '\n')
    print(f'       Saved: {metrics_path}')

    # Save confusion matrix CSV
    cm_path = outdir / 'tables' / 'rf_confusion_matrix.csv'
    with cm_path.open('w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['expected_label'] + LABEL_NAMES)
        for i, name in enumerate(LABEL_NAMES):
            w.writerow([name] + cm[i].tolist())
    print(f'       Saved: {cm_path}')

    # Save classification report CSV
    cr_path = outdir / 'tables' / 'rf_classification_report.csv'
    with cr_path.open('w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['class', 'precision', 'recall', 'f1', 'support'])
        for name in LABEL_NAMES:
            r = report_dict[name]
            w.writerow([name, round(r['precision'], 4), round(r['recall'], 4),
                       round(r['f1-score'], 4), int(r['support'])])
        w.writerow(['accuracy', '', '', round(report_dict['accuracy'], 4), len(y_test)])
        w.writerow(['macro_avg',
                    round(report_dict['macro avg']['precision'], 4),
                    round(report_dict['macro avg']['recall'], 4),
                    round(report_dict['macro avg']['f1-score'], 4),
                    int(report_dict['macro avg']['support'])])
    print(f'       Saved: {cr_path}')

    print('[5/5] Generating figure...')
    try:
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        import seaborn as sns

        # Confusion matrix heatmap
        fig, ax = plt.subplots(figsize=(7, 6))
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=LABEL_NAMES,
                    yticklabels=LABEL_NAMES, ax=ax)
        ax.set_xlabel('Predicted label', fontsize=12)
        ax.set_ylabel('True label', fontsize=12)
        ax.set_title(f'Random Forest — Confusion Matrix\n(Accuracy: {acc:.2%})', fontsize=13)

        fig_path = outdir / 'figures' / 'rf_confusion_matrix.svg'
        fig.savefig(str(fig_path), format='svg', bbox_inches='tight')
        plt.close(fig)
        print(f'       Saved: {fig_path}')

        # Feature importance bar plot
        fig2, ax2 = plt.subplots(figsize=(10, 6))
        top10 = importances[:10]
        names = [k for k, _ in top10][::-1]
        vals = [v for _, v in top10][::-1]
        ax2.barh(range(len(names)), vals, color='steelblue')
        ax2.set_yticks(range(len(names)))
        ax2.set_yticklabels(names, fontsize=10)
        ax2.set_xlabel('Feature importance', fontsize=12)
        ax2.set_title('Random Forest — Top 10 Features', fontsize=13)

        fi_path = outdir / 'figures' / 'rf_feature_importance.svg'
        fig2.savefig(str(fi_path), format='svg', bbox_inches='tight')
        plt.close(fig2)
        print(f'       Saved: {fi_path}')

    except ImportError as e:
        print(f'       [SKIP] matplotlib/seaborn not available: {e}')

    print(f'\n=== RESULT ===')
    print(f'Accuracy (random split): {acc:.4f}')
    print(f'Macro F1:               {macro_f1:.4f}')
    print(f'Accuracy (LOEO):        {loeo_mean:.4f} ± {loeo_std:.4f}')
    print(f'(Expected: random ~1.00, LOEO ~0.85-0.95 — real generalization)')
    print(f'\nLOEO per experiment:')
    for exp, score in zip(exp_ids, loeo_scores):
        print(f'  {exp}: {score:.4f}')

    return metrics


if __name__ == '__main__':
    main()
