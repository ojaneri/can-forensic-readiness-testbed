# Findings — Experiment 005: 100% Software CAN Attack

## Scope

The attack was executed in an authorized, 100% software environment using the `python-can` virtual backend. No vehicle, physical ECU, external network, or hardware was involved.

## Input

- Experiment ID: `005_real_attack_software`
- Virtual channel: `ssv2026-attack-virtual-can`
- Phases: `baseline`, `spoofing`, `flooding`, `recovery`
- Main IDs: `0x100`, `0x120`, `0x188`, `0x300`

## Duration and frame counts

- Total duration: 13.019 s
- Total frames: 2,088
- Baseline: 320 frames
- Spoofing: 296 frames
- Flooding: 1,392 frames
- Recovery: 80 frames

## Decoded speed on ID 0x100

- Baseline: 40–79 km/h, mean 60.56 km/h
- Spoofing: fixed at 200 km/h
- Recovery: 45–59 km/h

## Findings

1. The baseline generated stable periodic traffic on IDs `0x100`, `0x120`, and `0x188`.
2. The spoofing phase fabricated vehicle state on ID `0x100`, forcing the decoded speed to **200 km/h**.
3. Frame `0x188` was used as a didactic display-related signal, separating vehicle-state traffic from dashboard/display traffic.
4. The flooding phase substantially increased ID diversity and frame volume, creating noise for forensic triage.
5. The recovery phase showed a return to the normal pattern, enabling before/during/after comparison.

## Scientific limitation

Because the experiment used a virtual backend, it validates the software pipeline, logging, replay, preservation, and analysis workflow. It does **not** measure CAN electrical arbitration, physical bus saturation, transceiver errors, termination effects, or real ECU behavior.

## Use in the paper

This experiment can be used as a proof of concept for the software-defined testbed: zero-cost execution, reproducible workflow, hash-preserved evidence, and documented attack scenarios.
