# TKC installation and supervised Z commissioning

Reviewed source: [Tool-Klipper-Calibration f68dc99](https://github.com/IDcrazy123/Tool-Klipper-Calibration/tree/f68dc99).
Host: `voron@192.168.1.43`. Cartographer plugin: 1.9.0, existing V3 hardware.
Full five-tool Z repeatability is **not qualified**. See the
[measured results and defects](../experiments/tkc-f68dc99-20260908/REPORT.vi.md).

## Installed layout

- Source and isolated Python: `~/Tool-Klipper-Calibration` and its `env/`.
- User service: `systemctl --user status tool_calibrator.service`; localhost port 8090.
- Klipper include: `[include tool_calibrator/tool_calibrator.cfg]`.
- Editable master: `~/printer_data/config/tool_calibrator/tool_calibrator.cfg`.
- Machine-owned offsets: `tool_calibrator/tool_offsets.cfg`. Initially contains only
  production XY, copied unchanged for compensated Z positioning.
- Production Z remains in `printer.cfg` SAVE_CONFIG. No measured Z was applied.
- Moonraker update manager is configured for the user service.

The old inactive checkout and leftover configuration were archived outside active
config before a fresh clone and `./scripts/install.sh --user-service`. The upstream
installer created the service, Python environment, Klipper links and configuration.
The include and Moonraker update block were added explicitly as instructed by its output.
The source checkout itself has no local patches.

Machine adaptations: nozzle Touch reference, `carto_probe_x: 174`, `carto_probe_y: 168`,
`touch_home_gcode: CARTOGRAPHER_TOUCH_HOME EXPERIMENTAL_RANDOM_RADIUS=0`,
`touch_probe_gcode: CARTOGRAPHER_TOUCH_PROBE`. Convenience macros use
`SAVE_CONFIG=0` by default. The raw `CALIBRATE_TOOL_OFFSETS` command still defaults
to saving upstream; always pass `SAVE_CONFIG=0` explicitly during commissioning.

The reviewed default speed-up path omits redundant lifts during local Touch, while
real tool changes retain the separate 35 mm clearance and KTC dock motion.
Camera calibration was not commissioned by this Z-only installation.

## Supervised measurement

Use a clear bed, clean nozzles, safe travel paths and attended operation.
Confirm Klipper ready, printer idle, correct detected tool and heater targets zero.
Do not start from an unresolved toolchanger error.

```gcode
G28
CALIBRATE_TOOL_Z TOOL=0 SAVE_CONFIG=0 CLEAN_NOZZLE=0
TKC_STATUS
CHECK_OFFSETS
```

T0 is defined as zero. Inspect raw Touch samples and repeat-home corrections;
three printed `T0 Z=0` results alone do not establish repeatability.

Only after T0 passes, a diagnostic group command is:

```gcode
CALIBRATE_TOOLS_Z TOOLS=0,1,2,3,4 SAVE_CONFIG=0 CLEAN_NOZZLE=0 CONTINUE_ON_ERROR=0
```

T3 failed this commissioning run. Do not use this group as an unattended production
calibration, increase tolerance to force acceptance, or save the reported results.
The production reference offsets were measured at hotend 150 C / bed 70 C; cold
commissioning results are not directly comparable. Isolated T3 native probing at
150/70 setpoints passed three sequences but showed 0.016 mm between-run spread;
bed temperature was not fully stable. This does not qualify the complete TKC cycle.
After a failed probe, compare detected and active tool state: TKC's recovery message
can incorrectly claim success. On this machine the standard `G28` restored a correctly
detected T3 before further testing; recovery requires a clear path and known tool state.

Known XY-cache defect: after a completed Z-only run, TKC caches only Z and can omit
saved XY compensation on the next run. Until upstream fixes this, independent repeated
group tests require a Klipper restart, normal home and a fresh T0 baseline; preserve
the existing XY seed file. Do not trust a cached T0 baseline across another home,
origin change, model change or mechanical intervention.

`CALIBRATION_ABORT` is cooperative G-code, not an independently verified emergency
stop. Use the printer's emergency-stop mechanism when immediate stopping is required.
Do not resend a long calibration command after an HTTP timeout; inspect current status.

## Updates and rollback

The All-Config installer checks TKC runtime availability and excludes TKC offsets,
backups and manifest from rsync. Existing machine offsets are not overwritten by the
repository snapshot. A missing offsets file is seeded after backup.
The master config remains repository-owned: update its machine adaptations deliberately.

Upstream updates can change behavior; repeat commissioning before saving offsets.
Backup set: `extras/backups/pre-tkc-install-20260908-200037/` and remote
`~/printer_data/config_backups/pre-tkc-install-20260908-200037/`.
To deactivate TKC, restore the backed-up printer and Moonraker configuration after
reviewing later changes, stop/disable its user service, and restart while idle.
The old source and configuration archive remain available for recovery.
