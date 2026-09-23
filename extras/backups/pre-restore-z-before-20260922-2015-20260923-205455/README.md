# Backup before restoring the pre-20:15 tool Z offsets

- Date: 2026-09-23; task snapshot identified at 20:54:55 +07:00.
- Request: Restore only T1-T4 Z offsets to their values before commit `7763e82` (2026-09-22 20:15:07 +07:00), preserving current X/Y and all other settings.
- `repository/printer.cfg` and `live/printer.cfg`: Exact current copies before any rollback. SHA256 for both: `d29aa55da363ae1e09711053b16f2788339a8ab322193b1480526acf84dd247a`.
- Current Z (T1/T2/T3/T4): `0.242 / -0.284 / -0.232 / 0.086`.
- Requested target Z: `0.2465 / -0.2715 / -0.2465 / 0.1079`.
- Target evidence: `extras/backups/pre-sexbolt-z-1837-20260922-200957/live/printer.cfg`; do not overwrite that historical backup.
- Independent printer-side current backup: `/home/voron/printer_data/config_backups/restore-z-before-20260922-2015-20260923-205455/original/printer.cfg`.
- Journal: `extras/Nhat-ky-chinh-sua/2026-09-23-session-updates.md`.
