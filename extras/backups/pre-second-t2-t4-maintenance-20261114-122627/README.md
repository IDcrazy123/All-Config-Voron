# Pre second T2-T4 maintenance backup

- `printer.repo.cfg` and `printer.live.cfg` are byte-identical five-tool copies before this change (SHA-256 `a5bf84212ee4dde36a001ad9f7d401d5c67d7d3a21c26fc21e1ee09bab83d6ad`).
- The same live file is backed up on the printer at `/home/voron/printer_data/config_backups/pre-second-t2-t4-maintenance-20261114-122627/printer.cfg`.
- The temporary T0/T1 configuration has SHA-256 `9f620f3cfc1226d12de5e7ff0e0634351deb6ae9395e3589e27a5e3dc05cf534`. The prior preflight script in `extras/backups/pre-t2-t4-maintenance-20261114-073028/` was rerun against the current live file.
- Restore the five-tool include and the saved `extruder2`-`extruder4` PID and `tool T2`-`tool T4` offsets selectively after maintenance. Preserve any newer T0, T1, bed, mesh, or Cartographer calibration.
