# Artifact and Reproducibility Notes

## Environment

The generated experiments were prepared on Linux with Python 3.12 and `python-can` 4.6.1 for the software-defined internal runs.

## Core validation

Run:

```bash
python3 dataset/scripts/validate_hashes.py
```

This validates the experiment package files, the combined normalized dataset and the derived files listed in `dataset/manifest.json` (171 files). A one-byte change to any of them makes the command exit with status 1. For Experiments 014--017 only the
metadata, summary and manifest files are in the repository (see `dataset/experiments/HCRL_NOTICE.md`), so only those
are validated here.

## Experiment summary

| Experiment | Purpose | Main files |
|---|---|---|
| 005 | Short internal proof-of-concept | `dataset/experiments/005_short_attack/` |
| 006 | 10-minute internal run | `dataset/experiments/006_10min_attack/` |
| 007 | 10-run intensity matrix | `dataset/experiments/007_second_round_matrix/` |
| 008 | External ICSim trace ingestion | `dataset/experiments/008_external_icsim_replay/` |
| 009 | ICSim trace + didactic spoof injection | `dataset/experiments/009_icsim_spoof_injection/` |
| 010--012 | Wall-clock capture, python-can virtual bus, python-can ICSim replay; ten runs of each | `dataset/experiments/010_*`, `011_*`, `012_*`; `bench/campaign/` |
| 014--017 | HCRL Car-Hacking Dataset imports (real vehicle); frames not redistributed | metadata, summaries and manifests in `dataset/experiments/014_*` to `017_*`; `dataset/experiments/HCRL_NOTICE.md` |
| 018--019 | Linux SocketCAN `vcan` captures | `dataset/experiments/018_vcan_socketcan_capture/`, `019_vcan_varied_traffic/` |
| 020--022 | Physical two-node CAN bench | `physical-bench/` |

## Demos

The demos fetch JSON files, which browsers block from `file://`. Serve the repository root over HTTP, for example
`python3 -m http.server 8000`, and open (replace the path below by the demo you want):

- `demo-attack/index.html`
- `demo-external-icsim/index.html`
- `demo-icsim-spoof/index.html`

The demos replay stored artifacts. They do not transmit CAN frames or perform live attacks.

## Important interpretation boundary

The rule-based triage results are label-consistency and forensic-screening sanity checks. They are not a real-world IDS benchmark.
