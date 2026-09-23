# Voron 2.4 StealthChanger — 5-Tool Production Configuration

[English](README.md) | [Tiếng Việt](README.vi.md) | [Active config](config/README.md) | [Documentation](extras/docs/README.md) | [OrcaSlicer profiles](Orca%20Config/README.md)

Production Klipper configuration for a Voron 2.4 350 mm CoreXY with five StealthChanger toolheads. The current system uses KTC-Easy for tool handling, Cartographer V3 for Z homing and bed mesh, and an attended SexBolt `tools_calibrate` trial for relative tool offsets.

## Current production architecture

| Subsystem | Active implementation |
| --- | --- |
| Controller / host | BTT Manta M8P V2.0 + BTT CM4, CAN interface `can0` |
| Toolheads | 5 × BTT EBB36 V1.2, WW BMG extruders, TZ V6 2.0 hotends |
| Toolchanger | KTC-Easy, five rear docks, OptoTap presence sensing |
| Z home / mesh | Cartographer V3 Touch at `(174, 168)`; adaptive 55 × 55 scan mesh |
| Tool XYZ calibration | KTC-Easy SexBolt on `^PF2`; removable center-bed holder at configured `(174, 168)`; verified transit Z55; contact/probe-start heights still require measurement |
| Motion limits | XY 350 mm/s, 7000 mm/s²; Z 80 mm/s, 1000 mm/s² |
| Heated bed | 1000 W AC pad through SSR on `PA1`; sensor `PB0`; maximum 120 °C |
| Cooling | TMC `PF9`, CM4 `PF6`, enclosure/MCU `PF7`, chamber circulation `PF8` |
| Lighting | 40 × WS2812B chamber strip on `PD15` plus 3 LEDs per toolhead |
| Slicer | OrcaSlicer user presets synchronized from `%APPDATA%\OrcaSlicer\user` |

## Current tool map

Offsets below are the values currently persisted in `config/printer.cfg`.

| Tool | CAN UUID | Dock `(X, Y, Z)` | Offset `(X, Y, Z)` |
| --- | --- | --- | --- |
| T0 | `441e1484ac41` | `(30.2, 1.3, 343)` | `(0, 0, 0)` reference |
| T1 | `6475b5b9e028` | `(104, 1.1, 343)` | `(-0.139, -0.341, 0.2465)` |
| T2 | `4ad9d622a836` | `(176, 1.6, 343)` | `(1.095, -0.090, -0.2715)` |
| T3 | `c2465b7c36f8` | `(249.5, 2.5, 343)` | `(0.003, 0.369, -0.2465)` |
| T4 | `28650279df58` | `(321.5, 2.6, 343)` | `(0.213, -0.007, 0.1079)` |

At the operator's request on 2026-09-23, only Z was restored to the saved values from before the 2026-09-22 20:15 change (`7763e82`); current X/Y was retained. The 18:37 SexBolt Z set is no longer active. No print test was performed as part of this rollback.

Do not copy historical offsets from journals, downloaded snapshots, experiments, or retired configurations into production.

## Repository layout

```text
config/                     Deployable Klipper/Moonraker payload
  Printer-Setup/            Hardware and operational macros
  toolchanger/              User-owned KTC config plus installer-owned readonly files
  scripts/                  Install, update, cleanup, and runtime patch tooling
Orca Config/                Active OrcaSlicer user profiles and sync script
extras/docs/                Current documentation and historical-document index
extras/retired-configs/     Configurations no longer loaded by printer.cfg
extras/experiments/         Immutable test evidence
extras/backups/             Timestamped pre-change recovery copies
extras/Nhat-ky-chinh-sua/   Daily engineering journal
```

`config/toolchanger/readonly-configs/` is owned by KTC-Easy. Never edit it manually.

## Deployment

The recommended printer checkout uses sparse clone to avoid downloading historical artifacts:

```bash
git clone --depth=1 --filter=blob:none --sparse \
  https://github.com/IDcrazy123/All-Config-Voron.git ~/All-Config-Voron
cd ~/All-Config-Voron
git sparse-checkout set config
bash config/scripts/install.sh
```

`install.sh` verifies the six KTC-Easy readonly symlinks, validates/applies the reviewed active-tool patch to `tool_crash.py`, backs up the live configuration, deploys repository-owned files while preserving runtime data, and keeps the five newest printer-side install backups.

Axiscope is an external runtime managed by its Moonraker update-manager entry. The repository deployer does not install or modify Axiscope.

