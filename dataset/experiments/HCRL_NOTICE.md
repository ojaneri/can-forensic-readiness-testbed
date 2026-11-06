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

Regenerating from the official files with this script reproduced all 16 hashes (four files in each of the four
experiments), including the 492 MB `frames_normalized.csv` of Experiment 014. This was checked on 2026-11-05.

The unlabeled normal-driving capture of the HCRL release is not used by the paper.
