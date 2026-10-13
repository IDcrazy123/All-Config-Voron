# Oxplow 2.3.2 first-layer Z calibration

[Published project](https://www.printables.com/model/1846885-universal-oxplow-first-layer-z-offset-calibration) · [Integrated toolkit](README.md)

## Current machine files

Use the profiles and matching `.gcode`, `.svg`, `.report.json` under `output/`.
This integration follows the existing 2026-10-13 patch-only machine profile.
The old annotated 2.0.0 files are retained under `legacy-v2.0.0/` for recovery.

For a 0.4 mm nozzle, each current patch has 51 rows, nominal height 0.240 mm,
search range +/-0.040 mm, X length 20 mm and Y row spacing approximately
0.388496 mm. The high-to-low ramp starts at Z0.280 at lowest Y and ends at
Z0.200 at highest Y. Row 25 is the nominal center. The five-tool layout is
T0, T1, T2, T3, T4 from left to right, centered at X174/Y168.

## Generate, print, measure

1. Validate a machine profile with the live Moonraker read-only check.
2. Inspect its SVG and confirm installed runtime, selected material and a clear bed.
3. Upload the G-code as a file and start an attended single-tool test.
4. Identify smooth, joined lines without gaps or raised ridges; avoid turnarounds.
5. Calculate from the exact report, using the chosen row or distance from the
   center of the lowest-Y row. Do not use the old 20 mm lookup table.
6. Review the resulting physical correction and save through the machine's
   existing offset procedure. Reprint with `ramp_range=0` to confirm.

```bash
python generate_oxplow_gcode.py calculate --report output/Voron_Oxplow_2.3.2_PETG_T0-T4.report.json --tool 2 --row 35
```

For the supplied profiles:

```text
Delta Z = +0.040 - 0.0016 * row_index
Delta Z = Z_chosen - 0.240
```

Row 0 gives +0.040 mm; row 25 gives zero; row 50 gives -0.040 mm.
Positive physical correction raises the nozzle, negative lowers it. The toolkit
does not write offsets. Stored `gcode_z_offset` must be interpreted through the
installed toolchanger's verified convention; never add a correction to both
the stored tool offset and generated test Z.

## Runtime and retract

The required `_OXPLOW_CHECK` macro is installed through `config/Printer-Setup/oxplow_runtime.cfg`.
It checks tool/extruder mapping, saved Z references, bounds, temperatures and
motion/extrusion limits. Start/select checks are separate calls so they observe
the state after the preceding macro completes. PRINT_START supplies the normal
home/level/mesh/prime sequence. The generated file recovers 0.6 mm for its
initial printing tool and 5 mm for other already-primed tools exactly once.
The final tool is handed directly to PRINT_END for retract then lift.

Validation cannot measure physical nozzle clearance, certify mechanics or
choose the best row. Flow, filament, plate condition and thermal state affect
appearance. No new first-layer result has been measured by this integration.
