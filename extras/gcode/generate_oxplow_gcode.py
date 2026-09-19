#!/usr/bin/env python3
"""
Oxplow Multi-Tool Z-Offset Search Generator for Voron 2.4 StealthChanger (5-Tool)
================================================================================
Generates customized G-code files to accurately determine first-layer Z-offset
for each toolhead (T0 to T4) using the continuous gradient ramp (Oxplow) method.

Author: Antigravity AI & Voron Team
Date: 2026-09-19
"""

import os
import sys
import math
import argparse

def generate_digit_strokes(digit, x_origin, y_origin, scale=1.0):
    """
    Generate stroke vectors (line segments) for digits 0-4.
    x_origin, y_origin: bottom-left corner
    scale: 1.0 = ~3mm wide x 5mm high
    """
    w = 3.0 * scale
    h = 5.0 * scale
    
    # Coordinates relative to origin
    x0, x1 = x_origin, x_origin + w
    y0, y1, y2 = y_origin, y_origin + h / 2.0, y_origin + h
    
    strokes = []
    if digit == 0:
        # Box: (x0,y0)->(x1,y0)->(x1,y2)->(x0,y2)->(x0,y0)
        strokes = [
            [(x0, y0), (x1, y0)],
            [(x1, y0), (x1, y2)],
            [(x1, y2), (x0, y2)],
            [(x0, y2), (x0, y0)]
        ]
    elif digit == 1:
        # Vertical line at x1, with a small top tick
        strokes = [
            [(x0, y2 - h * 0.25), (x1 * 0.8, y2)],
            [(x1 * 0.8, y2), (x1 * 0.8, y0)]
        ]
    elif digit == 2:
        # (x0,y2)->(x1,y2)->(x1,y1)->(x0,y1)->(x0,y0)->(x1,y0)
        strokes = [
            [(x0, y2), (x1, y2)],
            [(x1, y2), (x1, y1)],
            [(x1, y1), (x0, y1)],
            [(x0, y1), (x0, y0)],
            [(x0, y0), (x1, y0)]
        ]
    elif digit == 3:
        # (x0,y2)->(x1,y2)->(x1,y1)->(x0,y1), and (x1,y1)->(x1,y0)->(x0,y0)
        strokes = [
            [(x0, y2), (x1, y2)],
            [(x1, y2), (x1, y1)],
            [(x0 + w * 0.3, y1), (x1, y1)],
            [(x1, y1), (x1, y0)],
            [(x1, y0), (x0, y0)]
        ]
    elif digit == 4:
        # (x0,y2)->(x0,y1)->(x1,y1), (x1,y2)->(x1,y0)
        strokes = [
            [(x0, y2), (x0, y1)],
            [(x0, y1), (x1, y1)],
            [(x1 * 0.9, y2), (x1 * 0.9, y0)]
        ]
    return strokes

