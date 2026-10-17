# CFG follow-up review and deployment — 2026-10-17

## Result and scope

The operator requested another review and completion of remaining software fixes
while the printer was idle. Nine user-owned CFG files were updated and deployed
to `192.168.1.43`; one soft `RESTART` completed successfully. Klipper is ready,
with no configuration or Moonraker warnings. No heating, movement, homing, tool
selection, calibration or print was performed during this task.

The changes build on `67df95b`. All 33 existing repository Python files and all
10 inspected live runtime Python files retain their original hashes. No PID,
motor current, hardware pin, saved calibration, offset, motion limit, dock
coordinate, KTC readonly file, Mainsail file or Orca JSON preset was changed.

## Confirmed defects and corrections

1. **Empty exclusion RESET bypass.** `RESET=` was considered a reset by the CFG
   guard solely because the parameter existed. The installed native command
   instead tests string truthiness and can exclude `NAME`/`CURRENT` when RESET is
   empty. The wrapper now follows that exact condition. Truthy resets, including
   the native string `RESET=0`, remain resets; empty query remains a query.
   Multi-tool/unknown-job exclusion remains blocked.
2. **Heater callback survives cancel/end.** An active dryer retained
   `is_drying=1` after cancel, while print phase became idle. Its next callback
   could emit `M140 S70` and undo shutdown. This was reproduced using the exact
   live pre-edit CANCEL_PRINT snapshot. PRINT_END and CANCEL_PRINT now turn
   heaters off first, then clear dryer/benchmark ownership and cancel both
   callbacks before optional cleanup. A stale callback cannot restart their heat.
3. **Dryer tool-relative Z restoration.** PARK=1 still used implicit
   `UNSELECT_TOOL`, which could restore tool-relative Z after removing the tool
   transform. It now uses empty `RESTORE_AXIS`, a bounded physical relative lift,
   and a fresh post-dock helper that requires an empty, ready, homed shuttle.
   The existing park remains X175/Y310 with at least Z200 clearance; the shuttle
   does not descend from a higher dock-exit height just to reach Z200. An active
   mesh is cleared before this fixed-route operation. PARK=0 retains no motion.
4. **Recovery admission gaps.** Cleaner entry and deferred helpers, prime entry
   and its tool helper, dryer start/park, benchmark start, XY/Z speed tests and
   switch-position/transit helpers now refuse a pending tool-recovery latch.
   This closes ordinary feature entry paths; it is not a universal interlock
   against arbitrary raw G-code or private backend commands.
5. **Repeated pause changes recovery state and parks again.** User-owned PAUSE
   retains normal Mainsail temperature/timeout/hook/parking behavior on its first
   call. Repeated calls preserve the original paused tool, temperature and
   position. Recovery/error calls route through the no-XYZ crash handler. The
   existing small E-only crash retract remains; already queued motion can finish.
6. **LED presentation changes safety state.** Five LED wrappers previously
   changed print/dryer phase or paused tool. A manual completion color could
   falsely mark an ongoing operation idle. They now change presentation only.
   `_PRINT_PAUSED`, existing print/resume owners and explicit dryer start/stop
   own lifecycle changes. Repeated pause hooks retain the original paused tool.
7. **Additional manual-entry gaps.** PRIME_LINES rejects concurrent print/pause,
   dryer/benchmark/calibration operations and temperatures below the selected
   heater's extrusion minimum before any output. It still permits the normal
   PRINT_START phase. G32/QGL preparation also checks native print status when
   outside PRINT_START, so an idle private phase cannot admit motion during a
   raw active job. Direct switch positioning rejects competing operations.

The affected production files are `print-macros.cfg`, `fans-leds.cfg`,
`filament-dryer.cfg`, `nozzle-clean.cfg`, `prime-lines.cfg`,
`tool-temp-bench.cfg`, `test-speed.cfg`, `calibration-probe.cfg` and
`tool-crash.cfg`, all under `config/Printer-Setup/`.

## Verification

- Production runner: **78 tests, 72 passed, 6 skipped, no failures/errors**.
  Existing six skips remain two superseded historical invariants and four
  Linux-only PTY tests. A third historical dryer test is replaced in the runner
  by current relative-lift/helper semantics while retaining preset/fit checks;
  it runs and passes. Direct historical Python discovery still has obsolete
  assertions and is not claimed green. No existing Python test was edited.
- Native installed Jinja2 2.11.3 compiles **142 templates**. The actual installed
  rename implementation verifies all **10 wrapper/base pairs**.
- **12 inert render scenarios** also pass under the printer's native Jinja,
  including empty RESET, cold priming, repeated/normal pause, empty-shuttle park
  and recovery refusal. These execute no G-code.
