# Demo — ICSim External Trace + Spoofed Packets

Visual browser demo for Experiment 009.

It replays the public ICSim sample trace imported in Experiment 008 plus labeled didactic spoofed packets injected into:

- Speed: ID `0x244`, bytes 3-4
- Doors: ID `0x19B`, byte 2
- Turn signals: ID `0x188`, byte 0

This is a safe visualization and forensic-readiness artifact. It is not a real vehicle attack and not an IDS benchmark.

Main package:

- `../dataset/experiments/009_icsim_spoof_injection/`

Key test package files:

- `spoof_injection_plan.json`
- `spoofed_packets.csv`
- `frames_normalized.csv`
- `manifest.json`
