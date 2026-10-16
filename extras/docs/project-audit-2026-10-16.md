# Production CFG and software review — 2026-10-16

## Scope and limits

Baseline: `a4fdef6` on `main`. Reviewed the complete production include chain (26 CFG files), host `.conf` files, deployment scripts/patches, all 20 Orca JSON presets and their synchronizer, offline tests, current documentation, issue registry and relevant historical evidence. The flattened CFG has 195 sections and 127 compilable G-code/hook templates, before interpreting the commented `SAVE_CONFIG` data. Saved PID, probe/mesh/twist models and tool offsets were inspected separately.

Backups, retired configurations, binary media, large generated G-code and historical experiments were inventoried/consulted as references, not treated as active configuration or exhaustively reviewed byte by byte. Oxplow's included runtime was reviewed; this is not a new audit of its independent upstream generator project.

This session did not connect to the printer. There was no G-code, motion, heating, restart, deployment or configuration change. October 9/15 live observations are historical evidence, not a fresh assertion about installed runtime versions, sensor health or physical clearance. Source-level risks below require the stated triggering conditions; they are not claims that every normal print fails.

Evidence, counts, render probes and reviewed-payload SHA-256 values: [audit evidence](../audits/2026-10-16/evidence.json).

## Assessment

Keep the functional file layout. Separating hardware, calibration, cleaner, priming, print lifecycle, drying and diagnostics is appropriate. The October 15 lifecycle move and cleaner changes provide useful ownership boundaries. A wholesale rewrite or arbitrary increases in acceleration, heater power, current, PID or flow limits would not address the findings below.

The highest-value software work is recovery correctness, early validation, consistent runtime state and regression coverage. Several known October 9 risks remain, while motion diagnostics have since improved. Documentation and tests must follow those changes.

## Prioritized findings

### F01 — P1: End-of-print lift can exceed the Z ceiling before its later clamp

**Evidence:** `config/Printer-Setup/print-macros.cfg:438-469`. With XYZ homed, a hot active extruder, physical Z345 and max Z347, rendering emits `G1 Z5 E-8.0 F12000` before `G0 Z347`. The relative lift requests Z350. The later clamp cannot protect the earlier move. Shutdown commands occur afterward in `PRINT_END`; a virtual-SD error may invoke the configured `CANCEL_PRINT` fallback, but that is a separate recovery path.

The absolute lift also calculates from `toolhead.position.z` and emits a G-code Z while offsets/transforms may still be active. Cancel has the same coordinate-frame concern at lines 751–755.

**Recommended change:** Implement bounded vertical clearance in a deliberately chosen coordinate frame, including the initial combined Z/E move. Define essential heater shutdown and cancellation behavior independently of successful docking/parking. Do not change measured travel limits to accommodate an invalid request.

**Acceptance:** Render/replay hot and cold extruders, unhomed axes, Z342/345/347, positive/negative manual offsets and each tool transform. Confirm no requested physical Z exceeds limits and movement failure still reaches a defined thermal shutdown policy. Physical verification must be attended.

### F02 — P1: Crash pause has no corresponding no-motion cancel path

**Evidence:** `config/Printer-Setup/tool-crash.cfg:89` requests a pause without XYZ parking. `config/Printer-Setup/print-macros.cfg:733-771` subsequently lifts, unselects and parks whenever XYZ remains homed, without a latched crash-recovery condition or explicit confirmation that the tool is secure.

**Correction to the October 9 report:** Current `mainsail.cfg:69-86` defaults `park_at_cancel` to false, and the effective `_CLIENT_VARIABLE` does not enable it. Therefore Mainsail's initial park is normally skipped here. The custom cleanup's own movement still creates the risk; changing only Mainsail's park flag does not fix it. Cancellation can also be entered through virtual-SD `on_error_gcode`.

**Recommended change:** Latch crash recovery, route cancel after a crash through heater/fan/base-cancel cleanup without XYZ travel, and require an explicit recovery transition before resuming normal docking. Ordinary cancel can retain its reviewed movement route. Keep the override in user-owned files.

**Acceptance:** Simulate detached tool, retained/missing detection, already paused, toolchanger error and unhomed axes. Crash cancel must contain no G0/G1 XYZ or implicit toolchange/home commands and must complete base cancellation.

### F03 — P1: Coarse-Z calibration returns to T0 before the safe finish hook

