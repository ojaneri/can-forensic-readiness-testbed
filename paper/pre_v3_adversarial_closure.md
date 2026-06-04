# Pre-v3 Adversarial Closure — Software-Defined CAN Testbed Paper

Target next manuscript: `article_ieee_v3`  
Current latest draft: `paper/article_ieee_v2.html`  
Purpose: close the main adversarial-review weaknesses before rewriting the article.

## Executive decision

The paper is now substantially stronger than the v2 draft, but the next version should **not** simply append every new artifact. Version 3 should reorganize the story around this claim:

> A low-cost software-defined CAN testbed can support reproducible cybersecurity education and forensic-readiness workflows by generating labeled internal experiments, preserving evidence packages, ingesting external traces, and safely replaying/injecting didactic events for review.

The safest framing remains:

- **Not** an IDS benchmark paper.
- **Not** a real-vehicle attack paper.
- **Not** a physical CAN fidelity paper.
- **Yes**: reproducible testbed, evidence workflow, external-trace compatibility, didactic spoof injection, safe observer demos.

---

## Closure matrix

| # | Original adversarial concern | Action taken | Evidence / artifact | Status | Residual risk |
|---:|---|---|---|---|---|
| 1 | Detector looked trivial/circular. | Reframed as **rule-based forensic triage sanity check**, not IDS benchmark. Metrics kept as label/workflow consistency evidence. | `analysis/scripts/rule_based_triage.py`; `analysis/tables/rule_based_triage_metrics.json`; v2 wording already softened. | Mostly closed | Still avoid putting accuracy/F1 in abstract or contribution list. |
| 2 | Dataset looked synthetic-only / toy simulator. | Added external-source compatibility experiment using public ICSim `sample-can.log`. | `dataset/experiments/008_external_icsim_replay/`; `analysis/tables/external_source_008_summary.csv`; `demo-external-icsim/`. | Closed for compatibility claim | Still not real-vehicle validation; state this explicitly. |
| 3 | Need stronger evidence than a single long run. | Added Matrix 007 with 10 runs and low/medium/high spoofing/flooding intensities. | `dataset/experiments/007_second_round_matrix/`; `analysis/tables/second_round_matrix_summary.csv`. | Closed for parameter sensitivity | Matrix 007 is deterministic fast-run schedule, not wall-clock bus execution; disclose. |
| 4 | Contribution looked like tool integration. | Built artifact package around evidence preservation: raw logs, normalized CSV, data dictionary, manifests, source metadata, demos. | `dataset/manifest.json`; `dataset/data_dictionary.md`; `dataset/scripts/validate_hashes.py`; demos. | Mostly closed | v3 must explicitly name this as the contribution. |
| 5 | Need external demonstration / safe demo. | Added external ICSim replay demo and ICSim + spoof injection visual dashboard. | `demo-external-icsim/`; `demo-icsim-spoof/`. | Closed | Clarify demos are observer-safe browser replays. |
| 6 | Need didactic attack visualization beyond speed only. | Added Experiment 009 with spoofed speed, doors, and turn signals using ICSim semantics. | `dataset/experiments/009_icsim_spoof_injection/`; `spoofed_packets.csv`; `spoof_injection_plan.json`. | Closed for educational demo | Do not imply exploit realism. |
| 7 | Methodology lacked reproducibility details. | Added experiment plans, scripts, seeds/configs, manifests, hash validation. | `input_attack_plan.json`; `spoof_injection_plan.json`; `manifest.json`; `validate_hashes.py`. | Mostly closed | v3 needs a compact reproducibility table. |
| 8 | Inter-arrival metrics had contamination risk. | Avoided old combined inter-arrival values; Experiment 008 computes inter-arrival on one continuous external trace with no negatives. | `dataset/experiments/008_external_icsim_replay/summary.json`. | Partially closed | Do not report inter-arrival for discontinuous combined internal dataset unless recomputed per experiment/window. |
| 9 | References not IEEE-grade. | Not fully fixed yet. | `bib/referencias_candidatas.bib`; current references in v2. | Open | Must curate BibTeX before final submission. |
| 10 | HTML is not official IEEE format. | LaTeX starter exists, but v3 should be ported properly. | `paper/article_ieee_v2.tex`. | Open | Generate real IEEEtran v3 after text stabilizes. |
| 11 | Figures need polish. | Demos and SVGs exist; no final publication figures yet. | `analysis/figures/`; `demo-icsim-spoof/`. | Partially open | Need print-safe figures/tables for v3. |

---

## Evidence package coverage

