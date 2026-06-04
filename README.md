# CAN Forensic-Readiness Testbed

A software-defined, low-cost CAN testbed for automotive cybersecurity education and forensic-readiness analysis.

This repository accompanies the paper draft:

**A Software-Defined Low-Cost CAN Testbed for Automotive Cybersecurity Education and Forensic-Readiness Analysis**

## Scope and safety boundary

This artifact is for authorized education, reproducibility, and forensic-readiness workflow validation.

It is **not**:

- a real-vehicle attack toolkit;
- an operational IDS benchmark;
- a claim of physical CAN fidelity;
- a production automotive security assessment tool.

All experiments are software-defined and observer-safe.

## What is included

- Internal labeled CAN experiments: baseline, spoofing, flooding, recovery.
- Experiment 007: 10-run low/medium/high spoofing/flooding matrix.
- Experiment 008: external ICSim `sample-can.log` ingestion and normalization.
- Experiment 009: didactic spoof injection into external ICSim trace.
- SHA-256 manifests and validation scripts.
- Normalized CSV datasets and data dictionary.
- Browser demos for replay and visualization.
- IEEE-style paper drafts and analysis tables/figures.

## Quick links

- Paper v3: [`paper/article_ieee_v3.html`](paper/article_ieee_v3.html)
- Latest paper alias: [`paper/article_ieee_latest.html`](paper/article_ieee_latest.html)
- Dataset package: [`dataset/`](dataset/)
- Experiment 007: [`dataset/experiments/007_second_round_matrix/`](dataset/experiments/007_second_round_matrix/)
- Experiment 008: [`dataset/experiments/008_external_icsim_replay/`](dataset/experiments/008_external_icsim_replay/)
- Experiment 009: [`dataset/experiments/009_icsim_spoof_injection/`](dataset/experiments/009_icsim_spoof_injection/)
- ICSim spoof demo: [`demo-icsim-spoof/index.html`](demo-icsim-spoof/index.html)

## Validate artifact hashes

```bash
python3 dataset/scripts/validate_hashes.py
```

Expected result: every listed experiment file should print `OK`.

## Reproduce / inspect

See [`ARTIFACT.md`](ARTIFACT.md) for reproduction notes and artifact layout.

## Licensing notes

Repository code is MIT licensed unless otherwise noted.

Experiment 008 imports the public ICSim `data/sample-can.log` trace from `https://github.com/zombieCraig/ICSim.git`, commit `2b3333ef866987d8adc9c15ff15b9b9189edf85b`. ICSim is distributed upstream under GPL-3.0; its license is preserved in `dataset/experiments/008_external_icsim_replay/ICSim_LICENSE`.