def generate_oxplow_gcode(
    tools=(0, 1, 2, 3, 4),
    material="PETG",
    bed_temp=75,
    nozzle_temp=240,
    nominal_height=0.25,
    ramp_range=0.10,
    patch_length=20.0,
    num_lines=51,
    line_step=0.40,
    line_width=0.42,
    filament_dia=1.75,
    print_speed=1800, # 30 mm/s
    travel_speed=6000, # 100 mm/s
    retract_length=0.8,
    retract_speed=2400,
    y_start=150.0
):
    """
    Generate full G-code text for the multi-tool Oxplow test.
    """
    filament_area = math.pi * ((filament_dia / 2.0) ** 2)
    
    # Calculate tool X layout centered on 350x350 bed
    # Bed center is at X=175.
    total_tools = len(tools)
    spacing = 58.0 # Spacing between tool patches
    total_span = (total_tools - 1) * spacing
    first_x = 175.0 - (total_span / 2.0) - (patch_length / 2.0)
    
    tool_x_positions = {t: first_x + i * spacing for i, t in enumerate(tools)}
    
    # Extrusion amount for one hatch line
    # V = L * W * H_nominal
    line_volume = patch_length * line_width * nominal_height
    line_e = line_volume / filament_area
    
    # Header
    lines = []
    lines.append("; ==========================================================================")
    lines.append("; OXPLOW MULTI-TOOL NOZZLE Z-OFFSET SEARCH - VORON 2.4 STEALTHCHANGER")
    lines.append(f"; Material: {material} | Bed: {bed_temp}C | Nozzle: {nozzle_temp}C")
    lines.append(f"; Tools included: {list(tools)}")
    lines.append(f"; Nominal Layer Height: {nominal_height:.2f}mm")
    lines.append(f"; Ramp Span: {nominal_height - ramp_range:.3f}mm to {nominal_height + ramp_range:.3f}mm (+/-{ramp_range:.2f}mm)")
    lines.append(f"; Lines per patch: {num_lines} (Z step: {2.0 * ramp_range / (num_lines - 1):.4f}mm/line)")
    lines.append("; ==========================================================================")
    lines.append("")
    
    # Start G-code
    tool_temp_params = " ".join([f"T{t}_TEMP={nozzle_temp}" for t in tools])
    lines.append("; --- MACHINE START SEQUENCE ---")
    lines.append(f"PRINT_START TOOL_TEMP={nozzle_temp} BED_TEMP={bed_temp} TOOL={tools[0]} MATERIAL={material} {tool_temp_params}")
    lines.append("M83 ; relative extrusion mode")
    lines.append("G90 ; absolute positioning")
    lines.append("")
    
    # Process each tool
    for t_idx, tool_num in enumerate(tools):
        px = tool_x_positions[tool_num]
        py = y_start
        
        lines.append("; --------------------------------------------------------------------------")
        lines.append(f"; TOOLHEAD T{tool_num} OXPLOW TEST PATCH")
        lines.append(f"; Location: X={px:.1f} to {px + patch_length:.1f}, Y={py:.1f} to {py + (num_lines - 1) * line_step:.1f}")
        lines.append("; --------------------------------------------------------------------------")
        
        # Toolchange safely
        lines.append(f"M117 Testing Tool T{tool_num}")
        lines.append("G0 Z20 F3000 ; safe Z lift before toolchange")
        lines.append(f"T{tool_num}")
        lines.append("")
        
        # 1. Purge / Prime Line next to patch (X = px - 8)
        purge_x = px - 8.0
        lines.append("; 1. Prime line to stabilize nozzle pressure")
        lines.append(f"G0 X{purge_x:.2f} Y{py:.2f} Z2.0 F{travel_speed}")
        lines.append(f"G0 Z0.30 F1500")
        lines.append(f"G1 E{retract_length + 0.5:.2f} F{retract_speed} ; prime unretract")
        lines.append(f"G1 X{purge_x:.2f} Y{py + 18.0:.2f} E1.2 F1500 ; purge line")
        lines.append(f"G1 E-{retract_length:.2f} F{retract_speed} ; retract")
        lines.append("G0 Z1.0 F3000")
        lines.append("")
        
        # 2. Tool Number Label (drawn at Y = py - 7 to py - 2)
        lines.append(f"; 2. Draw Tool Identifier 'T{tool_num}'")
        # Draw 'T'
        t_char_x = px + (patch_length / 2.0) - 4.5
        t_char_y = py - 7.0
        # Draw letter T
        lines.append(f"G0 X{t_char_x:.2f} Y{t_char_y + 4.5:.2f} Z{nominal_height:.2f} F{travel_speed}")
        lines.append(f"G1 E{retract_length:.2f} F{retract_speed}")
        lines.append(f"G1 X{t_char_x + 3.0:.2f} Y{t_char_y + 4.5:.2f} E0.13 F1200") # top bar
        lines.append(f"G1 E-{retract_length:.2f} F{retract_speed}")
        lines.append(f"G0 X{t_char_x + 1.5:.2f} Y{t_char_y + 4.5:.2f} F{travel_speed}")
        lines.append(f"G1 E{retract_length:.2f} F{retract_speed}")
        lines.append(f"G1 X{t_char_x + 1.5:.2f} Y{t_char_y:.2f} E0.19 F1200") # stem
        lines.append(f"G1 E-{retract_length:.2f} F{retract_speed}")
        
        # Draw Digit
        digit_strokes = generate_digit_strokes(tool_num, t_char_x + 4.5, t_char_y, scale=0.9)
        for stroke in digit_strokes:
            p1, p2 = stroke[0], stroke[1]
            dist = math.hypot(p2[0] - p1[0], p2[1] - p1[1])
            stroke_e = (dist * line_width * nominal_height) / filament_area
            lines.append(f"G0 X{p1[0]:.2f} Y{p1[1]:.2f} Z{nominal_height:.2f} F{travel_speed}")
            lines.append(f"G1 E{retract_length:.2f} F{retract_speed}")
            lines.append(f"G1 X{p2[0]:.2f} Y{p2[1]:.2f} E{stroke_e:.4f} F1200")
            lines.append(f"G1 E-{retract_length:.2f} F{retract_speed}")
        lines.append("G0 Z1.0 F3000")
        lines.append("")
        
        # 3. Ruler Tick Marks
        # Vạch chia tham chiếu tại -0.10, -0.05, 0.00 (TÂM), +0.05, +0.10 mm
        lines.append("; 3. Draw Scale Tick Marks")
        tick_y_offsets = [
            (0.0, -0.10, False),
            (5.0, -0.05, False),
            (10.0, 0.00, True),  # Center mark (longer)
            (15.0, +0.05, False),
            (20.0, +0.10, False)
        ]
        for y_off, z_diff, is_center in tick_y_offsets:
            ty = py + y_off
            tick_w = 4.0 if is_center else 2.5
            tx1 = px - 2.0 - tick_w
            tx2 = px - 2.0
            dist = tx2 - tx1
            te = (dist * line_width * nominal_height) / filament_area
            lines.append(f"; Mark {z_diff:+.2f}mm at Y={ty:.2f}")
            lines.append(f"G0 X{tx1:.2f} Y{ty:.2f} Z{nominal_height:.2f} F{travel_speed}")
            lines.append(f"G1 E{retract_length:.2f} F{retract_speed}")
            lines.append(f"G1 X{tx2:.2f} Y{ty:.2f} E{te:.4f} F1200")
            lines.append(f"G1 E-{retract_length:.2f} F{retract_speed}")
            
            # If center, draw right tick mark as well
            if is_center:
                rtx1 = px + patch_length + 2.0
                rtx2 = rtx1 + tick_w
                lines.append(f"G0 X{rtx1:.2f} Y{ty:.2f} F{travel_speed}")
                lines.append(f"G1 E{retract_length:.2f} F{retract_speed}")
                lines.append(f"G1 X{rtx2:.2f} Y{ty:.2f} E{te:.4f} F1200")
                lines.append(f"G1 E-{retract_length:.2f} F{retract_speed}")
        lines.append("G0 Z1.0 F3000")
        lines.append("")
        
        # 4. Oxplow Gradient Ramp Patch
        lines.append(f"; 4. Oxplow Ramp: Z={nominal_height - ramp_range:.3f}mm to {nominal_height + ramp_range:.3f}mm")
        # Move to start of patch
        z_start = nominal_height - ramp_range
        lines.append(f"G0 X{px:.2f} Y{py:.2f} Z{z_start:.3f} F{travel_speed}")
        lines.append(f"G1 E{retract_length:.2f} F{retract_speed}")
        
        # Zig-zag hatching
        z_step = (2.0 * ramp_range) / float(num_lines - 1)
        for i in range(num_lines):
            curr_y = py + (i * line_step)
            curr_z = z_start + (i * z_step)
            
            if i % 2 == 0:
                # Left to Right: (px, curr_y) -> (px + patch_length, curr_y)
                lines.append(f"G1 X{px + patch_length:.2f} Y{curr_y:.2f} Z{curr_z:.4f} E{line_e:.4f} F{print_speed}")
                if i < num_lines - 1:
                    next_y = py + ((i + 1) * line_step)
                    next_z = z_start + ((i + 1) * z_step)
                    lines.append(f"G0 X{px + patch_length:.2f} Y{next_y:.2f} Z{next_z:.4f}")
            else:
                # Right to Left: (px + patch_length, curr_y) -> (px, curr_y)
                lines.append(f"G1 X{px:.2f} Y{curr_y:.2f} Z{curr_z:.4f} E{line_e:.4f} F{print_speed}")
                if i < num_lines - 1:
                    next_y = py + ((i + 1) * line_step)
                    next_z = z_start + ((i + 1) * z_step)
                    lines.append(f"G0 X{px:.2f} Y{next_y:.2f} Z{next_z:.4f}")
                    
        # Retract and lift after patch
        lines.append(f"G1 E-{retract_length:.2f} F{retract_speed} ; retract")
        lines.append("G0 Z20 F3000 ; safe Z lift")
        lines.append("")
        
    # End G-code
    lines.append("; --- MACHINE END SEQUENCE ---")
    lines.append("PRINT_END")
    lines.append("M117 Oxplow Z-Test Completed!")
    lines.append("")
    
    return "\n".join(lines)

