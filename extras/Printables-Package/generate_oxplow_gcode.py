#!/usr/bin/env python3
"""Launch the unchanged published Oxplow toolkit; see README.md for profiles."""
from pathlib import Path
import runpy

if __name__ == "__main__":
    runpy.run_path(str(Path(__file__).resolve().parent / "upstream-2.3.2" / "generate_oxplow_gcode.py"), run_name="__main__")
