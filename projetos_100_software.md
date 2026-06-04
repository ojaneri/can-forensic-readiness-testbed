# 100% Software Projects for CAN / ECU / Automotive Traffic Simulation

## Quick conclusion

A fully software-defined path is feasible. The recommended stack is:

1. Linux `vcan` + `can-utils`.
2. ICSim — visual instrument cluster simulator.
3. Caring Caribou — CAN/UDS exploration and fuzzing tool.
4. `python-can` — custom simulated ECUs, attacks, logger, and dataset generation.
5. `opendbc` — DBC files and CAN parsing/building utilities.
6. CANdevStudio — GUI-based CAN signal simulation.
7. Public datasets such as ROAD and can-train-and-test.

## 1. Linux SocketCAN + vcan + can-utils

- GitHub: https://github.com/linux-can/can-utils

Useful tools:

- `candump` — capture CAN traffic.
- `cansend` — send a single frame.
- `canplayer` — replay CAN logs.
- `cangen` — generate random traffic.
- `cansniffer` — inspect payload differences.
- `canbusload` — estimate bus load.

## 2. ICSim — Instrument Cluster Simulator

- GitHub: https://github.com/zombieCraig/ICSim

Why it matters:

- Visual simulated instrument cluster.
- Uses SocketCAN/vcan.
- Useful for safe CAN hacking education.
- Supports randomized mappings for reverse-engineering exercises.

## 3. Caring Caribou

- GitHub: https://github.com/CaringCaribou/caringcaribou

Useful modules:

- `dump`
- `send`
- `listener`
- `fuzzer`
- `uds`
- `uds_fuzz`
- `doip`
- `xcp`

## 4. python-can

- GitHub: https://github.com/hardbyte/python-can

Use in this project:

- Simulated ECUs.
- Attack modules.
- Forensic logger.
- Dataset generator.
- Virtual backend for hardware-free experiments.

## 5. opendbc

- GitHub: https://github.com/commaai/opendbc

Use in this project:

- CAN DBC references.
- Parsing and building more realistic signals.
- Discussion of proprietary DBC limitations.

## 6. CANdevStudio

- GitHub: https://github.com/GENIVI/CANdevStudio

Use in this project:

- GUI CAN signal simulation.
- Education and demonstration.

## Recommended paper framing

**A Software-Defined Low-Cost CAN Testbed for Automotive Cybersecurity Education and Forensic Analysis**

Contribution:

1. Reproducible software-defined CAN pipeline.
2. Controlled attack scenarios.
3. Evidence-preserving logging and manifests.
4. Observer demo.
5. Future hardware-in-the-loop extension.
