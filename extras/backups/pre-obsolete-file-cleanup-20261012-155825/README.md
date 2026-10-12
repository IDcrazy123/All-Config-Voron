# Pre-cleanup recovery record

- Created: 2026-10-12T16:02:56+07:00
- Task: Remove superseded backups, downloaded snapshots, retired configuration copies, old G-code, offline logs and regenerable caches at the operator's explicit request.
- Base Git commit: `cc0a8dcda2835e49c77cebaed87e4da991d5b98a`
- External recovery archive: `D:\Desktop\Voron-cleanup-archive-20261012-155825\removed-files.zip`
- Inventory: [removed-files.csv](removed-files.csv), including SHA-256 and Git tracking status for every removed file.
- Original documentation: `original-documents/` preserves every existing document edited by this cleanup.
- Journal: `extras/Nhat-ky-chinh-sua/2026-10-12-session-updates.md`.
- Production configuration, Orca profiles, reference submodules, current Oxplow release files and existing engineering journals are preserved.

The external archive is local and is not uploaded to GitHub. Git-tracked files remain recoverable at the base commit after the cleanup commit is pushed; ignored/untracked files require the external archive. No Git history is rewritten.

For full local recovery, extract `removed-files.zip` to a new empty directory. Its paths start with `Voron 5 Tool/` or `.local-backups/`. Inspect individual files before copying them back; do not deploy an old configuration to the printer automatically.

## Executed safe fallback

- Removed from workspace by reversible move: **961 files / 925.66 MiB**, across 117 selected roots (including 107 backup directories).
- Original files remain under `D:\Desktop\Voron-cleanup-archive-20261012-155825\moved-originals`; **zero files were permanently deleted**.
- Verified ZIP: **229.54 MiB** (`removed-files.zip`), all member SHA-256 and CRC checks passed; the moved originals also passed the same per-file hashes.
- Automatic review rejected both recursive removal and individual file deletion with `blocked by policy`; no more specific reason was supplied. Reversible relocation succeeded.
- **No disk space was reclaimed on D:** the moved originals remain on the same drive, and the ZIP adds about 229.54 MiB. Permanently removing `moved-originals` after checking the ZIP must be done manually if disk reclamation is wanted. The ZIP alone would retain the original data in about 229.54 MiB.
- Production config, readonly files, Orca profiles, pending Printables edits, existing journals, experiment evidence, audits and workspace rules passed SHA-256 preservation checks.
- 18 prior backup directories remain, plus this cleanup recovery record (19 total).
- Historical links into removed directories are resolved through the manifest, archive and recorded base Git commit; existing dated journals/reports were not rewritten.
- Documentation indexes and the legacy troubleshooting baseline now point to the retained Axiscope architecture and recovery records.
- No connection to the printer, runtime deployment, heating, movement, restart or physical print test was performed.

## Final manifest validation

Use [removed-files-corrected.csv](removed-files-corrected.csv), identical to the final public manifest. The original prepared manifest above remains unchanged for traceability. Three workspace-only `.local-backups` rows were corrected to untracked; their files were never in the child repository Git history. File hashes/archive paths are unchanged. `manifest-correction.json` records the final manifest hash.
