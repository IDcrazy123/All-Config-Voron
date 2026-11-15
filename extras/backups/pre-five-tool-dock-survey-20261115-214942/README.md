# Before five-tool restoration for dock survey

Snapshot made before restoring T0–T4 on 2026-11-15. The active printer was in T1-only mode.

- `printer.repo.cfg`, `print-macros.repo.cfg`, `T1.repo.cfg`: repository copies before restoration.
- Matching `.live.cfg` files: exact Moonraker downloads before restoration.
- `T3.*.cfg` and `hardware.*.cfg`: evidence of two pre-existing live/repository differences. The live T3 runout input is `^EBB3:PB8`; the hardware difference is comments only. Production copies were retained and the repository was synchronized to them.
- `preflight.py`: parses the staged five-tool candidate and G-code templates against the T1-only live config.

The earlier five-tool configuration used for restoration is preserved in `../pre-t0-removal-t1-only-20261115-195358/`. A copy of the live pre-restoration files is also stored on the Pi under `/home/voron/printer_data/config-backups/five-tool-dock-survey-20261115-214942/`.
