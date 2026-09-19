#!/usr/bin/env python3
"""
Universal Oxplow Z-Offset Search Generator
=========================================
Generates ultra-fast, highly accurate first-layer Z-offset search G-code
using the continuous gradient ramp (Oxplow) method.

Compatible with:
- Single-Tool 3D Printers (Ender 3, Bambu, Prusa, Neptune, Voron, etc.)
- Multi-Tool / Toolchanger / IDEX Printers (StealthChanger, Jubilee, Prusa XL, etc.)
- Firmware: Klipper (with or without custom PRINT_START macro), Marlin, RepRapFirmware, Bambu

Features:
- Full vector font (0-9, 'T') for crisp in-print tool labels
- Smart nozzle-adaptive calculations (0.2, 0.4, 0.6, 0.8mm)
- Auto-centering & bed boundary safety collision checks
- Dual mode: One-click CLI presets OR interactive wizard
- Self-documenting: embeds the visual interpretation guide directly in G-code header

Author: Antigravity AI & Voron Community
License: MIT
"""

import os
import sys
import math
import argparse

# ==============================================================================
# PRESETS FOR POPULAR PRINTERS
# ==============================================================================
PRESETS = {
    "voron-350-5tool": {
        "description": "Voron 2.4 350mm with StealthChanger (5 Tools, T0-T4)",
        "bed_x": 350, "bed_y": 350,
        "tools": [0, 1, 2, 3, 4],
        "flavor": "stealthchanger",
        "nozzle": 0.4
    },
    "voron-300-4tool": {
        "description": "Voron 2.4 300mm with StealthChanger (4 Tools, T0-T3)",
        "bed_x": 300, "bed_y": 300,
        "tools": [0, 1, 2, 3],
        "flavor": "stealthchanger",
        "nozzle": 0.4
    },
    "voron-generic": {
        "description": "Voron 2.4 / Trident Single Tool (Klipper PRINT_START macro)",
        "bed_x": 300, "bed_y": 300,
        "tools": [0],
        "flavor": "klipper-macro",
        "nozzle": 0.4
    },
    "ender3": {
        "description": "Creality Ender 3 / V2 / S1 (220x220mm, Marlin)",
        "bed_x": 220, "bed_y": 220,
        "tools": [0],
        "flavor": "generic",
        "nozzle": 0.4
    },
    "prusa-mk3-mk4": {
        "description": "Prusa i3 MK3S+ / MK4 (250x210mm, Marlin/Prusa)",
        "bed_x": 250, "bed_y": 210,
        "tools": [0],
        "flavor": "generic",
        "nozzle": 0.4
    },
    "bambu-x1-p1-a1": {
        "description": "Bambu Lab X1 / P1P / P1S / A1 (256x256mm)",
        "bed_x": 256, "bed_y": 256,
        "tools": [0],
        "flavor": "generic",
        "nozzle": 0.4
    },
    "prusa-xl-5tool": {
        "description": "Prusa XL 5-Tool Multi-Toolchanger (360x360mm)",
        "bed_x": 360, "bed_y": 360,
        "tools": [0, 1, 2, 3, 4],
        "flavor": "prusa-xl",
        "nozzle": 0.4
    }
}

# Default material profiles
MATERIAL_DEFAULTS = {
    "PLA":  {"bed": 60,  "nozzle": 210, "speed": 1800},
    "PETG": {"bed": 75,  "nozzle": 240, "speed": 1800},
    "ABS":  {"bed": 100, "nozzle": 245, "speed": 1800},
    "ASA":  {"bed": 100, "nozzle": 250, "speed": 1800},
    "TPU":  {"bed": 50,  "nozzle": 225, "speed": 1200}
}

