"""Render/replay isolated CFG features against declared runtime prerequisites.

No printer/network access. This models macro expansion/variable writes, not
Klipper scheduling, motion clearance, firmware loading or thermal dynamics.
Run: python -m unittest discover -s extras/tests -v (requires jinja2).
"""
import ast
import configparser
from pathlib import Path
import shlex
import unittest
from collections import namedtuple

import jinja2

ROOT = Path(__file__).resolve().parents[2]
Coord = namedtuple('Coord', 'x y z e', defaults=[0])
ENV = jinja2.Environment('{%', '%}', '{', '}')


class Feature:
    def __init__(self, filename, numbers=(0, 1)):
        self.cfg = configparser.RawConfigParser(inline_comment_prefixes=('#', ';'))
        self.cfg.read(ROOT / 'config' / filename, encoding='utf-8-sig')
        p = self.p = {
            'configfile': {'config': {}, 'settings': {
                'printer': {'max_velocity': 350, 'max_accel': 7000,
                            'max_z_velocity': 80, 'max_z_accel': 1000}}},
            'print_stats': {'state': 'standby'}, 'pause_resume': {'is_paused': False},
            'toolhead': {'homed_axes': 'xyz', 'axis_minimum': Coord(0, -10, -5),
                         'axis_maximum': Coord(348, 336, 347),
                         'position': Coord(180, 168, 30), 'extruder': 'extruder',
                         'max_velocity': 125, 'max_accel': 900,
                         'minimum_cruise_ratio': 0.3},
            'gcode_move': {'homing_origin': Coord(0, 0, 0),
                           'gcode_position': Coord(180, 168, 30)},
            'toolchanger': {'tool_numbers': list(numbers),
                            'tool_names': ['tool custom' + str(n) for n in numbers],
                            'tool_number': numbers[0], 'status': 'ready'},
            'heater_bed': {'temperature': 25, 'target': 0},
        }
        for section in self.cfg.sections():
            p['configfile']['config'][section] = dict(self.cfg[section])
            if section.startswith('gcode_macro '):
                p[section] = {k[9:]: ast.literal_eval(v)
                              for k, v in self.cfg[section].items()
                              if k.startswith('variable_')}
        for index, n in enumerate(numbers):
            ext = 'extruder' if index == 0 else 'extruder' + str(index)
            p['tool custom' + str(n)] = {'extruder': ext, 'fan': 'cooling' + str(n),
                                        'params_standby_temp': 150}
            p[ext] = {'temperature': 150, 'target': 220, 'can_extrude': True}
            p['fan_generic cooling' + str(n)] = {'speed': 0}
            p['configfile']['config']['fan_generic cooling' + str(n)] = {}
            p['configfile']['settings'][ext] = {'max_temp': 290}
        p['configfile']['settings']['heater_bed'] = {'max_temp': 120}

    def render(self, name, params=None, delayed=False):
        section = ('delayed_gcode ' if delayed else 'gcode_macro ') + name

        def fail(message):
            raise ValueError(message)

        context = dict(printer=self.p, params=params or {}, rawparams='',
                       action_raise_error=fail, action_respond_info=lambda _: '')
        context.update(self.p.get(section, {}))
        return ENV.from_string(self.cfg[section]['gcode']).render(context)

    def replay(self, name, params=None):
        """Expand only this file's helpers; flag calls to undeclared project macros."""
        lines = []
        for raw in self.render(name, params).splitlines():
            line = raw.strip()
            if not line or line.startswith('#'):
                continue
            command, *words = shlex.split(line)
            args = dict(w.split('=', 1) for w in words if '=' in w)
            if command == 'SET_GCODE_VARIABLE':
                self.p['gcode_macro ' + args['MACRO']][args['VARIABLE']] = ast.literal_eval(args['VALUE'])
            elif 'gcode_macro ' + command in self.cfg:
                lines.extend(self.replay(command, args).splitlines())
                continue
            elif command.startswith('_'):
                raise AssertionError('Undeclared project helper: ' + command)
            elif command == 'SET_HEATER_TEMPERATURE':
                self.p[args['HEATER']]['target'] = float(args['TARGET'])
            lines.append(line)
        return '\n'.join(lines)


