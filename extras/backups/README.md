# Retained recovery snapshots

The operator requested obsolete-file cleanup on 2026-10-12. 107 pre-change backup directories before the 2026-09-30 baseline were moved to external recovery storage after ZIP integrity and every file hash were verified.

18 existing directories remain: snapshots at/after the September 30 baseline plus two excluded uncommitted backups (`pre-oxplow-generator-20260920-154612` and `pre-persist-live-calibration-20260929-203905`). This cleanup adds its own [recovery record](pre-obsolete-file-cleanup-20261012-155825/README.md).

New edits still require timestamped pre-change backups. This operator-requested cleanup does not authorize future automatic pruning. Use the [dated report](../docs/cleanup-2026-10-12.md) and [manifest](../docs/cleanup-2026-10-12-manifest.csv) to resolve historical backup links.
