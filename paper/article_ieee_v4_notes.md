# Article IEEE v4 — Submission-grade notes

Files:

- LaTeX: `paper/article_ieee_v4.tex`
- BibTeX: `paper/article_ieee_v4.bib`
- PDF: `paper/article_ieee_v4.pdf`
- Latest PDF alias: `paper/article_ieee_latest.pdf`

## What changed from v3

1. Ported the manuscript to local IEEEtran LaTeX.
2. Added explicit Research Questions:
   - RQ1 evidence preservation;
   - RQ2 controlled spoof/flood variation;
   - RQ3 external trace ingestion;
   - RQ4 observer-safe review.
3. Strengthened Related Work against:
   - classic automotive security studies;
   - CAN security surveys;
   - ICSim;
   - Caring Caribou;
   - VitroBench / CAN bus testbed work;
   - ROAD, can-train-and-test, can-sleuth.
4. Added Research Question Evaluation Matrix.
5. Added Artifact Evaluation Checklist.
6. Added Zenodo concept DOI as primary artifact DOI:
   - Concept DOI: `10.5281/zenodo.20541106`
   - First version DOI: `10.5281/zenodo.20541107`
7. Preserved safe claims:
   - not real-vehicle exploitation;
   - not physical CAN fidelity;
   - not an IDS benchmark;
   - triage is only a sanity check.

## Build result

- `latexmk -pdf article_ieee_v4.tex`: OK
- Pages: 5
- Page size: US Letter / IEEE conference default
- Citation undefined warnings: none
- Relevant overfull warnings: none after cleanup

## Remaining editorial caveats

- Some references still use conservative metadata (`and others`) where web metadata could not be fully verified without risking invented precision.
- For camera-ready submission, verify conference page limit, author block, blind-review rules, and whether IEEE wants DOI URL or plain DOI in artifact section.

## Zenodo release notes

- v0.2.0 Paper v4 DOI detected: `10.5281/zenodo.20541255`.
- Manuscript cites the Zenodo concept DOI `10.5281/zenodo.20541106` to avoid stale version-specific DOI after later releases.

- BibTeX artifact citation now uses concept DOI `10.5281/zenodo.20541106` for consistency.
