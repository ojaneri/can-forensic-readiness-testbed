# Adversarial Review — Article IEEE v4

## Verdict

**Much stronger than v3 and close to submission-grade.** The article now reads like an artifact/reproducibility paper rather than a loose testbed report. The safest contribution remains: a low-cost, software-defined CAN workflow for education and forensic-readiness evidence packaging.

## Strong points

- Claims are scoped correctly: no real-vehicle attack, no physical CAN fidelity, no IDS benchmark.
- The DOI-backed artifact materially improves credibility.
- RQs make the evaluation easier to defend.
- The evaluation matrix ties every claim to an artifact and a limitation.
- The Artifact Evaluation Checklist is aligned with artifact-review expectations.
- The paper compiles cleanly in IEEEtran and is compact: 5 pages.

## Remaining weaknesses

1. **References still need final human bibliographic polishing.**
   - Some entries use `and others` because metadata could not be fully verified automatically.
   - This is acceptable for draft, but not ideal for camera-ready.

2. **No HIL / real CAN timing validation.**
   - Correctly declared as limitation.
   - A reviewer focused on cyber-physical realism may still downscore it.

3. **Matrix 007 uses deterministic fast-run timing.**
   - Correctly disclosed.
   - Avoid calling it real-time anywhere.

4. **Rule-based triage numbers are extremely high.**
   - v4 keeps them framed as sanity check only.
   - Do not move accuracy/F1 into abstract/contributions.

5. **Figure set is intentionally minimal.**
   - The text compiles and is clear, but a cleaner visual pipeline/architecture diagram could improve presentation if page budget allows.

## Recommended final pre-submission actions

- Verify SBESC/SSV page limit and blind-review policy.
- Complete author metadata and affiliation.
- Replace `and others` with complete author lists where required.
- Optionally add one polished vector architecture figure if page budget allows.
- Confirm whether the conference accepts artifact DOI in the manuscript before acceptance or prefers anonymized artifact link.

## Risk assessment

- **Overclaim risk:** low.
- **Reproducibility risk:** low, due to GitHub + Zenodo + hashes.
- **Realism criticism risk:** medium, but mitigated by explicit threats to validity.
- **Reference/style criticism risk:** medium-low, fixable by bibliographic polishing.
- **Submission formatting risk:** low after IEEEtran PDF build, pending conference-specific rules.
