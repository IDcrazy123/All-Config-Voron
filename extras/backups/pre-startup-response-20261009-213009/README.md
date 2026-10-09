# Pre-change backup — startup G-code response

- Date: 2026-10-09 21:30:09, Asia/Saigon.
- Task: gate unused legacy PTY output at Klipper startup and document remaining production risks.
- Original files copied before edits: `gcode.py` from the actual printer; both documentation indexes; the daily journal; workspace `.agents/KNOWN_ISSUES.md`.
- `gitattributes.before`: original Git attributes before adding LF preservation for the new patch only.
- Printer backup before runtime mutation: `/home/voron/printer_data/config_backups/runtime-pty-20261009-213009/gcode.py`.
- Original Klipper revision: `7bc4d09465d31cd30fc0822e8d0abe02cc8c547f`.
- Original runtime SHA-256: `a2bcd6949b4263f608eaa71ba1cdfb713553542b7b90de739241b624f06415ae`.
- Patched runtime SHA-256: `4ba80ab638b6fa49b92ea07906a198fd49ed08dff42fafebff64be55da600dc8`.
- New files do not replace an earlier file: patch artifact, regression tests and follow-up report. No CFG was edited.
- `deployment.json`: guarded pre-write status, actual backup path, hashes, process ID and service-restart result.
- `verification.json`: both new startup segments, actual first-command serial response and runtime status. CAN counters are recorded separately in `can-status.json`, using the `canbus_stats` objects rather than MCU serial statistics.
- `thermal-observation.json`: later temperature-store sample, affected by separate T1 heater commands; not proof of a sensor fault.
- Journal: `extras/Nhat-ky-chinh-sua/2026-10-09-session-updates.md`, section 6.

Rollback on the same Klipper revision: preserve a fresh copy of current `gcode.py`, restore this original runtime file and restart the Klipper service while idle/unpaused/heaters off. A soft RESTART alone does not reload the core module. Re-home normally before movement. Do not overwrite new-version core source with this old backup after a Klipper update.
