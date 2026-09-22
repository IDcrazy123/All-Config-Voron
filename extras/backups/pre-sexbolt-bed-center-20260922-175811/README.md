# SexBolt bed-center relocation backup

- Date: 2026-09-22 17:58:11 +07:00
- Task: Move the attended SexBolt measurement target from X80/Y-5.5 to the configured bed center X174/Y168.
- `repository/`: Original repository copies of `Printer-Setup/calibration-probe.cfg` and `toolchanger/toolchanger-config.cfg`.
- `live/`: Exact copies of those files from the printer before deployment.
- Live overrides before this change: `lower_z: 0.3` and approach `variable_z: 12.0`; the repository had `1.0` and `18.0` respectively.
- The operator confirmed Z55 for safe transit. The new holder's contact and probe-start heights have not been supplied; guards prevent automatic probing with unmeasured heights.
- Production `printer.cfg` offsets are outside the deployment scope.
- Journal: `extras/Nhat-ky-chinh-sua/2026-09-22-session-updates.md`.
