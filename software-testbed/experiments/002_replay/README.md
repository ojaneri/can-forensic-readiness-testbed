# Experiment 002 — Replay

Objective: replay captured traffic and verify repeatability.

## Procedure

```bash
../../scripts/run_replay.sh vcan0 ../001_baseline/candump.log
```

Run the logger in another terminal to capture the replay.

## Metrics

- Replayed frames.
- IDs and frequencies compared with baseline.
- Hash of the replay log.
