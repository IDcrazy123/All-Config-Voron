# Adapting the reusable logic to another machine

This repository combines reusable macros with the measured profile of one Voron 2.4 StealthChanger. Use the table below as an input worksheet. Change the owning settings instead of searching through every G-code line. The current changes preserve this printer's pins, PID, offsets, docks, motor currents and motion limits.

## What can be reused

- Print temperatures come from the slicer, including only the tools used in that job.
- Tool loops enumerate KTC's registered `tool_numbers`. Selected helpers map numbers through the corresponding `tool_names` list; numbers are not assumed to be list indexes.
- Print-end/cancel fan and extruder shutdown use the selected tool's configured `fan` and `extruder` fields.
- The heat benchmark reads the selected heater's `max_temp` and shares the cleaning station's purge XY and transit Z. It rejects printing, paused, drying and invalid-control states. Print start and dryer start also reject an active benchmark.
- Prime-line X slots shorten automatically with bed width and scale extrusion with line length. Invalid initial-tool temperatures and an impossible X slot layout abort before prime commands.
- Soak durations are editable variables with the same production defaults; a per-job `SOAK` remains the highest-priority override.

These improvements cover the helpers described here. Other upstream routines, particularly Axiscope's return to T0, still require a reference T0. A different probe architecture, a tool without an extruder, a different dock mechanism, or multiple toolchangers needs a separate integration review.

## Machine input worksheet

| Input | Where to change | How to choose it |
| --- | --- | --- |
| MCU identity and CAN interface | `config/Printer-Setup/hardware.cfg`, `config/toolchanger/tools/Tn.cfg` | Enter UUIDs discovered on your own machine; match the physical CAN topology. |
| Motor/driver/endstop pins and directions | `hardware.cfg`, `Tn.cfg` | Use board schematics and verified wiring; test one axis at a time while attended. |
| Travel limits | `hardware.cfg` `[stepper_*]`; `printer.cfg` `[printer]` | Measure usable travel and clearance; do not infer limits from nominal bed size. |
| Extruder/heater/fan mapping | Each `[tool ...]` and associated extruder/fan sections | Set `tool_number`, `extruder`, `fan`, `detection_pin`; provide the matching `Tn` macro. A generic fan is required by these shutdown helpers. |
| Number of tools | KTC `tools/T*.cfg` includes plus Orca machine arrays/start G-code | Keep only your active definitions in the include glob; archive unused definitions outside it. Do not just change a UI count. Keep T0 for the existing calibration/print workflow. |
| Hotend/bed sensors and limits | Extruder sections; `[heater_bed]` | Use actual sensor types and approved hardware limits. Calibrate PID on your machine. The benchmark follows these configured limits. |
| Dock positions | Each tool's `params_park_x/y/z` | Align each dock physically. These are nozzle/G-code coordinates, not percentages of the bed. |
| Dock paths | `toolchanger-config.cfg` `params_pickup_path/dropoff_path` | Measure the mechanism's relative path; review every point and rounded transit. |
| Dock approach corridor | `params_safe_y`, `params_close_y` | Both are absolute G-code Y values. `close_y` is not a distance from `safe_y`. |
| Probe geometry, mesh and QGL | `calibration-probe.cfg`, `print-macros.cfg` | Enter probe offsets, probe-coordinate mesh bounds, nozzle reference position, QGL corners and points for your bed. Check resulting nozzle travel. |
| Tool XYZ offsets | Own machine's reviewed calibration data | Measure XY relative to T0 and finalize Z using first-layer tests. Do not import this machine's saved offsets. |
| Cleaning station | `CLEAN_NOZZLE` variable block in `nozzle-clean.cfg` | Measure `purge_x/y/z`, `safe_z`, `approach_z`, pad XYZ inset, and speeds together. The thermal benchmark follows purge XY and safe Z. |
| Brush contact limits | `CLEAN_NOZZLE`, `_CLEAN_NOZZLE_WIPE_PATH` guards | The current `0.5..1.0 mm` contract is measured for this pad. Review both guards for a different brush; changing only `default_clean_z` is insufficient. |
| Prime lines | `PRIME_LINES` variable block in `prime-lines.cfg` | Choose a clear strip of the bed; set margin/length/gap, Y/pass spacing, prime/travel Z, extrusion and retract amounts. Review purge cross-section against nozzle limits. |
| Heat soak | `_PRINT_START_HEAT_SOAK` variables | Tune after observing your bed mass/enclosure. Defaults: PLA/TPU 30 s, PETG 60 s, ABS-family 90 s, hot-bed fallback 90 s. |
| Dryer operating point | `START_DRYER MATERIAL=... BED=... CHAMBER=... TIME=... FAN=... PARK=...` | Override the current enclosure presets using material/spool limits and measured chamber response. `FAN` is 0..1. `PARK=0` avoids the fixed parking path. |
| Dryer parking | `START_DRYER` park block in `filament-dryer.cfg` | Current target is X175/Y310 and at least Z200, clamped to Z max. Measure a safe alternative; a smaller Z max does not guarantee spool clearance. |
| Filament runout park | `_FILAMENT_RUNOUT_PAUSE` in `print-macros.cfg` | Current explicit `PAUSE X=180 Y=10 Z_MIN=30` overrides Mainsail park defaults. Change that call for a different bed. |
| Pause/retract/resume defaults | `_CLIENT_VARIABLE` in `fans-leds.cfg` | Uncomment and fill the documented variables for your park/retract/speeds; retain the project hooks. Do not edit `mainsail.cfg`. |
| LEDs | `[neopixel ...]` sections and `_SET_TOOL_LED` | The helper expects `Tn_LED`, status index 1 and work-light indices 2/3. Adapt its name/index mapping for a different layout. States use the last executed setter, with no priority arbiter. |
| Bed/chamber fan names | `fans-leds.cfg`, dryer/start/end calls | Current logic expects `bed_fan`. Retain this logical name or update every caller as a group. |
| Input shaper | `input-shaper.cfg`, tool overrides, KTC `after_change_gcode` | Use your own resonance measurements. Audit the effective damping as well as frequency; see open finding A07. |
| Calibration switch | `[axiscope]` and `_CALIBRATION_SWITCH` | Enter actual pin, XY/contact Z and transit clearance. Keep report `probe_z = zswitch_z_pos + lift_z`; there are two owners to update. |
| Camera | `crowsnest.conf` | Replace the device-by-ID path, modes/resolution, port and mains-frequency setting; check compatibility with your host/camera. |
| Host integrations | `moonraker.conf`, KlipperScreen and runtime installs | Keep only installed services/update-manager paths; adapt access ranges and UI language. Local IPs and camera IDs are machine inputs. |
| Slicer | `Orca Config/` | Change printer host/bed/tool arrays, base-preset inheritance and compatibility; calibrate filament flow, PA and MVS on your hardware. |