# ==============================================================================
# VECTOR FONT ENGINE (0-9, 'T')
# ==============================================================================
def generate_char_strokes(char, x0, y0, w, h):
    """
    Generate normalized stroke line segments for characters '0'-'9' and 'T'.
    Coordinates: (x0, y0) is bottom-left, w is width, h is height.
    """
    x1 = x0 + w
    xm = x0 + w / 2.0
    y1 = y0 + h
    ym = y0 + h / 2.0
    
    strokes = []
    if char == '0':
        strokes = [[(x0, y0), (x1, y0)], [(x1, y0), (x1, y1)], [(x1, y1), (x0, y1)], [(x0, y1), (x0, y0)]]
    elif char == '1':
        strokes = [[(x0, y1 - h * 0.25), (xm, y1)], [(xm, y1), (xm, y0)], [(x0, y0), (x1, y0)]]
    elif char == '2':
        strokes = [[(x0, y1), (x1, y1)], [(x1, y1), (x1, ym)], [(x1, ym), (x0, ym)], [(x0, ym), (x0, y0)], [(x0, y0), (x1, y0)]]
    elif char == '3':
        strokes = [[(x0, y1), (x1, y1)], [(x1, y1), (x0 + w * 0.3, ym)], [(x0 + w * 0.3, ym), (x1, ym)], [(x1, ym), (x1, y0)], [(x1, y0), (x0, y0)]]
    elif char == '4':
        strokes = [[(x0, y1), (x0, ym)], [(x0, ym), (x1, ym)], [(x1 * 0.9, y1), (x1 * 0.9, y0)]]
    elif char == '5':
        strokes = [[(x1, y1), (x0, y1)], [(x0, y1), (x0, ym)], [(x0, ym), (x1, ym)], [(x1, ym), (x1, y0)], [(x1, y0), (x0, y0)]]
    elif char == '6':
        strokes = [[(x1, y1), (x0, y1)], [(x0, y1), (x0, y0)], [(x0, y0), (x1, y0)], [(x1, y0), (x1, ym)], [(x1, ym), (x0, ym)]]
    elif char == '7':
        strokes = [[(x0, y1), (x1, y1)], [(x1, y1), (xm, y0)]]
    elif char == '8':
        strokes = [[(x0, y0), (x1, y0)], [(x1, y0), (x1, y1)], [(x1, y1), (x0, y1)], [(x0, y1), (x0, y0)], [(x0, ym), (x1, ym)]]
    elif char == '9':
        strokes = [[(x1, ym), (x0, ym)], [(x0, ym), (x0, y1)], [(x0, y1), (x1, y1)], [(x1, y1), (x1, y0)], [(x1, y0), (x0, y0)]]
    elif char == 'T':
        strokes = [[(x0, y1), (x1, y1)], [(xm, y1), (xm, y0)]]
    return strokes

