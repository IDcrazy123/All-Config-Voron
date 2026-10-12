# Legacy Calibration Troubleshooting Signatures

This compact index preserves the useful lessons from retired ToolVision, kTAMV, TKC/KCC and earlier SexBolt trials. Current calibration ownership is Axiscope XY/coarse Z, Cartographer home/mesh and first-layer final Z. See the [2026-10-12 incident and recovery summary](cleanup-2026-10-12.md) for recorded fixes, open issues and archived-file locations.

## Active baseline

- Axiscope: camera XY and preliminary relative Z using PF2 at X80/Y-8, approach Z3 over observed contact Z0–2; Z15 for transit/tool changes, nozzle 150 °C. Automatic config writes are disabled. Do not load `[tools_calibrate]` alongside Axiscope.
- Cartographer: bed-referenced Z home, Touch model, adaptive mesh, and shuttle ADXL345.
- `printer.cfg` `SAVE_CONFIG`: authoritative T1–T4 XYZ offsets.

## Recognizable failure signatures

| Signature | Likely historical cause | Safe response |
| --- | --- | --- |
| `No nozzle found`, multiple bright blobs, or scale outlier near `0.028` vs `0.041–0.044` | kTAMV/ToolVision optical ambiguity, glare, or stretched camera frame | Do not widen tolerance. Treat it as historical camera evidence; current operation uses Axiscope. |
| `NameError: name 'time' is not defined` while reading calibration status | TKC `ce4ca303` status bug | Treat as retired TKC evidence, not CAN/Cartographer failure. Recover Klipper and do not reinstall that revision. |
| Negative elapsed time or toolchanger becomes uninitialized after abort | TKC mixed clocks and incomplete cleanup/recovery | Stop the experiment, verify physical/active tool state, then initialize KTC deliberately. Do not continue automatic motion. |
| Abort command is accepted only after a full calibration finishes | TKC abort shared the serialized G-code queue | Use emergency-safe printer controls; do not treat the old abort command as an immediate stop. |
| Z station move is displaced in the opposite XY direction | TKC applied camera compensation with the wrong sign | Never reuse the old compensation formula. Confirm sign with small attended moves. |
| Same Cartographer value appears for different tool positions or tools differ by about 5 mm Y | Old TKC cache/reference-coordinate defect | Reject the run; verify reference freshness and identical measurement coordinates. |
| T2/T3 Touch spread is large or a single tool fails repeatability | Root cause remains unconfirmed; historical observations do not establish a specific mechanical/sensor fault | Keep the raw evidence; stabilize conditions and collect repeated samples before changing offsets. Do not relax tolerance to force acceptance. |
| Offset differs after cold vs 150 °C measurement | Thermal expansion and/or plastic on nozzle | Keep temperature conditions consistent; current attended PF2 measurements use 150 °C and are preliminary only. Final Z requires first-layer verification. |
| `Expected tool ... but active is ...` | Detection-pin or mechanical state mismatch | Stop motion, inspect the mounted tool and sensor state, then initialize toolchanger. Do not force the requested tool in software. |
| `TMC ... ShortToSupply_A` during homing | Electrical fault on motor phase, connector, cable, or driver | Power down and inspect hardware. A successful Klipper restart does not prove the fault is gone. |
| Cartographer CAN timeout after restart | Unconfirmed CAN/reset issue from earlier operation | Capture `klippy.log`, `can0` state, MCU temperatures, and power state before power-cycling. |
| `heater_bed not heating at expected rate` during initial heat | Historical SSR/ADC noise case | Current `check_gain_time` is 240 s. Verify wiring and temperature trend before changing heater safety settings. |

## KTC command ownership

The old `tools_calibrate` workflow is retired. Current `calibration-probe.cfg` uses Axiscope and disables legacy automatic offset writers. `CALIBRATE_NOZZLE_PROBE_OFFSET` remains blocked because no `tool_probe_endstop` is configured; this is not a claim that Cartographer Touch cannot measure nozzle contact. KTC readonly files remain plugin-owned.

## Evidence locations

- `extras/experiments/tkc-*`: detailed TKC revision tests and reproductions.
- `extras/experiments/ktamv-xy-independent-cycles-20260831.md`: optical repeatability evidence.
- `extras/retired-configs/README.md`: recovery pointer for old configuration copies; see the cleanup manifest/archive for original files.
- `.agents/KNOWN_ISSUES.md`: Vietnamese issue registry and status.
- `extras/Nhat-ky-chinh-sua/`: chronological machine observations.

Preserve raw evidence when the failure mechanism remains uncertain. Remove only confirmed duplicates or files fully represented by Git history and a dated backup.
