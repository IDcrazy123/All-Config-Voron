# CFG software hardening — 2026-10-16

## Status

Implemented locally after the [review](project-audit-2026-10-16.md), checked
offline, **not deployed to the printer**. No printer API/SSH, heating, motion,
restart, physical calibration or print was performed.

All existing Python files, KTC readonly files, Mainsail, printer.cfg/SAVE_CONFIG,
hardware/tool wiring, docks, PID, currents, motion limits and Orca JSON presets
remain unchanged. The installer retains its pre-existing reviewed tool_crash
patch behavior; this task does not patch runtime algorithms.

Original files were copied and SHA-256 verified before editing in
`extras/backups/pre-cfg-software-hardening-20261016-200256/`. Its manifest also
records all 33 existing Python source hashes. Existing backups/unrelated files
are retained.

## Part 1 — Print lifecycle and recovery

- PRINT_START rejects repeated/paused/recovery calls before G-code output. New
  virtual-SD starts remain valid although print_stats already says printing.
  Every requested used-tool/bed temperature is checked before heat/home. Enabled
  filament sensors must show filament in used tools and mandatory purge tool T0.
  Explicitly disabled sensors retain the existing operator override policy.
- PRINT_END shuts heaters down first, clears mesh/live offsets without moving,
  caps the initial relative Z5/retract stage by physical headroom, then uses the
  remaining bounded relative lift. Hot mounted-tool retract remains 10 mm.
  Unhomed, toolchanger-error and recovery branches skip movement.
- Finish/cancel use `UNSELECT_TOOL RESTORE_AXIS=` so removal of the active tool
  transform cannot create an invalid tool-relative Z restore. A separate helper
  reads the actual empty shuttle and parks at or above dock-exit Z and requested
  minimum, capped by Z max. After a low print the empty shuttle stays high rather
  than descending to the former low park height. Tall-part clearance still needs
  physical commissioning; dock coordinates were not changed.
- User-owned CANCEL_PRINT shuts heat down and completes native cancellation
  before optional retract/docking. A failed dock therefore cannot prevent base
  cancellation. Crash recovery skips all XYZ/docking. Normal cancel retains its
  5 mm retract and reviewed route. Mainsail/KTC readonly files remain untouched.
- Tool crash latches attachment uncertainty; KTC pickup/dropoff errors use the
  same no-XYZ pause handler instead of upstream parking PAUSE. The existing small
  E-only pause retract is retained. The latch is volatile across restart.
- RESUME requires an actual pause and no pending recovery. Separate helpers
  re-read tool/extruder/filament after initialization and heater/filament after any
  temperature wait. The printing hook runs only after these checks. G32/QGL
  reject competing operations but remain usable during PRINT_START preparation.

After inspecting and physically securing the original tool:

```gcode
CONFIRM_TOOL_RECOVERY CONFIRM=1
```

This initializes/verifies attachment and only then clears the latch, without XYZ
movement. If the event had no identifiable active tool, explicitly provide the
inspected tool, e.g. `T=0`. A paused job still requires its original tool. Cancel
does not acknowledge attachment automatically. The start/tool-use contract relies
on normal lifecycle/slicer calls, not a lock against arbitrary manual commands.

## Part 2 — CFG integration around unchanged runtimes

Both `CALIBRATE_COARSE_Z_OFFSETS CONFIRM=1` and compatibility command
`CALIBRATE_ALL_Z_OFFSETS CONFIRM=1` now use attended CFG orchestration. T0 is
measured first regardless of registry order. Existing Axiscope pickup hooks,
MOVE_TO_ZSWITCH and PROBE_ZSWITCH are reused. A safe-transit helper runs **before
the final T0**, followed by reporting/finish. The original backend batch command
is renamed privately and never called by this workflow. Do not use private
aliases as operator procedures.

No probe algorithm, sample count, switch geometry or saved offset changed.
Verify released/pressed PF2 states, remove the holder before normal home/mesh/
printing, and commission calibration while attended. Results remain preliminary
and report-only; first layers determine final Z. A failed run may leave phase
calibrating; inspect and use the reviewed cancel/recovery procedure.

