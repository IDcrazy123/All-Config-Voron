# Pre T4 restore backup

- `printer.repo.cfg` and `printer.live.cfg` are byte-identical T0-T3-mode copies before restoration (SHA-256 `af24a88f0ec9aa5272b3b96b3b52cc7c944b749eddc2e43b090a8cf9e547e656`).
- `preflight.py` compares the expanded Klipper configuration and SAVE_CONFIG sections with the live four-tool version.
- The same live file is backed up on the printer at `/home/voron/printer_data/config_backups/pre-t4-restore-20261114-221714/printer.cfg`.
- The restored five-tool source from `extras/backups/pre-t4-maintenance-20261114-200533/printer.live.cfg` has SHA-256 `a5bf84212ee4dde36a001ad9f7d401d5c67d7d3a21c26fc21e1ee09bab83d6ad`.
