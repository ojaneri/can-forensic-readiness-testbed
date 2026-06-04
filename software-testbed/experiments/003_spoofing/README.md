# Experiment 003 — Spoofing / Fabrication

Objective: inject fabricated CAN frames to simulate manipulation of vehicular state.

## Procedure

```bash
../../scripts/run_spoof.sh vcan0 --id 188 --data 000000C800000000 --period 0.05 --count 50
```

Interpretation: ID `0x188` is used by the simulator as a display-related speed frame. The payload is didactic.

## Evidence

- Fabricated frame log.
- Difference between baseline and attacked traffic.
