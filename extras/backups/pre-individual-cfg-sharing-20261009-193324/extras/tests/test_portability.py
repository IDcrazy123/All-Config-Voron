"""Offline include/Jinja and portability regression checks. No printer access.

Run: python extras/tests/test_portability.py (requires jinja2).
These checks do not validate pins, plugin loading, physical clearance or heating.
"""
import ast
import configparser
import glob
import io
from pathlib import Path
from collections import namedtuple
import unittest

import jinja2

ROOT = Path(__file__).resolve().parents[2]
ENV = jinja2.Environment('{%', '%}', '{', '}')
Coord = namedtuple('Coord', 'x y z e', defaults=[0])


def load_config(root=ROOT / 'config'):
    parser = configparser.RawConfigParser(
        strict=False, inline_comment_prefixes=(';', '#'))
    visited = set()
    files = set()

    def read(path):
        path = path.resolve()
        if path in visited:
            raise ValueError('Recursive include: ' + str(path))
        visited.add(path)
        files.add(path)
        buf = []
        for raw in path.read_text(encoding='utf-8-sig').splitlines():
            line = raw.split('#', 1)[0]
            match = parser.SECTCRE.match(line)
            header = match and match.group('header')
            if header and header.startswith('include '):
                parser.read_file(io.StringIO('\n'.join(buf)), str(path))
                buf = []
                pattern = str(path.parent / header[8:].strip())
                matches = sorted(glob.glob(pattern))
                if not matches and not glob.has_magic(pattern):
                    raise FileNotFoundError(pattern)
                for filename in matches:
                    read(Path(filename))
            else:
                buf.append(line)
        parser.read_file(io.StringIO('\n'.join(buf)), str(path))
        visited.remove(path)

    read(root / 'printer.cfg')
    return parser, files


CFG, FILES = load_config()


def printer_fixture():
    p = {'configfile': {'config': {}, 'settings': {}}}
    for section in CFG.sections():
        options = dict(CFG[section])
        p['configfile']['config'][section] = options
        settings = {}
        for key, value in options.items():
            try:
                settings[key] = ast.literal_eval(value)
            except (ValueError, SyntaxError):
                settings[key] = value
        p['configfile']['settings'][section] = settings
        if section.startswith('gcode_macro '):
            p[section] = {}
            for key, value in options.items():
                if key.startswith('variable_'):
                    p[section][key[9:]] = ast.literal_eval(value)
    p.update({
        'toolhead': {'homed_axes': 'xyz', 'position': Coord(180, 168, 30),
                     'axis_minimum': Coord(0, -10, -5),
                     'axis_maximum': Coord(348, 336, 347), 'extruder': 'extruder'},
        'gcode_move': {'homing_origin': Coord(0, 0, 0),
                       'gcode_position': Coord(180, 168, 30)},
        'toolchanger': {'tool_numbers': list(range(5)),
                        'tool_names': ['tool T' + str(t) for t in range(5)],
                        'tool_number': 0, 'status': 'ready'},
        'print_stats': {'state': 'standby'},
        'pause_resume': {'is_paused': False},
        'heater_bed': {'temperature': 25},
    })
    for t in range(5):
        tool = 'tool T' + str(t)
        p[tool] = {'extruder': 'extruder' if t == 0 else 'extruder' + str(t),
                   'fan': 'T' + str(t) + '_part_fan', 'params_standby_temp': 150}
        p[p[tool]['extruder']] = {'temperature': 200, 'target': 220, 'can_extrude': True}
    return p


def render(name, printer=None, params=None):
    section = 'gcode_macro ' + name
    printer = printer or printer_fixture()

    def raise_error(message):
        raise ValueError(message)

    context = {'printer': printer, 'params': params or {}, 'rawparams': '',
               'action_raise_error': raise_error, 'action_respond_info': lambda _: ''}
    context.update(printer.get(section, {}))
    return ENV.from_string(CFG[section]['gcode']).render(context)


