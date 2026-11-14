# Pre T4 maintenance backup

- `printer.repo.cfg` and `printer.live.cfg` are byte-identical five-tool copies before disabling T4 (SHA-256 `a5bf84212ee4dde36a001ad9f7d401d5c67d7d3a21c26fc21e1ee09bab83d6ad`).
- `preflight.py` compares the expanded Klipper configuration and SAVE_CONFIG sections with the live five-tool version.
- The same live file is backed up on the printer at `/home/voron/printer_data/config_backups/pre-t4-maintenance-20261114-200533/printer.cfg`.
- The temporary T0-T3 configuration has SHA-256 `af24a88f0ec9aa5272b3b96b3b52cc7c944b749eddc2e43b090a8cf9e547e656`.
- Restore the five-tool include and saved `extruder4` PID / `tool T4` offsets selectively after maintenance. Preserve any newer T0-T3, bed, mesh, or Cartographer calibration.
