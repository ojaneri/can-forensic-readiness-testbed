# Analysis Outputs

Generated from the English dataset package.

## Figures

- `figures/frame_count_by_phase.svg`
- `figures/decoded_speed_id_0x100.svg`
- `figures/id_cardinality_10s.svg`

## Tables

- `tables/frame_counts_by_phase.csv`
- `tables/speed_stats_id_0x100.csv`

## Main result

Experiment 006 provides a 10-minute controlled run with 40,200 frames. Spoofing concentrates decoded speed on ID `0x100` around 180–200 km/h, while baseline and recovery remain around 61 km/h on average. Flooding increases arbitration ID diversity and frame volume.


## Rule-Based Forensic Triage Baseline

A simple explainable triage model was implemented over 1-second windows.

Rules:

1. Predict `flooding` when the window has high arbitration ID cardinality or high unknown-ID ratio.
2. Predict `spoofing` when decoded speed on ID `0x100` exceeds 130 km/h.
3. Otherwise predict `normal` for baseline/recovery traffic.

Results over 615 windows:

- Accuracy: 0.9984
- Macro-F1: 0.9982
- Normal F1: 0.9986
- Spoofing F1: 1.0
- Flooding F1: 0.996

Additional files:

- `tables/rule_based_triage_windows.csv`
- `tables/rule_based_triage_metrics.json`
- `tables/rule_based_triage_confusion_matrix.csv`
- `figures/rule_based_triage_confusion_matrix.svg`
