# Sharing individual CFG files

Implemented in the repository on 2026-10-09; not deployed or physically tested on the printer. This guide records the current implementation of the [revised proposal](stealthchanger-sharing-proposal.md).

Send the **existing complete CFG** for a feature. The receiver keeps their existing Klipper/KTC setup, includes that one file once, and edits values at their current native section or macro. No global parameter file, EDIT HERE block, generated package, or renamed macro framework is required.

Each of the 18 user-owned CFGs now describes its scope and prerequisites at the top. Local comments explain coordinates, units, calibration ownership and values that must change together. KTC readonly files and upstream `mainsail.cfg` remain untouched.

## Receiving a file

1. Back up the receiver's configuration. Read the file header, including required plugins and command names.
2. Copy the entire file, retaining its helpers and delayed callbacks. Add one include with its actual relative path, for example `[include tool-temp-bench.cfg]` when placed beside `printer.cfg`.
3. Check section/macro/pin conflicts with existing configuration. Merge an existing owner rather than defining another copy; do not include a tool both explicitly and through a tools glob.
4. Adapt the values identified below **where they already live**. Retain the receiver's verified PID, tool offsets, motion limits and current settings. A hardware reference containing another machine's pins/UUIDs is not ready until reconciled with the actual machine.
5. Check configuration loading while idle. Verify sensors and tool registry before attended feature tests. Native axis bounds do not prove that a route clears docks, clips, spools or printed objects.

Include order cannot substitute for a missing plugin or command. These files do not install KTC, Cartographer, Axiscope, ShakeTune, or `tool_crash`.

## Feature files

| Existing file | Minimum existing setup | Receiver's local changes / use |
| --- | --- | --- |
| [tool-temp-bench.cfg](../../config/Printer-Setup/tool-temp-bench.cfg) | KTC registry/tool heaters, `print_stats`, `pause_resume`, `respond` | No tool-count edit. Use `TOOL`, `START_TEMP`, `TARGET_TEMP` per call. Without cleaner, default parking is disabled. `PARK_BUCKET=0` also avoids station reads. Optional explicit `PARK_X/Y/Z` are G-code mm, with all three required. |
| [prime-lines.cfg](../../config/Printer-Setup/prime-lines.cfg) | KTC registry, `Tn`, tool-aware `M104/M109`, configured extruders and `respond` | Existing variables own clear bed geometry, first-layer height, extrusion and feedrates. Own PRINT_START prepares homing/leveling/mesh/offsets and passes the used `Tn_TEMP` values. Count/order come from the registry, including sparse numbers. |
| [nozzle-clean.cfg](../../config/Printer-Setup/nozzle-clean.cfg) | KTC ready with T0/`extruder`/generic part fan, `bed_mesh`, native safety state, `respond`; QGL applied for TOUCH | Measure bucket/pad/inset/clearance at existing variables. Contact-Z and temperature guards are part of this silicone-pad/Cartographer method. Manual calls require idle state. A receiver's pre-extrusion PRINT_START may pass `STARTING=1`; it never overrides installed `_PRINT_STATE` or native pause. |
| [filament-dryer.cfg](../../config/Printer-Setup/filament-dryer.cfg) | KTC registry/`M104`/`UNSELECT_TOOL`, bed heater, `fan_generic bed_fan`, native safety state, `respond` | Rename all fan/sensor references in this file if required. Choose `BED/CHAMBER/FAN/TIME` per call. `PARK=0` avoids this machine's dock/park moves. `CHAMBER=0` permits bed-only regulation; positive chamber/humidity targets require real feedback. |
| [test-speed.cfg](../../config/Printer-Setup/test-speed.cfg) | Modern Klipper runtime limits, native safety state and `respond`; QGL if installed | Call parameters select patterns/height/speed within native caps. Already homed/leveled, zero offsets, clear bed/routes. Runtime limits restore on normal completion; an interruption may skip restoration. |
| [tool-crash.cfg](../../config/Printer-Setup/tool-crash.cfg) | Installed `tool_crash`, KTC presence inputs, Mainsail PAUSE_BASE/RESUME contract, native safety state and `respond` | Existing detector values are retained. Verify detection-pin polarity in each tool file. Another pause implementation needs adaptation in this handler. Review the receiver's CANCEL_PRINT separately: this handler's no-XYZ pause does not make cancel parking safe. |

`print_stats` is provided by the receiver's existing `[virtual_sdcard]` setup. Install `[pause_resume]` and `[respond]` only if they are not already configured. Optional LEDs, dryer/benchmark state and `_PRINT_STATE` are detected before access in the feature paths where applicable; native print/pause checks remain mandatory.

Examples below start real operations; temperatures and geometry must match the receiver's hardware/material:

```gcode
MEASURE_TOOL_HEATUP TOOL=1 START_TEMP=150 TARGET_TEMP=220 PARK_BUCKET=0
PRIME_LINES INITIAL_TOOL=1 T0_TEMP=220 T1_TEMP=220
CLEAN_NOZZLE MODE=TOUCH TEMP=150 CLEAN_Z=1.0 WIPES=1
START_DRYER MATERIAL=PETG BED=70 CHAMBER=0 TIME=240 FAN=0.5 PARK=0
```

Benchmark parking requires the selected tool mounted, XYZ homed and zero live offsets. Without a cleaner, an optional station can be passed as `PARK_BUCKET=1 PARK_X=... PARK_Y=... PARK_Z=...`. Bounds checks reject impossible travel but the owner must verify the whole route. With the cleaner installed, the current station remains the default source.

