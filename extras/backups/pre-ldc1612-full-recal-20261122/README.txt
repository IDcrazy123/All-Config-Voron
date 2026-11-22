Pre-LDC1612 recalibration backup, 2026-11-22.

*.live.cfg files came from Moonraker immediately before SAVE_CONFIG changed
reg_drive_current from 17 to 19. *.git.cfg files are the corresponding
repository versions at the same point. The live QGL macro and tap setting
already differed from Git; this backup preserves both states for comparison.
printer.live.drive19-before-model.cfg was captured after saving drive current
19 and before saving the new 101-point hot Z model.
