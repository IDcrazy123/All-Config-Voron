"""Offline behavioral regression checks for the measured T0 cleaning station.

From the repository root:
    python extras/experiments/t0-cleaner-20261015/test_nozzle_clean_v2.py
Only reads nozzle-clean.cfg and print-macros.cfg. The small interpreter below
records rendered moves and models temperature waits; it never connects to or
controls a printer.
"""

from __future__ import annotations

import ast
import configparser
import copy
from dataclasses import dataclass
from pathlib import Path
import re
from types import SimpleNamespace as NS
import unittest

import jinja2


CONFIG_PATH = (Path(__file__).resolve().parents[3] /
               "config" / "Printer-Setup" / "nozzle-clean.cfg")
PRINT_MACROS_PATH = CONFIG_PATH.with_name("print-macros.cfg")
EXPECTED_GEOMETRY = {
    "safe_z": 15.0,
    "purge_x": 315.0, "purge_y": 1.0, "purge_z": 6.0,
    "purge_plate_x": 315.0, "purge_plate_y": 5.0, "purge_plate_z": 5.0,
    "breakoff_x": 315.0,
    "pad_x_left": 278.0, "pad_x_mid": 294.5, "pad_x_right": 311.0,
    "pad_y_top": -2.0, "pad_y_mid": -5.0, "pad_y_bottom": -8.0,
    "default_clean_z": 0.2,
}


class MacroRejected(RuntimeError):
    """The real macro called action_raise_error during template expansion."""


@dataclass
class Vector:
    x: float
    y: float
    z: float
    e: float = 0.0

    def __getitem__(self, index):
        return (self.x, self.y, self.z, self.e)[index]

    def xyz(self):
        return (self.x, self.y, self.z)


@dataclass
class Move:
    owner: str
    before: tuple
    after: tuple
    temperature: float
    line: str


@dataclass
class Invocation:
    name: str
    params: dict
    position: tuple
    temperature: float


def load_config():
    parser = configparser.RawConfigParser(interpolation=None, strict=True,
                                         inline_comment_prefixes=("#", ";"))
    parser.read(CONFIG_PATH, encoding="utf-8-sig")
    variables = {}
    for key, value in parser["gcode_macro CLEAN_NOZZLE"].items():
        if key.startswith("variable_"):
            try:
                variables[key.removeprefix("variable_")] = ast.literal_eval(value)
            except (ValueError, SyntaxError):
                variables[key.removeprefix("variable_")] = value
    templates = {section.removeprefix("gcode_macro "): parser[section]["gcode"]
                 for section in parser.sections()
                 if section.startswith("gcode_macro ")}
    print_parser = configparser.RawConfigParser(interpolation=None, strict=True,
                                               inline_comment_prefixes=("#", ";"))
    print_parser.read(PRINT_MACROS_PATH, encoding="utf-8-sig")
    templates["PRINT_START"] = print_parser["gcode_macro PRINT_START"]["gcode"]
    return variables, templates


def reject(message):
    raise MacroRejected(message)