Dryer `PARK=1` retains the production Z200 then KTC docking and X175/Y310 parking. Change the preflight bounds check **and** matching moves if adapting it. Presets describe this enclosure/bed; different machines should use suitable overrides. Explicit `FAN=0` is now honored during startup and timer regulation. The dryer checks the receiver's bed maximum; its overheat branch cannot raise a custom low bed target.

Benchmark and dryer yield their callbacks when print/pause state takes ownership. They stop their own timer without turning off print-owned heat/fans. They cannot detect arbitrary foreign macros that operate while reporting an idle printer or reuse the same heater target. Stop these operations before unrelated calibration/heating routines. Elapsed durations accumulate callback ticks; scheduling delays can extend them. STOP during a benchmark wait prevents its later measurement continuation, but cannot remove commands already queued by Klipper.

## Hardware and integration references

These files can be sent individually for reuse/review, but their headers explicitly identify dependencies and retained machine-specific behavior. They are not advertised as universal one-include features.

| Existing file | What to reconcile at the existing owners |
| --- | --- |
| [T0](../../config/toolchanger/tools/T0.cfg), [T1](../../config/toolchanger/tools/T1.cfg), [T2](../../config/toolchanger/tools/T2.cfg), [T3](../../config/toolchanger/tools/T3.cfg), [T4](../../config/toolchanger/tools/T4.cfg) | One file per physical tool. MCU UUID/pins, extruder/fan/sensor/LED names, motor/gearing/current, detection polarity and measured dock XYZ. Tool number is independent of the registered extruder suffix. Receiver provides its own heater control/PID and measured offsets; these are saved elsewhere on this machine. Runout has a local active-tool-only PAUSE fallback when the project handler is absent. |
| [toolchanger-config.cfg](../../config/toolchanger/toolchanger-config.cfg) | Existing KTC/rounded_path include chain and command overrides. Relative pickup/dropoff paths, absolute safe/close Y, speeds, homing settings and calibration aliases. LEDs, custom Tn color variables and project state are optional in change hooks. Dock paths remain measured mechanical inputs. |
| [hardware.cfg](../../config/Printer-Setup/hardware.cfg) | Manta/Cartographer UUIDs and every native pin/stepper/driver/sensor/bed section; reconcile against actual wiring/specifications. Retain the receiver's own travel and bed PID. |
| [fans-leds.cfg](../../config/Printer-Setup/fans-leds.cfg) | Fan wiring/controllers, LED chains and Mainsail client/RESUME/cancel integration. Owns `_PRINT_STATE`. Dynamic tool enumeration does not make different LED names/index layouts compatible. Includes startup LED/controller behavior. |
| [input-shaper.cfg](../../config/Printer-Setup/input-shaper.cfg) | Own measured frequencies/type/damping, actual accelerometer and accessible probe point. Omit `[shaketune]` and its commands when that plugin is absent. Check KTC inherited damping too. |
| [calibration-probe.cfg](../../config/Printer-Setup/calibration-probe.cfg) | Actual Cartographer/Axiscope installation, coil offsets, mesh/probe pins and switch geometry. Synchronize Axiscope switch geometry with `_CALIBRATION_SWITCH` in toolchanger-config. Backend sequencing remains under review. |
| [print-macros.cfg](../../config/Printer-Setup/print-macros.cfg) | Full T0/Cartographer/QGL/cleaner/prime/LED/bed-fan/Mainsail lifecycle integration. Supply equivalent existing commands before copying; retain the receiver's probe/first-layer procedure. Benchmark is optional. END/CANCEL and EXCLUDE_OBJECT issues remain open. |
| [printer.cfg](../../config/printer.cfg) | Complete entrypoint/include graph and machine calibration reference. Send the feature CFG instead for a single-feature request. Never import its SAVE_CONFIG PID/offsets as another machine's calibration. |

## Verification and remaining limits

Offline tests cover isolated feature prerequisites, 2/5/6 and sparse tool registries, custom extruder/fan mappings, missing optional helpers, park bounds, contact guards, native print/pause refusal, timer ownership, runout routing and supported diagnostic limits. They also compare all existing non-G-code options across the 18 CFGs, saved calibration and representative motion/heat commands against the pre-change backup.

Run `python -m unittest discover -s extras/tests -v`. On Windows, set `VORON_TEST_BASH` to the existing Git Bash executable for installer tests. Fixtures model template expansion and variable writes, not real firmware loading, motion, concurrency or thermal dynamics. The active include graph's templates are compiled separately by the same suite.

TEST_Z_SPEED now uses supported global `VELOCITY/ACCEL` for pure Z cycles while the native CoreXY Z caps continue to apply; unsupported `Z_VELOCITY/Z_ACCEL` parameters were removed. See the official [SET_VELOCITY_LIMIT commands](https://www.klipper3d.org/G-Codes.html#set_velocity_limit) and [toolhead runtime status](https://www.klipper3d.org/Status_Reference.html#toolhead).

Still open from the [machine/code audit](project-audit-2026-10-09.md): END/CANCEL max-Z and coordinate-frame handling, crash cancel parking, Axiscope's return-to-T0 sequence, inherited KTC shaper damping and multi-tool EXCLUDE_OBJECT. T1 CAN is already fixed per the operator. None of those open issues is claimed fixed by adding sharing comments.