## Simple changes without editing macro internals

For an exact 5-minute soak on one job, add `SOAK=300` to the existing `PRINT_START` call. For a persistent machine-specific ABS soak, change only the relevant variable:

```ini
[gcode_macro _PRINT_START_HEAT_SOAK]
variable_abs_soak: 300
```

Edit the existing section rather than adding a duplicate owner. The current duration variables replace the old constants; changing one does not change heater or motion safety limits.

For the heat benchmark, specify `TOOL=<registered number>` and `PARK_BUCKET=0` to measure a docked tool without station travel. Its target must stay below that tool's configured `max_temp`.

For a different prime strip, start with the existing `PRIME_LINES` variable block. The geometry must also leave clearance for the final sideways wipe. Y positions are clamped, so overly large pass spacing can overlap lines; X slot validation is not a physical collision check. Sliced objects/adaptive mesh can occupy the same strip: reserve it in the slicer and verify the preview.

For a different cleaning station, edit its coordinates once in `CLEAN_NOZZLE`; the benchmark reuses purge XY/transit Z. The cleaner remains T0-only because its contact path is tied to that reference nozzle and cleared offsets/mesh. Do not remove those checks to make it appear universal.

## Importing a machine profile

1. Work in your own fork or local copy. Record board, probe, dock and heater details using the worksheet.
2. Replace MCU/pin/travel/dock inputs before importing calibration. Keep heater verification enabled and preserve upstream-owned readonly links.
3. Generate PID, probe models, twist compensation, mesh, tool offsets and shaper results for your machine. This repository's `printer.cfg` `SAVE_CONFIG` block contains data belonging to this printer. Do not copy that block as your calibration.
4. Adapt Orca's per-extruder arrays and `Tn_TEMP` clauses, including every used tool. Renaming the printer also requires reviewing `compatible_printers` and inherited presets.
5. Install compatible KTC-Easy, Cartographer, Axiscope, ShakeTune and the reviewed `tool_crash` runtime. The deployer only integrates their configuration and applies its small crash patch; it does not install those projects.
6. Run offline checks, preview deployment, review its file changes, and commission homing/detection/heaters/docks/cleaning/first-layer behavior while attended. Offline rendering cannot prove clearance or wiring.

## Preview and deploy

On the idle target host, from the repository root:

```bash
VORON_DEPLOY_DRY_RUN=1 bash config/scripts/install.sh
```

For a nonstandard `printer_data` layout:

```bash
VORON_CONFIG_DIR=/absolute/path/to/printer_data/config \
VORON_BACKUP_ROOT=/absolute/path/to/printer_data/config_backups \
VORON_MOONRAKER_URL=http://127.0.0.1:7125 \
VORON_DEPLOY_DRY_RUN=1 bash config/scripts/install.sh
```

The URL must describe the same printer as the destination. Unavailable/unauthorized/unknown state fails closed. Remove the dry-run assignment only after reviewing the payload while idle. The check is an observation, not an exclusive deployment lock; keep new jobs/manual motion stopped until deployment finishes.

The deployer preserves destination-only files, all existing backups and KTC readonly links. It still replaces matching repository-owned filenames, including `printer.cfg` and host `.conf` files: first-time adaptation must be complete before deployment. A customized machine should update from its own fork; `update.sh` supports an `ARCHIVE_URL` override. Re-running the original archive updater can overwrite your custom settings.

`cleanup-voron.sh --apply` is a separate destructive maintenance command. It still removes listed old backup directories; use its default dry run and review the list before deciding to run it. The installer no longer runs that cleanup automatically.

## Next architecture step

Introduce a separately versioned generic macro payload and a small explicit machine profile only after these contracts are tested. The profile should own reference tool, station bounds, park/clearance settings, logical fan/LED mappings and optional feature flags. MCU/pin/PID/limits/calibration should retain distinct hardware owners, with no duplicate options in `SAVE_CONFIG` or included files. Feature flags must validate dependencies and disable the entire relevant workflow, including `PRINT_START` callers. Simply commenting out an include is insufficient.

See the [audit and follow-up plan](project-audit-2026-10-09.md). Klipper's [command-template documentation](https://www.klipper3d.org/Command_Templates.html) explains why helpers are rendered after waits/tool changes, and its [configuration reference](https://www.klipper3d.org/Config_Reference.html) defines the standard hardware options.
