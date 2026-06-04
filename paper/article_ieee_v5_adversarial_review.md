# Adversarial Review — Article IEEE v5

## Verdict

v5 is stronger than v4 for submission because it shifts the central claim from “low-cost” to “reproducible”, adds wall-clock timing evidence, improves artifact-review posture, and keeps claims conservative.

## Improvements confirmed

- Title is more academic: “Reproducible Software-Defined CAN Testbed”.
- Abstract is shorter and less overloaded.
- Exp. 010 reduces the criticism that all experiments are deterministic fast-run traces.
- Pipeline figure improves presentation quality.
- GitHub Actions increases artifact confidence.
- DOI concept is used consistently.
- BibTeX has fewer incomplete entries.
- Safety/ethical boundary is explicit.

## Remaining risks

1. Physical fidelity criticism remains possible.
   - Mitigation: explicitly disclosed; future work includes SocketCAN/HIL.
2. Exp. 010 is software-only, not kernel SocketCAN.
   - Mitigation: framed as wall-clock logging evidence only.
3. Some related-work artifacts are broad and may require final human bibliographic check.
   - Mitigation: no invented precision; conservative citations.
4. The paper is 5 pages and compact.
   - Benefit: fits workshops; risk: less room for detailed methodology.

## Recommendation

Use v5 as the current submission candidate. Before formal submission, verify blind-review policy and whether GitHub/Zenodo links should be anonymized.
