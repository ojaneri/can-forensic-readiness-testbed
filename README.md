# CAN Forensic-Readiness Testbed

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.20541106.svg)](https://doi.org/10.5281/zenodo.20541106)
[![Artifact CI](https://github.com/ojaneri/can-forensic-readiness-testbed/actions/workflows/artifact-ci.yml/badge.svg)](https://github.com/ojaneri/can-forensic-readiness-testbed/actions/workflows/artifact-ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

A reproducible software-defined CAN testbed for automotive cybersecurity and forensic-readiness analysis.

Earlier paper candidate (v6). The SBESC 2026 SSV manuscript that cites this artifact is under review and is not part of this repository:

**A Reproducible Software-Defined CAN Testbed for Automotive Cybersecurity and Forensic-Readiness Analysis**

## Main links

- Paper v6 PDF: `paper/article_ieee_v6.pdf`
- Paper v6 LaTeX: `paper/article_ieee_v6.tex`
- Zenodo concept DOI: https://doi.org/10.5281/zenodo.20541106
- GitHub repository: https://github.com/ojaneri/can-forensic-readiness-testbed
- Demo GIF: `demo-icsim-spoof/demo-icsim-spoof-preview.gif`
- Overleaf package: `paper/overleaf_article_ieee_v6.zip`

## Scope and safety boundary

This repository is for authorized cybersecurity education, reproducible experimentation, and forensic-readiness workflow validation.

It is not:

- a real-vehicle attack toolkit;
- an operational IDS benchmark;
- a claim of physical CAN fidelity;
- a production automotive security assessment tool.

All demos replay stored artifacts and do not transmit live CAN frames.

## Included evidence packages

- Experiments 005/006: internal labeled CAN experiments.
- Experiment 007: 10-run low/medium/high spoofing/flooding matrix.
- Experiment 008: external ICSim `sample-can.log` ingestion and normalization.
- Experiment 009: didactic spoof injection into external ICSim trace.
- Experiment 010: software-only wall-clock timing capture.
- Experiments 011--012: python-can virtual bus and ICSim replay; ten-run timing campaign of Experiments 010--012 in `bench/campaign/`.
- Experiments 014--017: HCRL Car-Hacking Dataset imports (metadata, summaries and SHA-256 manifests only; see `dataset/experiments/HCRL_NOTICE.md`).
- Experiments 018--019: Linux SocketCAN `vcan` captures.
- Experiments 020--022: physical two-node CAN bench captures, firmware and evaluation scripts (`physical-bench/`).
- Random Forest baseline and its ablation: `analysis/scripts/rf_baseline.py`, `analysis/scripts/ablation_loeo.py`, `analysis/tables/rf_*`.
- SHA-256 manifests and validation scripts.
- Normalized CSV datasets and data dictionary.
- Browser demos for safe replay and visualization.

## Validate artifact hashes

```bash
python3 dataset/scripts/validate_hashes.py
```

## Build paper

```bash
cd paper
latexmk -pdf -interaction=nonstopmode -halt-on-error article_ieee_v6.tex
```

## Regenerate visual assets

```bash
python3 -m pip install -r requirements-viz.txt
python3 analysis/scripts/generate_v5_visuals.py
```

Generated visual assets include:

- `analysis/figures/reproducible_evidence_pipeline_v5.*`
- `analysis/figures/evidence_coverage_dashboard_v5.*`
- `analysis/figures/exp010_wallclock_timing_v5.*`
- `demo-icsim-spoof/demo-icsim-spoof-preview.png`
- `demo-icsim-spoof/demo-icsim-spoof-preview.gif`
