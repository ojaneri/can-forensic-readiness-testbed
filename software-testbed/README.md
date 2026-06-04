# Software-Defined CAN Testbed

A 100% software CAN testbed for automotive cybersecurity education, controlled attack simulation, and preliminary forensic analysis.

Stack:

- Linux `vcan` / SocketCAN when available.
- `can-utils` for capture, replay, and traffic generation.
- `python-can` for virtual CAN experiments.
- Custom simulated ECU, logger, spoofing, and flooding scripts.
- Optional ICSim and Caring Caribou integration.

## Quick installation — Ubuntu/Debian

```bash
sudo apt update
sudo apt install -y can-utils python3 python3-pip git
python3 -m pip install --user python-can
```

Or use the helper script:

```bash
./scripts/install_deps_ubuntu.sh
```

## Virtual CAN setup

```bash
sudo ./scripts/setup_vcan.sh vcan0
```

Test:

```bash
candump vcan0
# in another terminal:
cansend vcan0 123#1122334455667788
```

## Scenarios

### 1. Baseline

Terminal A:

```bash
./scripts/run_logger.sh vcan0 experiments/001_baseline
```

Terminal B:

```bash
./scripts/run_ecu_sim.sh vcan0
```

### 2. Replay

```bash
./scripts/run_replay.sh vcan0 experiments/001_baseline/candump.log
```

### 3. Spoofing / Fabrication

```bash
./scripts/run_spoof.sh vcan0 --id 188 --data 000000C800000000 --period 0.05 --count 50
```

### 4. Controlled flooding

```bash
./scripts/run_flood.sh vcan0 --gap-ms 5 --duration 10
```

## Forensic artifacts

The logger creates:

- `candump.log` — raw capture in can-utils-like format.
- `frames.csv` — normalized frames.
- `manifest.json` — parameters, timestamps, host metadata, and SHA-256 hashes.

## Safety

The current experiments use a software-only environment. No physical vehicle, ECU, or external network is targeted. When migrating to real `can0` hardware, use only isolated and authorized benches.
