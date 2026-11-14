# Pre T2-T4 maintenance backup

- `printer.repo.cfg` and `printer.live.cfg` are byte-identical copies of the five-tool `printer.cfg` before this change (SHA-256 `a5bf84212ee4dde36a001ad9f7d401d5c67d7d3a21c26fc21e1ee09bab83d6ad`).
- `preflight.py` checks the expanded Klipper configuration against the live five-tool version.
- The same live file is backed up on the printer at `/home/voron/printer_data/config_backups/pre-t2-t4-maintenance-20261114-073028/printer.cfg`.
- Restore the five-tool include and the saved `extruder2`-`extruder4` PID and `tool T2`-`tool T4` offsets selectively after maintenance. Preserve any newer T0, T1, bed, mesh, or Cartographer calibration.
