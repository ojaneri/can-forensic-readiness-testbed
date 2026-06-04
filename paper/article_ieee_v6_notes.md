# Article IEEE v6 — python-can and Overleaf package

Files:

- PDF: `paper/article_ieee_v6.pdf`
- LaTeX: `paper/article_ieee_v6.tex`
- BibTeX: `paper/article_ieee_v6.bib`
- Overleaf ZIP: `paper/overleaf_article_ieee_v6.zip`
- Overleaf folder: `paper/overleaf_article_ieee_v6/`

## Main changes from v5

1. Added Experiment 011: `python-can` virtual-bus generated wall-clock capture.
2. Added Experiment 012: external ICSim replay through `python-can` virtual bus.
3. Added v6 figures:
   - `reproducible_evidence_pipeline_v6.*`
   - `evidence_coverage_dashboard_v6.*`
   - `python_can_virtual_bus_timing_v6.*`
4. Updated abstract, experiment table, methods, results, evaluation matrix and figures.
5. Added Overleaf-ready package with local IEEEtran files and figure paths adjusted.
6. Updated latest aliases to v6.

## Experiment 011

- Tool: `python-can 4.6.1`
- Channel: `oc_vcan_011`
- Duration: 29.998787 s
- Frames: 1,750
- Unique IDs: 4
- Mean inter-arrival: 0.017152 s
- Negative inter-arrival values: 0
- Mean send-to-receive latency: 0.000104 s

## Experiment 012

- Base: Experiment 008 external ICSim normalized trace
- Tool: `python-can 4.6.1`
- Input frames: 6,158
- Replayed frames: 6,158
- Unique IDs: 34
- Duration: 3.256474 s
- Mean inter-arrival: 0.000529 s
- Negative inter-arrival values: 0
- Mean send-to-receive latency: 0.000042 s

## Build results

- `latexmk -pdf article_ieee_v6.tex`: OK
- PDF pages: 6
- Undefined citations: none
- Relevant LaTeX warnings: none
- DOI in PDF: `10.5281/zenodo.20541106`
- Overleaf package local build: OK, 6 pages

## Boundary

Experiments 011/012 validate `python-can` virtual-bus replay and timing preservation. They are not physical CAN arbitration, electrical behavior, ECU, adapter, or vehicle validation.
