# Reproducibility Table — Experiment 006

| Item | Value |
|---|---|
| Backend | `python-can` virtual backend |
| Python | `3.12.3` |
| python-can | `4.6.1` |
| Channel | `ssv2026-attack-10min-virtual-can` |
| Duration | `600 s` planned / `600.06 s` observed |
| Phases | 180 s baseline, 120 s spoofing, 120 s flooding, 180 s recovery |
| Random seed | `2026060310` |
| Normal period | `0.05 s` |
| Spoof period | `0.04 s` |
| Flood period | `0.01 s` |
| Main script | `software-testbed/experiments/006_10min_attack_software/run_experiment_10min.py` |
| Evidence | input plan, raw log, normalized CSV, findings, manifest |
| Hash validation | `dataset/scripts/validate_hashes.py` |