- Dryer replay covers Z30/200/345/347 and tool offsets -0.3515/0/+0.1665 mm,
  including no invalid implicit restore and no descent below the park minimum.
  Cancel/end tests verify both callbacks stop and cannot reheat afterward.
- Bash syntax and Git whitespace checks pass. Initial current-log scans found
  no matching traceback/shutdown/error lines; this is not a full historical
  incident clearance or a hardware stress test.

The runner remains `extras/tests/Test-ProductionCfg.ps1`. Quote/comment handling
in its replay now respects semicolons inside response strings. The tests model
selected templates and command effects, not all Klipper/CAN scheduling.

## Backups and live acceptance

Verified local repository originals:
`extras/backups/pre-cfg-followup-20261017-161410/`.
Verified exact live originals (nine targets plus reference-only printer.cfg):
`extras/backups/pre-printer-cfg-followup-20261017-162039/`.

Printer backup, verified before writes and again after restart:
`/home/voron/printer_data/config_backups/pre-cfg-followup-20261017-162128-66m1xrah/`.
Original live files are in its `config/` subdirectory. Existing backups are
retained; no rollback was required.

Before writes and restart, status was confirmed standby/unpaused, virtual SD
inactive, native idle Ready/Idle, toolchanger ready/uninitialized, private phase
idle, recovery clear, auxiliary tasks stopped and all six heater targets zero.
All 34 observed config files, six symlinks and 10 runtime hashes were rechecked
against the captured state before writing. Nine target files were replaced
atomically one at a time, preserving permissions, then the whole set was checked.

After restart, all nine payload hashes match; the other 25 observed file hashes,
six symlinks and 10 runtime hashes remain unchanged. All **104 non-macro config
sections**, including delayed callbacks, match the previous loaded config. The
26 changed and three new sections are all user-owned G-code macros. PAUSE_BASE,
RESUME_BASE, CANCEL_PRINT_BASE and the three new helpers are registered.

Final state is ready/standby, no pause/active virtual SD, phase idle, recovery
clear, dryer/benchmark inactive and all six heater targets zero. Axes remain
unhomed and KTC uninitialized after restart, physically detecting T0. No live
motion/thermal acceptance was attempted.

Evidence: `extras/audits/2026-10-17-followup/{reproduced-before.json,tests.txt,
native-preflight.json,native-render-checks.json,deployment-events.jsonl,
verification.json,final-integrity.json,log-review.json}`. The workspace-owned
`.agents/KNOWN_ISSUES.md` was also updated; its original is preserved in
`extras/backups/pre-workspace-issue-register-20261017-162614/` and its narrow
change patch is in the audit folder. Full transient captures are ignored
`*.local.json` files and are not committed.

## Still open

- **T1 temperature sensor:** operator-confirmed hardware defect, replacement
  and cold/operating verification still pending. A near-ambient snapshot does
  not certify repair. No sensor type or PID was guessed.
- **Native multi-extruder exclusion defect:** the CFG policy blocks unsafe
  declared multi-tool/unknown jobs; the native E-state algorithm remains
  unchanged. Full exclusion support needs a reviewed runtime fix and an
  attended coupon. Single-tool admission relies on accurate slicer tool data.
- **Physical acceptance:** home normally before the next print. Check short
  print/end/cancel/pause/load/resume operation, high empty-shuttle/dryer park,
  tall-part routes and effective shaping while attended. Reserve and inspect
  the prime area in slicer/bed layout. Bounds alone cannot certify clearance.
- **PF2 and thermal commissioning:** confirm released/pressed switch states
  and fixture route while attended; first layers finalize Z. Heat-soak durations
  and hot-to-cool behavior require measurements before retuning.
- **Timing:** dryer/benchmark counters still count delayed callbacks. They are
  estimates, not monotonic cycle deadlines; benchmark TIMEOUT does not include
  baseline preparation waits. A supported clock/runtime or host telemetry and
  cancellation design is needed before promising those guarantees.
- **Slicer coupons:** verify PETG cooling/flow/Z-hop/toolchange position on a
  small sample; Orca-generated M220 resets remain a separate reslicing or
  reviewed postprocessor issue. No profile tuning was applied speculatively.

## References checked

- [Klipper template evaluation and fresh printer status](https://www.klipper3d.org/Command_Templates.html#the-printer-variable).
- [Klipper config/runtime state reference](https://www.klipper3d.org/Status_Reference.html#configfile).
- [Klipper exclusion commands](https://www.klipper3d.org/G-Codes.html#exclude_object).
- Installed sources inspected via SSH: Klipper `gcode_macro.py`,
  `exclude_object.py`, KTC `toolchanger.py`; runtime hashes are in verification.
