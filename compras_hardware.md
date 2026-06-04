# Hardware Shopping Notes — Optional HIL Extension

The current paper can be completed using the software-defined testbed only. Hardware should be treated as a future extension or optional hardware-in-the-loop validation.

## Recommended starter package

1. **USB-CAN adapter compatible with Linux/SocketCAN**
   - Used to connect the notebook to a physical CAN bus.
   - Prefer CANable/CANtact/candleLight/SocketCAN-compatible adapters.
   - Avoid adapters that only support proprietary Windows software.

2. **Three MCP2515 + TJA1050 CAN modules**
   - Used to build low-cost simulated CAN nodes with Arduino/STM32/ESP32.

3. **Two or three Arduino Nano/Uno-compatible boards**
   - Easier than ESP32 for first hardware experiments because many MCP2515 modules use 5 V logic.

4. **Breadboard, Dupont wires, and 120 ohm resistors**
   - Required for CAN wiring and bus termination.

5. **12 V power supply**
   - Required only when adding a real automotive module or instrument cluster.

6. **Optional OBD-II / DB9 connectors**
   - Useful for a clean bench setup.

## Suggested hardware path

### Package A — Minimal physical CAN simulation

- 1 Linux/SocketCAN-compatible USB-CAN adapter.
- 3 Arduino Nano/Uno boards.
- 3 MCP2515/TJA1050 CAN modules.
- Breadboard, jumpers, and 120 ohm resistors.

### Package B — Better for paper photographs

Package A plus:

- 1 ESP32 or STM32 board.
- 1 SN65HVD230 transceiver if using ESP32/TWAI.
- 1 12 V power supply.
- 1 OBD-II connector.
- Acrylic/MDF base or enclosure.

### Package C — Hardware-in-the-loop extension

Package B plus:

- 1 used CAN-enabled instrument cluster with connector/harness.
- Optional BCM or legacy ECU.
- Current-limited 12 V bench power supply.
- Inline fuse.

## Technical notes

- The best Linux workflow is to expose the adapter as `can0` through SocketCAN.
- CAN requires 120 ohm termination at both ends of the bus.
- MCP2515/TJA1050 modules are usually 5 V; be careful when using ESP32.
- For the paper, document invoice/price screenshots to support reproducibility and cost analysis.

## Recommendation

Do not depend on hardware for the first paper. Use hardware as a future extension after the software-defined dataset, demo, and analysis are complete.
