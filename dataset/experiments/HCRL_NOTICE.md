# HCRL experiments (014--017): what is and is not in this repository

Experiments 014--017 are imports of the HCRL Car-Hacking Dataset (Korea University Hacking and Countermeasure
Research Lab), which is available for academic use under the terms on the HCRL page:
https://ocslab.hksecurity.net/Datasets/car-hacking-dataset

Reference for the dataset: H. M. Song, J. Woo, and H. K. Kim, "In-vehicle network intrusion detection using deep
convolutional neural network," Vehicular Communications, vol. 21, art. 100198, 2020,
doi:10.1016/j.vehcom.2019.100198.

Its frames are not redistributed here. Each experiment folder holds only:

- `external_source_metadata.json`: source file name, label, license note and the SHA-256 of the official source file;
- `summary.json`: statistics of the normalized package;
- `manifest.json`: the SHA-256 of every output file of the import, including `frames_normalized.csv` and
  `raw_sample.log`, which are not deposited.

## Regenerate and verify

1. Download `DoS_dataset.csv`, `Fuzzy_dataset.csv`, `gear_dataset.csv` and `RPM_dataset.csv` from the HCRL page.
2. Check each file against `source_sha256` in the matching `external_source_metadata.json`.
3. Put them in `raw/` and run `python3 analysis/scripts/import_hcrl.py` from the repository root.
4. Compare the written files with `manifest.json`, for example
   `sha256sum dataset/experiments/014_hcrl_dos/frames_normalized.csv` against the value listed there.

The deposited manifests were produced on 2026-11-06 by running this importer (version v0.5.1) on the official files.
Its row counts match the totals published on the HCRL page: DoS 3,665,771; Fuzzy 3,838,860; Gear 4,443,142; RPM 4,621,702
(the `summary.json` of each experiment records `rows_read`, `rows_skipped_malformed` and `official_rows_expected`).

Version v0.5.0 of the importer had two defects, both fixed in v0.5.1. It dropped the 200,662 frames with DLC 2 or 5
(rows with fewer than ten comma-separated fields), which are real traffic. It also read three DLC-6 frames of the Fuzzy
file with the flag byte inside the payload. v0.5.1 keeps every frame and takes the payload as exactly DLC bytes. The
frames of Experiment 014 are about 496 MB in `frames_normalized.csv`. Independent regeneration on another machine is
the check that remains to be done.

The unlabeled normal-driving capture of the HCRL release is not used by the paper.
