UNIVERSAL OXPLOW FIRST-LAYER Z-OFFSET CALIBRATION

Product page:
https://www.printables.com/model/1846885-universal-oxplow-first-layer-z-offset-calibration

Oxplow prints a continuous first-layer height ramp instead of separate test squares. The front is intentionally too close, the back is intentionally too far away, and the smooth region between them reveals the required physical nozzle-height correction.

For the default 0.4 mm nozzle, the 20 x 20 mm patch ranges from Z=0.150 mm to Z=0.350 mm around a nominal Z=0.250 mm center. Its 51 lines provide 0.004 mm Z resolution. Every 1 mm measured along Y represents 0.010 mm of physical Z correction.

READING THE PRINT

1. Find the smooth region with joined lines and no ridges or gaps.
2. Measure from the front edge to the center of that region.
3. Calculate: Delta Z = (measured Y - 10.0 mm) x 0.010 mm/mm.
4. Positive means physically raise the nozzle; negative means physically lower it.

Firmware can store Z-offset with different sign conventions. On the author's StealthChanger configuration, use Z_new = Z_current + Delta Z. Verify your printer's convention before saving a value.

PYTHON GENERATOR

Interactive wizard:
python generate_oxplow_gcode.py -i

Author's 350 mm, 5-tool Voron preset:
python generate_oxplow_gcode.py --preset voron-350-5tool --material PETG

Ender 3-class Marlin printer with a saved mesh:
python generate_oxplow_gcode.py --preset ender3 --material PLA --mesh marlin

Preset with a 0.6 mm nozzle override:
python generate_oxplow_gcode.py --preset ender3 --nozzle-dia 0.6 --material PETG

Run python generate_oxplow_gcode.py --help for all options.

COMPATIBILITY AND SAFETY

The supplied G-code files are ready-to-run only on the author's Voron 2.4 350 mm StealthChanger macro setup. Generic output must be reviewed for the target printer. Klipper macros and tool changes are installation-specific. The Prusa XL preset is a review-before-use starting point. Bambu Lab is not advertised as ready-to-run; use only verified printer-specific custom start/end G-code.

Always verify temperatures, bed bounds, homing, mesh behavior, and Z-offset sign in a G-code viewer before printing.
