# Testbed Methodology

## Current architecture: software-defined CAN

The current testbed uses a fully software-defined CAN environment. It is safe, reproducible, and does not require physical ECUs, vehicles, or CAN adapters.

Core components:

- Python 3.
- `python-can` virtual backend.
- Simulated ECU traffic generator.
- Spoofing/fabrication attack module.
- Controlled flooding attack module.
- Forensic logger.
- CSV and annotated CAN log outputs.
- JSON manifests with SHA-256 hashes.
- Client-side observer demo.

## Experimental phases

### Phase 1 — Baseline

Objective: generate normal periodic CAN-like traffic.

Collected evidence:

- normalized CSV frames;
- annotated CAN log;
- phase labels;
- timestamps;
- SHA-256 hashes.

### Phase 2 — Spoofing / Fabrication

Objective: inject fabricated safety-relevant state into the stream.

Current example:

- ID `0x100`: engine/cluster state with decoded speed.
- ID `0x188`: display-related speed frame.
- Attack forces speed to 180–200 km/h.

### Phase 3 — Controlled Flooding

Objective: inject high-cardinality random arbitration IDs and payloads to create noise for triage.

Metrics:

- frame count;
- unique arbitration IDs;
- top IDs;
- payload distribution;
- phase-level changes.

### Phase 4 — Recovery

Objective: return to normal traffic after the attack window, enabling before/during/after comparison.

## Forensic evidence workflow

For each experiment:

1. Create experiment ID.
2. Store attack plan as JSON.
3. Generate raw annotated log.
4. Generate normalized CSV.
5. Generate findings JSON/Markdown.
6. Generate SHA-256 hashes for all artifacts.
7. Store manifest JSON.
8. Preserve scripts used to generate the experiment.

## Evaluation metrics

- Total frame count.
- Frame count by phase.
- Top arbitration IDs.
- Decoded speed statistics by phase.
- ID cardinality during flooding.
- Payload entropy.
- Inter-arrival time distribution.
- Rule-based triage performance.

## Scientific limitation

The software-defined testbed validates the workflow, reproducibility, logging, and forensic evidence handling. It does **not** model physical CAN arbitration, transceiver errors, bus termination, electrical noise, or real ECU behavior.

## Future hardware extension

A future hardware-in-the-loop version may include:

- USB-CAN adapter compatible with SocketCAN;
- Arduino/STM32/ESP32 simulated ECUs;
- MCP2515/TJA1050 or SN65HVD230 transceivers;
- a used CAN-enabled instrument cluster;
- optional legacy ECU or BCM.
