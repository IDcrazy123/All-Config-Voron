# Startup response fix and remaining production risks — 2026-10-09

## Result and scope

The operator reports stable operation after exercising the deployed CFG changes.
The console contains G28, QGL and repeated T0–T4 changes without error responses.
These are useful normal-operation checks, but do not exercise the failure paths
below. The T1 CAN issue remains resolved according to the operator; multi-tool
object exclusion remains open.

This follow-up fixes the startup serial-response failure on the actual printer.
No CFG, sensor model, PID, motor current, movement limit, dock coordinate or
calibration value was changed. Remaining motion/calibration/exclusion findings
are proposals, not deployed fixes.

## Startup failure: root cause and deployed fix

The previous 21:09:09 startup logged:

```text
Write g-code response
BlockingIOError: [Errno 11] Resource temporarily unavailable
```

Installed Klipper revision: `7bc4d09465d31cd30fc0822e8d0abe02cc8c547f`.
`GCodeIO` initially enabled legacy PTY output. `util.create_pty()` creates a
nonblocking master and keeps the slave descriptor open. Unread plugin/startup
messages can accumulate across soft restarts and exhaust the output buffer.
Inspection found no accessible external process consuming `klippy.serial`;
Klipper itself held the slave descriptor. This inspection is limited to readable
process descriptors. The exception was caught, so Klipper continued running.

