# TODO — SSV 2026 Paper

## Phase 1 — Scope

- [ ] Confirm final title.
- [ ] Use English for all paper, dataset, code-facing documentation, figures, and tables.
- [ ] Decide whether the first submission remains software-only or includes a hardware-in-the-loop appendix/future work.
- [ ] Define public artifact license.
- [ ] Decide whether to publish the dataset on GitHub, Zenodo, or both.

## Phase 2 — Literature

- [ ] Download and validate PDFs for core references.
- [ ] Complete BibTeX metadata with authors, venues, pages, and DOI.
- [ ] Read VitroBench in full.
- [ ] Read the CAN Bus Security Testbed Framework paper in full.
- [ ] Read the ROAD dataset paper for taxonomy and dataset quality criteria.
- [ ] Read CANBench and identify hardware/software reproducibility metrics.
- [ ] Read READ for CAN frame reverse engineering and forensic limitations.
- [ ] Search SBC/SOL for SSV 2024/2025 full papers and style expectations.

## Phase 3 — Dataset

- [ ] Create `dataset/` package in English.
- [ ] Normalize CSV columns in English.
- [ ] Add `data_dictionary.md`.
- [ ] Add `README.md` describing experiments 005 and 006.
- [ ] Add `validate_hashes.py`.
- [ ] Add `summarize_dataset.py`.
- [ ] Add license and citation file.

## Phase 4 — Analysis

- [ ] Generate frame count table by phase.
- [ ] Generate top arbitration IDs by phase.
- [ ] Plot decoded speed over time.
- [ ] Plot arbitration ID diversity over time.
- [ ] Compute payload entropy by phase.
- [ ] Compute inter-arrival time distribution.
- [ ] Implement rule-based forensic triage baseline.
- [ ] Create confusion matrix for phase detection.

## Phase 5 — Writing

- [ ] Abstract.
- [ ] Introduction.
- [ ] Related Work.
- [ ] Testbed Architecture.
- [ ] Experimental Methodology.
- [ ] Results.
- [ ] Discussion.
- [ ] Conclusion.
- [ ] IEEE formatting.
- [ ] 6-page limit check.

## Phase 6 — Risks

- [ ] If reviewers consider software-only weak, emphasize reproducibility, safety, evidence handling, and HIL extension.
- [ ] If dataset is considered synthetic, position it as an educational/forensic readiness artifact, not a real-world IDS benchmark.
- [ ] If page limit is tight, remove hardware shopping details and keep only future work.
