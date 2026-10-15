# StealthChanger Production Operation Guide

[English](huong-dan-he-thong-stealthchanger.en.md) | [Tiếng Việt](huong-dan-he-thong-stealthchanger.md)

## Backend ownership

- KTC-Easy owns tool pickup/dropoff, active-tool state, dock routes, and readonly macros.
- Axiscope owns camera-assisted XY measurement and preliminary relative-Z measurement through microswitch `^PF2`.
- Cartographer owns Z homing, Touch reference, adaptive bed mesh, and resonance sensing.
- OrcaSlicer owns per-filament/process choices such as pressure advance and prime-tower behavior.

Do not combine retired kTAMV, ToolVision, TKC/KCC, or earlier SexBolt procedures with the active Axiscope workflow.

## Before printing

1. Confirm Klipper is ready and no MCU/CAN error is present.
2. Inspect all five docks and verify no tool is partially seated.
3. Confirm the active tool reported by KTC matches the physically mounted tool.
4. Clean the reference nozzle before Cartographer Touch or a switch-Z run.
5. Verify Orca selected the correct five-tool machine, process, and filament mapping.
6. Remove the center-bed switch holder before homing, Cartographer Touch, mesh, or printing.

## Normal print flow

`PRINT_START` receives the initial tool, per-tool temperatures, bed temperature, and material from OrcaSlicer. It hands off any active dryer cycle, homes safely, selects T0 after homing, heats/soaks, performs QGL and Cartographer operations, cleans the nozzle, primes only used tools, and leaves the initial print tool active.

`PRINT_END` retracts, raises Z, drops the tool, parks the empty shuttle, turns off heaters/part fans, clears offsets/mesh, and schedules chamber-fan cooldown.

Use `PAUSE`/`RESUME` instead of ad-hoc tool motion. `RESUME` initializes KTC and verifies tool presence before continuing.

## Tool calibration

Production ownership is: Axiscope camera for XY; the PF2 switch at `(80, -8)` for preliminary relative Z; first-layer tests for final Z. The observed contact range is Z0–2, Axiscope starts at Z3, and Z15 is used for safe XY/tool-change transit. `config_file_path` is intentionally omitted, so Axiscope cannot write production offsets automatically.

1. Remove the holder and keep the build plate unobstructed for `G28`, QGL, bed mesh, and Cartographer Touch. KTC Z homing travels around `(174, 168)` at Z10; Touch also uses this center and mesh passes through the area at low Z. Do not run these operations with the holder installed.
2. Home XYZ, finish any required leveling/Touch steps, initialize the toolchanger, confirm tool detection, and clean the nozzles while the holder is removed.
3. Position the toolhead at Z15 and out of the installation path, then install the holder. Keep the axes homed.
4. Check `CALIBRATION_STATUS`, then run attended `CALIBRATE_MOVE_OVER_PROBE` to reach X80/Y-8 at Z15 without probing.
5. Run `QUERY_ENDSTOPS` with the switch released and manually pressed; continue only when the `Axiscope` line reads `open` and `TRIGGERED`, respectively.
6. After confirming clearance and both switch states, run attended `CALIBRATE_COARSE_Z_OFFSETS CONFIRM=1` with E-stop ready. Without `CONFIRM=1`, the wrapper rejects the request before motion or heating. It heats each nozzle to 150 °C, starts probing at Z3, takes five samples, and reports preliminary relative-Z results only.
7. Use the Axiscope interface on port 3000 for XY, then apply reviewed results manually with a backup. Never use automatic saving for Z. Finalize each Z with a first-layer test and run `CHECK_OFFSETS` for review. Remove the holder before any subsequent homing, leveling, mesh, Touch, or printing.

`CALIBRATE_NOZZLE_PROBE_OFFSET` remains blocked so this trial cannot modify the Cartographer offset.

## Nozzle cleaning

`CLEAN_NOZZLE` runs only with sensor-verified T0, KTC in the `ready` state, XYZ homed, zero live offsets, and no active bed mesh. Supported purge uses `X315 Y10 Z6`; bucket parking remains `X315 Y1 Z6`. After cooling to the warm-wipe window, it moves straight to `X315 Y-5` at Z6, descends through Z3 to contact Z0.2, then sweeps left to X278. The operator measured first silicone contact at X313. There is no Z15 lift in this approved purge-to-breakoff corridor; other approaches and departures use Z15 clearance.

Each wipe pass crosses the full X278–311 inset on all three measured silicone ridges, Y-8/-5/-2, with alternating row order. `MODE=DEEP` defaults to three passes: two warm passes at no more than 170 °C and one final pass at no more than 150 °C. A purging run adds exactly one right-edge breakoff strike before these passes. `PRINT_START` automatically purges T0 by `40 mm` at material temperature when the slicer supplies `T0_TEMP`; this recovers the `10 mm` `PRINT_END` retract and leaves about `30 mm` of output. It does not guess a purge temperature when T0 is unused. `MODE=TOUCH` prohibits purging, requires QGL to be applied, and performs one pass at no more than 150 °C immediately before `CARTOGRAPHER_TOUCH_HOME`.

Manual use must provide the loaded material temperature explicitly, for example `PURGE_AND_CLEAN PURGE_TEMP=230` for the PETG used during commissioning. The operator selected the new default `CLEAN_Z=0.2` after observing insufficient contact at Z1.0; accepted overrides are 0.2–1.0 mm. Observe the new path before relying on it unattended. These coordinates are specific to this printer; new installations must measure their own bed support, brush contact and clearance.

## Recovery rules

- Tool mismatch: stop, inspect physical seating and detection pins, then initialize KTC.
- Unhomed machine: do not request a tool drop or dock route.
- TMC electrical fault: power down and inspect wiring; do not clear-and-continue.
- Calibration anomaly: keep raw measurements and compare temperature, nozzle cleanliness, and tool seating before changing offsets.

See [legacy calibration troubleshooting](legacy-calibration-troubleshooting.md) for retired-system error signatures.
