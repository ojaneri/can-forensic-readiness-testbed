# CAN Forensic-Readiness Testbed: dataset

Normalized CAN frame packages and the combined dataset behind the testbed paper
"Reproducible and Forensic-Ready Software-Defined CAN Testbed for Automotive Cybersecurity" (SBESC 2026, under review).
The schema is documented in `schema.md`/`data_dictionary.md` when present and in the header of every `frames_normalized.csv`.

## Scope

Experiments 005-012 and 018-019 use no CAN hardware of ours. Experiments 014-017 are imports of the public HCRL
Car-Hacking Dataset (real vehicle traffic recorded by others). The physical two-node bench of Experiments 020-022 is in
`../physical-bench/`. No vehicle, production ECU or operational system was targeted.

## Experiment packages (`experiments/`)

| Experiments | Content |
|---|---|
| 005, 006 | internal runs with baseline, spoofing, flooding and recovery phases (synthetic, python-can) |
| 007 | ten-run intensity matrix (low, medium, high spoofing and flooding) |
| 008, 009 | external ICSim trace and the same trace with didactic injected packets |
| 010, 011, 012 | wall-clock capture, python-can virtual bus, python-can ICSim replay (ten-run campaign in `../bench/campaign/`) |
| 014-017 | HCRL imports: only `external_source_metadata.json`, `summary.json` and `manifest.json` are deposited; see `experiments/HCRL_NOTICE.md` |
| 018, 019 | Linux SocketCAN `vcan` loopback captures |

## Main files

- `all_frames_normalized.csv`: combined normalized frames of the internal experiments (477,738 frames).
- `dataset_summary.json`: summary statistics of the combined file (regenerate with `python3 dataset/scripts/summarize_dataset.py`).
- `manifest.json`: SHA-256 hashes of the package files, the combined file and the derived files.
- `experiments/*/frames_normalized.csv`, `experiments/*/summary.json`: per-experiment files.

## Validate

```bash
python3 dataset/scripts/validate_hashes.py     # 171 files; exit status 1 if any file differs
```

## Labels

- `baseline`: normal simulated traffic.
- `spoofing`: fabricated vehicle-state or display traffic.
- `flooding`: high-cardinality randomized traffic.
- `recovery`: return to normal traffic.
Labels come from the generator that produced the traffic, so triage metrics on this data show label consistency, not detection performance.

## Limitations

The data validate the software workflow, logging, labeling and file-level preservation. They do not model physical CAN
arbitration, electrical errors, termination or real ECU behavior (see `../physical-bench/README.md` for the bench).
Generator runs follow the host clock, so regenerated files are not bit-identical to the archived ones.
