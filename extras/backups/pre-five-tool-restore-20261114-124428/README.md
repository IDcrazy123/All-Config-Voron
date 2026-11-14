# Pre five-tool restore backup

- `printer.repo.cfg` and `printer.live.cfg` are byte-identical T0/T1-mode copies before restoration (SHA-256 `9f620f3cfc1226d12de5e7ff0e0634351deb6ae9395e3589e27a5e3dc05cf534`).
- The same live file is backed up on the printer at `/home/voron/printer_data/config_backups/pre-five-tool-restore-20261114-124428/printer.cfg`.
- The restored five-tool source from `extras/backups/pre-second-t2-t4-maintenance-20261114-122627/printer.live.cfg` has SHA-256 `a5bf84212ee4dde36a001ad9f7d401d5c67d7d3a21c26fc21e1ee09bab83d6ad`.
- The prior preflight script in `extras/backups/pre-five-tool-restore-20261114-121710/` was rerun against the current live file.