# ==============================================================================
# MAIN GENERATOR LOGIC
# ==============================================================================
def generate_oxplow_gcode(
    bed_x=350.0,
    bed_y=350.0,
    tools=(0,),
    flavor="generic",
    material="PETG",
    bed_temp=75,
    nozzle_temp=240,
    nozzle_dia=0.4,
    nominal_height=None,
    ramp_range=None,
    patch_length=20.0,
    num_lines=51,
    filament_dia=1.75,
    print_speed=None,
    travel_speed=6000,
    retract_length=0.8,
    retract_speed=2400,
    custom_start_gcode=None,
    custom_end_gcode=None
):
    """
    Generate universally compatible Oxplow first-layer Z-search G-code.
    """
    # 1. Compute adaptive geometry based on nozzle size if not explicitly set
    if nominal_height is None:
        nominal_height = round(nozzle_dia * 0.60, 2) # e.g. 0.24mm for 0.4 nozzle
    if ramp_range is None:
        ramp_range = round(nominal_height * 0.40, 2) # e.g. +/-0.10mm
    
    line_step = round(nozzle_dia * 1.0, 2)       # e.g. 0.40mm
    line_width = round(nozzle_dia * 1.05, 2)     # e.g. 0.42mm
    patch_height = (num_lines - 1) * line_step   # e.g. 50 * 0.40 = 20.0mm
    
    mat_defaults = MATERIAL_DEFAULTS.get(material.upper(), MATERIAL_DEFAULTS["PETG"])
    if print_speed is None:
        print_speed = mat_defaults["speed"]

    filament_area = math.pi * ((filament_dia / 2.0) ** 2)
    line_volume = patch_length * line_width * nominal_height
    line_e = line_volume / filament_area

    # 2. Multi-tool placement calculation & bed boundary safety
    total_tools = len(tools)
    is_multi_tool = total_tools > 1 or (tools[0] != 0 and flavor in ["stealthchanger", "prusa-xl"])
    
    # Calculate spacing: fit within 80% of bed X
    max_available_x = bed_x * 0.85
    spacing = 58.0
    if (total_tools - 1) * spacing + patch_length > max_available_x:
        spacing = max(patch_length + 15.0, (max_available_x - patch_length) / max(1, total_tools - 1))

    total_span = (total_tools - 1) * spacing
    first_x = (bed_x / 2.0) - (total_span / 2.0) - (patch_length / 2.0)
    y_start = (bed_y / 2.0) - (patch_height / 2.0)

    # Collision & Boundary Check
    min_test_x = first_x - 10.0
    max_test_x = first_x + total_span + patch_length + 5.0
    min_test_y = y_start - 12.0
    max_test_y = y_start + patch_height + 5.0
    
    if min_test_x < 5.0 or max_test_x > bed_x - 5.0 or min_test_y < 5.0 or max_test_y > bed_y - 5.0:
        raise ValueError(
            f"Test patches exceed safe bed limits! Required X: [{min_test_x:.1f}, {max_test_x:.1f}] mm, "
            f"Y: [{min_test_y:.1f}, {max_test_y:.1f}] mm for Bed {bed_x}x{bed_y}mm."
        )

    tool_x_positions = {t: first_x + i * spacing for i, t in enumerate(tools)}
    z_step = (2.0 * ramp_range) / float(num_lines - 1)
    z_min = nominal_height - ramp_range
    z_max = nominal_height + ramp_range

    lines = []
    # 3. Comprehensive Header & User Guide
    lines.append("; ==========================================================================")
    lines.append("; UNIVERSAL OXPLOW Z-OFFSET SEARCH - FIRST LAYER CALIBRATION")
    lines.append("; ==========================================================================")
    lines.append(f"; Firmware Flavor : {flavor.upper()}")
    lines.append(f"; Bed Dimensions  : {bed_x:.0f} x {bed_y:.0f} mm")
    lines.append(f"; Material / Temp : {material} (Bed: {bed_temp}C, Nozzle: {nozzle_temp}C)")
    lines.append(f"; Nozzle Diameter : {nozzle_dia} mm | Filament: {filament_dia} mm")
    lines.append(f"; Tools Included  : {list(tools)}")
    lines.append(f"; Nominal Height  : {nominal_height:.3f} mm")
    lines.append(f"; Ramp Span       : {z_min:.3f} mm (bottom) -> {z_max:.3f} mm (top) (+/-{ramp_range:.3f} mm)")
    lines.append(f"; Resolution      : {z_step:.4f} mm ({z_step * 1000.0:.1f} microns) per line ({num_lines} lines)")
    lines.append("; ==========================================================================")
    lines.append("; QUICK VISUAL INSPECTION GUIDE (HOW TO READ YOUR PRINT):")
    lines.append("; 1. Inspect the printed patch under slanted lighting.")
    lines.append("; 2. Locate the line with the smoothest, most uniform surface:")
    lines.append(";    - Bottom lines (Y < Center): Nozzle too close / over-squish / rough ridges.")
    lines.append(";    - PERFECT REGION           : Smooth, zero gaps, zero ridges, uniform sheen.")
    lines.append(";    - Top lines (Y > Center)   : Nozzle too far / under-squish / separate round lines.")
    lines.append("; 3. Measure distance or count tick marks relative to the Center Mark (0.00 mm):")
    lines.append(";    - If best line is BELOW center: Nozzle was TOO HIGH -> Lower Z-offset (-).")
    lines.append(";    - If best line is ABOVE center: Nozzle was TOO CLOSE -> Raise Z-offset (+).")
    lines.append(";    - Offset Formula: Z_new = Z_current - (Z_best - Nominal_Height)")
    lines.append("; ==========================================================================")
    lines.append("")

    # 4. Start G-code Sequence
    lines.append("; --- START G-CODE SEQUENCE ---")
    if custom_start_gcode:
        lines.append(custom_start_gcode.strip())
    elif flavor == "stealthchanger":
        tool_temp_params = " ".join([f"T{t}_TEMP={nozzle_temp}" for t in tools])
        lines.append(f"PRINT_START TOOL_TEMP={nozzle_temp} BED_TEMP={bed_temp} TOOL={tools[0]} MATERIAL={material} {tool_temp_params}")
    elif flavor == "klipper-macro":
        lines.append(f"PRINT_START BED_TEMP={bed_temp} EXTRUDER_TEMP={nozzle_temp}")
    elif flavor == "prusa-xl":
        lines.append(f"M140 S{bed_temp}")
        lines.append(f"M104 S{nozzle_temp}")
        lines.append("G28")
        lines.append(f"M190 S{bed_temp}")
        lines.append(f"M109 S{nozzle_temp}")
        lines.append(f"T{tools[0]}")
    else: # Generic Marlin / Klipper / RepRap
        lines.append("G90 ; absolute coordinates")
        lines.append("M83 ; relative extrusion mode")
        lines.append(f"M140 S{bed_temp} ; set bed temp")
        lines.append(f"M104 S{nozzle_temp} ; set nozzle temp")
        lines.append("G28 ; home all axes")
        lines.append(f"M190 S{bed_temp} ; wait for bed temp")
        lines.append(f"M109 S{nozzle_temp} ; wait for nozzle temp")
        lines.append("; Bed leveling mesh loading (if supported)")
        lines.append("BED_MESH_PROFILE LOAD=default 2>/dev/null || M420 S1 2>/dev/null || G29 ; load mesh")

    lines.append("M83 ; ensure relative extrusion")
    lines.append("G90 ; ensure absolute positioning")
    lines.append("")

    # 5. Build Each Toolhead Patch
    for t_idx, tool_num in enumerate(tools):
        px = tool_x_positions[tool_num]
        py = y_start
        
        lines.append("; --------------------------------------------------------------------------")
        lines.append(f"; TOOLHEAD {tool_num} OXPLOW TEST PATCH")
        lines.append(f"; Coords: X={px:.1f}..{px + patch_length:.1f}, Y={py:.1f}..{py + patch_height:.1f}")
        lines.append("; --------------------------------------------------------------------------")
        
        if is_multi_tool:
            lines.append(f"M117 Testing Tool T{tool_num}")
            lines.append("G0 Z20 F3000 ; safe Z lift before toolchange")
            lines.append(f"M104 T{tool_num} S{nozzle_temp} ; preheat target tool before pickup")
            lines.append(f"T{tool_num}")
            lines.append(f"M109 S{nozzle_temp} ; wait for nozzle to reach printing temperature")
            lines.append("")
        else:
            lines.append(f"M109 S{nozzle_temp} ; ensure active nozzle at printing temperature")
            lines.append("")


        # Prime line beside the patch
        purge_x = px - 8.0
        lines.append("; Prime / Purge line to stabilize nozzle pressure")
        lines.append(f"G0 X{purge_x:.2f} Y{py:.2f} Z2.0 F{travel_speed}")
        lines.append("G0 Z0.30 F1500")
        lines.append(f"G1 E{retract_length + 0.5:.2f} F{retract_speed} ; unretract")
        lines.append(f"G1 X{purge_x:.2f} Y{py + 18.0:.2f} E1.5 F1500 ; purge line")
        lines.append(f"G1 E-{retract_length:.2f} F{retract_speed} ; retract")
        lines.append("G0 Z1.0 F3000")
        lines.append("")

        # Tool Identifier Label ('T' + Digit)
        lines.append(f"; In-print label: 'T{tool_num}'")
        label_y = py - 7.5
        label_x = px + (patch_length / 2.0) - 4.5
        
        # Draw 'T'
        for stroke in generate_char_strokes('T', label_x, label_y, 3.0, 5.0):
            p1, p2 = stroke[0], stroke[1]
            dist = math.hypot(p2[0] - p1[0], p2[1] - p1[1])
            se = (dist * line_width * nominal_height) / filament_area
            lines.append(f"G0 X{p1[0]:.2f} Y{p1[1]:.2f} Z{nominal_height:.2f} F{travel_speed}")
            lines.append(f"G1 E{retract_length:.2f} F{retract_speed}")
            lines.append(f"G1 X{p2[0]:.2f} Y{p2[1]:.2f} E{se:.4f} F1200")
            lines.append(f"G1 E-{retract_length:.2f} F{retract_speed}")

        # Draw Tool Digit (0-9)
        digit_char = str(tool_num)[-1] # last digit if multi-digit
        for stroke in generate_char_strokes(digit_char, label_x + 4.5, label_y, 3.0, 5.0):
            p1, p2 = stroke[0], stroke[1]
            dist = math.hypot(p2[0] - p1[0], p2[1] - p1[1])
            se = (dist * line_width * nominal_height) / filament_area
            lines.append(f"G0 X{p1[0]:.2f} Y{p1[1]:.2f} Z{nominal_height:.2f} F{travel_speed}")
            lines.append(f"G1 E{retract_length:.2f} F{retract_speed}")
            lines.append(f"G1 X{p2[0]:.2f} Y{p2[1]:.2f} E{se:.4f} F1200")
            lines.append(f"G1 E-{retract_length:.2f} F{retract_speed}")
        lines.append("G0 Z1.0 F3000")
        lines.append("")

        # Tick Marks on Left & Right
        lines.append("; Scale Tick Marks (-0.10, -0.05, 0.00 CENTER, +0.05, +0.10 mm)")
        mid_idx = (num_lines - 1) // 2
        tick_offsets = [
            (0.0, -ramp_range, False),
            (patch_height * 0.25, -ramp_range * 0.5, False),
            (patch_height * 0.50, 0.00, True),  # Center mark
            (patch_height * 0.75, +ramp_range * 0.5, False),
            (patch_height, +ramp_range, False)
        ]
        for y_off, diff, is_center in tick_offsets:
            ty = py + y_off
            tick_w = 4.0 if is_center else 2.5
            tx1 = px - 2.0 - tick_w
            tx2 = px - 2.0
            te = ((tx2 - tx1) * line_width * nominal_height) / filament_area
            lines.append(f"; Mark {diff:+.3f}mm at Y={ty:.2f}")
            lines.append(f"G0 X{tx1:.2f} Y{ty:.2f} Z{nominal_height:.2f} F{travel_speed}")
            lines.append(f"G1 E{retract_length:.2f} F{retract_speed}")
            lines.append(f"G1 X{tx2:.2f} Y{ty:.2f} E{te:.4f} F1200")
            lines.append(f"G1 E-{retract_length:.2f} F{retract_speed}")
            if is_center:
                rtx1 = px + patch_length + 2.0
                rtx2 = rtx1 + tick_w
                lines.append(f"G0 X{rtx1:.2f} Y{ty:.2f} F{travel_speed}")
                lines.append(f"G1 E{retract_length:.2f} F{retract_speed}")
                lines.append(f"G1 X{rtx2:.2f} Y{ty:.2f} E{te:.4f} F1200")
                lines.append(f"G1 E-{retract_length:.2f} F{retract_speed}")
        lines.append("G0 Z1.0 F3000")
        lines.append("")

        # Oxplow Ramp Patch
        lines.append(f"; Oxplow Ramp Patch: Z={z_min:.3f}mm to {z_max:.3f}mm")
        lines.append(f"G0 X{px:.2f} Y{py:.2f} Z{z_min:.3f} F{travel_speed}")
        lines.append(f"G1 E{retract_length:.2f} F{retract_speed}")

        for i in range(num_lines):
            curr_y = py + (i * line_step)
            curr_z = z_min + (i * z_step)
            
            if i % 2 == 0:
                lines.append(f"G1 X{px + patch_length:.2f} Y{curr_y:.2f} Z{curr_z:.4f} E{line_e:.4f} F{print_speed}")
                if i < num_lines - 1:
                    next_y = py + ((i + 1) * line_step)
                    next_z = z_min + ((i + 1) * z_step)
                    lines.append(f"G0 X{px + patch_length:.2f} Y{next_y:.2f} Z{next_z:.4f}")
            else:
                lines.append(f"G1 X{px:.2f} Y{curr_y:.2f} Z{curr_z:.4f} E{line_e:.4f} F{print_speed}")
                if i < num_lines - 1:
                    next_y = py + ((i + 1) * line_step)
                    next_z = z_min + ((i + 1) * z_step)
                    lines.append(f"G0 X{px:.2f} Y{next_y:.2f} Z{next_z:.4f}")

        lines.append(f"G1 E-{retract_length:.2f} F{retract_speed} ; retract")
        lines.append("G0 Z20 F3000 ; safe Z lift")
        lines.append("")

    # 6. End G-code Sequence
    lines.append("; --- END G-CODE SEQUENCE ---")
    if custom_end_gcode:
        lines.append(custom_end_gcode.strip())
    elif flavor in ["stealthchanger", "klipper-macro"]:
        lines.append("PRINT_END")
    else:
        lines.append("M104 S0 ; turn off hotend")
        lines.append("M140 S0 ; turn off bed")
        lines.append("G91 ; relative positioning")
        lines.append("G1 Z10 F3000 ; raise Z")
        lines.append("G90 ; absolute positioning")
        lines.append(f"G0 X10 Y{bed_y - 10:.0f} F6000 ; present print")
        lines.append("M84 ; disable steppers")

    lines.append("M117 Oxplow Test Finished!")
    lines.append("")

    return "\n".join(lines)

