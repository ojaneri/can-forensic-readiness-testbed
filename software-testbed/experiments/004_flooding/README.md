# Experiment 004 — Controlled Flooding

Objective: generate intense traffic to study availability and forensic triage.

## Procedure

```bash
../../scripts/run_flood.sh vcan0 --gap-ms 5 --duration 10
```

Optional high-priority fixed ID:

```bash
../../scripts/run_flood.sh vcan0 --fixed-id 001 --gap-ms 2 --duration 10
```

## Limitation

In `vcan`, there is no physical layer, electrical arbitration, transceiver error, or real bus saturation. The experiment measures only software/logging effects.
