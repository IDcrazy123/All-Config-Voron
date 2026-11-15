# Before five-tool dock coordinate update

Snapshot made before applying operator-provided dock positions on 2026-11-15.

- `T0` through `T4` `.repo.cfg` and `.live.cfg` files preserve the Git and Moonraker versions before editing; they matched byte for byte.
- `preflight.py` compares the proposed configuration with production and checks the candidate dock path coordinates against configured travel limits.
- Only T0, T2, T3 and T4 require value changes. T1 was already X104 Y0 Z330.

The dock coordinates are operator-provided geometry. Static checks do not verify physical pickup or dropoff. The production backup, if deployment proceeds, is under `/home/voron/printer_data/config-backups/five-dock-coordinates-20261115-221710/`.
