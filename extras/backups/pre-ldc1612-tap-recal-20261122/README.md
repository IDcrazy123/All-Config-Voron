# Pre-tap calibration live backup

Captured from `/home/voron/printer_data/config/` on 2026-11-22 before recalibrating the replacement LDC1612 tap threshold at bed 100°C and T0 150°C.

- `printer.live.cfg`: active root config and SAVE_CONFIG values before the tap run.
- `calibration-probe.live.cfg`: active probe and tap macro configuration.
- `printer.git-pre-sync.cfg`: repository root config before copying the verified live tap threshold.
- `calibration-probe.git-pre-sync.cfg`: repository probe config before copying the operator's live tap Z offset.

These are reference copies. Do not deploy them over newer live settings without comparing every section.
