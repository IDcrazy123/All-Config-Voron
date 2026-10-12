# Offline log recovery

Historical offline Klipper/Moonraker/TKC captures were moved out of this checkout on 2026-10-12 after verified compression. Names, sizes and hashes are in the [cleanup manifest](../docs/cleanup-2026-10-12-manifest.csv); recovery locations are in the [summary](../docs/cleanup-2026-10-12.md).

Daily journals, [T1 temperature history](../experiments/t1-temperature-history-20261009/README.md), October audits and raw experiment evidence remain available. Ignored log captures require the local recovery archive; Git alone does not contain them all. Capture a fresh dated log for new failures instead of treating an old snapshot as current machine state.
