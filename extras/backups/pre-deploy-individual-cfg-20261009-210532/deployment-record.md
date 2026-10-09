# Deployment result

- Printer: 192.168.1.43 / voron
- Deployed source commit: 4041d5ee90db9b1e55485d40402ef5ed0c82cad2
- Remote full live backup: /home/voron/printer_data/config_backups/config-install-20261009-210823-F2BuYW
- Local live pre-change payload: live-config-before.tar (28 existing files; no secrets or generated data).
- Installed content changes: 18 user-owned CFGs and scripts/install.sh.
- Nine other payload files retained their exact live content, including mainsail.cfg and service configuration.
- Six KTC readonly links preserved; tool_crash runtime was already patched and was not changed.
- Live Jinja 2.11.3: 25 include files, 126 templates compiled before writes.
- Klipper RESTART succeeded; state ready, T0-T4 registered, new heatup continuation loaded, heater targets zero.
- Read-only CALIBRATION_STATUS, CHECK_OFFSETS, QUERY_ENDSTOPS succeeded.
- See verification-after-restart.json for loaded state, offsets, CAN status and one nonfatal startup G-code output-pipe BlockingIOError.
- No homing/toolchange, heating, calibration or print test performed.
- Existing EXCLUDE_OBJECT/lifecycle/calibration/shaper issues remain open.
