#!/usr/bin/env bash
# measure_cost.sh — resource indicators for the "low-cost" claim.
# Re-runs the RF baseline on the internal labeled corpus (writes only under out/,
# never over estudo/), records wall time and peak RSS, plus host and footprint facts.
if [ -z "${BASH_VERSION:-}" ]; then exec bash "$0" "$@"; fi
set -euo pipefail
HERE=$(cd "$(dirname "$0")" && pwd)
ROOT=$(cd "$HERE/../.." && pwd)
OUT="$HERE/out"; mkdir -p "$OUT"
IN="$ROOT/dataset/all_frames_normalized.csv"

{
  echo "date_utc: $(date -u +%FT%TZ)"
  echo "cpu: $(lscpu | sed -n 's/^Model name: *//p' | head -1)"
  echo "vcpus: $(nproc)"
  echo "ram_total_gb: $(free -g | awk '/^Mem:/{print $2}')"
  echo "kernel: $(uname -r)"
  echo "python: $(python3 --version 2>&1)"
  python3 -c "import sklearn,can;print('sklearn:',sklearn.__version__);print('python_can:',can.__version__)"
  echo "input_csv_mb: $(du -m "$IN" | cut -f1)"
  echo "dataset_dir_mb: $(du -sm "$ROOT/dataset" | cut -f1)"
  echo "raw_dir_mb: $(du -sm "$ROOT/raw" | cut -f1)"
} > "$OUT/host.txt"

/usr/bin/time -v python3 "$ROOT/analysis/scripts/rf_baseline.py" \
  --input "$IN" --outdir "$OUT/rf" > "$OUT/rf_stdout.txt" 2> "$OUT/rf_time.txt"

grep -E "Elapsed \(wall|Maximum resident|User time|System time" "$OUT/rf_time.txt" >> "$OUT/host.txt"
cat "$OUT/host.txt"