# ==============================================================================
# INTERACTIVE CLI WIZARD
# ==============================================================================
def run_interactive_wizard():
    print("\n" + "=" * 70)
    print("      UNIVERSAL OXPLOW Z-OFFSET SEARCH - CONFIGURATION WIZARD")
    print("=" * 70)
    print("Available Printer Presets:")
    preset_keys = list(PRESETS.keys())
    for idx, key in enumerate(preset_keys, 1):
        print(f"  [{idx}] {key:<18} : {PRESETS[key]['description']}")
    print("  [C] Custom Configuration (manual bed size & options)\n")
    
    choice = input("Select a preset [1-7] or 'C' for Custom (Default: 1): ").strip().lower()
    selected_preset = None
    if choice.isdigit() and 1 <= int(choice) <= len(preset_keys):
        selected_preset = PRESETS[preset_keys[int(choice) - 1]]
    elif choice in ["", "1"]:
        selected_preset = PRESETS[preset_keys[0]]
        
    if selected_preset:
        bed_x = selected_preset["bed_x"]
        bed_y = selected_preset["bed_y"]
        tools = selected_preset["tools"]
        flavor = selected_preset["flavor"]
        nozzle = selected_preset["nozzle"]
    else:
        bed_x = float(input("Enter Bed X size in mm [default 350]: ").strip() or "350")
        bed_y = float(input("Enter Bed Y size in mm [default 350]: ").strip() or "350")
        tools_str = input("Enter tool numbers separated by space [default 0]: ").strip() or "0"
        tools = [int(t) for t in tools_str.split()]
        print("\nFirmware flavor: [1] generic (Marlin/Klipper)  [2] klipper-macro  [3] stealthchanger")
        flav_choice = input("Select flavor [default 1]: ").strip() or "1"
        flavor_map = {"1": "generic", "2": "klipper-macro", "3": "stealthchanger"}
        flavor = flavor_map.get(flav_choice, "generic")
        nozzle = float(input("Enter nozzle diameter in mm [default 0.4]: ").strip() or "0.4")

    print("\nSelect Material:")
    mats = ["PETG", "ABS", "PLA", "TPU"]
    for idx, m in enumerate(mats, 1):
        print(f"  [{idx}] {m} (Bed: {MATERIAL_DEFAULTS[m]['bed']}C, Nozzle: {MATERIAL_DEFAULTS[m]['nozzle']}C)")
    mat_choice = input("Choose material [1-4] (Default: 1 - PETG): ").strip() or "1"
    mat_idx = int(mat_choice) - 1 if mat_choice.isdigit() and 1 <= int(mat_choice) <= len(mats) else 0
    material = mats[mat_idx]
    
    default_out = f"Oxplow_{flavor}_{material}_{len(tools)}Tool.gcode"
    out_name = input(f"\nOutput file name [default '{default_out}']: ").strip() or default_out

    gcode = generate_oxplow_gcode(
        bed_x=bed_x,
        bed_y=bed_y,
        tools=tuple(tools),
        flavor=flavor,
        material=material,
        nozzle_dia=nozzle
    )
    with open(out_name, "w", encoding="utf-8") as f:
        f.write(gcode)
        
    print("\n" + "=" * 70)
    print(f"SUCCESS: Generated '{out_name}'!")
    print(f"Details: Bed={bed_x}x{bed_y}mm, Tools={tools}, Flavor={flavor}, Nozzle={nozzle}mm")
    print("=" * 70 + "\n")

