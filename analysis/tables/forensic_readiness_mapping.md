# Forensic-Readiness Mapping

| Forensic-readiness requirement | Implemented artifact | Boundary |
|---|---|---|
| Traceability | `input_attack_plan.json` | Synthetic experiment plan, not real incident acquisition |
| Integrity | `manifest.json` with SHA-256 hashes | File-level integrity only |
| Repeatability | Experiment scripts, fixed seed, phase schedule | Repeats virtual behavior, not physical CAN effects |
| Normalization | `frames_normalized.csv` and `data_dictionary.md` | Didactic signal semantics |
| Reviewability | Project index and client-side observer demo | Demo replays stored artifacts only |
| Interpretation control | Limitations and safety boundary | No claim of OEM signal accuracy |
