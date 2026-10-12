# Historical Calibration Documentation

Files in this directory describe retired calibration systems. They are retained for failure analysis and migration history, not for current operation.

| Document | Historical scope | Replacement |
| --- | --- | --- |
| `ktamv-usage-comparison.en.md` / `.vi.md` | kTAMV runtime and ToolVision comparison used before 2026-09-18 | Axiscope Web UI on port 3000 |
| `tkc-commissioning-20260908.md` | Experimental TKC/KCC commissioning and defects | Axiscope for tool offsets; Cartographer for home/mesh |

Before using any command from these documents, confirm the corresponding backend is intentionally installed in an isolated test environment. None of these procedures belongs in the production include chain.

Old references into backup, log, downloaded-snapshot and retired-configuration directories now resolve through the [2026-10-12 cleanup inventory](../cleanup-2026-10-12.md). The historical documents themselves are retained unchanged; recover referenced files from the manifest/archive or the recorded base Git commit.
