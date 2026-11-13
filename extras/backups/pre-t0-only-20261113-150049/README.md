# Backup record

- Date: 2026-11-13 (Asia/Saigon)
- Task: temporary T0-only Klipper include mode.
- printer.repo.cfg: repository entry point before editing.
- printer.live.cfg: Moonraker production file before editing; acquired read-only.
- Restore the five-tool include only after all toolhead boards are reconnected and verified.
- print-macros.repo.cfg and print-macros.live.cfg: original PRINT_START guard before editing.
- Printer-side backup: `/home/voron/printer_data/config_backups/pre-t0-only-20261113-3L1jG9/`.
- The temporary printer.cfg omits saved PID/tool offsets for T1-T4; these remain in the original backups. Merge any newer T0/bed/probe calibration before restoring the five-tool file.
