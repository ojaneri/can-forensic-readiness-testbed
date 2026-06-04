# Article IEEE v5 — Reproducibility polish notes

Files:

- PDF: `paper/article_ieee_v5.pdf`
- LaTeX: `paper/article_ieee_v5.tex`
- BibTeX: `paper/article_ieee_v5.bib`
- Latest aliases: `article_ieee_latest.pdf/.tex/.bib`

## Main changes from v4

1. Title changed to: `A Reproducible Software-Defined CAN Testbed for Automotive Cybersecurity and Forensic-Readiness Analysis`.
2. Abstract tightened and reframed around reproducibility.
3. Added Experiment 010: software-only wall-clock timing capture.
4. Added improved pipeline figure: `analysis/figures/reproducible_evidence_pipeline_v5.*`.
5. Added Artifact Reproducibility Comparison table.
6. Added explicit Ethical Scope and Safety Boundary subsection.
7. Updated evaluation matrix to include Exp. 010.
8. Added CI-ready criterion to the artifact checklist.
9. Added GitHub Actions workflow: `.github/workflows/artifact-ci.yml`.
10. Generated demo GIF: `demo-icsim-spoof/demo-icsim-spoof-preview.gif`.
11. Cleaned key BibTeX entries:
    - VitroBench authors/DOI corrected;
    - CAN bus security testbed 2022 authors corrected;
    - can-train-and-test authors/volume/page corrected.

## Experiment 010

- Total frames: 1,167
- Duration: 20.000022 s
- Unique IDs: 4
- Mean inter-arrival: 0.017153 s
- Median inter-arrival: 0.009923 s
- Negative inter-arrival values: 0

Boundary: software-only wall-clock timing capture. It is not physical CAN or vehicle validation.

## Build result

- `latexmk -pdf article_ieee_v5.tex`: OK
- PDF pages: 5
- Relevant LaTeX warnings: none
- Undefined citations: none
- DOI in final PDF: `10.5281/zenodo.20541106`

## Remaining caveats

- `can-sleuth` remains cited conservatively as project/artifact documentation.
- A real SocketCAN kernel-interface or HIL experiment would still strengthen external validity but is no longer necessary for the current reproducibility claim.


## Visual polish update

- Installed/used matplotlib, pandas, numpy, pillow, cairosvg and python-can locally.
- Rebuilt v5 figures with professional matplotlib styling.
- Inserted two additional figures into the PDF:
  - `evidence_coverage_dashboard_v5.pdf`
  - `exp010_wallclock_timing_v5.pdf`
- PDF increased from 5 to 6 pages due to richer visual presentation.
- Added `requirements-viz.txt` and `analysis/scripts/generate_v5_visuals.py`.
