Backup of repository and live printer.cfg before updating preliminary PF2 tool Z offsets on 2026-11-27.
Live is the source for the production edit; unrelated live SAVE_CONFIG and QGL differences must be preserved.

- printer.git.cfg: repository copy before the edit.
- printer.live.cfg: exact production copy before the edit, SHA-256 a7813e58a7dd711dd9930068e8d7fa61fc2c9aceb6092db09993ea9c05596aa8.
- printer.live.proposed.cfg: reviewed four-line production edit, SHA-256 3b27bf87626b64f654477d14a51a38e310ce3890d0beef1e53f5c4aae7462273.
- AGENTS.before.md and KNOWN_ISSUES.before.md: project notes before documenting the change.
- apply_live_offsets.py: verifies both hashes, backs up and atomically replaces the live file.
- Production backup: /home/voron/printer_data/config/printer-20261127-pre-pf2-z-offsets.cfg.
