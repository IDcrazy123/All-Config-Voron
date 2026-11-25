"""Compare temporal-row and fixed-bed-wavelength models on saved Klipper meshes.

Usage: python analyze_mesh.py PATH_TO_KLIPPY_LOG
Only reads the log. Matrix line numbers refer to the 25 Nov 2026 snapshot.
Requires NumPy.
"""

import re
import sys
from pathlib import Path

import numpy as np


MESH_LINES = [210557, 227000, 234595, 234760, 234977, 235334, 235570,
              259277, 259450, 259754]
HEATER_OFF = {210557, 227000}
# Time between the Stats lines bracketing each LDC start and mesh completion.
# Resolution is about one second; includes a little setup/zero-reference time.
DURATION_SECONDS = {210557: 117.1, 227000: 117.1, 234595: 69.0,
                    234760: 89.1, 234977: 117.2, 235334: 117.1,
                    235570: 117.1, 259277: 117.1, 259450: 68.1,
                    259754: 68.0}


def read_mesh(lines, line_number):
    i = line_number - 1
    assert lines[i] == "save_config: set [bed_mesh default] points = "
    rows = []
    for row in lines[i + 1:]:
        if not row.startswith("  "):
            break
        rows.append([float(x) for x in row.strip().split(",")])
    mesh = np.asarray(rows)
    tail = lines[i + 1 + len(rows):i + 15 + len(rows)]
    values = {}
    for row in tail:
        match = re.match(r"save_config: set \[bed_mesh default\] (\w+) = (.*)", row)
        if match and match.group(1) in {"x_count", "y_count", "min_y", "max_y"}:
            values[match.group(1)] = float(match.group(2))
    assert mesh.shape == (int(values["y_count"]), int(values["x_count"]))
    y = np.linspace(values["min_y"], values["max_y"], len(mesh))
    z = mesh.mean(axis=1)
    # Remove broad bed bow before fitting the repeating component.
    trend = np.polyval(np.polyfit(np.linspace(-1, 1, len(z)), z, 3),
                       np.linspace(-1, 1, len(z)))
    return y, z - trend


def fit_harmonic(z, coordinate, period):
    phase = 2 * np.pi * coordinate / period
    basis = np.column_stack((np.sin(phase), np.cos(phase)))
    coefficients = np.linalg.lstsq(basis, z, rcond=None)[0]
    predicted = basis @ coefficients
    r2 = 1 - np.sum((z - predicted) ** 2) / np.sum(z ** 2)
    amplitude_um = 1000 * np.linalg.norm(coefficients)
    return r2, amplitude_um


def common_fit(meshes, space=False):
    periods = np.linspace(25, 90, 1301) if space else np.linspace(5, 9, 801)
    scores = []
    for period in periods:
        scores.append(np.mean([fit_harmonic(z, y if space else np.arange(len(z)), period)[0]
                               for y, z in meshes.values()]))
    best = int(np.argmax(scores))
    return periods[best], scores[best]


def time_fit(meshes):
    periods = np.linspace(12, 18, 1201)
    scores = []
    for period in periods:
        scores.append(np.mean([
            fit_harmonic(z, np.arange(len(z)) * DURATION_SECONDS[number] / len(z), period)[0]
            for number, (_, z) in meshes.items()]))
    best = int(np.argmax(scores))
    return periods[best], scores[best]


def main():
    lines = Path(sys.argv[1]).read_text(errors="replace").splitlines()
    meshes = {number: read_mesh(lines, number) for number in MESH_LINES}
    row_period, row_score = common_fit(meshes)
    space_period, space_score = common_fit(meshes, space=True)
    seconds_period, seconds_score = time_fit(meshes)
    print(f"Shared period: rows={row_period:.3f}, mean R2={row_score:.3f}; "
          f"bed Y={space_period:.2f}mm, mean R2={space_score:.3f}; "
          f"approx time={seconds_period:.2f}s, mean R2={seconds_score:.3f}")
    print("line;shape;heater;Ystep_mm;row_R2;bed_R2;row_amp_um;individual_row_period;individual_Y_period_mm")
    for number, (y, z) in meshes.items():
        row = np.arange(len(z))
        rr, amp = fit_harmonic(z, row, row_period)
        sr, _ = fit_harmonic(z, y, space_period)
        candidates = np.linspace(5, 9, 801)
        individual = candidates[np.argmax([fit_harmonic(z, row, p)[0] for p in candidates])]
        individual_y = individual * (y[1] - y[0])
        width = len(lines[number].strip().split(","))
        print(f"{number};{len(z)}x{width};{'off' if number in HEATER_OFF else 'on'};"
              f"{y[1]-y[0]:.2f};{rr:.3f};{sr:.3f};{amp:.1f};{individual:.3f};{individual_y:.1f}")


if __name__ == "__main__":
    main()
