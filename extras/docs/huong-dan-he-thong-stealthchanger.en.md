# StealthChanger Production Operation Guide

[English](huong-dan-he-thong-stealthchanger.en.md) | [Tiếng Việt](huong-dan-he-thong-stealthchanger.md)

## Backend ownership

- KTC-Easy owns tool pickup/dropoff, active-tool state, dock routes, and readonly macros.
- KTC-Easy `tools_calibrate` owns the attended SexBolt XYZ trial through microswitch `^PF2`.
- Cartographer owns Z homing, Touch reference, adaptive bed mesh, and resonance sensing.
- OrcaSlicer owns per-filament/process choices such as pressure advance and prime-tower behavior.

Do not combine retired kTAMV, ToolVision, TKC/KCC, Axiscope, or earlier SexBolt procedures with the active trial.

## Before printing

1. Confirm Klipper is ready and no MCU/CAN error is present.
2. Inspect all five docks and verify no tool is partially seated.
3. Confirm the active tool reported by KTC matches the physically mounted tool.
4. Clean the reference nozzle if Cartographer Touch or a SexBolt run will be used.
5. Verify Orca selected the correct five-tool machine, process, and filament mapping.

## Normal print flow

`PRINT_START` receives the initial tool, per-tool temperatures, bed temperature, and material from OrcaSlicer. It hands off any active dryer cycle, homes safely, selects T0 after homing, heats/soaks, performs QGL and Cartographer operations, cleans the nozzle, primes only used tools, and leaves the initial print tool active.

`PRINT_END` retracts, raises Z, drops the tool, parks the empty shuttle, turns off heaters/part fans, clears offsets/mesh, and schedules chamber-fan cooldown.

Use `PAUSE`/`RESUME` instead of ad-hoc tool motion. `RESUME` initializes KTC and verifies tool presence before continuing.

## Tool calibration

1. After restart, run `SEXBOLT_QUERY` with the switch released and manually pressed; continue only if the results are `open` and `TRIGGERED` respectively.
2. Home XYZ, initialize the toolchanger, confirm tool detection, and clean the nozzles.
3. Run `CALIBRATE_MOVE_OVER_PROBE`; it only raises to Z18 and moves to `(80, -5.5)` without touching the switch.
4. After verifying the safe position, run attended `CALIBRATE_ALL_OFFSETS`. It heats each nozzle to 150 °C and uses five median samples.
5. Run `CHECK_OFFSETS`, compare with the baseline, and issue `SAVE_CONFIG` only after the result is plausible.

`CALIBRATE_NOZZLE_PROBE_OFFSET` remains blocked so this trial cannot modify the Cartographer offset.

## Nozzle cleaning

`CLEAN_NOZZLE` requires a KTC active tool. It uses the bucket at `(320, -8)`, the silicone brush from X 277 to 309, and cleaning Z 1.2 mm. `PURGE_AND_CLEAN` additionally purges at material temperature before cooling to the cleaning temperature.

## Recovery rules

- Tool mismatch: stop, inspect physical seating and detection pins, then initialize KTC.
- Unhomed machine: do not request a tool drop or dock route.
- TMC electrical fault: power down and inspect wiring; do not clear-and-continue.
- Calibration anomaly: keep raw measurements and compare temperature, nozzle cleanliness, and tool seating before changing offsets.

See [legacy calibration troubleshooting](legacy-calibration-troubleshooting.md) for retired-system error signatures.
