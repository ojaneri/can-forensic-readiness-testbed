# Next Steps — SSV 2026 Software-Defined CAN Testbed Paper

## Language Policy

All scientific artifacts must be written in English:

- paper manuscript;
- title, abstract, keywords;
- dataset fields and labels;
- experiment names;
- figure captions;
- tables;
- model names;
- code comments when relevant;
- README files intended for publication;
- GitHub repository documentation.

Portuguese may be used only for internal notes to Osvaldo, not for the final scientific package.

## Current Status

We already have:

1. A literature review folder for the SSV 2026 paper.
2. A software-defined CAN testbed skeleton.
3. A short attack experiment (`005_real_attack_software`) with input, output, findings and hashes.
4. A visual web demo for observers.
5. A longer 10-minute experiment (`006_10min_attack_software`) currently running/being prepared for statistical analysis.

## Recommended Scientific Direction

Paper title candidate:

**A Software-Defined Low-Cost CAN Testbed for Automotive Cybersecurity Education and Forensic Analysis**

Subtitle/positioning:

**From Virtual Attack Simulation to Evidence-Preserving CAN Traffic Analysis**

Core claim:

A fully software-defined CAN testbed can support reproducible automotive cybersecurity education and preliminary forensic analysis by combining virtual CAN simulation, controlled attack scenarios, structured logging, and evidence-preserving metadata.

## Priority 1 — Produce a Clean Public Dataset

Create a dataset package from experiments 005 and 006:

```text
dataset/
  README.md
  data_dictionary.md
  experiments/
    005_short_attack/
      input_attack_plan.json
      output_frames.csv
      output_candump_annotated.log
      findings.json
      manifest.json
    006_10min_attack/
      input_attack_plan.json
      output_frames.csv
      output_candump_annotated.log
      findings.json
      manifest.json
  scripts/
    validate_hashes.py
    summarize_dataset.py
  LICENSE
  CITATION.cff
```

Dataset fields must be standardized in English:

- `timestamp`
- `relative_time_s`
- `phase`
- `arbitration_id`
- `dlc`
- `payload_hex`
- `attack_label`
- `semantic_label`
- `source_component`
- `notes`

Recommended labels:

- `normal`
- `spoofing`
- `flooding`
- `recovery`

## Priority 2 — Add Dataset Analysis Scripts

Create analysis scripts that generate tables and figures for the paper:

1. Frame count per phase.
2. Top arbitration IDs per phase.
3. Time series of decoded speed from ID `0x100`.
4. Arbitration ID cardinality over time.
5. Payload entropy per phase.
6. Inter-arrival time distribution.
7. Simple rule-based detector baseline.
8. Confusion matrix for attack phase detection.

Potential figures:

- Figure 1: Testbed architecture.
- Figure 2: Attack timeline.
- Figure 3: Speed signal before/during/after spoofing.
- Figure 4: Arbitration ID diversity during flooding.
- Figure 5: Forensic evidence workflow.

## Priority 3 — Define a Minimal Detection Model

Do not overcomplicate with deep learning yet. For SSV, a clear baseline is better.

Recommended model:

**Rule-Based Forensic Triage Model**

Features:

- `arbitration_id_frequency`
- `payload_value_range`
- `decoded_speed_range`
- `inter_arrival_time_ms`
- `id_cardinality_window`
- `phase_transition_marker`

Rules:

- Spoofing if decoded speed on ID `0x100` exceeds expected range or changes abruptly.
- Flooding if unique arbitration IDs per time window exceed baseline threshold.
- Suspicious replay if repeated frame sequences recur with high similarity.

Why this is better now:

- Explainable.
- Reproducible.
- Fits forensic analysis.
- Easy to justify in 6 pages.
- Avoids the “yet another ML IDS” problem.

Optional later model:

- Isolation Forest.
- One-Class SVM.
- Random Forest using statistical windows.
- LSTM only if there is enough time and data.

## Priority 4 — Turn the Demo into a Research Artifact

The observer demo should be preserved as:

```text
demo/
  index.html
  assets/
    sample_frames.json
    findings.json
    manifest.json
```

Add a statement:

> The demo is client-side only and does not perform live attacks. It replays experiment artifacts for reproducibility, teaching, and review.

For the paper, cite it as:

**Interactive Demonstration Artifact**

## Priority 5 — Prepare GitHub Repository

Recommended repository name:

`software-defined-can-forensics-testbed`

Suggested structure:

```text
software-defined-can-forensics-testbed/
  README.md
  paper/
  dataset/
  demo/
  scripts/
  src/
  experiments/
  docs/
  LICENSE
  CITATION.cff
```

README sections:

- Overview
- Research Motivation
- Testbed Architecture
- Quick Start
- Running Experiments
- Dataset Description
- Forensic Manifest and Hash Validation
- Limitations
- Citation

## Priority 6 — Paper Outline

### Title

A Software-Defined Low-Cost CAN Testbed for Automotive Cybersecurity Education and Forensic Analysis

### Abstract

Focus on problem, method, experiments, dataset, forensic evidence handling, and limitations.

### 1. Introduction

- Automotive CAN remains relevant and insecure.
- Access to real vehicles/ECUs is costly and risky.
- Education and forensic readiness need reproducible environments.
- Contributions.

### 2. Background and Related Work

- CAN security.
- Automotive testbeds.
- CAN IDS datasets.
- Automotive forensics.

### 3. Testbed Design

- Virtual CAN architecture.
- Simulated ECUs.
- Attack modules.
- Logger and forensic manifest.
- Observer demo.

### 4. Experimental Methodology

- Baseline.
- Spoofing.
- Flooding.
- Recovery.
- Data collection.
- Hashing and evidence preservation.

### 5. Results

- Frame counts.
- Speed spoofing effect.
- Flooding ID diversity.
- Evidence artifacts.
- Detection/triage baseline.

### 6. Discussion

- Educational value.
- Forensic value.
- Reproducibility.
- Limitations of software-only simulation.
- Hardware-in-the-loop extension.

### 7. Conclusion

- Summary and future work.

## Priority 7 — Hardware Extension as Future Work

Do not depend on hardware for the first submission. Present hardware as future/extension:

- USB-CAN adapter.
- Instrument cluster with CAN.
- Arduino + MCP2515 simulated ECUs.
- Legacy ECU/BCM.

This keeps the paper feasible and still credible.

## Immediate Action List

1. Wait for the 10-minute experiment to finish.
2. Generate analysis plots from experiment 006.
3. Create English dataset package.
4. Rename/normalize CSV columns in English.
5. Implement `summarize_dataset.py` and `validate_hashes.py`.
6. Draft paper abstract in English.
7. Build first architecture diagram.
8. Convert current internal notes into an English manuscript outline.
9. Decide GitHub repository name and license.
10. Prepare a reproducibility checklist.
