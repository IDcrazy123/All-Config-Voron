# Pre five-tool restore backup

- `printer.repo.cfg` and `printer.live.cfg` are byte-identical T0/T1-mode copies before restoration (SHA-256 `9f620f3cfc1226d12de5e7ff0e0634351deb6ae9395e3589e27a5e3dc05cf534`).
- `preflight.py` compares the expanded Klipper configuration and SAVE_CONFIG sections before restoration.
- The same live file is backed up on the printer at `/home/voron/printer_data/config_backups/pre-five-tool-restore-20261114-121710/printer.cfg`.
- The five-tool source restored from `extras/backups/pre-t2-t4-maintenance-20261114-073028/printer.live.cfg` has SHA-256 `a5bf84212ee4dde36a001ad9f7d401d5c67d7d3a21c26fc21e1ee09bab83d6ad`.
