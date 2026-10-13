# Oxplow Continuous-Ramp First-Layer Z-Offset Method

Product page: https://www.printables.com/model/1846885-universal-oxplow-first-layer-z-offset-calibration

## 1. Purpose

The method finds the physical nozzle-height correction that produces a good first layer at printing temperature. It is especially useful on toolchangers, where each tool may need a different offset, but the same geometry also works on conventional single-tool printers.

This is a first-layer calibration aid, not a replacement for homing, gantry leveling, a valid bed mesh, clean nozzles, correct extrusion calibration, or a mechanically sound printer.

## 2. Principle

Each patch consists of adjacent extrusion lines. The commanded Z height increases linearly from the front edge to the back edge while extrusion per line remains constant:

- The low-Z edge is deliberately over-squished.
- The nominal center line represents zero physical correction.
- The high-Z edge is deliberately under-squished.
- The smooth transition region indicates the best physical nozzle height.

For the default 0.4 mm nozzle, the generator uses:

| Property | Value |
| --- | ---: |
| Patch length | 20.0 mm |
| Patch width along Y | 20.0 mm |
| Number of lines | 51 |
| Line spacing | 0.40 mm |
| Front Z | 0.150 mm |
| Center Z | 0.250 mm |
| Back Z | 0.350 mm |
| Z change per line | 0.004 mm |
| Z change per 1 mm measured along Y | 0.010 mm |

Other nozzle diameters produce different geometry. Always use the parameters written in the generated G-code header.

## 3. Reading the result

Inspect the cooled patch under angled light and, if useful, flex or peel it from the plate:

1. Ridges, plowing, or excessive translucency indicate that the nozzle is too close at that part of the ramp.
2. A continuous smooth sheet with joined lines is the target region.
3. Round lines or gaps indicate that the nozzle is too far away at that part of the ramp.

Measure from the front edge of the patch to the center of the target region. For the default 0.4 mm geometry:

```text
Delta Z = (measured Y - 10.0 mm) x 0.010 mm/mm
```

This `Delta Z` is a physical direction:

- Positive: raise the nozzle.
- Negative: lower the nozzle.
- Zero: keep the current physical height.

Do not blindly copy this sign into a firmware setting. Different firmware, probes, and toolchanger macros may define stored Z-offset in opposite directions. On the author's current StealthChanger configuration, the update is:

```text
Z_new = Z_current + Delta Z
```

Verify the convention on any other machine with a small, safe adjustment before saving it.

## 4. Default 0.4 mm lookup table

| Measured from front | Physical correction | Action |
| ---: | ---: | --- |
| 0 mm | -0.100 mm | Lower nozzle |
| 4 mm | -0.060 mm | Lower nozzle |
| 8 mm | -0.020 mm | Lower nozzle |
| 10 mm | 0.000 mm | No change |
| 12 mm | +0.020 mm | Raise nozzle |
| 16 mm | +0.060 mm | Raise nozzle |
| 20 mm | +0.100 mm | Raise nozzle |

## 5. Generator workflow

1. Install Python 3.
2. Open a terminal in this package directory.
3. Run `python generate_oxplow_gcode.py -i` or choose a command-line preset.
4. Confirm bed size, tool list, nozzle diameter, material, and temperatures in the generated header.
5. Inspect the path in a G-code viewer. Pay special attention to homing, tool changes, mesh behavior, XY bounds, and minimum Z.
6. On the first run, supervise the printer and be ready to stop it.
7. Measure each tool's patch and apply the correction using that printer's verified sign convention.
8. Reprint once to confirm the best region is near the center mark.

Useful commands:

```bash
python generate_oxplow_gcode.py --help
python generate_oxplow_gcode.py --preset voron-350-5tool --material PETG
python generate_oxplow_gcode.py --preset ender3 --material PLA --mesh marlin
python generate_oxplow_gcode.py --preset ender3 --nozzle-dia 0.6 --material PETG
```

## 6. Compatibility boundaries

- The included PETG and ABS G-code files target the author's Voron 2.4 350 mm StealthChanger macros.
- Generic mode emits standard heating, homing, motion, and extrusion commands. It emits no mesh command by default.
- `--mesh marlin` emits `M420 S1`; `--mesh klipper` emits `BED_MESH_PROFILE LOAD=default`.
- Custom Klipper installations should use a matching `PRINT_START` preset or verified `--start-gcode-file` and `--end-gcode-file` inputs.
- The Prusa XL preset is a starting point that must be compared with the current slicer profile before printing.
- Bambu Lab does not have a ready-to-run preset in this package because its machine start sequence is printer- and slicer-specific.

## 7. Known limitations

- A gradient test finds a useful visual region; it does not prove an offset to micrometer-level accuracy. Surface texture, filament, flow, temperature, pressure advance, and plate cleanliness influence appearance.
- The nominal layer height and search span must suit the nozzle and plate. Never use a ramp range greater than or equal to the nominal height.
- A bed mesh error can shift or distort the result. Calibrate the mesh and use the same thermal conditions as normal printing.
- Tool offsets should be measured with the same mounted hardware, nozzle condition, material, and thermal state used in production.
