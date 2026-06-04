# Demo — External ICSim CAN Trace Replay

Observer-safe browser demo for Experiment 008.

Purpose: demonstrate that the forensic-readiness workflow can ingest, normalize, hash, summarize, and safely replay a trace from an external source (`ICSim/data/sample-can.log`).

This is **not** an IDS benchmark. The upstream sample does not provide attack labels in this package.

Files:

- `index.html` — browser replay demo
- `assets/icsim_frames.json` — normalized frames for replay
- `assets/summary.json` — experiment summary
- `assets/external_source_metadata.json` — upstream repo, commit, license and source hash
- `assets/viz_stats.json` — derived visualization stats
- `assets/manifest.json` — demo asset hashes

Source experiment:

- `dataset/experiments/008_external_icsim_replay/`