The machine uses Moonraker through `klippy.sock`. Klipper's
[API output subscription](https://www.klipper3d.org/API_Server.html#gcodesubscribe_output)
is independent of the legacy serial output handler.

The [minimal patch](../../config/scripts/patches/klipper-pty-client-gate.patch)
initializes `pipe_is_active` to false. Existing input handling enables it upon
receiving serial input. The command processor, write exception handler, debug
file input, API subscribers and real-time motion/heater code are unchanged.
This prevents unsolicited startup writes to an unused serial channel rather
than hiding the exception or blocking the reactor while retrying writes.

Compatibility limit: serial clients must send input, such as M115, before they
receive serial responses after startup/restart. A client waiting only for an
unsolicited startup banner must change its handshake. The patch does not solve
backpressure after a serial client has already enabled output and stops reading.

### Verification on this printer

- Six regression tests pass on Linux against a patched copy of the actual
  installed source. An isolated nonblocking PTY reproduces the original failure;
  patched repeated restarts preserve API output without filling an unread PTY.
  First-command serial response and existing error/recovery behavior pass.
- Two structural tests also pass on Windows; four real PTY tests require Linux.
- Guarded deployment verified standby/unpaused/idle macro state and all six
  heater targets zero, backed up the runtime, and wrote only the tested change.
- A full Klipper service restart changed PID 767 to 8125, loading the core Python
  change. A subsequent soft RESTART used the same process.
- Both new startup segments, **21:33:51** and **21:34:42** local time, loaded
  Cartographer and contain no matching response-write traceback, config-loading
  failure or shutdown transition. Old tracebacks remain as historical log data.
- M115 through Moonraker returns the firmware identity. The first M115 on the
  actual legacy serial device returns `ok FIRMWARE_NAME:Klipper ...` as well.
- Klipper is ready, registry T0–T4 is loaded, targets/power were zero at the
  verification snapshot, dryer/benchmark were stopped and no print was paused.
  XYZ is unhomed and toolchanger uninitialized after restart, with T0 detected.
  Home/initialize through the normal machine workflow before moving again.
- A separate `canbus_stats` snapshot shows all seven buses active and
  rx_error/tx_error/tx_retries zero. These are sampled counters, not a soak test.

No audit command heated, homed, moved, changed tools or ran calibration. Later
console entries contain brief T1 heater commands from outside this audit; they
must be considered separately when interpreting the temperature history.

### Recovery and maintenance

Runtime backup on the printer:
`/home/voron/printer_data/config_backups/runtime-pty-20261009-213009/gcode.py`.
The [local backup record](../backups/pre-startup-response-20261009-213009/README.md)
contains the same original source, deployment hashes and verification evidence.

Original SHA-256: `a2bcd6949b4263f608eaa71ba1cdfb713553542b7b90de739241b624f06415ae`.
Patched SHA-256: `4ba80ab638b6fa49b92ea07906a198fd49ed08dff42fafebff64be55da600dc8`.

This is a local Klipper runtime patch. Sharing a CFG does not require it. The CFG
installer copies the patch artifact but **does not apply it automatically**.
A Klipper update may remove it or require different context. Check the current
source and repeat the Linux tests before applying it to another revision.
The artifact is also installed at
`~/printer_data/config/scripts/patches/klipper-pty-client-gate.patch`.

For an unpatched compatible checkout, first confirm the printer is idle,
unpaused, with heaters/dryer/benchmark off and no queued operation. Then, over
SSH, create a fresh backup and check the patch with exact context:

```sh
task_backup=$(mktemp -d "$HOME/printer_data/config_backups/runtime-pty-XXXXXX")
cp -p "$HOME/klipper/klippy/gcode.py" "$task_backup/gcode.py"
cd "$HOME/klipper"
patch --dry-run --fuzz=0 -p1 < "$HOME/printer_data/config/scripts/patches/klipper-pty-client-gate.patch"
```

If dry-run fails, stop: it may already be patched or the source may differ.
After reviewing the diff and repeating the PTY tests, apply the same patch and
restart the **Klipper service**, not just the firmware or soft RESTART:

```sh
patch --fuzz=0 -p1 < "$HOME/printer_data/config/scripts/patches/klipper-pty-client-gate.patch"
curl --fail -H 'Content-Type: application/json' -d '{"service":"klipper"}' \
  http://127.0.0.1:7125/machine/services/restart
```

The [Moonraker service API](https://moonraker.readthedocs.io/en/latest/external_api/machine/#restart-a-service)
performs the service restart. Wait for ready, inspect the new startup segment
and check M115. This resets homing state. For rollback on the same Klipper
checkout, back up the current file, restore `gcode.py` from this runtime backup,
and restart the service while idle. Do not restore an old core file over a
different Klipper revision; review/reverse the small patch instead.

## Remaining risks and proposed next changes

| Priority | Trigger / consequence | Concrete proposed change and validation |
| --- | --- | --- |
| P1 | **PRINT_END near max Z.** `print-macros.cfg:422` still requests relative Z+5 before later clamping. At physical Z345/max347 it requests Z350 and can abort before heater shutdown. END/CANCEL also combine physical Z with G-code coordinates while offsets are active. | Compute the lift in one frame using actual remaining physical clearance; validate resulting XY/Z commands with positive/negative tool offsets. Put essential heater shutdown in a separately evaluated stage that still runs if parking fails. Cold replay at bottom/top limits before attended motion tests. |
| P1 | **Cancel after a crash.** Homed axes do not prove that a dropped/skewed tool is safely attached. `_CUSTOM_CANCEL_CLEANUP` in `fans-leds.cfg:655` lifts, UNSELECTs and parks whenever XYZ is homed. | Latch crash recovery state and route the whole cancel entry to a no-motion heater-off path until the operator confirms attachment/recovery. Review retract and client hooks too. Test crash/no-crash cancel paths without modifying upstream `mainsail.cfg`. |
| P1 | **Axiscope final return.** Installed `cmd_CALIBRATE_ALL_Z_OFFSETS` issues final T0 at line 267 before `finish_gcode`. The Z probe can return near Z3; the finish hook is too late to protect that toolchange. | Add a reviewed pre-final-toolchange lift/hook or split wrapper. Verify snapshot timing, homing, offsets and all return paths. Keep calibration save disabled until an attended test proves clearance. |
| P1 | **EXCLUDE_OBJECT with multiple extruders.** Current runtime has per-extruder offsets but shared last/max/adjust extrusion state. Exclusion exit can turn a travel into unintended extrusion and abort. | Backport E state per extruder against the installed API; replay the previously failing G-code with tool changes, absolute/relative E, G92 and object transitions, then an attended small multi-tool coupon. Continue avoiding object exclusion in multi-tool jobs; raising extrusion limits is not a fix. |
| P2 | **Inherited KTC damping.** Per-tool damping defaults to truthy 0.1 while the measured global values are X0.124/Y0.080. Zero frequency overrides alone do not select the whole global profile. | Explicitly choose the entire global profile when no per-tool profile is enabled, then inspect shaping after every toolchange. Keep current tuning until this change is deliberately commissioned. |
| P2 | **Diagnostic interruption.** Normal speed-test completion restores captured runtime limits; a command error/interruption may bypass restoration. Benchmark/dryer timeout uses ticks rather than an absolute clock. | Add an explicit recover/status procedure for interrupted diagnostics; consider monotonic runtime timing if bounded wall-clock duration is required. Test queued cancellation and ownership transfer before claiming a hard timeout. |
| P2 | **Prime/mesh/object clearance on other machines.** Axis limits include docking travel and do not define printable bed or adaptive-mesh coverage. | Reserve the prime area in the slicer and verify mesh coverage, brush/dock paths and all final wipes for the recipient's bed/tools. Local comments cannot establish physical clearance. |
| Investigation | **T1 temperature difference.** Initial idle snapshots showed about 56°C for T1 versus 32–33°C for the other tools, with target/power zero. The operator says the preceding print used T0/T4, not T1, and asks to investigate later. Later manual T1 heating complicates the current history. | After a full cool-down with all heaters off, compare T1 with an independent measurement and the other tools; check thermistor specification, connector and EBB input/pull-up only against actual hardware. No sensor/PID adjustment from an assumed ambient temperature. |

Crash-cancel clarification: upstream Mainsail's **early park is conditional** on
`park_at_cancel`, which is not enabled by this machine's client variables.
The always-relevant current hazard is the project's later custom cleanup motion.
Thus the earlier audit's unconditional wording about early Mainsail parking was
too broad; the crash-cancel finding itself remains valid.

Axiscope and exclude-object source hashes were rechecked against the installed
files and match the runtime copies used in the original audit. Their findings
are still present, not inferred solely from an old issue list. Normal operator
tests do not close these edge cases. The
[original audit](project-audit-2026-10-09.md) remains historical evidence; this
follow-up records current status and the clarification above.