class OfflinePrinter:
    def __init__(self, variables, templates):
        # Fallbacks keep failures on the old CFG behavioral and readable rather
        # than failing because newly required fixture attributes are absent.
        self.cfg = NS(**(EXPECTED_GEOMETRY | variables))
        self.templates = templates
        self.env = jinja2.Environment(
            block_start_string="{%", block_end_string="%}",
            variable_start_string="{", variable_end_string="}",
            comment_start_string="{#", comment_end_string="#}",
            autoescape=False,
        )
        self.printer = {
            "gcode_macro CLEAN_NOZZLE": self.cfg,
            "gcode_macro _PRINT_STATE": NS(state="idle"),
            "toolchanger": NS(status="ready", tool_number=0,
                              tool_numbers=[0, 1, 2, 3, 4],
                              tool_names=[f"tool T{i}" for i in range(5)]),
            "tool T0": NS(extruder="extruder", fan="T0_part_fan"),
            "toolhead": NS(extruder="extruder", homed_axes="xyz",
                           position=Vector(100.0, 100.0, 15.0)),
            "gcode_move": NS(homing_origin=Vector(0.0, 0.0, 0.0),
                             gcode_position=Vector(100.0, 100.0, 15.0)),
            "print_stats": NS(state="standby"),
            "pause_resume": NS(is_paused=False),
            "bed_mesh": NS(mesh_matrix=[[]]),
            "quad_gantry_level": NS(applied=True),
            "extruder": NS(temperature=150.0, target=150.0, can_extrude=False),
            "heater_bed": NS(temperature=30.0, target=0.0),
            "fan_generic T0_part_fan": NS(speed=0.25),
        }
        for tool in range(5):
            self.printer[f"tool T{tool}"] = NS(
                extruder="extruder" if tool == 0 else f"extruder{tool}",
                fan=f"T{tool}_part_fan", params_standby_temp=150)
        self.moves = []
        self.calls = []
        self.events = []
        self.absolute = True
        self.absolute_e = True
        self.saved = {}

    def set_position(self, xyz):
        self.printer["toolhead"].position = Vector(*xyz)
        self.printer["gcode_move"].gcode_position = Vector(*xyz)

    def render(self, name, **params):
        return self.env.from_string(self.templates[name]).render(
            printer=self.printer, params={key.upper(): str(value)
                                         for key, value in params.items()},
            action_raise_error=reject,
            action_respond_info=lambda message: "",
            rawparams=" ".join(f"{key}={value}" for key, value in params.items()),
        )

    def run(self, name, **params):
        self.calls.append(Invocation(name, {key.upper(): str(value)
                                           for key, value in params.items()},
                                     self.printer["gcode_move"].gcode_position.xyz(),
                                     self.printer["extruder"].temperature))
        rendered = self.render(name, **params)
        for line in rendered.splitlines():
            line = line.split("#", 1)[0].split(";", 1)[0].strip()
            if not line:
                continue
            command, *tokens = line.split()
            arguments = dict(token.split("=", 1) for token in tokens if "=" in token)
            self.events.append((name, command, arguments, line))
            if command in self.templates:
                self.run(command, **arguments)
            elif command == "G90":
                self.absolute = True
            elif command == "G91":
                self.absolute = False
            elif command == "M82":
                self.absolute_e = True
            elif command == "M83":
                self.absolute_e = False
            elif command in ("G0", "G1"):
                position = copy.copy(self.printer["gcode_move"].gcode_position)
                before = position.xyz()
                for axis, value in re.findall(r"(?:^|\s)([XYZE])(-?\d+(?:\.\d+)?)", line):
                    attr = axis.lower()
                    is_absolute = self.absolute_e if axis == "E" else self.absolute
                    setattr(position, attr, float(value) if is_absolute else
                            getattr(position, attr) + float(value))
                self.printer["gcode_move"].gcode_position = position
                self.printer["toolhead"].position = copy.copy(position)
                self.moves.append(Move(name, before, position.xyz(),
                                       self.printer["extruder"].temperature, line))
            elif command == "SET_HEATER_TEMPERATURE":
                self.printer[arguments["HEATER"]].target = float(arguments["TARGET"])
            elif command == "TEMPERATURE_WAIT":
                heater = self.printer[arguments["SENSOR"]]
                if "MINIMUM" in arguments:
                    heater.temperature = max(heater.temperature, float(arguments["MINIMUM"]))
                if "MAXIMUM" in arguments:
                    heater.temperature = min(heater.temperature, float(arguments["MAXIMUM"]))
                heater.can_extrude = heater.temperature >= 170.0
            elif command == "SET_FAN_SPEED":
                self.printer["fan_generic " + arguments["FAN"]].speed = float(arguments["SPEED"])
            elif command == "SAVE_GCODE_STATE":
                self.saved[arguments["NAME"]] = (self.absolute, self.absolute_e)
            elif command == "RESTORE_GCODE_STATE":
                if int(arguments.get("MOVE", 0)) != 0:
                    raise AssertionError("Cleaner must not restore a prior XYZ position")
                self.absolute, self.absolute_e = self.saved[arguments["NAME"]]
        return rendered


