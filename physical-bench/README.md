# Physical two-node CAN bench (Exp. 020--022)

Captures, firmware and evaluation scripts for the physical-bench experiments reported in the paper
(section "Physical CAN Bench Validation"). Everything here was produced on an isolated bench of our own
hardware. No vehicle, production ECU or operational system was involved, and the attack frames were sent only
on that bench bus. Do not connect this setup to a vehicle.

## Hardware and wiring

- ECU node: STM32 Nucleo-L476RG with an MCP2515/TJA1050 module (8 MHz crystal), SPI at 1 MHz, bus at 500 kbit/s.
- Monitor and attacker node: CANable V2.0 Pro (slcan firmware), driven from a PC with `python-can` (`slcan` interface).
- Module wiring: `VCC` to the Nucleo 5 V pin; `GND`; `CS` to D10; `SCK` to D13; `SI` to D11; `SO` to D12 through a
  voltage divider (1 kOhm in series, 2.2 kOhm from the junction to GND); `INT` not connected.
- Bus: `H` to `CANH`, `L` to `CANL`, common ground. Termination: module jumper J1 fitted and the CANable 120 Ohm switch ON.
  Header J3 (between the H and L markings) must stay without a jumper: a jumper there shorts H to L.
- The TJA1050 needs a 5 V supply. Powered from 3.3 V, the module received the injected frames but could not transmit
  (`runs/2026-11-05_3v3_short`).
- Firmware: `firmware/can_ecu.ino` (smooth speed profile, used in Exp. 021, 022 and the 3.3 V test) and
  `firmware/can_ecu_exp020_random_speed.ino` (random speed byte, used in Exp. 020). Both: STM32duino core 3.0.0, `mcp_can` 1.5.1, FQBN
  `STMicroelectronics:stm32:Nucleo_64:pnum=NUCLEO_L476RG`). It sends IDs 0x100, 0x120, 0x188 and 0x300 every
  20, 50, 100 and 200 ms and prints its receive counters on the ST-Link serial port once per second. Exp. 020 used a
  random speed byte (`27 + random(0, 66)`); Exp. 021, 022 and the 3.3 V test use the smooth profile in this file.

## Runs

| Directory | Exp. | Protocol | Injected / delivered | One-second windows |
|---|---|---|---|---|
| `runs/2026-11-05_runA` | 020 | 180/120/120/180 s baseline/spoofing/flooding/recovery; spoofing 50 Hz (speed 180-200), flooding 100 Hz random IDs; seed 2026110501 | 18,000 / 18,000 | 600 (360/120/120) |
| `runs/2026-11-05_runB` | 021 | same protocol, smooth ECU speed; seed 2026110502 | 18,000 / 18,000 | 600 (360/120/120) |
| `runs/2026-11-05_runC` | 022 | 60 s baseline, then six attackers of 45 s with 15 s recovery between; seed 2026110503 | 30,824 / 30,824 | 421 (151/135/135) |
| `runs/2026-11-05_3v3_short` | - | 4 x 10 s, module powered from 3.3 V | 1,500 received; 1 ECU frame seen by the monitor | - |

Exp. 022 attackers: spoofing at 5 Hz (180-200 km/h), flooding at 10 Hz (random IDs), spoofing at 50 Hz (95-110 km/h),
flooding at 100 Hz with eight unknown IDs (0x7E0-0x7E7), spoofing at 20 Hz (140-160 km/h), ID 0x000 at 500 Hz.

A CAN node does not receive its own frames. Injected frames are therefore logged at send time (`*_tx.log`), frames seen
on the bus are in `*_rx.log`, and delivery is checked against the receive counters that the victim ECU prints
(`*_nucleo_serial.txt`, difference between the first and the last counter).

## Files in each run

- `*_rx.log`, `*_tx.log`: `candump -L` style lines, `(epoch) can0 ID#DATA`.
- `*_phases.json`: start and end (epoch seconds), planned length, injection rate, injected frames and send errors per phase.
- `*_nucleo_serial.txt`: one line per second, `send= TEC= EFLG= rx= spoof= other=` (counters from the victim ECU).
- `derived_*.json`, `eval_physical_bench.json`: results written by the scripts.
- Not committed (the scripts generate them): `frames_normalized.csv` and a per-run `MANIFEST.sha256.json`.

## Reproduce the evaluation

Needs `numpy` and `scikit-learn`, plus `dataset/all_frames_normalized.csv` and `analysis/scripts/rf_baseline.py`
from this repository. Run in this order from the repository root (the scripts write the normalized CSVs that the
later ones read):

```bash
python3 physical-bench/scripts/normalize_and_eval.py
python3 physical-bench/scripts/strategies_eval.py
python3 physical-bench/scripts/strategies_eval_B.py physical-bench/runs/2026-11-05_runB bench006B_20261105_201635
python3 physical-bench/scripts/strategies_eval_C.py physical-bench/runs/2026-11-05_runC bench006C_20261105_203622
python3 physical-bench/scripts/cross_run_rf.py
```

Capturing needs the hardware plus `python-can` and `pyserial`: `bench_capture.py --out <prefix> [--port COM9]` for the
four-phase protocol and `bench_capture_variants.py --out <prefix>` for Exp. 022.

Check file integrity with `sha256sum -c MANIFEST.sha256` from this directory.

## Frozen scripts

`strategies_eval_B.py` and `strategies_eval_C.py` were frozen by file timestamp (2026-11-05 20:14:55 and 20:36:07,
UTC-3, as recorded in the as-run files) and by as-run SHA-256 (`scripts/AS_RUN_SHA256.txt`). The hash list was published
in this repository on 2026-11-05 at 21:19, after the captures, so the timing is not independently timestamped. The
docstrings of the deposited copies state the intent of the freeze; they are not evidence of its timing. The as-run files
themselves are in `scripts/as_run/`; check them with
`cd scripts/as_run && grep -v '^#' ../AS_RUN_SHA256.txt | sha256sum -c` (they contain the server path of the project as a
constant). The copies in `scripts/` differ from the as-run versions only in path constants, made relative to the
repository, and re-running them reproduces the derived JSON files.

Post-hoc ablation (not a frozen strategy): `scripts/suffix_rate_ablation.py` writes
`runs/2026-11-05_runC/derived_suffix_ablation.json`. It separates the 6-byte payload suffix of the injected frames from
the injection rate in the augmentation recipe, with three seeds per variant. Removing the suffix keeps the 5 Hz and 20 Hz
spoofing detections in all seeds; the 50 Hz spoofing detection ranges from 0.14 to 1.0 across seeds, so the single
100 % reported for the augmented forest is one of several outcomes. Mixed injection rates detect the 50 Hz attacker in
all seeds but flag, on average, 37 to 39 % of recovery windows as attacks (one seed reached 100 %).

Run C evaluates only strategies defined before it. The cross-run forest of `cross_run_rf.py` and the strategies of
`strategies_eval.py` were chosen after seeing the data and are exploratory.

## Limits

One bench, one injector implementation per attacker, phase-level labels, and an ECU that reuses the synthetic IDs and the
speed byte of ID 0x100 but not the synthetic timing: it sends at fixed periods of 20, 50, 100 and 200 ms, whereas the
synthetic ECUs of Exp. 006 send three IDs every 50.4 ms and one every 403 ms. The augmentation used in `strategies_eval*.py`
and the injector share the payload tail of the spoofed 0x100 frames, so the spoofing results of that strategy do not
show that it generalizes to other payloads. The results show how the bench exposes shortcut learning in the triage
models; they do not measure detection performance on vehicles.
