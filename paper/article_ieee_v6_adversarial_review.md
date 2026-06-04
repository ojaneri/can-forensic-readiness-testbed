# Adversarial Review — Article IEEE v6

## Verdict

v6 is the strongest version so far. It adds actual `python-can` virtual-bus experiments after installing the relevant tooling and provides an Overleaf-ready package. The contribution remains safely framed as reproducibility and forensic-readiness, not IDS benchmarking or physical CAN fidelity.

## Strengths

- `python-can` is now part of the evidence, not just future work.
- Experiment 012 replays the external ICSim trace through the same virtual-bus workflow.
- The figures are visibly more professional and paper-ready.
- Overleaf package reduces collaboration friction.
- CI and hash validation remain in place.
- DOI concept remains stable.

## Remaining risks

- No physical SocketCAN kernel interface or hardware CAN adapter yet.
- No HIL/real ECU validation.
- v6 is now 6 pages; check target venue page limit.
- If submitting blind, GitHub/Zenodo links may need anonymization.

## Recommendation

Use v6 for coauthor review and Overleaf collaboration. If the venue allows 6 pages, keep the figures. If limited to 5 pages, remove either the dashboard figure or compress the related-work/evaluation tables.