class NozzleCleanV2(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.variables, cls.templates = load_config()

    def fixture(self):
        return OfflinePrinter(self.variables, self.templates)

    def test_measured_geometry_and_bucket_compatibility(self):
        for key, expected in EXPECTED_GEOMETRY.items():
            with self.subTest(variable=key):
                self.assertIn(key, self.variables)
                self.assertAlmostEqual(float(self.variables[key]), expected)

    def assert_station_path(self, simulator, passes, reverse, breakoff, clean_z):
        moves = [move for move in simulator.moves
                 if move.owner == "_CLEAN_NOZZLE_WIPE_PATH"]
        strokes = []
        breakoff_strokes = []
        purge_corridors = []
        for move in moves:
            ax, ay, az = move.before
            bx, by, bz = move.after
            xy_changed = (ax, ay) != (bx, by)
            for x, y, z in (move.before, move.after):
                self.assertTrue(0 <= x <= 350 and -10 <= y <= 350 and 0 <= z <= 350,
                                f"Move outside machine bounds: {move}")
            if not xy_changed:
                continue
            if min(az, bz) >= 15.0:
                continue
            if (move.before, move.after) == ((315.0, 5.0, 5.0), (315.0, -5.0, 5.0)):
                self.assertEqual(breakoff, 1,
                                 "Only a guarded breakoff may use the low purge corridor")
                purge_corridors.append(move)
                continue
            self.assertAlmostEqual(az, clean_z, msg=f"Low XY transfer: {move}")
            self.assertAlmostEqual(bz, clean_z, msg=f"Sloped contact move: {move}")
            if (ax, ay, bx, by) == (315.0, -5.0, 278.0, -5.0):
                breakoff_strokes.append(move)
                continue
            self.assertTrue(278.0 <= ax <= 311.0 and 278.0 <= bx <= 311.0,
                            f"Contact outside pad X inset: {move}")
            self.assertTrue(-8.0 <= ay <= -2.0 and -8.0 <= by <= -2.0,
                            f"Contact outside measured silicone ribs: {move}")
            if ay == by and {ax, bx} == {278.0, 311.0}:
                strokes.append(move)
        self.assertEqual(len(breakoff_strokes), breakoff)
        self.assertEqual(len(purge_corridors), breakoff,
                         "Breakoff must approach on the same X directly from the purge plate")
        if breakoff:
            contacts = [move for move in moves if move.before[:2] != move.after[:2]
                        and min(move.before[2], move.after[2]) <= clean_z]
            self.assertEqual(contacts[0], breakoff_strokes[0],
                             "Blob must be broken off before the raster")
            first_strike_index = moves.index(breakoff_strokes[0])
            for move in moves[:first_strike_index + 1]:
                self.assertLessEqual(max(move.before[2], move.after[2]), 5.0,
                                     "Do not lift between supported purge and first strike")
        self.assertEqual(len(strokes), passes * 3,
                         "Each pass must sweep the full width of all three ribs")
        for index in range(passes):
            group = strokes[index * 3:index * 3 + 3]
            self.assertEqual({move.before[1] for move in group}, {-8.0, -5.0, -2.0})
            first_y = -2.0 if (index + reverse) % 2 == 0 else -8.0
            self.assertEqual(group[0].before[1], first_y,
                             "Successive passes must reverse the row order")
        self.assertGreaterEqual(moves[-1].after[2], 15.0)

    def test_raster_coverage_direction_and_safe_transfers(self):
        for passes in range(1, 6):
            for reverse in (0, 1):
                for breakoff in (0, 1):
                    for clean_z in (0.2, 1.0):
                        with self.subTest(passes=passes, reverse=reverse,
                                          breakoff=breakoff, clean_z=clean_z):
                            sim = self.fixture()
                            sim.set_position((315.0, 5.0, 5.0))
                            sim.run("_CLEAN_NOZZLE_WIPE_PATH", WIPES=passes,
                                    START_REVERSE=reverse, BREAKOFF=breakoff,
                                    CLEAN_Z=clean_z)
                            self.assert_station_path(sim, passes, reverse, breakoff, clean_z)

    def test_default_breakoff_is_disabled(self):
        sim = self.fixture()
        sim.run("_CLEAN_NOZZLE_WIPE_PATH")
        self.assert_station_path(sim, 1, 0, 0, 0.2)

    def test_main_sequence_purge_location_cooldown_and_one_breakoff(self):
        for purge in (0, 40):
            for wipes in (1, 3):
                with self.subTest(purge=purge, wipes=wipes):
                    sim = self.fixture()
                    sim.run("CLEAN_NOZZLE", MODE="DEEP", PURGE=purge,
                            PURGE_TEMP=250, WIPES=wipes)
                    wipe_calls = [call for call in sim.calls
                                  if call.name == "_CLEAN_NOZZLE_WIPE_PATH"]
                    purge_calls = [call for call in sim.calls
                                   if call.name == "_CLEAN_NOZZLE_PURGE"]
                    self.assertEqual(sum(int(call.params.get("WIPES", 1))
                                         for call in wipe_calls), wipes)
                    self.assertEqual(sum(int(call.params.get("BREAKOFF", 0))
                                         for call in wipe_calls), int(purge > 0))
                    self.assertLessEqual(wipe_calls[-1].temperature, 150.0)
                    self.assertTrue(all(call.temperature <= 170 for call in wipe_calls))
                    self.assertEqual(len(purge_calls), int(purge > 0))
                    if purge:
                        self.assertEqual(purge_calls[0].position, (315.0, 5.0, 5.0),
                                         "Extrusion must happen on the PEI plate, not at the bucket")
                        self.assertGreaterEqual(purge_calls[0].temperature, 250)
                        self.assertEqual(int(wipe_calls[0].params.get("BREAKOFF", 0)), 1)
                        purge_indices = [i for i, move in enumerate(sim.moves)
                                         if move.owner == "_CLEAN_NOZZLE_PURGE"]
                        strike_indices = [i for i, move in enumerate(sim.moves)
                                          if move.before == (315.0, -5.0, 0.2)
                                          and move.after == (278.0, -5.0, 0.2)]
                        self.assertEqual(len(strike_indices), 1)
                        for move in sim.moves[purge_indices[-1]:strike_indices[0] + 1]:
                            self.assertLessEqual(max(move.before[2], move.after[2]), 5.0,
                                                 "Parent must preserve the supported blob until breakoff")
                    self.assertEqual(sim.printer["gcode_move"].gcode_position.xyz(),
                                     (315.0, 1.0, 6.0), "DEEP must finish parked at the bucket")
                    self.assertAlmostEqual(sim.printer["fan_generic T0_part_fan"].speed, 0.25)
                    for move in sim.moves:
                        for x, y, z in (move.before, move.after):
                            self.assertTrue(0 <= x <= 350 and -10 <= y <= 350 and 0 <= z <= 350,
                                            f"Parent sequence outside machine bounds: {move}")
                        if move.owner == "CLEAN_NOZZLE" and move.before[:2] != move.after[:2]:
                            self.assertGreaterEqual(min(move.before[2], move.after[2]), 15.0,
                                                    f"Unsafe station/parking transfer: {move}")

    def test_mode_and_wrapper_default_passes(self):
        for macro, params, expected in (
            ("CLEAN_NOZZLE", {"MODE": "DEEP"}, 3),
            ("CLEAN_NOZZLE", {"MODE": "TOUCH"}, 1),
            ("PURGE_AND_CLEAN", {"PURGE_TEMP": 250}, 3),
        ):
            with self.subTest(macro=macro, params=params):
                sim = self.fixture()
                sim.run(macro, **params)
                wipes = [call for call in sim.calls
                         if call.name == "_CLEAN_NOZZLE_WIPE_PATH"]
                self.assertEqual(sum(int(call.params.get("WIPES", 1)) for call in wipes), expected)
                self.assertTrue(all(float(call.params.get("CLEAN_Z", 0.2)) == 0.2
                                    for call in wipes))

    def test_clean_z_guards_and_breakoff_domain(self):
        for macro in ("CLEAN_NOZZLE", "_CLEAN_NOZZLE_WIPE_PATH"):
            for clean_z in (-1, 0.199, 1.001):
                with self.subTest(macro=macro, clean_z=clean_z):
                    with self.assertRaises(MacroRejected):
                        self.fixture().render(macro, CLEAN_Z=clean_z)
        for breakoff in (-1, 2, 9):
            with self.subTest(breakoff=breakoff):
                sim = self.fixture()
                sim.set_position((315.0, 5.0, 5.0))
                with self.assertRaises(MacroRejected):
                    sim.render("_CLEAN_NOZZLE_WIPE_PATH", BREAKOFF=breakoff)

    def test_breakoff_rejects_an_unverified_start_pose(self):
        for position in ((315.0, 1.0, 6.0), (315.0, -5.0, 15.0),
                         (315.3, 5.0, 5.0), (315.0, 5.3, 5.0),
                         (315.0, 5.0, 5.3)):
            with self.subTest(position=position):
                sim = self.fixture()
                sim.set_position(position)
                with self.assertRaises(MacroRejected):
                    sim.render("_CLEAN_NOZZLE_WIPE_PATH", BREAKOFF=1)

    def purge_fixture(self):
        sim = self.fixture()
        sim.set_position((315.0, 5.0, 5.0))
        sim.printer["extruder"].temperature = 250.0
        sim.printer["extruder"].can_extrude = True
        return sim

    def test_purge_rechecks_temperature_and_actual_plate_position(self):
        params = {"EXTRUDER": "extruder", "PURGE": 40}
        good = self.purge_fixture()
        good.run("_CLEAN_NOZZLE_PURGE", **params)
        self.assertTrue(any("E40" in move.line for move in good.moves))
        for position in ((315, 1, 6), (315.3, 5, 5), (315, 5.3, 5), (315, 5, 5.3)):
            with self.subTest(position=position):
                sim = self.purge_fixture()
                sim.set_position(position)
                with self.assertRaises(MacroRejected):
                    sim.render("_CLEAN_NOZZLE_PURGE", **params)
        for temperature, can_extrude in ((160, False), (283, True)):
            with self.subTest(temperature=temperature):
                sim = self.purge_fixture()
                sim.printer["extruder"].temperature = temperature
                sim.printer["extruder"].can_extrude = can_extrude
                with self.assertRaises(MacroRejected):
                    sim.render("_CLEAN_NOZZLE_PURGE", **params)

    def test_shared_safety_guards(self):
        mutations = {
            "mesh": lambda p: setattr(p["bed_mesh"], "mesh_matrix", [[0.0]]),
            "offset": lambda p: setattr(p["gcode_move"].homing_origin, "z", 0.01),
            "wrong_tool": lambda p: setattr(p["toolchanger"], "tool_number", 1),
            "wrong_extruder": lambda p: setattr(p["toolhead"], "extruder", "extruder1"),
            "not_ready": lambda p: setattr(p["toolchanger"], "status", "uninitialized"),
            "unhomed": lambda p: setattr(p["toolhead"], "homed_axes", "xy"),
            "paused": lambda p: setattr(p["pause_resume"], "is_paused", True),
            "printing": lambda p: setattr(p["print_stats"], "state", "printing"),
        }
        for macro in ("CLEAN_NOZZLE", "_CLEAN_NOZZLE_WIPE_PATH",
                      "_CLEAN_NOZZLE_PURGE", "_CLEAN_NOZZLE_PARK"):
            params = {"EXTRUDER": "extruder", "PURGE": 40, "PURGE_TEMP": 250}
            self.purge_fixture().render(macro, **params)
            for label, mutate in mutations.items():
                # Purge checks its EXTRUDER argument as the selected heater;
                # all other helpers validate the toolhead extruder directly.
                if macro == "_CLEAN_NOZZLE_PURGE" and label == "wrong_extruder":
                    continue
                with self.subTest(macro=macro, condition=label):
                    sim = self.purge_fixture()
                    mutate(sim.printer)
                    with self.assertRaises(MacroRejected):
                        sim.render(macro, **params)

    @staticmethod
    def command_arguments(lines, command):
        matches = [line for line in lines if line.split()[0] == command]
        return [dict(token.split("=", 1) for token in line.split()[1:]
                     if "=" in token) for line in matches]

    def print_start_plan(self, **overrides):
        params = {"TOOL": 2, "TOOL_TEMP": 235, "T2_TEMP": 235,
                  "BED_TEMP": 70, "MATERIAL": "ABS",
                  "T0_PURGE_TEMP": 225, "T0_MATERIAL": "PLA"}
        params.update(overrides)
        rendered = self.fixture().render("PRINT_START", **params)
        return [line.split("#", 1)[0].split(";", 1)[0].strip()
                for line in rendered.splitlines()
                if line.strip() and not line.lstrip().startswith(("#", ";"))]

    def test_print_start_purges_even_when_t0_is_not_a_print_tool(self):
        lines = self.print_start_plan()
        cleans = self.command_arguments(lines, "CLEAN_NOZZLE")
        deep = next(args for args in cleans if args.get("MODE") == "DEEP")
        touch = next(args for args in cleans if args.get("MODE") == "TOUCH")
        self.assertEqual(float(deep["PURGE"]), 40.0)
        self.assertEqual(float(deep["PURGE_TEMP"]), 225.0,
                         "Use T0's own profile temperature, not initial tool/material temperature")
        self.assertEqual(float(deep["TEMP"]), 150.0)
        self.assertEqual(int(deep["WIPES"]), 3)
        self.assertEqual(float(touch["TEMP"]), 150.0)
        prime = self.command_arguments(lines, "PRIME_LINES")
        self.assertEqual(len(prime), 1)
        self.assertNotIn("T0_TEMP", prime[0],
                         "A cleaning temperature must not mark T0 as used for printing")
        self.assertEqual(float(prime[0]["T2_TEMP"]), 235.0)
        touch_index = next(i for i, line in enumerate(lines)
                           if line.split()[0] == "CARTOGRAPHER_TOUCH_HOME")
        final_targets = {}
        for line in lines[touch_index + 1:]:
            match = re.fullmatch(r"M104\s+T(\d+)\s+S([\d.]+)", line)
            if match:
                final_targets[int(match[1])] = float(match[2])
        self.assertEqual(final_targets[0], 0.0)
        self.assertEqual(final_targets[2], 235.0)

    def test_print_start_dedicated_temperature_is_independent_of_used_mask(self):
        unused = self.print_start_plan(T0_PURGE_TEMP=250)
        used = self.print_start_plan(T0_PURGE_TEMP=250, T0_TEMP=225)
        for lines in (unused, used):
            deep = next(args for args in self.command_arguments(lines, "CLEAN_NOZZLE")
                        if args.get("MODE") == "DEEP")
            self.assertEqual(float(deep["PURGE_TEMP"]), 250.0)
        unused_prime = self.command_arguments(unused, "PRIME_LINES")[0]
        used_prime = self.command_arguments(used, "PRIME_LINES")[0]
        self.assertNotIn("T0_TEMP", unused_prime)
        self.assertEqual(float(used_prime["T0_TEMP"]), 225.0,
                         "T0's print temperature must remain independent of its purge temperature")

    def test_print_start_missing_t0_temperature_rejects_before_actions(self):
        sim = self.fixture()
        with self.assertRaises(MacroRejected):
            sim.run("PRINT_START", TOOL=2, TOOL_TEMP=235, T2_TEMP=235,
                    BED_TEMP=70, MATERIAL="ABS")
        self.assertEqual(sim.events, [],
                         "Missing T0 temperature must fail before heater, homing or other G-code")
        self.assertEqual(sim.moves, [])

    def test_print_start_legacy_t0_temperature_fallbacks(self):
        scenarios = (
            ({"TOOL": 2, "TOOL_TEMP": 235, "T2_TEMP": 235, "T0_TEMP": 225}, 225),
            ({"TOOL": 0, "TOOL_TEMP": 220, "T0_TEMP": 225}, 225),
            ({"TOOL": 0, "TOOL_TEMP": 220}, 220),
        )
        for params, expected in scenarios:
            with self.subTest(params=params):
                rendered = self.fixture().render("PRINT_START", BED_TEMP=70, **params)
                lines = [line.strip() for line in rendered.splitlines() if line.strip()]
                deep = next(args for args in self.command_arguments(lines, "CLEAN_NOZZLE")
                            if args.get("MODE") == "DEEP")
                self.assertEqual(float(deep["PURGE_TEMP"]), float(expected))
                self.assertEqual(float(deep["PURGE"]), 40.0)

    def test_print_start_invalid_t0_temperature_rejects_before_actions(self):
        for temperature in (0, 169, 281, 999):
            with self.subTest(temperature=temperature):
                sim = self.fixture()
                with self.assertRaises(MacroRejected):
                    sim.run("PRINT_START", TOOL=2, TOOL_TEMP=235, T2_TEMP=235,
                            BED_TEMP=70, T0_PURGE_TEMP=temperature, T0_MATERIAL="PLA")
                self.assertEqual(sim.events, [])


if __name__ == "__main__":
    unittest.main(verbosity=2)
