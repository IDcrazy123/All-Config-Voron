# Retired Tool-Klipper-Calibration (TKC) Configuration

`tool_calibrator.cfg` and `tool_offsets.cfg` were removed from the active production include tree on 2026-09-13 during the cleanup of experimental calibration backends.

The repository standardizes on **kTAMV** for supervised camera-based XY tool alignment.

The files are preserved here for historical reference and potential rollback. They are not deployed to `~/printer_data/config` and must not be included in `printer.cfg`.

The pre-removal state is preserved in the backup directory:
`extras/backups/pre-cleanup-kcc-tkc-and-ktamv-autocalib-20260913-171300/`.
