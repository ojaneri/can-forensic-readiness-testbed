# Article IEEE v2 — Corrections Applied

This version addresses the adversarial review by:

1. Retitling the paper to **Forensic-Readiness Analysis** instead of broad forensic analysis.
2. Reframing the detector as a **triage sanity check**, not an IDS benchmark.
3. Adding a related-artifact comparison table.
4. Adding a reproducibility table with Python, python-can, seed, channel, phases, rates and validation command.
5. Adding a forensic-readiness mapping table.
6. Explicitly stating that the dataset is synthetic and does not model physical CAN behavior.
7. Removing contaminated inter-arrival statistics from the article narrative and saving a corrected summary in `analysis/tables/dataset_summary_corrected.json`.
8. Adding an artifact availability statement.
9. Noting that HTML is for preview and final submission should be ported to official IEEEtran/IEEE template.

Remaining work before submission:

- Complete references with full authors, venues, pages and DOI.
- Add one independent scenario: ICSim, public CAN trace replay, or real SocketCAN/vcan capture.
- Generate official IEEEtran LaTeX/PDF and check 6-page limit.
