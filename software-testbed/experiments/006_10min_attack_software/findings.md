# Findings — Experiment 006: 10-Minute Software CAN Attack

## Scope

Authorized, 100% software execution using the `python-can` virtual backend. No vehicle, physical ECU, or external network was involved.

## Duration and phases

- Total duration: 600.06 s
- Total frames: 40,200
- Frames by phase: `{'baseline': 11157, 'spoofing': 6240, 'flooding': 11646, 'recovery': 11157}`

## Decoded speed on ID 0x100

```json
{
  "baseline": {
    "count": 3570,
    "min": 27,
    "max": 92,
    "mean": 61.04,
    "stdev": 18.5
  },
  "spoofing": {
    "count": 2971,
    "min": 180,
    "max": 200,
    "mean": 195.0,
    "stdev": 8.66
  },
  "flooding": {
    "count": 8,
    "min": 1192,
    "max": 61453,
    "mean": 27253.38,
    "stdev": 18982.09
  },
  "recovery": {
    "count": 3570,
    "min": 27,
    "max": 92,
    "mean": 61.56,
    "stdev": 18.93
  }
}
```

## Findings

1. Baseline and recovery maintained normal periodic traffic on IDs `0x100`, `0x120`, `0x188`, and `0x300`.
2. Spoofing fabricated speed/RPM/throttle values, concentrating ID `0x100` around 180–200 km/h.
3. Flooding generated high arbitration ID cardinality, useful for noise measurement and forensic triage.
4. The artifacts support temporal statistical analysis and hash-based chain-of-custody validation.

## Limitation

The virtual backend does not model the CAN physical layer, electrical arbitration, bus termination, transceiver behavior, or real bus errors.