**Evidence:** Local reference `extras/Axiscope-reference/klippy/extras/axiscope.py:250-277` runs final `T0` before `finish_gcode`. Probing returns to its start near Z3. The configured `_CALIBRATE_SAFE_TRANSIT` inside `finish_gcode` therefore runs too late for that first final toolchange. The [upstream Axiscope source](https://raw.githubusercontent.com/nic335/Axiscope/main/klippy/extras/axiscope.py) inspected during this review has the same ordering.

**Recommended change:** Put the clearance operation before the backend's final T0, using a reviewed runtime hook/patch or controlled workflow that covers every switch. A CFG wrapper that merely adds another finish lift does not repair this ordering. Retain report-only offset handling and attended commissioning.

**Acceptance:** Trace all five probes and the final return, verifying clearance before every lateral/toolchange motion, including the last T4-to-T0 transition. Verify the installed backend before applying any patch.

### F04 — P1: Multi-tool exclusion remains an unresolved runtime dependency

**Evidence:** `print-macros.cfg` still enables `[exclude_object]`. September's documented replay showed cross-tool E-state corruption; no reviewed fix exists in the active payload. Current `0.20mm Multicolor PetG.json` disables both exclusion and labels, but `0.20mm ABS no hole.json:61,90` explicitly enables them. That is conditional risk when the ABS preset is used for a multi-tool job and exclusion is invoked, not proof that its single-tool use fails.

The [Klipper source inspected during this review](https://raw.githubusercontent.com/Klipper3d/klipper/master/klippy/extras/exclude_object.py) still stores extrusion offsets by extruder while keeping last/max/adjustment state shared. Simply selecting a newer branch is not evidence of a fix.

**Recommended change:** Establish an explicit multi-tool preset policy until a compatible per-extruder-state fix passes replay and hardware testing. Do not raise `max_extrude_cross_section` to hide the error. Disabling labels also affects object-based adaptive mesh, so choose that tradeoff deliberately.

**Acceptance:** Replay relative/absolute E, retract/recover, G92, toolchange, exclusion and unexclusion against the installed Klipper API, followed by an attended multi-tool coupon.

### F05 — P2: RESUME can continue with the active runout sensor still empty

**Evidence:** `print-macros.cfg:641` only checks `client.runout_sensor`; that variable is commented out in the effective client configuration. A render fixture with active T0, an enabled `filament_sensor_T0` reporting false and an otherwise hot/paused printer still emits `_CLIENT_EXTRUDE` and `RESUME_BASE`. `VERIFY_TOOL_DETECTED` verifies attachment, not filament.

The runout handler only reacts to sensor callbacks for an active tool. A tool that became empty while parked can later be selected without a new runout edge. Also, the enclosing RESUME template reads heater/runout status before its emitted `INITIALIZE_TOOLCHANGER` runs.

**Recommended change:** Resolve the currently mounted tool's filament sensor and heater in a separate helper after initialization/verification. Require the expected paused job/tool before recovery and define explicit policy for intentionally disabled sensors. Consider a fresh filament check before selecting/priming a used tool.

**Acceptance:** Empty active tool, empty parked tool selected later, sensor disabled, replaced tool during pause, cold resume and a normal loaded-tool resume. Preserve Mainsail's temperature/idle restoration contract.

### F06 — P2: PRINT_START lacks an active-print guard and complete early heater validation

**Evidence:** Current validation rejects a running benchmark and bad T0 purge temperature, but does not reject an already printing/paused job. A fixture with `print_stats=printing` and `is_paused=true` still renders `CLEAR_PAUSE` and `G28`. This is reproducible through a mistaken manual/API call; ordinary virtual-SD starts normally enter through the intended lifecycle.

`TOOL_TEMP=350 BED_TEMP=130 T0_PURGE_TEMP=230` also renders `M140 S130` and a final prime request at 350. Native heater validation or PRIME_LINES eventually rejects these, but startup side effects/state changes may already have happened. Other used tools' maximum temperatures are checked late in priming rather than at PRINT_START entry.

**Recommended change:** Add lifecycle-aware admission and validate every requested bed/tool temperature against configured limits before output. Do not reject the legitimate new-file start merely because virtual-SD already reports `printing`: use the explicit project phase/paused state and a deliberate fresh-start contract. Keep dryer handoff behavior.

G32/QGL and calibration entry points also need a consistent policy for manual invocation during a job. Internal PRINT_START calls must remain valid; blanket independent guards on every helper are insufficient.

### F07 — P2: The measured global shaper is overwritten by inherited damping

**Evidence:** `input-shaper.cfg:43,46` defines X=0.124, Y=0.080. Readonly KTC defaults give each tool X/Y=0.1. User hook `toolchanger-config.cfg:143,146` prefers the truthy inherited values. Commenting per-tool frequency/type overrides does not disable inherited damping. October 9's runtime snapshot also observed 0.1/0.1; no fresh machine query was made today.

**Recommended change:** Choose the complete global profile when no per-tool profile is explicitly enabled. Preserve valid explicit tool overrides as a separate opt-in. Change the user hook rather than readonly KTC files. Invalidate/update the `_ACTIVE_INPUT_SHAPER` cache whenever another operation changes shaping, so cache equality cannot hide stale actual settings.

**Acceptance:** Inspect actual shaping after boot, T0–T4 selection, resonance calibration and any manual `SET_INPUT_SHAPER`. This changes effective tuning and needs measured validation.

### F08 — P2: The current regression suite is not green after approved behavior changes

**Evidence:** `python -m unittest discover -s extras/tests -v` ran 38 tests: **32 passed, 2 errors, 4 Linux PTY skips**.

- `test_cfg_native_hardware_and_dock_paths_unchanged` raises `KeyError: 'gcode_macro _PRINT_STATE'` because it compares same-file section placement against the October 9 backup, predating the October 15 lifecycle move.
- `test_measured_feature_moves_and_default_heat_commands_match_backup` runs the old cleaner template with today's 0.2 mm fixture; its old 0.5–1.0 guard rejects it. The new cleaner path intentionally differs from that historical baseline.

The newer standalone cleaner harness passes **14/14**, but is outside the standard test discovery directory. These failures do not establish a broken production CFG; they establish obsolete regression expectations.

**Recommended change:** Keep immutable backups intact. Replace historical whole-file invariants with current semantic contracts, compare moved sections through the flattened include graph and retain immutable fixtures only where unchanged behavior is required. Include cleaner coverage in the normal test entry point. Add the boundary/recovery cases above and a declared Python/Jinja2 test environment. Linux PTY tests need an actual Linux runner. No tracked `.github` workflow currently exists.

### F09 — P2: Orca synchronization creates backups but omits them from commit paths

**Evidence:** `Orca Config/Sync-OrcaProfiles.ps1:187-212` creates backup files and README. Lines 315–373 build the scoped stage/commit lists from profiles, journal and optional diagnostics; they never add `$backupRoot`. Consequently the one-click sync/push does not upload its newly created backup, contrary to repository backup policy. The pre-existing untracked `pre-orcaslicer-profile-sync-20261012-161629/` is consistent with this code path; it was not staged by this review.

**Recommended change:** Include only this run's backup paths in the scoped commit and reject timestamp collisions with an existing backup directory. Check repository-relative destinations before the first write, rather than relying on late commit-path checks. Do not sweep unrelated untracked backups into an audit commit.

**Acceptance:** Temporary-repository sync with one changed preset must commit preset, alias, journal and this run's backup together; unrelated staged/untracked files must remain untouched. Two runs must never overwrite a backup.

### F10 — P2: Software deployment also replaces machine-local saved calibration

**Evidence:** `config/scripts/install.sh:141-152` nondeletingly syncs the full payload, including `printer.cfg` and its `SAVE_CONFIG`. Backup-first behavior and idle checks are improvements, but a future on-printer `SAVE_CONFIG` change can still be replaced by an older repository copy. Existing tests use an rsync argument stub, so they do not prove actual copying/calibration-preservation behavior.

**Recommended change:** Add a drift report and explicit policy for deploying macro software versus machine-owned saved data. Refuse an unreviewed calibration mismatch or provide a separately reviewed calibration update operation. Keep unique live backups and nondeleting sync. Add disposable Linux integration coverage with real rsync; never exercise the real printer destination for this test.

Moonraker's `All-Config-Voron` updater points to `~/All-Config-Voron`, whereas `update.sh` describes a transient archive with no persistent clone. These can be intentional alternate modes; document the selected mode and verify the actual service paths before changing either. Pin/test compatible KTC, Axiscope, Cartographer and local patch versions as a set. A blanket update of all plugins is not a validated upgrade strategy.

### F11 — P2: Prime lines, shutdown travel and thermal settling need explicit operating envelopes

**Evidence:** Prime lines occupy Y0/3/6 and fixed X slots, while Orca's declared printable area includes those coordinates. There is no reserved-object-area contract in the machine preset. Adaptive mesh is based on sliced objects, so prime lines may be outside its subset. Mesh extrapolation and a successful bounds check do not establish first-layer quality or object clearance.

For end/cancel, KTC `t_command_restore_axis: Z` restores Z after unselecting; do not assume the shuttle necessarily stays at the last dock Z331. The [KTC source at the historically observed revision](https://github.com/jwellman80/klipper-toolchanger-easy/blob/e881fe4/klipper/extras/toolchanger.py) restores selected axes in `_restore_state_and_transform`. Subsequent parking and docking routes still need clearance against the completed object's envelope, particularly tall parts.

**Recommended change:** Reserve the real prime/wipe region in slicer placement rules, verify mesh coverage and commission routes for the maximum intended part envelope. Do not infer usable bed area from negative dock/brush travel limits. Retain separate tests for T0-only, non-T0-only and five-tool starts.

Automatic soak uses the initial bed temperature and short material defaults; a hot-to-cooler-material transition intentionally skips waiting for bed cooldown. Improve this only from observed bed/chamber stability and first-layer results. Make hot-to-cool transition behavior explicit rather than silently replacing all soak durations.

### F12 — P3: Timer arithmetic is useful for display but not accurate elapsed measurement

**Evidence:** Dryer decrements a fixed ten seconds per callback; heat benchmark adds `vars.tick`. Queued waits/motion and reactor scheduling can change elapsed wall time. Benchmark `TIMEOUT` starts after baseline temperature preparation, so it does not bound that preparation wait. The comments already disclose callback-based timing.

**Recommended change:** For accurate heat-rate comparison or a firm cycle deadline, use a monotonic clock supplied by a small reviewed runtime extension, or host telemetry. Keep display counters separate from control deadlines. Define a separate preparation timeout/cancel policy; do not imply native heater verification is disabled or absent.

### F13 — P3: Current documentation contains stale operational facts

**Evidence:** `config/README.md` still lists Y endstop PF1 while `hardware.cfg` uses PF4. Orca inventory says 19 presets and lists three processes; the folder now contains 20 JSONs and four processes, including `0.20mm ABS no hole`. Workspace TODO still calls for redesign of TEST_Z_SPEED using supported commands, but current code already uses supported VELOCITY/ACCEL, guards configured ceilings and restores runtime limits. Physical acceptance remains distinct from implementation completion.

**Recommended change:** Update current English/Vietnamese companion documentation and TODO together after checking the exact implementation/validation status. Leave dated journals and backup reports unchanged. Generate small inventory/consistency checks for pin references, included modules and preset counts.

## Additional engineering improvements

- Keep safety state separate from LED presentation. Lifecycle sections now live in print-macros, but LED status wrappers still mutate `_PRINT_STATE`; manually changing a color can therefore affect admission to dryer/benchmark/cleaner operations. Move state transitions to explicit lifecycle owners in a behavior-preserving follow-up, retaining the existing helper render boundaries.
- Add a read-only preflight report for tool mapping, dock waypoint bounds, calibration backend ownership, runtime patch/version compatibility and slicer start-G-code arguments. Physical geometry still requires measurement.
- Review standalone `cleanup-voron.sh --apply` retention separately: it deletes install backups beyond five without checking their recovery value or producing an archive. It is not called automatically by the current installer; do not run it merely to tidy this review.
- Review the broad Moonraker trusted-network list against actual network topology when maintaining host access. It intentionally grants trusted clients passwordless API access according to [Moonraker authorization documentation](https://moonraker.readthedocs.io/en/latest/configuration/#trusted-clients). No exposure or compromise was established in this offline review.
- T1's failed temperature sensor remains an operator-confirmed open hardware issue in the issue registry. Software tuning, sensor-type guessing or widening temperature guards cannot certify its repair. Preserve the pending-replacement status until cold and operating checks are available. The previously repaired CAN fault is a separate issue.

## Work sequence

1. Restore a trustworthy regression baseline (F08) and correct current documentation (F13).
2. Correct end/crash-cancel behavior and early lifecycle/runout checks (F01/F02/F05/F06), with offline boundary replay before attended trials.
3. Resolve Axiscope return ordering and multi-extruder exclusion against verified installed source (F03/F04); verify global shaping selection (F07).
4. Fix backup commit scope and add deployment drift protection (F09/F10).
5. Commission prime/tall-part/thermal envelopes and improve timing/telemetry only where measurement needs justify it (F11/F12).

For every later CFG/script modification: back up before writing, preserve unrelated comments/sections, record the change, run relevant checks, and only deploy/restart under the project's machine-operation constraints. This report itself does not authorize an unmeasured hardware parameter change.

## Validation completed in this review

- Complete include traversal and compilation: 26 files, 195 effective sections, 127 templates; no missing explicit include or template syntax error found by the offline loader.
- All 20 Orca JSON files parse successfully. This does not resolve inherited slicer settings or constitute a fresh reslice.
- General suite: 38 run, 32 pass, 2 obsolete-expectation errors, 4 real Linux PTY tests skipped on Windows.
- Cleaner suite: 14 pass, including dedicated T0 metadata, tool-use mask, contact bounds, raster coverage and deferred purge checks.
- All three Bash scripts pass individual `bash -n`; the PowerShell synchronizer has zero parser errors.
- Explicit render probes reproduce F01, F05 and F06 without executing generated G-code.
- Jinja render probes are snapshots, not a Klipper scheduler/hardware simulation. Klipper's [template evaluation rules](https://www.klipper3d.org/Command_Templates.html#the-printer-variable) require separate helpers where status must be read after initialization or waits. Coordinate choices must follow the [status reference](https://www.klipper3d.org/Status_Reference.html#gcode_move).
- No claim of live wiring, heater health, sensor repair, mechanical clearance or successful physical printing is made.
