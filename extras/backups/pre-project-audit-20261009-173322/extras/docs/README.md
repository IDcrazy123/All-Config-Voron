# Documentation Index

[English](README.md) | [Tiếng Việt](README.vi.md)

Current documents describe the loaded production code as of 2026-09-21. Historical reports remain immutable and are clearly separated so retired commands are not mistaken for active procedures.

## Current documentation

| Topic | English | Vietnamese |
| --- | --- | --- |
| Project overview | [README](../../README.md) | [README](../../README.vi.md) |
| Active config payload | [README](../../config/README.md) | [README](../../config/README.vi.md) |
| OrcaSlicer profiles | [README](../../Orca%20Config/README.md) | [README](../../Orca%20Config/README.vi.md) |
| StealthChanger operation | [Guide](huong-dan-he-thong-stealthchanger.en.md) | [Guide](huong-dan-he-thong-stealthchanger.md) |
| Mainsail deployment cross-check | — | [Guide](danh-sach-doi-chieu-va-huong-dan-update-mainsail.md) |
| Legacy calibration failure signatures | [Guide](legacy-calibration-troubleshooting.md) | Same technical guide |
| Oxplow multi-tool Z calibration | [Comprehensive method](Oxplow-Z-Offset-Comprehensive-Method.md) | [Quick guide](Oxplow-Z-Offset-Guide.md) |
| Input shaper / speed evaluation | — | [Report](danh-gia-input-shaper-va-test-speed-2026-09-04.md) |

## Historical documentation

The following guides describe retired integrations and have moved to [`history/`](history/README.md):

- kTAMV usage and method comparison (English/Vietnamese);
- TKC commissioning notes from 2026-09-08.

They must not be used as installation or calibration instructions for the current machine.

## Immutable evidence

- `extras/Nhat-ky-chinh-sua/`: dated engineering history.
- `extras/experiments/`: raw test reports and reproductions.
- `extras/retired-configs/`: last known configurations for removed backends.
- `extras/backups/`: pre-change recovery snapshots.
- `extras/Config download/`: downloaded machine snapshots; not active configuration.

Ten ZIP archives that were byte-for-byte duplicates of retained extracted snapshot directories were removed during the 2026-09-20 audit. `config-20260903-080600.zip` was retained because it contains six ShakeTune files not present in its extracted directory. Standalone ZIP snapshots and all recovery backups were also retained.

## Maintenance rules

1. Read loaded code before changing current-state claims.
2. Update English/Vietnamese companion files together.
3. Never modernize old journals, experiment reports, backup records, or downloaded snapshots in place.
4. Move retired procedures to `history/` and add a short current warning.
5. When code behavior changes, update documentation and the daily journal in the same commit.
