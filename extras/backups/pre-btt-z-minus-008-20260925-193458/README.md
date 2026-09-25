# Backup before persisting BTT screen Z adjustments

- Date: 2026-09-25 19:34:58 +07:00.
- Task: Apply the operator-confirmed additional `-0.0800 mm` adjustment to T1-T4 saved tool Z offsets, then restart only while idle.
- Files: `repository/printer.cfg` and `live/printer.cfg`, exact pre-change copies.
- SHA256 for both: `8d6b2958bab328e8afeace4b0d6aa11fb2f05854ceef9f738e9f083d978878b9`.
- Original Z (T1/T2/T3/T4): `0.2465 / -0.2715 / -0.2465 / 0.1079`.
- Confirmed target Z: `0.1665 / -0.3515 / -0.3265 / 0.0279`.
- Preserve T0, X/Y, Cartographer, mesh, PID, and all other configuration.
- Printer-side backup: `/home/voron/printer_data/config_backups/btt-z-minus-008-20260925-193458/original/printer.cfg`.
- Journal: `extras/Nhat-ky-chinh-sua/2026-09-25-session-updates.md`.
