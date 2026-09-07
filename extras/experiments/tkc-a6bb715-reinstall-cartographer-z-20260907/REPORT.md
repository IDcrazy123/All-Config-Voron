# TKC a6bb715 Clean Reinstall and Cartographer Z Trial

Date: 2026-09-07
Printer: `voron@192.168.1.43`
Upstream: `IDcrazy123/Tool-Klipper-Calibration`
Tested commit: `a6bb71564a982b867fb7c1a310a6b4eef764cfd6` (`v0.8.19-1-ga6bb715`)

## Scope

This session performed a complete supervised uninstall, clean checkpoint, documented reinstall, live Klipper integration audit, and an experimental Cartographer-only Z run. No TKC source code was changed. Machine-specific configuration remained under `Printer-Setup` and was restored byte-for-byte after the installer created its files.

The camera had been removed from the measuring position. No camera calibration was run. Every experimental Z command used `SAVE_CONFIG=0` and `CLEAN_NOZZLE=0`; the operator confirmed that all nozzle tips were clean.

## Backup and preservation

- Local backup: `extras/backups/pre-tkc-a6bb715-z-20260907-160309/`
- Remote backup: `/home/voron/printer_data/config_backups/tkc-a6bb715-z-20260907-160309/`
- The remote backup includes configuration, hashes, service state, a Git bundle of the former checkout, installer output, and preserved uninstall residue.
- Production `printer.cfg` and `tool_offsets.cfg` hashes were unchanged after all trials.

## Uninstall audit

The latest uninstaller was invoked with the documented full-source option:

```text
./scripts/uninstall.sh --config-subdir Printer-Setup --purge-repo
```

It successfully removed the user service, Klipper module links, macro links, environment file, Moonraker updater entry, ASVC entry, manifest, and source checkout. Klipper and Moonraker restarted successfully. Port 8090 closed, no TKC Klipper objects remained, and all four TKC includes were commented. The new hyphenated include matching correctly found `Printer-Setup/tool-calibrator.cfg`.

The command did not produce a byte-clean removal. It intentionally retained the machine-owned `Printer-Setup/tool-calibrator.cfg`, archived `tool_offsets.cfg`, and left one orphan explanatory comment in `moonraker.conf`. These items were manually moved into the remote backup before reinstalling. The resulting clean checkpoint had no source, unit, port, symlink, active include, TKC object, or TKC config artifact.

Evidence: [uninstall output](./02-uninstall-output.txt), [automatic residue audit](./03-post-uninstaller-audit.txt), and [clean checkpoint](./04-clean-removal-checkpoint.txt).

## Install audit

The repository was cloned from upstream immediately after confirming that remote `main` resolved to `a6bb71564a982b867fb7c1a310a6b4eef764cfd6`. Installation used the documented command exactly:

```text
./scripts/install.sh --user-service --config-subdir Printer-Setup
```

The installer completed without manual source patches. It created and enabled `tool_calibrator.service`, opened port 8090, added Moonraker update management, installed Klipper links and macros, and restarted services. The machine-specific files were then restored from the backup so that this printer continued to use `Printer-Setup` as its canonical configuration location.

At final audit:

- local `HEAD` and remote `main` were both `a6bb71564a982b867fb7c1a310a6b4eef764cfd6`;
- branch `main` was clean and Moonraker reported zero commits behind;
- the TKC service was active and enabled, and port 8090 was listening;
- Klipper loaded `tool_calibrator` and was ready;
- kTAMV continued listening on port 8086 with no port or service conflict;
- the upstream suite passed 112 of 112 tests.

The installer's success message initially reported camera/scale/matrix readiness as pending or unset. This is a component-readiness limitation in the install report rather than an installation failure. After the machine configuration and calibration data were restored, `/health` reported the process, camera endpoint, scale, and matrix ready.

Evidence: [install output](./05-install-output.txt), [post-restore verification](./06-post-install-restore-verify.txt), [upstream tests](./22-upstream-tests.txt), [final audit](./21-final-audit.txt), and [temporary-helper cleanup check](./24-temp-cleanup-and-state.txt).

## Upstream fixes verified on the live printer

Commit `a6bb715` fixed several earlier findings:

1. Repeated Moonraker polling of `tool_calibrator` during active calibration no longer raises the former `NameError: time is not defined`; Klipper remained ready during all trials.
2. Cartographer defaults to `measurement_reference=shuttle` and rejects per-tool Z by default with `ERR_Z_003`.
3. The experimental override `ALLOW_SHUTTLE_Z=1` works explicitly.
4. Installation path handling no longer creates the former carriage-return-suffixed config directory.
5. `--purge-repo` removes the checkout, and the uninstaller recognizes the machine's hyphenated config include.

The default shuttle gate was verified after the measurement trials by omitting `ALLOW_SHUTTLE_Z=1`; TKC returned the expected `ERR_Z_003` instead of probing.

## Cartographer Z procedure

For the supervised experiment only, the two disabled Z hooks were temporarily changed to:

```ini
touch_home_gcode: CARTOGRAPHER_TOUCH_HOME
touch_probe_gcode: CARTOGRAPHER_TOUCH_PROBE
```

Klipper was restarted and a normal `G28` completed. Tests used:

```text
CALIBRATE_XY=0 CALIBRATE_Z=1 ALLOW_SHUTTLE_Z=1 SAVE_CONFIG=0 DRY_RUN=0 CLEAN_NOZZLE=0
```

The Cartographer touch configuration required three samples within a 0.010 mm range in a moving window of five, with at most ten touches.

| Trial | Physical point | Cartographer result | TKC outcome |
|---|---:|---|---|
| T0 reference, first run | about X174 Y168 | touch-home adjustment +0.398 mm | reference accepted |
| T1 | about X174 Y163 | 0.1395, 0.1395, 0.1375 mm | computed Z +0.140 mm |
| T2 | about X174 Y163 | -0.0145, -0.3905, -0.3145, +0.5855, -0.4525, +0.1275, +0.3735, -0.2965, -0.4685, -0.0145 mm | failed; spread 1.054 mm |
| T0 reference, T3 run | about X174 Y168 | touch-home adjustment +0.454 mm | reference accepted |
| T3 | about X174 Y163 | -0.1140, -0.1640, +0.1600, -0.1680, +0.0040, -0.1760, -0.1900, -0.1900, -0.0260, +0.5200 mm | failed; spread 0.710 mm |
| T0 reference, T4 run | about X174 Y168 | touch-home adjustment +0.443 mm | reference accepted |
| T4 | about X174 Y163 | +0.0886, +0.0966, +0.2866, +0.1406, +0.0966 mm | computed Z +0.097 mm |

T2 and T3 failed inside Cartographer's sample-consistency check before their values reached TKC's offset arithmetic. Raising tolerance would not be a valid fix: Cartographer permits at most 0.015 mm, while the measured spreads were 0.710 mm and 1.054 mm. T1 and T4 passing through the same command path also rules out a universal command-registration failure.

The reference touch-home adjustments changed from 0.398 to 0.454 and 0.443 mm, a 0.056 mm range across runs. This further prevents treating the experimental values as production offsets.

Evidence: [full T0-T4 attempt](./09-cartographer-z-run.txt), [T2 investigation](./10-t2-failure-investigation.txt), [T3 trial](./13-cartographer-z-t3.txt), and [T4 trial](./15-cartographer-z-t4.txt).

## Confirmed same-point defect

The reference and secondary measurements did not use the same XY point:

- `CARTOGRAPHER_TOUCH_HOME` moved T0 to the configured bed-mesh zero reference, approximately `(174, 168)`.
- TKC moved T1-T4 to approximately `(174, 163)` before `CARTOGRAPHER_TOUCH_PROBE`.

This 5 mm Y difference is a confirmed TKC lookup defect. `BaseZBackend.get_probe_xy()` checks `bed_mesh.zero_ref_pos` and then `bed_mesh.bmc.zero_ref_pos`. On this Klipper version, the value belongs to `bed_mesh.bmc.probe_mgr.zero_ref_pos`. Both attempted lookups therefore miss it, and TKC silently falls back to the travel center:

```text
X = (0 + 348) / 2 = 174
Y = (-10 + 336) / 2 = 163
```

Cartographer independently reads the configured `zero_reference_position=(174,168)` for touch home. No `Compensating Z-probe position` message appeared, and the TKC offset store had no saved tool XY values, so TKC's explicit `offset_xy` compensation did not cause this difference.

Evidence: [observed coordinate comparison](./18-coordinate-comparison.txt), [object-path and fallback proof](./23-coordinate-root-cause-confirmation.txt), and [Klipper/Cartographer source context](./20-bed-mesh-coordinate-root-cause.txt).

## Remaining TKC defects and risks

