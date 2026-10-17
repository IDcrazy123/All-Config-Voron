# CFG hardening deployment — 2026-10-17

## Result

Deployed the reviewed CFG hardening from commit `4e55588` to
`voron@192.168.1.43:/home/voron/printer_data/config`, together with the installer
phase guard described below. One Moonraker `RESTART` completed successfully.
Klipper reports `ready`; Klipper configuration and Moonraker warnings are empty.
No heating, movement, homing, tool selection, calibration or print was requested.

## Payload and preflight

The eight files transferred, preserving their original permissions, were:

- `Printer-Setup/print-macros.cfg`
- `Printer-Setup/tool-crash.cfg`
- `Printer-Setup/fans-leds.cfg`
- `Printer-Setup/filament-dryer.cfg`
- `Printer-Setup/calibration-probe.cfg`
- `Printer-Setup/input-shaper.cfg`
- `toolchanger/toolchanger-config.cfg`
- `scripts/install.sh`

Before transfer, the printer was confirmed ready/idle, with no active virtual-SD
job or pause, macro phase idle, dryer/heatup bench inactive and all six heater
targets zero. All observed config hashes and runtime Python hashes were checked
again before writing. The live target files matched the pre-hardening baseline;
no unexpected configuration drift was found.

Installed revisions inspected through SSH:

- Klipper: `7bc4d09465d31cd30fc0822e8d0abe02cc8c547f`
- KTC: `e881fe40949a3999b0d63f59c22df589474eae9b`
- Axiscope: `9a1a9efe3cfa6dc1e816acaaea87f8ac513282f6`

Klipper reports `v0.13.0-777-g7bc4d0946-dirty`; existing runtime modifications
were retained. Native Jinja2 2.11.3 compiled 139 templates. The installed macro
rename implementation accepted all five wrapper/base command pairs. Existing
Axiscope lower-level interfaces, KTC empty `RESTORE_AXIS` and the existing crash
patch were verified without running their physical operations.

The installer had admitted the new `calibrating` phase because its old busy
list omitted that value. Its predicate now rejects every phase other than
`idle`, with missing optional macro state still defaulting to idle. A regression
contract checks both `calibrating` and an unknown busy phase before any backup or
copy action. The production CFG runner reports **69 tests: 63 passed, 6 skipped,
zero failures/errors**. The six skips retain the documented two obsolete
historical invariants and four Linux-only PTY checks. Bash syntax also passes.
No existing `.py` source was edited.

## Backups and transfer

Local verified originals and manifest:
`extras/backups/pre-printer-deploy-hardening-20261017-160508/`.
This includes nine exact live originals (eight targets plus `printer.cfg`) and
the pre-edit repository installer, test runner and hardening guide.

Printer backup, verified before the first write:
`/home/voron/printer_data/config_backups/pre-cfg-hardening-deploy-20261017-160614-7hw1x39d/`.
Its `config/` subdirectory preserves the nine live originals; its manifest and
README describe the snapshot. Existing backup directories were retained.

Files were replaced atomically one at a time after all backups and idle checks.
The complete payload was hash-verified before restart and again afterward.
Rollback was not required. Any future rollback should first preserve the new
live state and check for intervening calibration changes, then restore only the
eight target files from this backup while idle; `printer.cfg` is reference-only.

## Post-restart evidence

- All eight deployed hashes match the payload.
- All 26 other observed config/script hashes, six config symlinks and nine
  runtime Python module hashes remain unchanged.
- All 103 pre-existing non-macro hardware/calibration sections, excluding the
  intentionally modified `toolchanger` section, match the pre-deployment state.
- All 14 expected helper/base command names are registered.
- Print status is standby, virtual SD inactive, pause false, macro phase idle,
  recovery latch clear and all six heater targets zero.
- Axes are unhomed after restart. KTC is uninitialized and physically detects T0.
  Initialization/homing was deliberately left for attended operation.

Evidence is stored in `extras/audits/2026-10-17-deployment/`:
`native-preflight.json`, `tests.txt`, `deployment-events.jsonl`,
`verification.json` and `final-integrity.json`. Full transient source/status
captures use ignored `*.local.json` files and are not committed.

## Remaining acceptance

Before the next print, home through the normal reviewed procedure, then perform
an attended short print with end/cancel and pause/load/resume checks on a clear
route. Inspect the new high empty-shuttle park and verify effective shaping
after tool selection. Offline contracts and successful loading do not validate
physical clearance or the complete Klipper/CAN scheduler.

Commission the PF2 calibration fixture separately while attended. No Z offsets,
PID, dock geometry, motor currents, motion limits, hardware wiring, Python runtime
algorithms or Orca JSON presets were changed by this deployment. The previously
reported T1 sensor issue and other hardware/thermal commissioning remain pending.
