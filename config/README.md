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

`Printer-Setup/calibration-probe.cfg` activates Axiscope as the only `probe_multi_axis` backend. Axiscope owns camera-assisted XY; the removable PF2 switch provides coarse relative Z; first-layer tests own final production Z.

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

## Individual CFG sharing

Use the [individual-file sharing guide](../extras/docs/sharing-cfg-files.md) to send an existing feature CFG without this full payload. All 18 user-owned CFGs now declare prerequisites and local adaptation points. Settings stay at their native owners; no global EDIT HERE/profile file is required. Benchmark/prime/cleaner/dryer can omit optional project helpers under their declared contracts. Hardware/lifecycle/calibration references retain their documented integration requirements and open issues.

## Adaptation inputs

Use the [machine adaptation guide](../extras/docs/machine-adaptation.md) before copying this payload. Existing variables and native sections own their adjustment points; measured pins, offsets, docks, and heater/motion limits remain in their original files. A safe preview is `VORON_DEPLOY_DRY_RUN=1 bash config/scripts/install.sh` from the repository root on the idle target host.

## Authoritative hardware values

| Function | Active value |
| --- | --- |
| Main MCU | CAN UUID `19b203d75137` |
| Cartographer | CAN UUID `da13d909ce34`; Touch home at `(174, 168)` |
| Coarse-Z calibration switch | `^PF2`; holder at `(80, -8)`; observed contact range Z0–2; Axiscope starts at Z3 and uses Z15 transit |
| XY | X `PE6`/`PF0`, Y `PE2`/`PF1`; 350 mm/s, 7000 mm/s² |
| Z | `PG9`, `PB4`, `PG13`, `PB8`; 80 mm/s, 1000 mm/s² |
| Bed | Heater `PA1`, sensor `PB0`, maximum 120 °C |
| Chamber | Sensor `PB1`, circulation fan `PF8` |
| Electronics cooling | TMC `PF9`, CM4 `PF6`, enclosure/MCU `PF7` |
| Lights | Chamber strip `PD15`; tool LEDs on each EBB36 `PD3` |

## Calibration ownership

- Cartographer: Z homing, Touch reference, adaptive bed mesh, and shuttle ADXL345.
- Axiscope: camera-assisted XY measurement and attended coarse relative-Z measurement on PF2.
- `printer.cfg` `SAVE_CONFIG`: authoritative T1–T4 XYZ offsets.
- `_CALIBRATION_SWITCH.z: 15` is the safe XY/tool-change transit height. Axiscope starts at Z3 over the observed Z0–2 contact range. After checking both PF2 states with `QUERY_ENDSTOPS`, use `CALIBRATE_COARSE_Z_OFFSETS CONFIRM=1`; it reports preliminary Z only. Axiscope config writes and legacy KTC save helpers are disabled; XY changes are reviewed and applied manually, while final Z always comes from first-layer tests. The retired `CALIBRATE_ALL_OFFSETS` and probe-offset calibration remain blocked.
- kTAMV, ToolVision, TKC, KCC, and earlier SexBolt configurations are historical references only.

Before every tool change in the calibration sequence, `_CALIBRATE_SAFE_TRANSIT` lifts vertically to at least the configured transit Z15; it does not move XY.

The holder must be removed before `G28`, QGL, bed mesh, Cartographer Touch, or printing. Home with an unobstructed plate, raise to Z15, install the holder, then verify X80/Y-8 and the PF2 switch state before attended probing.

## Deployment behavior

`scripts/install.sh` refuses deployment if the six KTC-Easy readonly links are missing or broken. It backs up the live config, preserves machine-local runtime paths, applies the reviewed `tool_crash` patch when necessary, and preserves all existing install backups and destination-only files. It checks the same printer through Moonraker before writing and fails if the required crash runtime/patch is missing.

The Axiscope service and Klipper extra are externally managed through Moonraker; repository deployment changes only their `.cfg` integration.

Run configuration deployment only while the printer is idle, then restart Moonraker/Klipper and verify `CALIBRATION_STATUS`, `CHECK_OFFSETS`, heaters, fans, homing, and tool detection before printing.