class IndividualFeatureTests(unittest.TestCase):
    def bench(self, numbers=(0, 1)):
        return Feature('Printer-Setup/tool-temp-bench.cfg', numbers)

    def dryer(self):
        f = Feature('Printer-Setup/filament-dryer.cfg')
        f.p['fan_generic bed_fan'] = {'speed': 0}
        return f

    def cleaner(self):
        f = Feature('Printer-Setup/nozzle-clean.cfg')
        f.p['bed_mesh'] = {'mesh_matrix': [[]]}
        f.p['quad_gantry_level'] = {'applied': True}
        return f

    def test_bench_isolated_two_five_six_and_sparse_tools(self):
        for numbers in ((0, 1), tuple(range(5)), tuple(range(6)), (0, 7)):
            with self.subTest(numbers=numbers):
                f = self.bench(numbers)
                out = f.replay('MEASURE_TOOL_HEATUP', {'TOOL': str(numbers[-1]), 'TARGET': '240'})
                ext = 'extruder' + str(len(numbers) - 1)
                self.assertIn('HEATER=' + ext + ' TARGET=240.0', out)
                self.assertNotRegex(out, r'(?m)^G[01] ')
                self.assertNotIn('_SET_', out)
                self.assertEqual(f.p['gcode_macro _TOOL_HEATUP_VARS']['is_running'], 1)

    def test_bench_explicit_park_preflight(self):
        f = self.bench()
        with self.assertRaisesRegex(ValueError, 'no station'):
            f.render('MEASURE_TOOL_HEATUP', {'PARK_BUCKET': '1'})
        with self.assertRaisesRegex(ValueError, 'together'):
            f.render('MEASURE_TOOL_HEATUP', {'PARK_BUCKET': '1', 'PARK_X': '100'})
        params = {'PARK_BUCKET': '1', 'PARK_X': '100', 'PARK_Y': '40', 'PARK_Z': '50'}
        self.assertIn('G1 X100.0 Y40.0', f.render('MEASURE_TOOL_HEATUP', params))
        f.p['gcode_move']['homing_origin'] = Coord(0, 0, 0.2)
        with self.assertRaisesRegex(ValueError, 'offset'):
            f.render('MEASURE_TOOL_HEATUP', params)
        self.assertNotRegex(f.render('MEASURE_TOOL_HEATUP', {'PARK_BUCKET': '0'}), r'(?m)^G[01] ')

    def test_bench_stop_and_changed_heater_ownership(self):
        f = self.bench()
        f.replay('MEASURE_TOOL_HEATUP')
        f.p['extruder']['target'] = 230
        out = f.render('_TOOL_HEATUP_TIMER', delayed=True)
        self.assertIn('VARIABLE=is_running VALUE=0', out)
        self.assertNotIn('SET_HEATER_TEMPERATURE', out)
        f.p['pause_resume']['is_paused'] = True
        self.assertNotIn('SET_HEATER_TEMPERATURE', f.render('STOP_TOOL_HEATUP'))
        f.replay('STOP_TOOL_HEATUP')
        with self.assertRaisesRegex(ValueError, 'stopped during preparation'):
            f.render('_TOOL_HEATUP_START_TIMER')

    def test_bench_rejects_missing_or_unknown_safety_status(self):
        f = self.bench()
        f.p.pop('pause_resume')
        with self.assertRaisesRegex(ValueError, 'safety state'):
            f.render('MEASURE_TOOL_HEATUP')
        f = self.bench()
        f.p['print_stats']['state'] = 'unknown'
        with self.assertRaisesRegex(ValueError, 'unknown'):
            f.render('MEASURE_TOOL_HEATUP')

    def test_cleaner_isolated_start_hint_and_native_pause(self):
        f = self.cleaner()
        out = f.replay('CLEAN_NOZZLE', {'MODE': 'TOUCH'})
        self.assertIn('G1', out)
        f.p['print_stats']['state'] = 'printing'
        with self.assertRaisesRegex(ValueError, 'idle or starting'):
            f.render('CLEAN_NOZZLE', {'MODE': 'TOUCH'})
        self.assertIn('STARTING=1', f.render('CLEAN_NOZZLE', {'MODE': 'TOUCH', 'STARTING': '1'}))
        f.replay('CLEAN_NOZZLE', {'MODE': 'TOUCH', 'STARTING': '1'})
        f.p['pause_resume']['is_paused'] = True
        with self.assertRaises(ValueError):
            f.render('CLEAN_NOZZLE', {'STARTING': '1'})

    def test_cleaner_project_state_and_contact_guards_win(self):
        f = self.cleaner()
        f.p['gcode_macro _PRINT_STATE'] = {'state': 'printing'}
        with self.assertRaisesRegex(ValueError, 'idle or starting'):
            f.render('CLEAN_NOZZLE', {'STARTING': '1'})
        f.p.pop('gcode_macro _PRINT_STATE')
        with self.assertRaisesRegex(ValueError, 'contact range'):
            f.render('CLEAN_NOZZLE', {'CLEAN_Z': '0.1'})
        self.assertIn('FAN=cooling0', f.replay('CLEAN_NOZZLE', {'MODE': 'TOUCH'}))

    def test_dryer_bed_only_zero_fan_without_sensor_or_project_macros(self):
        f = self.dryer()
        out = f.replay('START_DRYER', {'CHAMBER': '0', 'FAN': '0', 'PARK': '0'})
        self.assertIn('FAN=bed_fan SPEED=0', out)
        self.assertNotIn('ID=bed_fan_off_delay', out)
        self.assertNotRegex(out, r'(?m)^G[01] ')
        self.assertNotIn('UNSELECT_TOOL', out)
        self.assertIn('_DRYER_STATUS', f.render('DRYER_TIMER', delayed=True))
        out = f.render('_DRYER_STATUS')
        self.assertIn('FAN=bed_fan SPEED=0.0', out)

    def test_dryer_missing_feedback_and_fan_fail_before_output(self):
        f = self.dryer()
        with self.assertRaisesRegex(ValueError, 'Chamber control'):
            f.render('START_DRYER', {'PARK': '0'})
        with self.assertRaisesRegex(ValueError, 'humidity sensor'):
            f.render('START_DRYER', {'PARK': '0', 'CHAMBER': '0', 'TARGET_HUMIDITY': '20'})
        f.p.pop('fan_generic bed_fan')
        with self.assertRaisesRegex(ValueError, 'bed_fan'):
            f.render('START_DRYER', {'CHAMBER': '0', 'PARK': '0'})

    def test_dryer_respects_local_bed_limit_and_never_raises_low_target_in_overheat(self):
        f = self.dryer()
        f.p['configfile']['settings']['heater_bed']['max_temp'] = 60
        with self.assertRaisesRegex(ValueError, 'heater_bed max_temp'):
            f.render('START_DRYER', {'CHAMBER': '0', 'PARK': '0'})
        f.p['temperature_sensor chamber'] = {'temperature': 60}
        f.replay('START_DRYER', {'BED': '35', 'CHAMBER': '40', 'PARK': '0'})
        self.assertIn('M140 S35.0', f.render('_DRYER_STATUS'))

    def test_dryer_existing_preset_and_park_retained(self):
        f = self.dryer()
        f.p['temperature_sensor chamber'] = {'temperature': 25}
        out = f.replay('START_DRYER')
        for command in ('G0 Z200.0 F3000', 'UNSELECT_TOOL', 'G0 X175 Y310 F6000',
                        'M140 S70.0', 'FAN=bed_fan SPEED=0.75'):
            self.assertIn(command, out)
        f = self.dryer()
        f.p['temperature_sensor chamber'] = {'temperature': 25}
        f.p['toolhead']['axis_maximum'] = Coord(200, 200, 180)
        with self.assertRaisesRegex(ValueError, 'does not fit'):
            f.render('START_DRYER')

    def test_dryer_timer_handoff_never_changes_print_heaters_or_fan(self):
        for state, paused in (('printing', False), ('standby', True), ('unknown', False)):
            f = self.dryer()
            f.replay('START_DRYER', {'CHAMBER': '0', 'PARK': '0'})
            f.p['print_stats']['state'] = state
            f.p['pause_resume']['is_paused'] = paused
            out = f.render('_DRYER_STATUS')
            self.assertIn('_DRYER_HANDOFF_TO_PRINT', out)
            self.assertNotIn('M140', out)
            self.assertNotIn('SET_FAN_SPEED', out)
            self.assertNotIn('M140', f.replay('STOP_DRYER'))

    def test_prime_isolated_tool_counts_and_sparse_registry(self):
        for numbers in ((0, 1), tuple(range(5)), tuple(range(6)), (0, 7)):
            f = Feature('Printer-Setup/prime-lines.cfg', numbers)
            params = {'INITIAL_TOOL': str(numbers[-1]),
                      **{'T%d_TEMP' % n: '220' for n in numbers}}
            out = f.render('PRIME_LINES', params)
            calls = [line.strip() for line in out.splitlines()
                     if line.strip().startswith('_PRIME_LINES_TOOL ')]
            self.assertEqual([int(line.split('T=')[1].split()[0]) for line in calls], list(numbers))
            self.assertIn('COUNT=%d FINAL=1' % len(numbers), calls[-1])
            f.replay('PRIME_LINES', params)
            params['T%d_TEMP' % numbers[0]] = '300'
            with self.assertRaisesRegex(ValueError, 'heater limit'):
                f.render('PRIME_LINES', params)

    def test_tool_runout_fallback_and_project_routing(self):
        for n in range(5):
            f = Feature('toolchanger/tools/T%d.cfg' % n, (n, n + 7))
            f.p['print_stats']['state'] = 'printing'
            sensor = 'filament_switch_sensor filament_sensor_T%d' % n
            f.p[sensor] = {'filament_detected': False}
            name = '_FILTER_RUNOUT_T%d' % n
            self.assertEqual(f.render(name, delayed=True).strip(), 'PAUSE')
            f.p['toolchanger']['tool_number'] = n + 7
            self.assertNotIn('PAUSE', f.render(name, delayed=True))
            f.p['toolchanger']['tool_number'] = n
            f.p[sensor]['filament_detected'] = True
            self.assertNotIn('PAUSE', f.render(name, delayed=True))
            f.p[sensor]['filament_detected'] = False
            f.p['pause_resume']['is_paused'] = True
            self.assertNotIn('PAUSE', f.render(name, delayed=True))
            f.p['gcode_macro _FILAMENT_RUNOUT_HANDLE'] = {}
            self.assertIn('_FILAMENT_RUNOUT_HANDLE T=%d' % n, f.render(name, delayed=True))

    def test_motion_limits_restore_actual_runtime(self):
        f = Feature('Printer-Setup/test-speed.cfg')
        for name in ('TEST_SPEED', 'TEST_Z_SPEED'):
            out = f.render(name, {'SPEED': '60', 'ACCEL': '500', 'ITERATIONS': '1'})
            self.assertIn('SET_VELOCITY_LIMIT VELOCITY=125.0 ACCEL=900.0 MINIMUM_CRUISE_RATIO=0.3', out)
            self.assertNotIn('Z_VELOCITY=', out)
            self.assertNotIn('Z_ACCEL=', out)
            self.assertNotIn('STOP_CRASH_DETECTION', out)
            with self.assertRaisesRegex(ValueError, 'configured'):
                f.render(name, {'SPEED': '999'})
            with self.assertRaisesRegex(ValueError, 'positive'):
                f.render(name, {'ITERATIONS': '0'})
            f.p['print_stats']['state'] = 'printing'
            with self.assertRaisesRegex(ValueError, 'idle'):
                f.render(name)
            f.p['print_stats']['state'] = 'standby'
        f.p['toolhead']['homed_axes'] = ''
        with self.assertRaisesRegex(ValueError, 'Home XYZ'):
            f.render('TEST_SPEED')
        f.p['toolhead']['homed_axes'] = 'xyz'
        f.p['quad_gantry_level'] = {'applied': False}
        with self.assertRaisesRegex(ValueError, 'QUAD_GANTRY_LEVEL'):
            f.render('TEST_Z_SPEED')

    def test_crash_pause_checks_mainsail_prerequisites(self):
        f = Feature('Printer-Setup/tool-crash.cfg')
        f.p['print_stats']['state'] = 'printing'
        with self.assertRaisesRegex(ValueError, 'Mainsail RESUME'):
            f.render('_TOOL_CRASH_SAFE_PAUSE')
        f.p['gcode_macro RESUME'] = {'last_extruder_temp': {}, 'restore_idle_timeout': 0}
        f.p['configfile']['config']['gcode_macro PAUSE'] = {'rename_existing': 'PAUSE_BASE'}
        out = f.render('_TOOL_CRASH_SAFE_PAUSE')
        self.assertIn('PAUSE_BASE', out)
        self.assertNotRegex(out, r'(?m)^G[01] ')

    def test_cfg_native_hardware_and_dock_paths_unchanged(self):
        backup = ROOT / 'extras/backups/pre-individual-cfg-sharing-20261009-193324/config'
        count = 0
        for original in backup.rglob('*.cfg'):
            current = ROOT / 'config' / original.relative_to(backup)
            before = configparser.RawConfigParser(strict=False, inline_comment_prefixes=('#', ';'))
            after = configparser.RawConfigParser(strict=False, inline_comment_prefixes=('#', ';'))
            before.read(original, encoding='utf-8-sig')
            after.read(current, encoding='utf-8-sig')
            for section in before.sections():
                for key, value in before[section].items():
                    if key == 'gcode' or key.endswith('_gcode'):
                        continue
                    self.assertEqual(after[section][key], value, (str(current), section, key))
            before_saved = original.read_text(encoding='utf-8').partition('#*# <')[2]
            after_saved = current.read_text(encoding='utf-8').partition('#*# <')[2]
            self.assertEqual(after_saved, before_saved)
            count += 1
        self.assertEqual(count, 18)

    def test_ktc_hooks_without_project_led_color_or_state(self):
        f = Feature('toolchanger/toolchanger-config.cfg')
        tool = dict(tool_number=7)
        for hook in ('before_change_gcode', 'after_change_gcode'):
            out = ENV.from_string(f.cfg['toolchanger'][hook]).render(
                printer=f.p, tool=tool, action_respond_info=lambda _: '')
            self.assertNotIn('_SET_TOOL_LED', out)
            self.assertNotIn('_SYNC_INACTIVE_LEDS', out)
            self.assertNotIn('VARIABLE=color', out)
        f.p['gcode_macro T7'] = {}
        out = ENV.from_string(f.cfg['toolchanger']['after_change_gcode']).render(printer=f.p, tool=tool)
        self.assertNotIn('VARIABLE=color', out)

    def test_measured_feature_moves_and_default_heat_commands_match_backup(self):
        backup = ROOT / 'extras/backups/pre-individual-cfg-sharing-20261009-193324/config'
        cases = [
            (self.cleaner(), 'nozzle-clean.cfg', 'CLEAN_NOZZLE', {'MODE': 'TOUCH'}),
            (self.cleaner(), 'nozzle-clean.cfg', '_CLEAN_NOZZLE_WIPE_PATH', {'TEMP': '150', 'CLEAN_Z': '1', 'WIPES': '1'}),
            (self.dryer(), 'filament-dryer.cfg', 'START_DRYER', {}),
            (Feature('Printer-Setup/prime-lines.cfg'), 'prime-lines.cfg', '_PRIME_LINES_TOOL',
             {'T': '0', 'TEMP': '220', 'SLOT': '0', 'COUNT': '2', 'FINAL': '0'}),
        ]
        for f, filename, macro, params in cases:
            f.p['gcode_macro _PRINT_STATE'] = {'state': 'idle'}
            f.p['gcode_macro _TOOL_HEATUP_VARS'] = {'is_running': 0}
            if filename == 'nozzle-clean.cfg':
                f.p['tool custom0']['fan'] = 'T0_part_fan'
                f.p['fan_generic T0_part_fan'] = {'speed': 0}
            if filename == 'filament-dryer.cfg':
                f.p['temperature_sensor chamber'] = {'temperature': 25}
            old = configparser.RawConfigParser(inline_comment_prefixes=('#', ';'))
            old.read(backup / 'Printer-Setup' / filename, encoding='utf-8-sig')
            current = f.cfg
            now = f.render(macro, params)
            f.cfg = old
            before = f.render(macro, params)
            f.cfg = current

            def physical_commands(text):
                return [line.strip() for line in text.splitlines()
                        if line.strip().split(' ', 1)[0] in
                        {'G0', 'G1', 'G90', 'G91', 'G92', 'M83', 'M82', 'M104', 'M109',
                         'M140', 'M190', 'SET_FAN_SPEED', 'SET_HEATER_TEMPERATURE',
                         'TEMPERATURE_WAIT', 'UNSELECT_TOOL'}]

            self.assertEqual(physical_commands(now), physical_commands(before), macro)

if __name__ == '__main__':
    unittest.main(verbosity=2)
