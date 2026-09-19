UNIVERSAL OXPLOW FIRST-LAYER Z-OFFSET CALIBRATION
The Ultra-Fast, Visual, Zero-Guesswork Nozzle Height Tuner

Tired of wasting 15 minutes printing traditional flat square patches (Ellis style) only to scratch them with your fingernails trying to guess which one is smoothest?

The Oxplow Continuous Gradient Ramp calibration solves this once and for all. By printing a micro-stepped incline ramp instead of flat squares, you can visually locate the exact transition between over-squish, perfect adhesion, and under-squish in under 60 seconds.

==================================================
KEY ADVANTAGES
==================================================
• Ultra-Fast & Filament Saving: Takes under 1 minute and less than 0.3g of filament per toolhead.
• Continuous Incline (0.150 -> 0.350 mm): Covers a full +/-0.10 mm range around nominal height (0.25 mm) with 0.004 mm (4 microns) micro-steps per hatch line.
• Integrated Scale & Center Ticks: Prominent center tick mark indicates nominal 0.00 mm error.
• Direct Ruler Measurement: Measure with any simple caliper or ruler from the front edge to calculate your exact offset in seconds.
• Universal Compatibility: Includes ready-to-run G-codes and an interactive Python generator supporting:
  - Single-Tool: Ender 3, Prusa MK3/MK4, Bambu Lab, Voron 2.4 / Trident
  - Multi-Tool / Toolchanger: Voron StealthChanger (4-5 tools), Prusa XL (5 tools), Jubilee, IDEX

==================================================
HOW IT WORKS
==================================================
The test patch is a 20 x 20 mm square where the Z-height continuously rises from front to back:

               SIDE-PROFILE CROSS SECTION OF THE TEST RAMP

  Z-Height (mm)
      ^
0.350 |                                            / (Back Edge: Y = 20mm) -> Under-squish (Gaps)
      |                                          /
      |                                        /
0.250 | ----------------- [ CENTER MARK ] --- / (Center: Y = 10mm) -> Ideal Target
      |                                     /
      |                                   /
0.150 | (Front Edge: Y = 0mm) -----------/  -> Over-squish (Plowing / Ridges)
      +----------------------------------------------------> Y Position (mm)
      0mm               5mm              10mm              15mm              20mm

Slope Ratio:
Every 1.0 mm along the Y axis corresponds to exactly 0.010 mm (10 microns) in Z-height change.

==================================================
HOW TO READ YOUR PRINT
==================================================
Inspect the printed patch under angled light:
1. Front Section (Y < 10 mm): Plastic is squished too hard, creating rough ridges / plowing marks from the nozzle.
2. SWEET SPOT: Completely flat, mirror-smooth sheen with seamless line bonding.
3. Back Section (Y > 10 mm): Separate round extruded lines with visible gaps between them.

Use calipers or a ruler to measure the distance from the front edge (Y = 0) to the center of your sweet spot (Y_measured):

Calculation Formulas:
• Offset Difference: Delta_Z = (Y_measured - 10.0 mm) * 0.010
• New Z-Offset: Z_new = Z_current + Delta_Z

Rules of Thumb:
• If the sweet spot is BEHIND center (Y > 10 mm): The nozzle was too close. ADD (+) Delta_Z to raise the nozzle.
• If the sweet spot is IN FRONT of center (Y < 10 mm): The nozzle was too high. SUBTRACT (-) Delta_Z to lower the nozzle.
• If the sweet spot is AT the center mark (Y = 10 mm): Your Z-offset is 100% PERFECT!

==================================================
QUICK LOOKUP TABLE
==================================================
• 0.0 mm (Front edge) -> LOWER nozzle by -0.100 mm
• 2.0 mm              -> LOWER nozzle by -0.080 mm
• 4.0 mm              -> LOWER nozzle by -0.060 mm
• 6.0 mm              -> LOWER nozzle by -0.040 mm
• 8.0 mm              -> LOWER nozzle by -0.020 mm
• 10.0 mm (CENTER)    -> PERFECT (0.000 mm) - Keep as is!
• 12.0 mm             -> RAISE nozzle by +0.020 mm
• 14.0 mm             -> RAISE nozzle by +0.040 mm
• 16.0 mm             -> RAISE nozzle by +0.060 mm
• 18.0 mm             -> RAISE nozzle by +0.080 mm
• 20.0 mm (Back edge) -> RAISE nozzle by +0.100 mm

==================================================
PYTHON GENERATOR (generate_oxplow_gcode.py)
==================================================
Run the included Python script to instantly generate custom G-codes for your exact bed size, nozzle diameter (0.2, 0.4, 0.6, 0.8 mm), and material:

Interactive wizard:
python generate_oxplow_gcode.py -i

One-click CLI presets:
python generate_oxplow_gcode.py --preset voron-350-5tool --material PETG
python generate_oxplow_gcode.py --preset ender3 --material PLA
python generate_oxplow_gcode.py --preset prusa-xl-5tool --material PETG
