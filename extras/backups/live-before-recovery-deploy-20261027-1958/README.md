# Live printer backup before selective macro deployment

- Source: Moonraker `192.168.1.43:7125`, `config` root, 2026-10-27 19:58 +07:00.
- Files: `Printer-Setup/print-macros.cfg`, `Printer-Setup/tool-crash.cfg`, and
  `Printer-Setup/hardware.cfg`.
- The two macro files exactly matched their pre-edit repository backups by
  SHA256 when downloaded. `hardware.cfg` is included to preserve the live
  `heater_bed.max_temp: 150` difference; it is not part of the selective upload.
- Restore either macro from this folder only while the printer is idle, then
  restart Klipper and verify the active configuration.
- At 20:14 +07:00, only those two macro files were uploaded and Klipper was
  restarted while the printer was idle. Both uploads matched the repository
  SHA256 hashes; `hardware.cfg` remained unchanged with `max_temp: 150`.