The native multi-extruder exclusion defect remains unfixed. A CFG EXCLUDE_OBJECT
wrapper blocks NAME/CURRENT exclusion in multi-tool or unknown jobs. Query and
RESET pass through; declared single-tool jobs retain exclusion. Object labels
remain available for adaptive mesh. Presets and extrusion safety limits were
not retuned to hide the defect.

Shaping now selects the complete global profile when per-axis tool frequency is
zero, including measured damping X0.124/Y0.080. Positive explicit frequency opts
that axis into a tool profile. SET_INPUT_SHAPER forwards natively and invalidates
the cache; first selection reapplies the desired profile and unchanged later
selections remain quiet. Internal extension changes can bypass this G-code
wrapper: verify/restart after resonance calibration and do not treat cache values
as proof of actual runtime state. Effective damping changes from the former
inherited 0.1/0.1 even though measured tuning values remain untouched.

## Part 3 — Backup and deployment

Orca sync validates destination scope before writing, uses a timestamp plus
random suffix, refuses existing backup paths, and commits only its own new backup
with profiles/journal. Temporary-repository tests make two actual commits and
verify unrelated staged/untracked content remains separate. Real AppData presets
were not copied or changed.

The installer checks live/payload SAVE_CONFIG before any write and again before
backup. Mismatch refuses an ordinary update. Preserve/reconcile live calibration
first. Only an explicitly reviewed calibration replacement should use:

```bash
VORON_ALLOW_CALIBRATION_REPLACE=1 bash config/scripts/install.sh
```

This still creates a unique live backup; it does not selectively merge models.
Other matching machine filenames can still be replaced. Idle checking remains
observational, not an exclusive lock. Installer fixtures stub rsync and do not
prove real Linux copying. Standalone destructive cleanup was not run or changed.

## Verification and remaining work

```powershell
& extras/tests/Test-ProductionCfg.ps1 -Bash 'D:/App Installs/Git/bin/bash.exe'
```

Use an existing Python/Jinja2 and Bash. The PowerShell runner loads existing
tests, supplies configured heater bounds to the historical cleaner fixture, and
explicitly supersedes two October 9 same-file/old-cleaner invariants with current
semantic/hash checks. All existing .py files remain unchanged. Direct historical
Python discovery still reports those obsolete failures. Four Linux PTY checks
are skipped on Windows; they need Linux for runtime changes, which are outside
this task. Detailed results are in `extras/audits/2026-10-16/hardening-tests.txt`.

Tests cover Z0.28/30/342/345/347, positive/negative tool/manual offsets, hot/cold
finish, crash cancel without XYZ, base cancel before simulated dock failure,
empty filament/original-tool checks, deferred resume heat, Axiscope T0-first/final
lift, exclusion, shaping/cache, calibration drift/opt-in, actual temporary Git
commits, and the cleaner's full temperature/contact/tool-mask checks. These are
template/replay contracts, not a full Klipper/CAN scheduler or hardware simulator.

Before real use: compare live/runtime versions, take a verified live backup,
deploy the coordinated CFG set only while idle, restart and verify alias/helper
registration, saved calibration and effective shaping. Run attended short
print/end/cancel/pause/load/resume checks on a clear route; inspect the high empty-
shuttle park. Commission PF2 separately without inducing a real detached-tool
motion. No physical acceptance is claimed here.

T1 sensor replacement, monotonic timing, measured thermal-soak tuning, prime-area
reservation and tall-part route commissioning remain separate pending work.

## Primary references

- [Klipper template evaluation](https://www.klipper3d.org/Command_Templates.html#the-printer-variable) and [coordinate frames](https://www.klipper3d.org/Status_Reference.html#gcode_move): separate fresh-state helpers and relative motion.
- [Klipper G-code state commands](https://www.klipper3d.org/G-Codes.html#save_gcode_state).
- [KTC source at the historically observed revision](https://github.com/jwellman80/klipper-toolchanger-easy/blob/e881fe4/klipper/extras/toolchanger.py): empty RESTORE_AXIS, transforms, restoration/error hook.
- [Axiscope commands/hooks/results](https://github.com/nic335/Axiscope/blob/main/klippy/extras/axiscope.py): unchanged lower-level measurement interface.
- [Klipper exclusion implementation](https://github.com/Klipper3d/klipper/blob/master/klippy/extras/exclude_object.py): the runtime defect is guarded, not repaired.