# ==============================================================================
# MAIN ENTRY POINT
# ==============================================================================
def main():
    parser = argparse.ArgumentParser(
        description="Universal Oxplow First-Layer Z-Offset Search Generator",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument("--preset", choices=list(PRESETS.keys()), help="Load predefined printer preset")
    parser.add_argument("--interactive", "-i", action="store_true", help="Launch interactive configuration wizard")
    parser.add_argument("--flavor", choices=["generic", "klipper-macro", "stealthchanger", "prusa-xl"], default="stealthchanger",
                        help="Firmware / Start sequence flavor (default: stealthchanger)")
    parser.add_argument("--bed-x", type=float, default=350.0, help="Bed X dimension in mm (default: 350.0)")
    parser.add_argument("--bed-y", type=float, default=350.0, help="Bed Y dimension in mm (default: 350.0)")
    parser.add_argument("--tools", nargs="+", type=int, default=None, help="Tools to test (e.g. 0 or 0 1 2 3 4)")
    parser.add_argument("--material", choices=["PETG", "ABS", "PLA", "ASA", "TPU"], default="PETG", help="Filament material")
    parser.add_argument("--bed", type=int, default=None, help="Bed temperature in C (default: auto from material)")
    parser.add_argument("--nozzle", type=int, default=None, help="Nozzle temperature in C (default: auto from material)")
    parser.add_argument("--nozzle-dia", type=float, default=0.4, help="Nozzle diameter in mm (default: 0.4)")
    parser.add_argument("--height", type=float, default=None, help="Nominal layer height in mm (default: 0.6*nozzle_dia)")
    parser.add_argument("--range", type=float, default=None, help="Ramp search range +/- mm (default: 0.4*height)")
    parser.add_argument("-o", "--output", type=str, default=None, help="Output G-code filename")

    # If run with no arguments in interactive terminal, prompt or use default
    if len(sys.argv) == 1:
        # Check if running interactively
        if sys.stdin.isatty():
            print("No arguments provided. Launching Interactive Wizard (use --help for CLI flags)...")
            run_interactive_wizard()
            return

    args = parser.parse_args()

    if args.interactive:
        run_interactive_wizard()
        return

    # Apply preset if specified
    bed_x = args.bed_x
    bed_y = args.bed_y
    tools = args.tools
    flavor = args.flavor
    nozzle_dia = args.nozzle_dia

    if args.preset:
        p = PRESETS[args.preset]
        bed_x = p["bed_x"]
        bed_y = p["bed_y"]
        tools = args.tools if args.tools is not None else p["tools"]
        flavor = p["flavor"]
        nozzle_dia = p["nozzle"]
    elif tools is None:
        tools = [0]


    mat_defaults = MATERIAL_DEFAULTS.get(args.material.upper(), MATERIAL_DEFAULTS["PETG"])
    bed_temp = args.bed if args.bed is not None else mat_defaults["bed"]
    nozzle_temp = args.nozzle if args.nozzle is not None else mat_defaults["nozzle"]

    gcode = generate_oxplow_gcode(
        bed_x=bed_x,
        bed_y=bed_y,
        tools=tuple(tools),
        flavor=flavor,
        material=args.material,
        bed_temp=bed_temp,
        nozzle_temp=nozzle_temp,
        nozzle_dia=nozzle_dia,
        nominal_height=args.height,
        ramp_range=args.range
    )

    if args.output:
        out_path = args.output
    else:
        if len(tools) == 1 and tools[0] == 0:
            out_path = f"Oxplow_{flavor}_{args.material}_{nozzle_dia}mm.gcode"
        else:
            tools_str = "T" + "_T".join(map(str, tools))
            out_path = f"Oxplow_{flavor}_{tools_str}_{args.material}_{nozzle_dia}mm.gcode"

    with open(out_path, "w", encoding="utf-8") as f:
        f.write(gcode)

    print(f"Successfully generated: {out_path}")
    print(f"Settings: Flavor={flavor}, Bed={bed_x}x{bed_y}mm, Tools={tools}, Nozzle={nozzle_dia}mm, Material={args.material}")
    print(f"Temperatures: Bed={bed_temp}C, Nozzle={nozzle_temp}C")

if __name__ == "__main__":
    main()
