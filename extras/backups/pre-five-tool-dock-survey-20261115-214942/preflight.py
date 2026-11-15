from pathlib import Path
import re
from configfile import ConfigFileReader
from jinja2 import Environment

live = Path('/home/voron/printer_data/config/printer.cfg')
trial = Path('/tmp/five-tool-dock-survey-20261115-214942/printer.cfg')
reader = ConfigFileReader()

def parsed(path):
    body = path.read_text().partition('#*# <')[0]
    return reader.build_fileconfig_with_includes(body, str(path))

def saved(path):
    result = {}
    section = None
    for line in path.read_text().splitlines():
        match = re.match(r'#\*# \[([^]]+)\]', line)
        if match:
            section = match.group(1)
            result[section] = []
        elif section is not None and line.startswith('#*# '):
            result[section].append(line)
    return result

before, after = parsed(live), parsed(trial)
added = set(after.sections()) - set(before.sections())
removed = set(before.sections()) - set(after.sections())
changed = sorted(s for s in set(before.sections()) & set(after.sections()) if dict(before.items(s)) != dict(after.items(s)))
print('sections:', len(before.sections()), '->', len(after.sections()))
print('added:', sorted(added))
print('removed:', sorted(removed))
print('changed:', changed)
assert removed == {'gcode_macro _PRINT_START_REQUIRE_T1_MOUNTED', 'gcode_macro _PRINT_START_SELECT_PROBE_TOOL'}
assert len(added) == 45 and len(after.sections()) == 201
assert changed == ['extruder', 'gcode_macro PRINT_START', 'gcode_macro _PRINT_FINISH_DOCK_AND_PARK', 'heater_fan T1_hotend_fan', 'tmc2209 extruder', 'tool T1']
for n in range(5):
    assert f'tool T{n}' in after
    assert f'mcu EBB{n}' in after
assert 'gcode_macro _PRINT_START_SELECT_T0' in after
assert after.get('tool T1', 'extruder') == 'extruder1'
assert after.get('heater_fan T1_hotend_fan', 'heater') == 'extruder1'
assert after.get('filament_switch_sensor filament_sensor_T3', 'switch_pin') == '^EBB3:PB8'
for section in after.sections():
    if (section.startswith('gcode_macro ') or section.startswith('delayed_gcode ')) and after.has_option(section, 'gcode'):
        Environment('{%', '%}', '{', '}').parse(after.get(section, 'gcode'))
print('Parsed all G-code templates')

a, b = saved(live), saved(trial)
print('SAVE_CONFIG added:', sorted(set(b) - set(a)))
print('SAVE_CONFIG removed:', sorted(set(a) - set(b)))
print('SAVE_CONFIG changed:', sorted(s for s in set(a) & set(b) if a[s] != b[s]))
assert set(b) - set(a) == {'extruder1', 'extruder2', 'extruder3', 'extruder4', 'tool T2', 'tool T3', 'tool T4'}
assert not set(a) - set(b)
assert b['extruder1'][2:5] == a['extruder'][2:5]
assert b['tool T1'][-1] == '#*# gcode_z_offset = 0.1665'
print('PASS')