For normal updates, push this repository and use **Mainsail → Settings → Machine → Update Manager → All-Config-Voron → Update**. Restart only while the printer is idle.

## OrcaSlicer start G-code

```gcode
PRINT_START TOOL_TEMP={first_layer_temperature[initial_tool]} {if is_extruder_used[0]}T0_TEMP={first_layer_temperature[0]}{endif} {if is_extruder_used[1]}T1_TEMP={first_layer_temperature[1]}{endif} {if is_extruder_used[2]}T2_TEMP={first_layer_temperature[2]}{endif} {if is_extruder_used[3]}T3_TEMP={first_layer_temperature[3]}{endif} {if is_extruder_used[4]}T4_TEMP={first_layer_temperature[4]}{endif} BED_TEMP=[first_layer_bed_temperature] TOOL=[initial_tool] MATERIAL={filament_type[initial_tool]}
```

The active Orca profile inventory and synchronization workflow are documented in [`Orca Config/README.md`](Orca%20Config/README.md).

## Main operator commands

| Area | Commands |
| --- | --- |
| Print lifecycle | `PRINT_START`, `PRINT_END`, `PAUSE`, `RESUME`, `CANCEL_PRINT`, `G32` |
| Nozzle service | `CLEAN_NOZZLE`, `PURGE_AND_CLEAN`, `PRIME_LINES` |
| Filament drying | `START_DRYER`, `STOP_DRYER`, `DRYER_STATUS` |
| Calibration/reporting | `SEXBOLT_QUERY`, `CALIBRATE_MOVE_OVER_PROBE`, `CALIBRATE_ALL_OFFSETS`, `CALIBRATION_STATUS`, `CHECK_OFFSETS` |
| Motion/thermal tests | `TEST_SPEED`, `TEST_Z_SPEED`, `MEASURE_TOOL_HEATUP` |
| Lighting/fans | `LIGHTS_ON`, `LIGHTS_OFF`, `BED_FAN_ON`, `BED_FAN_OFF` |

The attended SexBolt trial uses the upstream defaults `spread: 5.0` and `lower_z: 0.5`. `_CALIBRATION_SWITCH.z: 55` is the operator-confirmed transit clearance. By default, `CALIBRATE_MOVE_OVER_PROBE` travels to the configured center at or above Z55 without probing. The new holder's `contact_z: -1` and `probe_z: -1` remain unmeasured sentinels: `CALIBRATE_ALL_OFFSETS` rejects the run before tool selection, heating, or movement until both are valid. Its internal `PROBE=1` approach may descend below transit height only after these height checks pass. `CALIBRATION_STATUS` reports the configured values. `CALIBRATE_NOZZLE_PROBE_OFFSET` remains blocked so the trial cannot rewrite the Cartographer probe offset.

Before each tool change, the calibration sequence lifts vertically to at least Z55 so the docking route leaves the fixture at transit clearance.

Remove the holder before `G28`, QGL, bed mesh, Cartographer Touch, or printing: these operations use or cross the center of the bed. Home with the plate unobstructed, then position the toolhead at the confirmed Z55 clearance and outside the installation path before installing the holder. Confirm the T0 nozzle is centered over the ball and measure the contact/probe-start heights before enabling calibration. See the [tool calibration procedure](extras/docs/huong-dan-he-thong-stealthchanger.en.md#tool-calibration).

## Safety and rollback

- Treat this repository as production firmware configuration.
- Back up every `.cfg`, `.conf`, or `.sh` before editing.
- Do not change PID values, motor current, motion limits, heater limits, or probe geometry without measured evidence.
- Do not deploy while printing or while a tool change is in progress.
- Every `install.sh` run creates a timestamped printer-side snapshot under `~/printer_data/config_backups/`.

Use [`extras/docs/legacy-calibration-troubleshooting.md`](extras/docs/legacy-calibration-troubleshooting.md) to recognize failure signatures from retired ToolVision, kTAMV, TKC/KCC, earlier SexBolt attempts, and Axiscope trials.

## Credits

This configuration builds on [Voron Design](https://vorondesign.com/), [StealthChanger](https://stealthchanger.com/), [KTC-Easy](https://github.com/jwellman80/klipper-toolchanger-easy), [Axiscope](https://github.com/nic335/Axiscope), [Cartographer](https://cartographer3d.com/), [Mainsail](https://mainsail.xyz/), and [Klippain Shake&Tune](https://github.com/Frix-x/klippain-shaketune).
