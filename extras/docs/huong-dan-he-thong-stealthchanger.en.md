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
6. Remove the center-bed SexBolt holder before homing, Cartographer Touch, mesh, or printing.

## Normal print flow

`PRINT_START` receives the initial tool, per-tool temperatures, bed temperature, and material from OrcaSlicer. It hands off any active dryer cycle, homes safely, selects T0 after homing, heats/soaks, performs QGL and Cartographer operations, cleans the nozzle, primes only used tools, and leaves the initial print tool active.

`PRINT_END` retracts, raises Z, drops the tool, parks the empty shuttle, turns off heaters/part fans, clears offsets/mesh, and schedules chamber-fan cooldown.

Use `PAUSE`/`RESUME` instead of ad-hoc tool motion. `RESUME` initializes KTC and verifies tool presence before continuing.

## Tool calibration

The removable SexBolt holder now uses the configured bed-center position `(174, 168)`, with the upstream defaults `spread: 5.0` and `lower_z: 0.5`. Confirm the actual ball center with the T0 nozzle; the configured XY is not a new physical measurement. The operator confirmed Z55 as safe transit clearance, stored in `_CALIBRATION_SWITCH.z`. The new contact and probe-start heights remain unmeasured: `contact_z: -1` and `probe_z: -1` are disabled sentinels, not travel coordinates. Default `CALIBRATE_MOVE_OVER_PROBE` is available for travel at or above Z55 without probing. `CALIBRATE_ALL_OFFSETS` rejects the run before tool selection, heating, or movement until valid contact/probe-start heights are configured; its internal `PROBE=1` approach checks these heights before descending.

1. Remove the holder and keep the build plate unobstructed for `G28`, QGL, bed mesh, and Cartographer Touch. KTC Z homing travels around `(174, 168)` at Z10; Touch also uses this center and mesh passes through the area at low Z. Do not run these operations with the holder installed.
2. Home XYZ, finish any required leveling/Touch steps, initialize the toolchanger, confirm tool detection, and clean the nozzles while the holder is removed.
3. Position the toolhead at the confirmed Z55 clearance and out of the installation path, then install the holder. Keep the axes homed. Do not reuse the old fixture's Z12/Z18 values for the new base.
4. Check `CALIBRATION_STATUS`, which reports the current variables. Run attended `CALIBRATE_MOVE_OVER_PROBE` without `PROBE=1` to reach the configured center at or above Z55 without descending to the ball.
5. Run `SEXBOLT_QUERY` with the switch released and manually pressed; continue only if the results are `open` and `TRIGGERED` respectively. Under attendance, confirm the T0 nozzle's ball-center XY and measure the new nozzle contact Z. Set `_CALIBRATION_SWITCH.contact_z` to this measurement and `.probe_z` to a verified probe-start height above contact and no higher than transit Z55. Keep `.z: 55` for XY transit. Confirm these values with `CALIBRATION_STATUS` before automatic probing.
6. After confirming clearance, run attended `CALIBRATE_ALL_OFFSETS`. It heats each nozzle to 150 °C and uses five median samples. Before every tool change, it lifts vertically to at least transit Z55 before leaving the fixture for the dock.
7. Run `CHECK_OFFSETS`, compare repeated complete runs with the saved baseline, and issue `SAVE_CONFIG` only after the result is consistent and plausible. Remove the holder again before any subsequent homing, leveling, mesh, Touch, or printing.

`CALIBRATE_NOZZLE_PROBE_OFFSET` remains blocked so this trial cannot modify the Cartographer offset.

## Nozzle cleaning

`CLEAN_NOZZLE` requires a KTC active tool. It uses the bucket at `(320, -8)`, the silicone brush from X 277 to 309, and cleaning Z 1.2 mm. `PURGE_AND_CLEAN` additionally purges at material temperature before cooling to the cleaning temperature.

## Recovery rules

- Tool mismatch: stop, inspect physical seating and detection pins, then initialize KTC.
- Unhomed machine: do not request a tool drop or dock route.
- TMC electrical fault: power down and inspect wiring; do not clear-and-continue.
- Calibration anomaly: keep raw measurements and compare temperature, nozzle cleanliness, and tool seating before changing offsets.

See [legacy calibration troubleshooting](legacy-calibration-troubleshooting.md) for retired-system error signatures.