| Experiment | Purpose | Raw/source trace | Normalized CSV | Manifest SHA-256 | Source metadata | Labels | Demo | Main limitation |
|---|---|---:|---:|---:|---:|---:|---:|---|
| 005 | Short internal proof-of-concept | Yes | Yes | Yes | Internal plan | Yes | Yes, attack demo sample | Short run; synthetic. |
| 006 | 10-minute internal statistical run | Yes | Yes | Yes | Internal plan | Yes | Indirect through figures/tables | Synthetic; single seed. |
| 007 | Second-round intensity matrix | Generated scheduled trace | Yes | Yes | Matrix plan | Yes | No dedicated panel | Deterministic fast-run; not wall-clock physical bus. |
| 008 | External ICSim trace ingestion | Yes, upstream `sample-can.log` | Yes | Yes | Yes: repo, commit, license, source hash | No attack labels | Yes, external replay demo | Compatibility only; no IDS labels. |
| 009 | ICSim + spoofed packet injection | Base external trace + injected package | Yes | Yes | Base ICSim metadata + injection plan | Yes for injected packets | Yes, visual dashboard | Didactic injection; not real exploit. |

---

## Claim-safety checklist for v3

Use these phrases:

- “forensic-readiness workflow”
- “software-defined CAN testbed”
- “educational and reproducible artifact”
- “external-source compatibility evidence”
- “didactic spoof injection”
- “observer-safe browser replay”
- “triage sanity check”
- “hash-based artifact integrity”

Avoid or heavily qualify these phrases:

- “IDS performance”
- “robust detection”
- “realistic automotive traffic”
- “real-vehicle attack”
- “physical CAN fidelity”
- “generalizable intrusion detection benchmark”

Suggested safe sentence:

> The rule-based triage heuristic is used to verify label consistency and illustrate explainable forensic screening in the packaged artifacts; it is not intended as a real-world IDS benchmark.

Suggested safe sentence for Experiment 009:

> The spoofed packets are controlled didactic injections into an external ICSim trace to support visualization and evidence-workflow validation, not to demonstrate exploitation of a production vehicle.

---

## Recommended v3 structure

1. **Introduction**
   - Problem: CAN education and forensic-readiness are hard to teach/reproduce safely.
   - Gap: tools/datasets exist, but evidence packaging, safe replay, and low-cost reproducibility are fragmented.
   - Contribution: internal labeled runs + external ingestion + safe spoof demo + manifests.

2. **Background and Related Work**
   - CAN security.
   - Testbeds: ICSim, Caring Caribou, VitroBench, CANBench.
   - Datasets: ROAD, can-train-and-test, can-sleuth.
   - Standards: ISO/SAE 21434, UNECE R155.

3. **Testbed and Evidence Workflow**
   - Architecture.
   - Evidence package lifecycle.
   - Hash validation.
   - Safety boundary.

4. **Experiments**
   - 005/006 internal labeled generation.
   - 007 matrix.
   - 008 external ICSim ingestion.
   - 009 external ICSim + spoof injection demo.

5. **Results**
   - Dataset counts.
   - Matrix 007 parameter sensitivity.
   - External ingestion summary.
   - Triage sanity-check metrics, secondary only.

6. **Discussion**
   - Why this is not just a simulator.
   - Strength: reproducible forensic-readiness package.
   - Trade-off: lower physical realism.

7. **Threats to Validity**
   - Internal validity.
   - External validity.
   - Construct validity.
   - Conclusion validity.

8. **Limitations and Future Work**
   - Hardware-in-the-loop.
   - SocketCAN/vcan wall-clock capture.
   - ROAD/can-train-and-test import.
   - IEEE/Zenodo artifact release.

---

## Threats to validity draft

| Category | Threat | Mitigation already applied | Residual limitation |
|---|---|---|---|
| Internal validity | Labels are generated by the same framework that creates internal traces. | External ICSim ingestion in Experiment 008; injected packets separately labeled in Experiment 009. | Internal detection metrics remain label-consistency evidence only. |
| External validity | Software-only traces may not represent physical CAN behavior. | Clear safety boundary; comparison to external ICSim trace. | No real vehicle, ECU, bus arbitration, transceiver, or error-state validation yet. |
| Construct validity | “Forensic readiness” could be underspecified. | Evidence packages include raw/source logs, normalized CSV, manifests, SHA-256 validation, metadata, and safe demos. | Needs concise definition in v3. |
| Conclusion validity | High triage scores could be overinterpreted. | Reframed as sanity-check, not IDS benchmark. | Keep metrics secondary. |
| Reproducibility | Artifact paths and scripts may be hard to follow. | Project index, dataset index, manifest validation, scripts. | Before submission, publish stable GitHub/Zenodo archive. |

---

## Remaining work before v3

Priority 1 — must do before v3:

- Curate references into proper IEEE/BibTeX form.
- Create v3 comparison/evidence table using Experiments 005–009.
- Add formal “Threats to Validity” section.
- Move triage metrics out of the center of the paper.
- Add clear artifact availability note.

Priority 2 — good before submission:

- Generate print-safe figures from the final data.
- Port v3 to official IEEEtran LaTeX.
- Create a GitHub/Zenodo release plan.
- Add one more external import later: ROAD or can-train-and-test sample.

---

## Go / no-go assessment for writing v3

**Go for v3 draft:** yes.

The main adversarial weaknesses are now addressed enough to justify a new manuscript version. The two still-open weaknesses are references and official IEEE formatting. They do not block drafting v3, but they do block final submission.

Recommended next action:

> Write `article_ieee_v3` using the safer structure above, then do a final reference/IEEEtran pass.
