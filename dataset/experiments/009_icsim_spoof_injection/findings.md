# Experiment 009 — ICSim External Trace with Spoofed Packet Injection

## Scope

This package starts from the external ICSim sample trace imported in Experiment 008 and injects labeled spoofed packets using ICSim didactic semantics: speed, door status, and turn signals.

It is designed for a visual dashboard demo and forensic workflow validation. It is not a real-vehicle attack and not an IDS benchmark.

## Results

- Base frames: 6158
- Spoofed frames: 45
- Total frames: 6203
- Duration: 3.257991 s
- Unique arbitration IDs: 37
- Injected ID counts: `{'244': 33, '19B': 7, '188': 5}`
- Injected speed stats: `{'count': 33, 'min': 190.0, 'max': 202.0, 'mean': 195.727}`

## ICSim semantics used

- Speed: ID `0x244`, bytes 3-4.
- Doors: ID `0x19B`, byte 2.
- Turn signals: ID `0x188`, byte 0.

## Interpretation

The experiment demonstrates that an external trace can be augmented with labeled didactic events while preserving base-source provenance, normalized evidence records, and SHA-256 manifests.

## Boundary

Spoofed packets are controlled didactic injections into an external ICSim trace. They are labeled for visualization and workflow validation only.