### 1. Fixed-shuttle Cartographer cannot provide nozzle-tip offsets

The new default gate is correct. A Cartographer fixed to the shuttle observes shuttle/probe-to-bed distance, not the individual nozzle tip length. The override enabled a diagnostic experiment; it did not make the geometry valid. Even perfectly repeatable, same-point values must not be saved as per-tool nozzle Z offsets on this arrangement.

### 2. Failure cleanup leaves the toolchanger uninitialized

After both a Cartographer repeatability exception and the early `ERR_Z_003` preflight rejection, Klipper remained ready and the sensor correctly detected the physical tool, but `toolchanger.status` became `uninitialized` with `tool_number=-1`. TKC's exception path marks the run failed and departs the station, but does not reconcile the detected tool with the active logical tool. A normal `G28` recovered the state each time.

### 3. Runtime elapsed time uses incompatible clocks

During an active run, `elapsed_sec` was a very large negative value. The run record stores `start_time` with Unix wall time while `get_status(eventtime)` subtracts it from Klipper reactor monotonic time. The prior NameError is fixed, but live telemetry remains wrong. The 112-test suite passes because it does not exercise status with a real Klipper monotonic `eventtime`.

### 4. One failing tool aborts all remaining tools

The T2 repeatability error aborted the combined T0-T4 request, so T3 and T4 were never attempted. They had to be tested in separate runs. This reduces diagnostic coverage and makes recovery more disruptive.

### 5. Full uninstall still requires manual residue handling

The uninstaller safely preserves user data, which is appropriate by default, but `--purge-repo` is not a complete purge. It should clearly enumerate retained paths, or offer a separate explicit, backup-first purge option for machine configuration and archives.

## Recommended changes

1. Resolve the bed-mesh zero reference through the supported Klipper object path/API and log both the requested and actual probe XY. Reject a run when reference and secondary touch points differ beyond a small coordinate tolerance.
2. Keep the fixed-shuttle gate mandatory for saving per-tool Z. If `ALLOW_SHUTTLE_Z=1` is used, mark results as experimental and force `SAVE_CONFIG=0`.
3. Put tool-state reconciliation in a `finally` cleanup path. Restore the reference tool or explicitly initialize the detected physical tool before returning from any failure, including preflight failures.
4. Store and calculate elapsed time with one clock source. Add a test that calls `get_status()` with a real monotonic-style event time while a run is active.
5. Support a diagnostic continue-on-error mode that records per-tool failures and raw touch samples, then safely returns to T0.
6. Report installation health in separate layers: files/service/Klipper integration and optional camera/scale/matrix calibration readiness.
7. Add an opt-in backup-first config purge mode, or print an exact retained-artifact list at uninstall completion.
8. Investigate Cartographer/mechanical repeatability for T2 and T3 at the same physical point before any further offset work. Do not relax the 0.010 mm gate to mask 0.7-1.05 mm spreads.

## Post-audit standalone command event

After the first final-state checkpoint, Moonraker's G-code store recorded a new `T2` command at `1788774631.699` and a separate `cartographer_touch_probe` command at `1788774636.260`. The probe ran after T2 was selected and failed the same three-samples-within-0.010-mm rule. The command source was not established.

At this time `tool_calibrator` was `IDLE` and both TKC Z hooks were already `_TKC_Z_DISABLED`, so this was not a TKC calibration run or a TKC self-trigger. The standalone T2 touch failure strengthens the finding that T2's sample-repeatability problem occurs inside the Cartographer touch path before TKC offset arithmetic.

The error again left toolchanger state uninitialized while the sensor detected T2. A normal `G28` initialized T2, and a normal `T0` restored the reference tool. Evidence: [post-audit command sequence and recovery](./26-post-audit-command-sequence.txt).

## Final state

The experimental hooks were restored to `_TKC_Z_DISABLED` and the original config hash. A firmware restart and normal `G28` completed. The printer was left in this state:

- Klipper: `ready`
- Homed axes: `xyz`
- Toolchanger: `ready`
- Active and detected tool: T0
- Position: approximately X30.2, Y120, Z10
- All hotend and bed targets: 0 °C
- TKC: installed at exact upstream `a6bb715`, clean and current
- kTAMV: still available on port 8086
- Production offsets: unchanged

The experimental T1 `+0.140 mm` and T4 `+0.097 mm` results were not applied. T2 and T3 produced no valid result. No Cartographer-derived per-tool Z value from this session is suitable for production use.
