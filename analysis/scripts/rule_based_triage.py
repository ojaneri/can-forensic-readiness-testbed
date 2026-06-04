#!/usr/bin/env python3
from __future__ import annotations

import argparse, csv, json, math
from collections import Counter, defaultdict
from pathlib import Path

LABELS = ['baseline', 'spoofing', 'flooding', 'recovery']
PRED_LABELS = ['normal', 'spoofing', 'flooding']
EXPECTED_NORMAL_IDS = {'100', '120', '188', '300'}

def safe_float(x, default=0.0):
    try: return float(x)
    except Exception: return default

def load_rows(path: Path):
    with path.open(newline='', encoding='utf-8') as f:
        rows = list(csv.DictReader(f))
    for r in rows:
        r['relative_time_s_float'] = safe_float(r.get('relative_time_s'))
        r['decoded_speed_kmh_float'] = safe_float(r.get('decoded_speed_kmh'), math.nan) if r.get('decoded_speed_kmh') else math.nan
        r['arbitration_id_norm'] = r.get('arbitration_id','').upper()
    return rows

def build_windows(rows, window_s=1.0):
    by_key = defaultdict(list)
    for r in rows:
        exp = r.get('experiment_id', 'unknown')
        idx = int(r['relative_time_s_float'] // window_s)
        by_key[(exp, idx)].append(r)
    windows = []
    for (exp, idx), wr in sorted(by_key.items()):
        labels = Counter(r['attack_label'] for r in wr)
        true_label = labels.most_common(1)[0][0]
        ids = [r['arbitration_id_norm'] for r in wr]
        id_counts = Counter(ids)
        unique_ids = len(id_counts)
        total = len(wr)
        speed_values = [r['decoded_speed_kmh_float'] for r in wr if r['arbitration_id_norm'] == '100' and not math.isnan(r['decoded_speed_kmh_float'])]
        max_speed = max(speed_values) if speed_values else None
        mean_speed = sum(speed_values)/len(speed_values) if speed_values else None
        unknown_ratio = sum(1 for x in ids if x not in EXPECTED_NORMAL_IDS) / total if total else 0
        timestamps = sorted(r['relative_time_s_float'] for r in wr)
        duration = max(timestamps)-min(timestamps) if len(timestamps) > 1 else 0
        frame_rate = total / duration if duration > 0 else total
        windows.append({
            'experiment_id': exp,
            'window_index': idx,
            'window_start_s': round(idx*window_s, 3),
            'window_end_s': round((idx+1)*window_s, 3),
            'true_label': true_label,
            'frame_count': total,
            'unique_arbitration_ids': unique_ids,
            'unknown_id_ratio': round(unknown_ratio, 6),
            'max_decoded_speed_kmh': '' if max_speed is None else round(max_speed, 3),
            'mean_decoded_speed_kmh': '' if mean_speed is None else round(mean_speed, 3),
            'frame_rate_estimate_fps': round(frame_rate, 3),
        })
    return windows

def predict(w):
    # Explainable forensic triage baseline.
    # Rule priority matters: flooding is high-cardinality/high-unknown-ID behavior;
    # spoofing is abnormal decoded speed on the known state ID 0x100.
    if w['unique_arbitration_ids'] >= 20 or w['unknown_id_ratio'] >= 0.35:
        return 'flooding', 'high_id_cardinality_or_unknown_id_ratio'
    max_speed = w['max_decoded_speed_kmh']
    if max_speed != '' and float(max_speed) >= 130:
        return 'spoofing', 'decoded_speed_threshold_exceeded'
    return 'normal', 'no_rule_triggered'

def expected_detection_label(true_label):
    return {'baseline':'normal', 'recovery':'normal', 'spoofing':'spoofing', 'flooding':'flooding'}.get(true_label, true_label)

def metrics(windows):
    matrix = {t:{p:0 for p in PRED_LABELS} for t in PRED_LABELS}
    for w in windows:
        t = expected_detection_label(w['true_label'])
        p = w['predicted_label']
        matrix[t][p] += 1
    per_class = {}
    for label in PRED_LABELS:
        tp = matrix[label][label]
        fp = sum(matrix[t][label] for t in PRED_LABELS if t != label)
        fn = sum(matrix[label][p] for p in PRED_LABELS if p != label)
        precision = tp/(tp+fp) if tp+fp else 0
        recall = tp/(tp+fn) if tp+fn else 0
        f1 = 2*precision*recall/(precision+recall) if precision+recall else 0
        per_class[label] = {'precision':round(precision,4), 'recall':round(recall,4), 'f1':round(f1,4), 'support':sum(matrix[label].values())}
    total = sum(sum(row.values()) for row in matrix.values())
    correct = sum(matrix[l][l] for l in PRED_LABELS)
    macro_f1 = sum(v['f1'] for v in per_class.values())/len(PRED_LABELS)
    return {'confusion_matrix': matrix, 'accuracy': round(correct/total,4) if total else 0, 'macro_f1': round(macro_f1,4), 'per_class': per_class, 'window_count': total}

def write_csv(path, rows, fields):
    with path.open('w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader(); w.writerows(rows)

def svg_confusion(matrix, out):
    labels=PRED_LABELS; cell=110; left=150; top=90; width=left+cell*len(labels)+40; height=top+cell*len(labels)+80
    maxv=max(max(row.values()) for row in matrix.values()) or 1
    parts=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">', '<rect width="100%" height="100%" fill="#f8fafc"/>', f'<text x="{width/2}" y="34" text-anchor="middle" font-family="Arial" font-size="22" font-weight="700">Rule-Based Triage Confusion Matrix</text>', f'<text x="{width/2}" y="64" text-anchor="middle" font-family="Arial" font-size="14">Predicted label</text>', f'<text x="25" y="{height/2}" transform="rotate(-90 25 {height/2})" text-anchor="middle" font-family="Arial" font-size="14">Expected label</text>']
    for j,p in enumerate(labels): parts.append(f'<text x="{left+j*cell+cell/2}" y="{top-14}" text-anchor="middle" font-family="Arial" font-size="13">{p}</text>')
    for i,t in enumerate(labels):
        parts.append(f'<text x="{left-14}" y="{top+i*cell+cell/2+5}" text-anchor="end" font-family="Arial" font-size="13">{t}</text>')
        for j,p in enumerate(labels):
            v=matrix[t][p]; shade=int(245 - 170*(v/maxv)); fill=f'rgb({shade},{min(255,shade+25)},255)'
            x=left+j*cell; y=top+i*cell
            parts.append(f'<rect x="{x}" y="{y}" width="{cell}" height="{cell}" fill="{fill}" stroke="#334155"/>')
            parts.append(f'<text x="{x+cell/2}" y="{y+cell/2+6}" text-anchor="middle" font-family="Arial" font-size="24" font-weight="700">{v}</text>')
    parts.append('</svg>')
    out.write_text('\n'.join(parts), encoding='utf-8')

def main():
    ap=argparse.ArgumentParser(description='Rule-based forensic triage baseline for the software-defined CAN dataset.')
    ap.add_argument('--input', default='/var/www/html/admin.janeri.com.br/adriana/artigo/testbed/dataset/all_frames_normalized.csv')
    ap.add_argument('--outdir', default='/var/www/html/admin.janeri.com.br/adriana/artigo/testbed/analysis')
    ap.add_argument('--window-s', type=float, default=1.0)
    args=ap.parse_args()
    outdir=Path(args.outdir); (outdir/'tables').mkdir(parents=True, exist_ok=True); (outdir/'figures').mkdir(parents=True, exist_ok=True)
    rows=load_rows(Path(args.input))
    windows=build_windows(rows, args.window_s)
    for w in windows:
        pred, reason = predict(w)
        w['expected_detection_label'] = expected_detection_label(w['true_label'])
        w['predicted_label'] = pred
        w['rule_reason'] = reason
    fields=['experiment_id','window_index','window_start_s','window_end_s','true_label','expected_detection_label','predicted_label','rule_reason','frame_count','unique_arbitration_ids','unknown_id_ratio','max_decoded_speed_kmh','mean_decoded_speed_kmh','frame_rate_estimate_fps']
    write_csv(outdir/'tables'/'rule_based_triage_windows.csv', windows, fields)
    m=metrics(windows)
    (outdir/'tables'/'rule_based_triage_metrics.json').write_text(json.dumps(m,indent=2,ensure_ascii=False)+'\n', encoding='utf-8')
    # confusion matrix csv
    with (outdir/'tables'/'rule_based_triage_confusion_matrix.csv').open('w', newline='', encoding='utf-8') as f:
        wr=csv.writer(f); wr.writerow(['expected_label']+PRED_LABELS)
        for t in PRED_LABELS: wr.writerow([t]+[m['confusion_matrix'][t][p] for p in PRED_LABELS])
    svg_confusion(m['confusion_matrix'], outdir/'figures'/'rule_based_triage_confusion_matrix.svg')
    print(json.dumps(m,indent=2,ensure_ascii=False))

if __name__ == '__main__':
    main()
