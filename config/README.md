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

Axiscope is a Klipper extra and external web service; it does not require a repository `.cfg` include beyond the `[axiscope]` section in `Printer-Setup/calibration-probe.cfg`.

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
| Axiscope Z switch | `^PF2`; `(80, -5, 8)`; `lift_z: 2`; safe tool-change height 15 mm |
| XY | X `PE6`/`PF0`, Y `PE2`/`PF1`; 350 mm/s, 7000 mm/s² |
| Z | `PG9`, `PB4`, `PG13`, `PB8`; 80 mm/s, 1000 mm/s² |
| Bed | Heater `PA1`, sensor `PB0`, maximum 120 °C |
| Chamber | Sensor `PB1`, circulation fan `PF8` |
| Electronics cooling | TMC `PF9`, CM4 `PF6`, enclosure/MCU `PF7` |
| Lights | Chamber strip `PD15`; tool LEDs on each EBB36 `PD3` |

## Calibration ownership

- Cartographer: Z homing, Touch reference, adaptive bed mesh, and shuttle ADXL345.
- Axiscope: attended camera-crosshair XY alignment and PF2 microswitch tool Z measurement.
- `printer.cfg` `SAVE_CONFIG`: authoritative T1–T4 XYZ offsets.
- Legacy KTC `tools_calibrate` commands are explicitly blocked in `toolchanger-config.cfg`.
- kTAMV, ToolVision, TKC, KCC, and SexBolt configurations are historical only.

## Deployment behavior

`scripts/install.sh` refuses deployment if the six KTC-Easy readonly links are missing or broken. It backs up the live config, preserves machine-local runtime paths, applies the reviewed `tool_crash` patch when necessary, and retains five printer-side install backups.

The live machine must already have Axiscope installed and managed by the `[update_manager axiscope]` entry in `moonraker.conf`; this repository does not install that service.

Run configuration deployment only while the printer is idle, then restart Moonraker/Klipper and verify `CALIBRATION_STATUS`, `CHECK_OFFSETS`, heaters, fans, homing, and tool detection before printing.
