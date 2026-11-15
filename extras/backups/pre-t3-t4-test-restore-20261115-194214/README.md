# Pre T3/T4 test restore backup

- `printer.repo.cfg` and `printer.live.cfg` are byte-identical T0-T2-mode copies before restoration (SHA-256 `000c9a1ee7d1570bd4c105721e41df27988a264872ab04e87f6f824fae72fe52`).
- `preflight.py` compares the expanded Klipper configuration and SAVE_CONFIG sections with the live three-tool version.
- The same live file is backed up on the printer at `/home/voron/printer_data/config_backups/pre-t3-t4-test-restore-20261115-194214/printer.cfg`.
- The restored five-tool source from `extras/backups/pre-t4-filament-sensor-maintenance-20261115-091735/printer.live.cfg` has SHA-256 `a5bf84212ee4dde36a001ad9f7d401d5c67d7d3a21c26fc21e1ee09bab83d6ad`.
