# Results — Draft Section

## Dataset Overview

The software-defined testbed now contains the initial two labeled experiments plus a second experimental round and an external-source compatibility experiment. Experiment 005 is a short proof-of-concept run, Experiment 006 is a longer 10-minute statistical run, and Matrix 007 adds 10 scheduled 10-minute runs with low/medium/high spoofing and flooding intensities. Across the internal labeled experiments, the normalized dataset contains 477,738 CAN frames with phase labels for baseline, spoofing, flooding, and recovery.

Experiment 006 produced 40,200 frames over 600.06 seconds. Matrix 007 added 435,450 frames over 6,000 seconds of deterministic synthetic schedule. Combined internal phase counts are 123,977 baseline frames, 78,986 spoofing frames, 151,038 flooding frames, and 123,737 recovery frames. Experiment 008 separately imports 6,158 frames from the public ICSim `data/sample-can.log` trace as external-source ingestion/replay-readiness evidence.

## Spoofing Effect on Decoded Speed

The testbed encodes a didactic speed signal in arbitration ID `0x100`. During the baseline phase of Experiment 006, the decoded speed ranged from 27 to 92 km/h, with a mean of 61.04 km/h. During spoofing, the fabricated speed values ranged from 180 to 200 km/h, with a mean of 195.00 km/h. After the attack window, the recovery phase returned to a normal range of 27 to 92 km/h, with a mean of 61.56 km/h.

This before/during/after behavior demonstrates that the testbed can produce labeled traffic suitable for reproducible attack demonstration and forensic triage.

## Flooding and Arbitration ID Diversity

The controlled flooding phase generated high-cardinality arbitration IDs and randomized payloads. In Experiment 006, flooding contributed 11,646 frames and increased the number of unique arbitration IDs per time window. Matrix 007 varied flooding intensity from approximately 50 fps to 200 fps, producing 6,000, 12,000, or 24,000 flooding frames per 120-second flooding phase depending on the selected profile. This behavior provides a clear contrast against the stable baseline, where traffic is dominated by a small set of simulated IDs: `0x100`, `0x120`, `0x188`, and `0x300`.

## Second-Round Matrix

Matrix 007 strengthens the paper by replacing single-run evidence with a controlled parameter-sensitivity round. It contains 10 runs of 600 seconds each, with four phases per run: 180 seconds baseline, 120 seconds spoofing, 120 seconds flooding, and 180 seconds recovery. Spoofing intensity controls fabricated speed range and injection period; flooding intensity controls high-cardinality frame rate. One medium/medium combination is repeated with a different seed to document run-to-run variation.

This round should be described as deterministic fast-run event simulation: timestamps follow the declared 10-minute schedule, but the generator does not wait for real wall-clock execution. The evidence supports reproducibility, parameter sensitivity, and forensic-readiness analysis; it does not claim physical CAN fidelity.

## External-Source Compatibility: ICSim Sample Trace

Experiment 008 addresses the adversarial-review concern that the artifact could be perceived as a closed synthetic toy simulator. It imports the public ICSim `data/sample-can.log` trace from commit `2b3333ef866987d8adc9c15ff15b9b9189edf85b`, preserves the raw log, records upstream metadata and GPL-3.0 licensing, normalizes the frames into the same CSV schema, computes SHA-256 manifests, and generates a summary report.

The imported trace contains 6,158 frames over 3.257991 seconds, 34 unique arbitration IDs, and payload byte entropy of 3.361537 bits. Mean inter-arrival time is 0.000529152 seconds, with no negative inter-arrival values after parsing. Because the upstream sample does not include attack labels in this package, it is not used for IDS performance claims. Its role is external-source ingestion, normalization, hashing, and replay-readiness evidence.

## Evidence Preservation

Each experiment stores the input attack plan, raw annotated CAN log, normalized CSV, findings, execution output, and a manifest with SHA-256 hashes. This supports reproducibility and forensic chain-of-custody discussion, even though the environment is software-defined.



## Rule-Based Forensic Triage Baseline

To provide an explainable reference model, we implemented a rule-based forensic triage baseline over 1-second traffic windows. The model uses only interpretable features extracted from the CAN logs: unique arbitration ID count, unknown-ID ratio, and decoded speed on arbitration ID `0x100`.

The rules are intentionally simple. A window is classified as `flooding` when it exhibits high arbitration ID cardinality or a high ratio of IDs outside the expected simulated baseline set. A window is classified as `spoofing` when decoded speed on ID `0x100` exceeds 130 km/h. Otherwise, the window is classified as `normal`, covering both baseline and recovery periods.

Across the combined dataset, 6,615 one-second windows were evaluated. The rule-based triage baseline achieved 0.9998 accuracy and 0.9998 macro-F1. The confusion matrix contained 3,968/3,969 normal windows correctly classified, 1,323/1,323 spoofing windows correctly classified, and 1,323/1,323 flooding windows correctly classified. One normal window was flagged as flooding.

This result should not be interpreted as evidence that the detection problem is solved in real vehicles. Instead, it shows that the dataset labels, simulator behavior, and evidence workflow are internally consistent and suitable for teaching, reproducible demonstrations, and forensic triage exercises.

## Limitations

The experiments validate the software workflow, labeling, logging, replayability, and evidence-preservation process. They do not model physical CAN arbitration, transceiver behavior, electrical noise, bus termination, or real ECU reactions. Hardware-in-the-loop validation is therefore treated as future work.

## Figures and Tables

The generated analysis artifacts are available in `analysis/`:

- `figures/frame_count_by_phase.svg`
- `figures/decoded_speed_id_0x100.svg`
- `figures/id_cardinality_10s.svg`
- `figures/rule_based_triage_confusion_matrix.svg`
- `tables/frame_counts_by_phase.csv`
- `tables/speed_stats_id_0x100.csv`
- `tables/second_round_matrix_summary.csv`
- `tables/external_source_008_summary.csv`
- `tables/rule_based_triage_windows.csv`
- `tables/rule_based_triage_metrics.json`
- `tables/rule_based_triage_confusion_matrix.csv`
