# Printables Model Upload Details

Product page: https://www.printables.com/model/1846885-universal-oxplow-first-layer-z-offset-calibration

## Title

```text
Universal Oxplow First-Layer Z-Offset Calibration (Single and Multi-Tool)
```

## Category

```text
3D Printers > 3D Printer Calibration
```

## Short summary

```text
Fast continuous-ramp first-layer test with a Python generator for custom beds, nozzle sizes, materials, and Voron StealthChanger toolheads.
```

## Tags

```text
z-offset, calibration, first layer, toolchanger, stealthchanger, voron, prusa xl, klipper, marlin, bed leveling, oxplow
```

## Description

```markdown
# Universal Oxplow First-Layer Z-Offset Calibration

Oxplow prints a continuous first-layer height ramp instead of a group of separate squares. One edge is intentionally too close to the bed, the opposite edge is intentionally too far away, and the best-looking region reveals the required physical nozzle-height correction.

## What is included

- Ready-to-run G-code for the author's Voron 2.4 350 mm StealthChanger configuration.
- A Python 3 generator for custom bed sizes, tool lists, nozzle diameters, and materials.
- Presets for the author's 5-tool Voron, a 4-tool 300 mm Voron, a generic single-tool Voron macro, Ender 3-class Marlin printers, Prusa MK3/MK4, and Prusa XL.
- In-print tool labels and scale marks.

The ramp itself takes roughly one minute per tool after the printer's normal homing, heating, probing, and tool preparation sequence. Multi-tool jobs take longer.

## How the 0.4 mm nozzle test works

The default patch is 20 x 20 mm with 51 adjacent lines:

- Front edge: Z = 0.150 mm, intentionally over-squished.
- Center mark: Z = 0.250 mm, the nominal target.
- Back edge: Z = 0.350 mm, intentionally under-squished.
- Resolution: 0.004 mm of Z change per line.
- Scale: 1 mm measured along Y equals 0.010 mm of physical Z correction.

The generator scales the geometry for other nozzle diameters, so use the values embedded in the generated G-code header rather than assuming the 0.4 mm figures above.

## Reading the print

1. Inspect the patch under angled light.
2. Find the center of the smooth region with joined lines and no ridges or gaps.
3. Measure from the front edge of the ramp to that region.
4. Use the generated header or the formula below to calculate the physical correction.

For the default 0.4 mm patch:

`Delta Z = (measured Y - 10.0 mm) x 0.010 mm/mm`

- A result behind the center is a positive physical correction: raise the nozzle.
- A result in front of the center is a negative physical correction: lower the nozzle.
- At the center, no physical correction is needed.

Important: firmware and macros do not all store Z-offset with the same sign convention. On the author's StealthChanger configuration, the saved value is updated with `Z_new = Z_current + Delta Z`. Verify how your printer represents Z-offset before saving any value.

## Generator examples

```bash
# Interactive wizard
python generate_oxplow_gcode.py -i

# Ready-to-run preset for this project's Voron StealthChanger
python generate_oxplow_gcode.py --preset voron-350-5tool --material PETG

# Generic Marlin-style printer using an already saved mesh
python generate_oxplow_gcode.py --preset ender3 --material PLA --mesh marlin

# Override a preset for a 0.6 mm nozzle
python generate_oxplow_gcode.py --preset ender3 --nozzle-dia 0.6 --material PETG

# Use printer-specific start and end sequences
python generate_oxplow_gcode.py --bed-x 300 --bed-y 300 --start-gcode-file start.gcode --end-gcode-file end.gcode
```

Run `python generate_oxplow_gcode.py --help` for every option.

## Compatibility and safety

- The included StealthChanger files target the author's macros and are the only ready-to-run files in this package.
- Generic mode uses standard heating, homing, and motion commands. It does not guess a mesh command unless `--mesh marlin` or `--mesh klipper` is selected.
- Klipper `PRINT_START`, tool-change, and end macros are installation-specific. Use a matching preset or provide custom start/end files.
- The Prusa XL preset should be reviewed in a G-code viewer and checked against the current printer profile before use.
- Bambu Lab is not offered as a ready-to-run preset because its machine start sequence is printer- and slicer-specific. Advanced users may provide verified custom start/end files.
- Dry-run the file above the bed or inspect it in a G-code viewer before the first print. Keep a hand near Emergency Stop and never use a generated file whose temperatures or motion bounds do not match the printer.

## Included files

1. `generate_oxplow_gcode.py` - Python 3 generator.
2. `Oxplow_5Tool_Z_Test_PETG.gcode` - Voron 2.4 350 mm, StealthChanger T0-T4, PETG.
3. `Oxplow_5Tool_Z_Test_ABS.gcode` - Voron 2.4 350 mm, StealthChanger T0-T4, ABS.
4. `Oxplow_T1_Z_Test_PETG.gcode` - the same Voron configuration, tool T1 only, PETG.
5. `README.md` - generator usage and safety notes.
```
