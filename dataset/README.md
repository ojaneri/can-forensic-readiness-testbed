# Software-Defined CAN Attack Dataset

This dataset was produced for the paper **A Software-Defined Low-Cost CAN Testbed for Automotive Cybersecurity Education and Forensic Analysis**.

## Scope

All experiments were executed in authorized software-only environments using virtual CAN backends. No vehicle, physical ECU, external network, or real CAN hardware was targeted.

## Included experiments

- `005_short_attack`: short proof-of-concept run with baseline, spoofing, flooding, and recovery.
- `006_10min_attack`: 10-minute statistical run with the same phases.

## Main files

- `all_frames_normalized.csv`: combined normalized frames from all experiments.
- `dataset_summary.json`: combined summary statistics.
- `manifest.json`: dataset-level hashes and file metadata.
- `experiments/*/frames_normalized.csv`: normalized per-experiment CSV files.
- `experiments/*/summary.json`: per-experiment summary statistics.

## Labels

- `baseline`: normal simulated traffic.
- `spoofing`: fabricated vehicle-state/display traffic.
- `flooding`: controlled high-cardinality randomized traffic.
- `recovery`: return to normal simulated traffic.

## Limitations

The dataset validates software workflow, logging, labeling, and forensic preservation. It does not model physical CAN arbitration, electrical errors, bus termination, transceiver behavior, or real ECU reactions.
