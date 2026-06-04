# Paper Notes — Software-Defined Version

## Proposed contribution

This testbed integrates open tools to create a reproducible virtual CAN environment with controlled attack scenarios and forensic logging. It lowers the entry barrier for automotive cybersecurity education and preliminary forensic analysis, while remaining extensible to real SocketCAN hardware.

## Suggested architecture figure

- `vcan0` or `python-can virtual` bus in the center.
- Simulated ECUs using `python-can`.
- Optional visual cluster using ICSim.
- Attacker/fuzzer using custom scripts or Caring Caribou.
- Forensic logger producing CSV, raw logs, manifests, and SHA-256 hashes.
- Replay component using `canplayer` or public datasets.

## Scenario table

| Scenario | Tool | Evidence | Limitation |
|---|---|---|---|
| Baseline | ECU simulator + logger | CSV/log/hash | synthetic traffic |
| Replay | canplayer | replayed log | depends on log fidelity |
| Spoofing | attacker_spoof | fabricated frame | no physical effect without HIL |
| Flooding | attacker_flood/cangen | frame rate and ID diversity | virtual CAN does not model physical layer |

## Difference from existing work

- Lower cost than HIL/FPGA systems.
- More reproducible than hardware-specific benches.
- More forensic-oriented than purely didactic simulators.
- Includes manifests, hashes, and evidence workflow.