class PortabilityTests(unittest.TestCase):
    def test_all_loaded_templates_compile(self):
        count = 0
        for section in CFG.sections():
            for key, value in CFG[section].items():
                if key == 'gcode' or key.endswith('_gcode'):
                    ENV.from_string(value)
                    count += 1
        self.assertGreater(count, 60)
        self.assertIn((ROOT / 'config/printer.cfg').resolve(), FILES)

    def test_soak_defaults_and_machine_override(self):
        params = {'BED_TEMP': '100', 'BED_START': '25', 'MATERIAL': 'ABS'}
        self.assertIn('G4 P90000', render('_PRINT_START_HEAT_SOAK', params=params))
        p = printer_fixture()
        p['gcode_macro _PRINT_START_HEAT_SOAK']['abs_soak'] = 300
        self.assertIn('G4 P300000', render('_PRINT_START_HEAT_SOAK', p, params))
        params['SOAK'] = '120'
        self.assertIn('G4 P120000', render('_PRINT_START_HEAT_SOAK', p, params))

    def test_custom_sparse_tool_mapping_and_heater_limit(self):
        p = printer_fixture()
        p['toolchanger'].update(tool_numbers=[0, 7], tool_names=['tool T0', 'tool spare'])
        p['tool spare'] = {'extruder': 'extruder1', 'fan': 'spare_cooling',
                           'params_standby_temp': 160}
        p['configfile']['config']['fan_generic spare_cooling'] = {}
        p['fan_generic spare_cooling'] = {'speed': 0}
        out = render('MEASURE_TOOL_HEATUP', p, {'TOOL': '7', 'TARGET': '240'})
        self.assertIn('HEATER=extruder1 TARGET=240.0', out)
        p['configfile']['settings']['extruder1']['max_temp'] = 230
        with self.assertRaisesRegex(ValueError, 'max_temp'):
            render('MEASURE_TOOL_HEATUP', p, {'TOOL': '7', 'TARGET': '240'})
        for name in ('PRINT_END', '_CUSTOM_CANCEL_CLEANUP'):
            out = render(name, p)
            self.assertIn('SET_FAN_SPEED FAN=spare_cooling SPEED=0', out)
            self.assertIn('SET_STEPPER_ENABLE STEPPER=extruder1 ENABLE=0', out)
            self.assertNotIn('extruder7', out)
        out = render('_PRIME_LINES_TOOL', p, {'T': '7', 'TEMP': '220',
                                             'SLOT': '0', 'COUNT': '2', 'FINAL': '0'})
        self.assertIn('M104 T7 S160', out)

    def test_benchmark_uses_station_geometry(self):
        p = printer_fixture()
        p['gcode_macro CLEAN_NOZZLE'].update(purge_x=250, purge_y=8, safe_z=45)
        out = render('MEASURE_TOOL_HEATUP', p, {'TOOL': '0'})
        self.assertIn('G1 X250.0 Y8.0', out)
        self.assertIn('G1 Z45.0', out)

    def test_deadband_maps_tool_number_without_changing_thermal_window(self):
        p = printer_fixture()
        p['toolchanger'].update(tool_numbers=[0, 7], tool_names=['tool T0', 'tool spare'])
        p['tool spare'] = {'extruder': 'extruder1'}
        out = render('SET_TEMPERATURE_WITH_DEADBAND', p, {'T': '7', 'S': '220'})
        self.assertIn('HEATER=extruder1 TARGET=220', out)
        self.assertIn('SENSOR=extruder1 MINIMUM=218.0 MAXIMUM=222.0', out)
        with self.assertRaisesRegex(ValueError, 'positive'):
            render('SET_TEMPERATURE_WITH_DEADBAND', p, {'T': '7', 'S': '220', 'D': '0'})

    def test_benchmark_rejects_print_pause_dryer_and_invalid_controls(self):
        for state in ('printing', 'paused'):
            p = printer_fixture()
            p['print_stats']['state'] = state
            with self.assertRaisesRegex(ValueError, 'print'):
                render('MEASURE_TOOL_HEATUP', p)
        p = printer_fixture()
        p['gcode_macro _DRYER_STATUS']['is_drying'] = 1
        with self.assertRaisesRegex(ValueError, 'dryer'):
            render('MEASURE_TOOL_HEATUP', p)
        for params in ({'TOOL': '9'}, {'TIMEOUT': '0'}, {'COOLDOWN': '2'}, {'PARK_BUCKET': '2'}):
            with self.assertRaises(ValueError):
                render('MEASURE_TOOL_HEATUP', params=params)

    def test_print_and_dryer_reject_active_benchmark(self):
        p = printer_fixture()
        p['gcode_macro _TOOL_HEATUP_VARS']['is_running'] = 1
        for name in ('PRINT_START', 'START_DRYER'):
            with self.assertRaisesRegex(ValueError, 'benchmark'):
                render(name, p, {'TOOL_TEMP': '220', 'BED_TEMP': '70'})

    def test_prime_rejects_missing_initial_temp_before_output(self):
        with self.assertRaisesRegex(ValueError, 'temperature'):
            render('PRIME_LINES', params={'INITIAL_TOOL': '0', 'T1_TEMP': '220'})

    def test_prime_slots_reject_impossible_small_bed(self):
        p = printer_fixture()
        p['toolhead']['axis_maximum'] = Coord(65, 80, 100)
        with self.assertRaisesRegex(ValueError, 'fit'):
            render('PRIME_LINES', p, {'INITIAL_TOOL': '0', 'T0_TEMP': '220', 'T1_TEMP': '220'})

    def test_current_five_tool_prime_order(self):
        params = {'INITIAL_TOOL': '2', **{'T%d_TEMP' % t: '220' for t in range(5)}}
        lines = [line.strip() for line in render('PRIME_LINES', params=params).splitlines()
                 if line.strip().startswith('_PRIME_LINES_TOOL ')]
        self.assertEqual([int(line.split('T=')[1].split()[0]) for line in lines], [0, 1, 3, 4, 2])
        self.assertIn('COUNT=5 FINAL=1', lines[-1])


if __name__ == '__main__':
    unittest.main(verbosity=2)
