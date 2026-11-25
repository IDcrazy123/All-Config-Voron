# Temporary EBB isolation test backup

- `klipper.env.original` is the exact live `/home/voron/printer_data/systemd/klipper.env` before changing the Klipper config entry point. SHA-256: `F1A5D00872196EC546FAA2060DF58D4F182E31B8B4D7C1FFE92D3A53CA47CB7C`.
- The first temporary profile is `config/diagnostics/ldc-only.cfg`; it declares only the main Manta MCU and EBB0. The second, `config/diagnostics/ldc-main-only.cfg`, declares only Manta. Neither provides motion or heater outputs.
- The active `klipper.env` was still unchanged when this backup was created. Candidate env files are staged on the host as `klipper.env.ldc-only` and `klipper.env.ldc-main-only`; the latter was activated for the EBB0 test.
- Restoration completed on 25 Nov: the original env was copied back before the operator reconnected EBB0–EBB4 with printer power off. After power-up, the hash matched this backup, Klipper was `ready` under `printer.cfg`, all six MCUs were visible, and heater targets were zero. T0 was detected; toolchanger was `uninitialized` and XYZ unhomed after reboot. No motion or heater command was sent.