def main():
    parser = argparse.ArgumentParser(description="Generate Oxplow Multi-Tool Z-Offset test G-code")
    parser.add_argument("--material", choices=["PETG", "ABS", "PLA"], default="PETG", help="Filament material")
    parser.add_argument("--tools", nargs="+", type=int, default=[0, 1, 2, 3, 4], help="Tools to include (e.g. 0 1 2 3 4)")
    parser.add_argument("--bed", type=int, default=None, help="Bed temperature in C")
    parser.add_argument("--nozzle", type=int, default=None, help="Nozzle temperature in C")
    parser.add_argument("--height", type=float, default=0.25, help="Nominal layer height in mm")
    parser.add_argument("--range", type=float, default=0.10, help="Ramp variation +/- range in mm")
    parser.add_argument("-o", "--output", type=str, default=None, help="Output G-code filename")
    
    args = parser.parse_args()
    
    # Defaults by material
    default_temps = {
        "PETG": {"bed": 75, "nozzle": 240},
        "ABS": {"bed": 100, "nozzle": 245},
        "PLA": {"bed": 60, "nozzle": 210}
    }
    
    bed = args.bed if args.bed is not None else default_temps[args.material]["bed"]
    nozzle = args.nozzle if args.nozzle is not None else default_temps[args.material]["nozzle"]
    
    gcode = generate_oxplow_gcode(
        tools=tuple(args.tools),
        material=args.material,
        bed_temp=bed,
        nozzle_temp=nozzle,
        nominal_height=args.height,
        ramp_range=args.range
    )
    
    if args.output:
        out_path = args.output
    else:
        if len(args.tools) == 5:
            out_path = f"Oxplow_5Tool_Z_Test_{args.material}.gcode"
        else:
            tools_str = "T" + "_T".join(map(str, args.tools))
            out_path = f"Oxplow_{tools_str}_Z_Test_{args.material}.gcode"
            
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(gcode)
        
    print(f"Successfully generated: {out_path}")
    print(f"Parameters: Material={args.material}, Bed={bed}C, Nozzle={nozzle}C, Tools={args.tools}")
    print(f"Ramp range: {args.height - args.range:.3f}mm to {args.height + args.range:.3f}mm (Center = {args.height:.3f}mm)")

if __name__ == "__main__":
    main()
