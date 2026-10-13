# Oxplow G-code Generator

This directory contains the source and release files for the [Universal Oxplow First-Layer Z-Offset Calibration](https://www.printables.com/model/1846885-universal-oxplow-first-layer-z-offset-calibration) model.

## Quick start

```bash
python generate_oxplow_gcode.py -i
```

For the author's Voron 2.4 350 mm StealthChanger:

```bash
python generate_oxplow_gcode.py --preset voron-350-5tool --material PETG
```

For a generic Marlin-style printer with a saved mesh:

```bash
python generate_oxplow_gcode.py --preset ender3 --material PLA --mesh marlin
```

Run `python generate_oxplow_gcode.py --help` for all presets and overrides.

## Safety

Only the supplied StealthChanger G-code files are matched to the author's printer macros. Generated files for other printers must be checked in a G-code viewer and compared with the printer's normal start/end G-code before use. Verify temperatures, bed dimensions, homing, mesh loading, tool selection, motion limits, and the printer's stored Z-offset sign convention.

The generator deliberately refuses empty/duplicate tool lists, invalid dimensions, even line counts, non-positive speeds, and ramps that could command Z=0 or below.

## Files

- `generate_oxplow_gcode.py`: generator and interactive wizard.
- `Oxplow_5Tool_Z_Test_PETG.gcode`: T0-T4 PETG release file.
- `Oxplow_5Tool_Z_Test_ABS.gcode`: T0-T4 ABS release file.
- `Oxplow_T1_Z_Test_PETG.gcode`: T1-only PETG release file.
- `Oxplow-Z-Offset-Comprehensive-Method.md`: method, formula, limitations, and workflow.
- `PRINTABLES_POST_CONTENT.md`: publication-ready Markdown.
- `DESCRIPTION_ONLY.md`: plain-text description.
