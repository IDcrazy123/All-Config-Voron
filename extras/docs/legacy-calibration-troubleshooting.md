# Legacy Calibration Troubleshooting Signatures

This compact index preserves the useful lessons from retired ToolVision, kTAMV, TKC/KCC, SexBolt, and early Axiscope work. It does not reactivate those systems.

## Active baseline

- Axiscope: camera-crosshair XY plus PF2 microswitch Z at `(80, -5, 8)`, Web UI port 3000.
- Cartographer: bed-referenced Z home, Touch model, adaptive mesh, and shuttle ADXL345.
- `printer.cfg` `SAVE_CONFIG`: authoritative T1–T4 XYZ offsets.

## Recognizable failure signatures

| Signature | Likely historical cause | Safe response |
| --- | --- | --- |
| `No nozzle found`, multiple bright blobs, or scale outlier near `0.028` vs `0.041–0.044` | kTAMV/ToolVision optical ambiguity, glare, or stretched camera frame | Do not widen tolerance. Fix focus, lighting, reflections, and nozzle centering. Current production uses manual Axiscope crosshair instead. |
| `NameError: name 'time' is not defined` while reading calibration status | TKC `ce4ca303` status bug | Treat as retired TKC evidence, not CAN/Cartographer failure. Recover Klipper and do not reinstall that revision. |
| Negative elapsed time or toolchanger becomes uninitialized after abort | TKC mixed clocks and incomplete cleanup/recovery | Stop the experiment, verify physical/active tool state, then initialize KTC deliberately. Do not continue automatic motion. |
| Abort command is accepted only after a full calibration finishes | TKC abort shared the serialized G-code queue | Use emergency-safe printer controls; do not treat the old abort command as an immediate stop. |
| Z station move is displaced in the opposite XY direction | TKC applied camera compensation with the wrong sign | Never reuse the old compensation formula. Confirm sign with small attended moves. |
| Same Cartographer value appears for different tool positions or tools differ by about 5 mm Y | Old TKC cache/reference-coordinate defect | Reject the run; verify reference freshness and identical measurement coordinates. |
| T2/T3 Touch spread is large or a single tool fails repeatability | Nozzle contamination, temperature mismatch, tool seating, or retired TKC sample handling | Clean nozzle, stabilize bed/nozzle temperature, verify dock seating, and collect raw repeated samples before changing offsets. |
| Offset differs after cold vs 150 °C measurement | Thermal expansion and/or plastic on nozzle | Use the production 150 °C Axiscope workflow; never mix cold and hot datasets. |
| `Expected tool ... but active is ...` | Detection-pin or mechanical state mismatch | Stop motion, inspect the mounted tool and sensor state, then initialize toolchanger. Do not force the requested tool in software. |
| `TMC ... ShortToSupply_A` during homing | Electrical fault on motor phase, connector, cable, or driver | Power down and inspect hardware. A successful Klipper restart does not prove the fault is gone. |
| Cartographer CAN timeout after restart | Unconfirmed CAN/reset issue from earlier operation | Capture `klippy.log`, `can0` state, MCU temperatures, and power state before power-cycling. |
| `heater_bed not heating at expected rate` during initial heat | Historical SSR/ADC noise case | Current `check_gain_time` is 240 s. Verify wiring and temperature trend before changing heater safety settings. |

## Commands that must remain blocked

`CALIBRATE_ALL_OFFSETS`, `CALIBRATE_MOVE_OVER_PROBE`, and `CALIBRATE_NOZZLE_PROBE_OFFSET` came from the readonly KTC calibration file. Production has no active `[tools_calibrate]` or `tool_probe_endstop`; the user-owned config overrides these macros with explicit errors.

## Evidence locations

- `extras/experiments/tkc-*`: detailed TKC revision tests and reproductions.
- `extras/experiments/ktamv-xy-independent-cycles-20260831.md`: optical repeatability evidence.
- `extras/retired-configs/`: last removed configuration files.
- `.agents/KNOWN_ISSUES.md`: Vietnamese issue registry and status.
- `extras/Nhat-ky-chinh-sua/`: chronological machine observations.

Preserve raw evidence when the failure mechanism remains uncertain. Remove only confirmed duplicates or files fully represented by Git history and a dated backup.
