# Documentation Index

[English](README.md) | [Tiếng Việt](README.vi.md)

Current documents include the production reviews and deployments through 2026-10-17. Historical reports remain immutable and are clearly separated so retired commands are not mistaken for active procedures.

## Current documentation

| Topic | English | Vietnamese |
| --- | --- | --- |
| CFG follow-up 2026-10-17 | [Fixes and remaining issues](cfg-followup-2026-10-17.md) | Deployed; physical acceptance pending; Python unchanged |
| CFG software hardening 2026-10-16 | [Changes and commissioning](cfg-hardening-2026-10-16.md), [deployment](cfg-deployment-2026-10-17.md) | Deployed October 17; Python files unchanged |
| Cleanup, incident lessons and recovery 2026-10-12 | [Summary](cleanup-2026-10-12.md) | [Tổng hợp](cleanup-2026-10-12.vi.md) |
| Code/machine audit 2026-10-09 | [Report](project-audit-2026-10-09.md) | English technical report |
| Startup G-code response and remaining risks | [Follow-up](startup-response-and-risk-review-2026-10-09.md) | Runtime fix verified; motion/exclusion risks remain open |
| Adaptation to another machine | [Guide](machine-adaptation.md) | English technical guide |
| Sharing existing CFG files individually | [Implementation guide](sharing-cfg-files.md) | File prerequisites/local edits; deployed to current printer, no physical feature tests |
| Sharing design rationale | [Revised proposal](stealthchanger-sharing-proposal.md) | Implemented scope/status is recorded in the guide above |
| Project overview | [README](../../README.md) | [README](../../README.vi.md) |
| Active config payload | [README](../../config/README.md) | [README](../../config/README.vi.md) |
| OrcaSlicer profiles | [README](../../Orca%20Config/README.md) | [README](../../Orca%20Config/README.vi.md) |
| StealthChanger operation | [Guide](huong-dan-he-thong-stealthchanger.en.md) | [Guide](huong-dan-he-thong-stealthchanger.md) |
| Mainsail deployment cross-check | — | [Guide](danh-sach-doi-chieu-va-huong-dan-update-mainsail.md) |
| Legacy calibration failure signatures | [Guide](legacy-calibration-troubleshooting.md) | Same technical guide |
| Oxplow 2.3.2 multi-tool Z calibration | [Comprehensive method](Oxplow-Z-Offset-Comprehensive-Method.md) | [Quick guide](Oxplow-Z-Offset-Guide.md) |
| Input shaper / speed evaluation | — | [Report](danh-gia-input-shaper-va-test-speed-2026-09-04.md) |

## Historical documentation

The following guides describe retired integrations and have moved to [`history/`](history/README.md):

- kTAMV usage and method comparison (English/Vietnamese);
- TKC commissioning notes from 2026-09-08.

They must not be used as installation or calibration instructions for the current machine.

## Immutable evidence

- `extras/Nhat-ky-chinh-sua/`: dated engineering history.
- `extras/experiments/`: raw test reports and reproductions.
- `extras/retired-configs/`: recovery index; old configuration copies were archived outside the checkout on 2026-10-12.
- `extras/backups/`: retained pre-change recovery snapshots and the dated cleanup recovery record.
- `extras/Config download/`: recovery index for archived downloaded machine snapshots; not active configuration.
- `extras/Printables-Package/`: current Oxplow generator and release files; the older `extras/gcode/` copy was archived.

The September 20 audit removed ten duplicate ZIPs and retained the other snapshots/backups at that time. On October 12, the operator requested cleanup of obsolete files. 107 superseded backup directories, all old downloaded snapshots (including the September 3 ZIP with unique ShakeTune data), retired configuration copies, old G-code and offline logs were moved to local recovery storage after verified compression. Their data remains in the archive and, where tracked, Git history. See the [per-file manifest](cleanup-2026-10-12-manifest.csv); existing historical links into these locations should be resolved through that manifest. Reports, reproductions, journals and raw experiment evidence remain in this checkout.

## Maintenance rules

1. Read loaded code before changing current-state claims.
2. Update English/Vietnamese companion files together.
3. Never modernize old journals, experiment reports, backup records, or downloaded snapshots in place.
4. Move retired procedures to `history/` and add a short current warning.
5. When code behavior changes, update documentation and the daily journal in the same commit.

Oxplow 2.3.2: [machine profiles, G-code, SVG and reports](../Printables-Package/README.md). The upstream published toolkit is preserved unchanged; retired 2.0.0 files are retained separately.
