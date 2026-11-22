# Backup before restoring native default QGL probing

The `*.git.cfg` files are the repository versions before this change.
The `*.live.cfg` files were copied from the printer before editing.
The live `print-macros.cfg` matched Git. The live probe config had a
commented I2C speed override and tap_z_offset 0.1; the live printer.cfg had
tap_threshold 18555.665. These live operator changes were preserved in Git
before deployment.

No backup file is in the active Klipper include tree.
