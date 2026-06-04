# Used Real ECU / Module Notes — Optional Hardware Extension

The current paper should not depend on used real hardware. If a hardware-in-the-loop extension is added later, the safest and most useful first component is a **CAN-enabled used instrument cluster with its connector/harness**.

## Best first choice: used CAN-enabled instrument cluster

Why it is useful:

- It provides visible effects: speedometer, RPM, warning lights, fuel, temperature.
- It is safer than engine ECUs, ABS modules, or airbag modules.
- It can be used to demonstrate replay/spoofing in a bench environment.
- It supports strong photographs and demonstration material for the paper.

Questions to ask the seller:

1. What vehicle, year, and trim did it come from?
2. Does it include the connector or a cut harness?
3. Does it communicate over CAN? Are CAN-H and CAN-L present?
4. Is the part number visible in the label?
5. Was it tested on a bench or vehicle?
6. Is return accepted if it does not communicate on a bench?

## Second choice: Body Computer / BCM

Advantages:

- Common in Fiat, VW, GM, and other vehicles.
- Relevant to real vehicle network architecture.

Disadvantages:

- May require immobilizer/key pairing.
- May not show visible behavior by itself.
- Pinout may be harder to identify.

## Third choice: ABS module

Advantages:

- Safety-relevant and often CAN-connected.

Disadvantages:

- More complex and potentially unsafe if powered incorrectly.
- May require sensors or actuators.
- Not recommended for the first hardware experiment.

## Fourth choice: engine ECU

Advantages:

- Strong realism.

Disadvantages:

- May require immobilizer, sensors, harness, correct power sequencing, and documentation.
- Some older ECUs may use K-line instead of CAN.
- It may not transmit useful traffic by itself.

## Recommendation

For a first hardware extension, buy a **used CAN-enabled instrument cluster with connector/harness**, not an engine ECU.
