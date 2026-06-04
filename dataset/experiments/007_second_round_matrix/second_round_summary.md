# Second Experimental Round — Matrix 007

## Scope

Authorized, software-only CAN traffic generation for the article testbed. This round uses deterministic fast-run event simulation: frame timestamps follow the declared schedule, but the script does not wait for ten real minutes per run.

## Design

- 10 runs of 600 s each.
- Four phases per run: 180 s baseline, 120 s spoofing, 120 s flooding, 180 s recovery.
- Spoofing intensity levels: low, medium, high.
- Flooding intensity levels: low, medium, high.
- One medium/medium repetition is included to show seed variability.

## Aggregate results

- Total runs: 10
- Total synthetic duration: 6000.0 s
- Total frames: 435450
- Phase counts: `{'baseline': 112500, 'spoofing': 72450, 'flooding': 138000, 'recovery': 112500}`

## Matrix summary

| Spoof | Flood | Runs | Mean total frames | Mean flood frames | Mean unique flood IDs | Mean unknown-ID ratio | Mean spoof speed |
|---|---:|---:|---:|---:|---:|---:|---:|
| high | high | 1 | 59100 | 24000 | 2045 | 0.998125 | 225.082 |
| high | low | 1 | 41100 | 6000 | 1942 | 0.998 | 224.908 |
| high | medium | 1 | 47100 | 12000 | 2041 | 0.9975 | 224.93 |
| low | high | 1 | 49650 | 24000 | 2045 | 0.997792 | 155.221 |
| low | low | 1 | 31650 | 6000 | 1923 | 0.998 | 155.347 |
| low | medium | 1 | 37650 | 12000 | 2039 | 0.998333 | 155.175 |
| medium | high | 1 | 52800 | 24000 | 2045 | 0.998042 | 190.036 |
| medium | low | 1 | 34800 | 6000 | 1939 | 0.997833 | 190.248 |
| medium | medium | 2 | 40800 | 12000 | 2038.5 | 0.99825 | 189.871 |

## Interpretation

This round strengthens the article by replacing a single demonstrative run with a controlled matrix. The resulting evidence supports discussion of parameter sensitivity, run-to-run reproducibility, and triage consistency under different spoofing and flooding intensities.

## Limitation

The data remains synthetic and software-defined. It validates the reproducible workflow, labels, evidence packaging, and preliminary triage logic; it does not validate electrical CAN behavior, ECU timing constraints, or real-vehicle attack performance.
