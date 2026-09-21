# StealthChanger Production Operation Guide

[English](huong-dan-he-thong-stealthchanger.en.md) | [Tiếng Việt](huong-dan-he-thong-stealthchanger.md)

## Backend ownership

- KTC-Easy owns tool pickup/dropoff, active-tool state, dock routes, and readonly macros.
- Axiscope owns attended tool XY/Z calibration through the Web UI on port 3000 and microswitch `^PF2`.
- Cartographer owns Z homing, Touch reference, adaptive bed mesh, and resonance sensing.
- OrcaSlicer owns per-filament/process choices such as pressure advance and prime-tower behavior.

Do not combine retired kTAMV, ToolVision, TKC/KCC, or SexBolt procedures with the active stack.

## Before printing

1. Confirm Klipper is ready and no MCU/CAN error is present.
2. Inspect all five docks and verify no tool is partially seated.
3. Confirm the active tool reported by KTC matches the physically mounted tool.
4. Clean the reference nozzle if Cartographer Touch or an Axiscope Z run will be used.
5. Verify Orca selected the correct five-tool machine, process, and filament mapping.

## Normal print flow

`PRINT_START` receives the initial tool, per-tool temperatures, bed temperature, and material from OrcaSlicer. It hands off any active dryer cycle, homes safely, selects T0 after homing, heats/soaks, performs QGL and Cartographer operations, cleans the nozzle, primes only used tools, and leaves the initial print tool active.

`PRINT_END` retracts, raises Z, drops the tool, parks the empty shuttle, turns off heaters/part fans, clears offsets/mesh, and schedules chamber-fan cooldown.

Use `PAUSE`/`RESUME` instead of ad-hoc tool motion. `RESUME` initializes KTC and verifies tool presence before continuing.

## Tool calibration

1. Open Axiscope on port 3000.
2. Use the camera crosshair for attended XY alignment.
3. Use the PF2 microswitch workflow for Z; production coordinates are `(80, -5, 8)` with 10 samples.
4. The workflow preheats all tools to 150 °C, waits for each selected tool, and raises Z to at least 15 mm before pickup.
5. Review the measured offsets, persist them through the supported Axiscope/Klipper save path, and confirm `CHECK_OFFSETS` before a test print.

Never invoke legacy `CALIBRATE_ALL_OFFSETS` or `CALIBRATE_MOVE_OVER_PROBE`; they are intentionally blocked.

## Nozzle cleaning

`CLEAN_NOZZLE` requires a KTC active tool. It uses the bucket at `(320, -8)`, the silicone brush from X 277 to 309, and cleaning Z 1.2 mm. `PURGE_AND_CLEAN` additionally purges at material temperature before cooling to the cleaning temperature.

## Recovery rules

- Tool mismatch: stop, inspect physical seating and detection pins, then initialize KTC.
- Unhomed machine: do not request a tool drop or dock route.
- TMC electrical fault: power down and inspect wiring; do not clear-and-continue.
- Calibration anomaly: keep raw measurements and compare temperature, nozzle cleanliness, and tool seating before changing offsets.

See [legacy calibration troubleshooting](legacy-calibration-troubleshooting.md) for retired-system error signatures.
