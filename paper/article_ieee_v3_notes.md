# Article IEEE v3 — Notes

File: `paper/article_ieee_v3.html`  
Alias updated target: `paper/article_ieee_latest.html`

## Main v3 changes

- Reorganized manuscript around forensic-readiness workflow instead of detector performance.
- Added experiments 007, 008, and 009 into the paper narrative.
- Updated abstract with:
  - 477,738 internal labeled frames;
  - 10-run Matrix 007;
  - 6,158-frame external ICSim ingestion;
  - 45 spoofed packets in Experiment 009;
  - explicit IDS/physical-fidelity boundary.
- Added evidence package coverage table for Experiments 005–009.
- Added Experiment 008 external ICSim compatibility discussion.
- Added Experiment 009 ICSim spoof injection discussion.
- Added formal `Threats to Validity` section.
- Moved triage metrics to secondary/sanity-check framing.
- Added safer `Artifact Availability` language.

## Safe framing preserved

The v3 article explicitly avoids claiming:

- real-vehicle attack realism;
- physical CAN fidelity;
- IDS benchmark performance;
- generalizable detection robustness.

It claims:

- low-cost software-defined CAN testbed;
- educational reproducibility;
- forensic-readiness evidence packaging;
- external-source compatibility;
- observer-safe replay and didactic spoof injection.

## Still open before final submission

- Curate references into full IEEE/BibTeX quality.
- Port the stabilized v3 text to official IEEEtran LaTeX.
- Generate print-safe final figures if page limit requires.
- Replace internal artifact URLs with public GitHub/Zenodo DOI.

## Public repository

- GitHub: https://github.com/ojaneri/can-forensic-readiness-testbed
- GitHub release: https://github.com/ojaneri/can-forensic-readiness-testbed/releases/tag/v0.1.1-zenodo
- Zenodo version DOI: 10.5281/zenodo.20541107 — https://doi.org/10.5281/zenodo.20541107
- Zenodo concept DOI: 10.5281/zenodo.20541106 — https://doi.org/10.5281/zenodo.20541106
