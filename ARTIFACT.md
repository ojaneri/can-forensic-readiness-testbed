# Artifact and Reproducibility Notes

## Environment

The generated experiments were prepared on Linux with Python 3.12 and `python-can` 4.6.1 for the software-defined internal runs.

## Core validation

Run:

```bash
python3 dataset/scripts/validate_hashes.py
```

This validates experiment package files against `dataset/manifest.json`.

## Experiment summary

| Experiment | Purpose | Main files |
|---|---|---|
| 005 | Short internal proof-of-concept | `dataset/experiments/005_short_attack/` |
| 006 | 10-minute internal run | `dataset/experiments/006_10min_attack/` |
| 007 | 10-run intensity matrix | `dataset/experiments/007_second_round_matrix/` |
| 008 | External ICSim trace ingestion | `dataset/experiments/008_external_icsim_replay/` |
| 009 | ICSim trace + didactic spoof injection | `dataset/experiments/009_icsim_spoof_injection/` |

## Demos

Open locally in a browser:

- `demo-attack/index.html`
- `demo-external-icsim/index.html`
- `demo-icsim-spoof/index.html`

The demos replay stored artifacts. They do not transmit CAN frames or perform live attacks.

## Important interpretation boundary

The rule-based triage results are label-consistency and forensic-screening sanity checks. They are not a real-world IDS benchmark.
