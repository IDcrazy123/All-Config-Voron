# Pre T3 maintenance backup

- `printer.repo.cfg` and `printer.live.cfg` are byte-identical T0-T3-mode copies before disabling T3 (SHA-256 `af24a88f0ec9aa5272b3b96b3b52cc7c944b749eddc2e43b090a8cf9e547e656`). T4 was already disabled.
- `preflight.py` compares the expanded Klipper configuration and SAVE_CONFIG sections with the live T0-T3 version.
- The same live file is backed up on the printer at `/home/voron/printer_data/config_backups/pre-t3-maintenance-20261115-163710/printer.cfg`.
- The temporary T0-T2 configuration has SHA-256 `000c9a1ee7d1570bd4c105721e41df27988a264872ab04e87f6f824fae72fe52`.
- Restore the T3 include and saved `extruder3` PID / `tool T3` offsets selectively after its maintenance. T4 remains disabled until separately restored. Preserve newer calibration of T0-T2, bed, mesh, and Cartographer.
