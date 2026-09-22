# Active Klipper Configuration Payload

[English](README.md) | [Tiếng Việt](README.vi.md) | [Project overview](../README.md)

This directory is the repository-owned payload deployed to `~/printer_data/config`. Markdown is excluded during deployment. Runtime output, local backups, generated calibration data, and KTC-Easy readonly links are preserved by `scripts/install.sh`.

## Include chain

`printer.cfg` loads the active modules in this order:

```ini
[include mainsail.cfg]
[include toolchanger/readonly-configs/toolchanger-include.cfg]
[include Printer-Setup/calibration-probe.cfg]
[include Printer-Setup/hardware.cfg]
[include Printer-Setup/fans-leds.cfg]
[include Printer-Setup/input-shaper.cfg]
[include Printer-Setup/nozzle-clean.cfg]
[include Printer-Setup/prime-lines.cfg]
[include Printer-Setup/print-macros.cfg]
[include Printer-Setup/filament-dryer.cfg]
[include Printer-Setup/test-speed.cfg]
[include Printer-Setup/tool-temp-bench.cfg]
[include Printer-Setup/tool-crash.cfg]
```

The attended SexBolt trial uses KTC-Easy `[tools_calibrate]` in `Printer-Setup/calibration-probe.cfg`. Axiscope remains installed externally but its Klipper section is disabled because both backends claim the same PF2 calibration input and cannot coexist.

## Ownership

| Path | Owner / purpose |
| --- | --- |
| `printer.cfg` | Git/user; main includes, kinematics, limits, and live `SAVE_CONFIG` values |
| `Printer-Setup/*.cfg` | Git/user; probe, hardware, fans, LEDs, and operational macros |
| `toolchanger/toolchanger-config.cfg` | Git/user; dock workflow, input-shaper hook, and compatibility overrides |
| `toolchanger/tools/T0.cfg` … `T4.cfg` | Git/user; EBB36, extruder, fans, sensors, and dock coordinates |
| `toolchanger/readonly-configs/` | KTC-Easy installer; never edit manually |
| `scripts/` | Git/user; deploy, update, cleanup, and reviewed runtime patch |
| `moonraker.conf` | Git/user; API and update-manager definitions |

## Authoritative hardware values

| Function | Active value |
| --- | --- |
| Main MCU | CAN UUID `19b203d75137` |
| Cartographer | CAN UUID `da13d909ce34`; Touch home at `(174, 168)` |
| SexBolt calibration switch | `^PF2`; removable center-bed holder at configured `(174, 168)`; upstream defaults `spread: 5.0`, `lower_z: 0.5`; transit Z55 confirmed; contact/probe-start Z unmeasured |
| XY | X `PE6`/`PF0`, Y `PE2`/`PF1`; 350 mm/s, 7000 mm/s² |
| Z | `PG9`, `PB4`, `PG13`, `PB8`; 80 mm/s, 1000 mm/s² |
| Bed | Heater `PA1`, sensor `PB0`, maximum 120 °C |
| Chamber | Sensor `PB1`, circulation fan `PF8` |
| Electronics cooling | TMC `PF9`, CM4 `PF6`, enclosure/MCU `PF7` |
| Lights | Chamber strip `PD15`; tool LEDs on each EBB36 `PD3` |

## Calibration ownership

- Cartographer: Z homing, Touch reference, adaptive bed mesh, and shuttle ADXL345.
- SexBolt `tools_calibrate`: attended relative XYZ measurement on PF2.
- `printer.cfg` `SAVE_CONFIG`: authoritative T1–T4 XYZ offsets.
- `_CALIBRATION_SWITCH.z: 55` is the operator-confirmed transit height. Default `CALIBRATE_MOVE_OVER_PROBE` travels to the center at or above Z55 without probing. `contact_z: -1` and `probe_z: -1` mark the contact and probe-start heights as unmeasured. `CALIBRATE_ALL_OFFSETS` blocks before tool selection, heating, or movement until valid heights are configured; internal `PROBE=1` descent requires the same height checks. Homing/toolchanger checks still apply. `CALIBRATION_STATUS` reports the configured values. Probe-offset calibration remains blocked.
- kTAMV, ToolVision, TKC, KCC, Axiscope, and earlier SexBolt configurations are historical references only.

Before every `SELECT_TOOL` in the calibration sequence, `_CALIBRATE_SAFE_TRANSIT` lifts vertically to at least the configured transit Z55; it does not move XY.

The holder must be removed before `G28`, QGL, bed mesh, Cartographer Touch, or printing because their paths overlap the bed center. Home with an unobstructed plate, position the toolhead at the confirmed Z55 clearance and outside the installation path, then install the holder. Confirm the T0 nozzle's actual ball-center XY and measure contact/probe-start Z before enabling automatic probing. The former front-mounted fixture's heights do not apply to this holder.

## Deployment behavior

`scripts/install.sh` refuses deployment if the six KTC-Easy readonly links are missing or broken. It backs up the live config, preserves machine-local runtime paths, applies the reviewed `tool_crash` patch when necessary, and retains five printer-side install backups.

The live machine may retain the externally managed Axiscope service and update-manager entry, but the service is not the active Klipper calibration backend during this trial.

Run configuration deployment only while the printer is idle, then restart Moonraker/Klipper and verify `CALIBRATION_STATUS`, `CHECK_OFFSETS`, heaters, fans, homing, and tool detection before printing.
