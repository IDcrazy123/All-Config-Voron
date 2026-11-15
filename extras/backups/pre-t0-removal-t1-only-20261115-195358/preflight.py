from pathlib import Path
import re
from configfile import ConfigFileReader
from jinja2 import Environment

root = Path('/tmp/t0-removal-t1-only-20261115-195358')
live = Path('/home/voron/printer_data/config/printer.cfg')
reader = ConfigFileReader()

def parsed(path):
    return reader.build_fileconfig_with_includes(path.read_text().partition('#*# <')[0], str(path))

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

before, after = parsed(live), parsed(root / 'printer.cfg')
removed = sorted(set(before.sections()) - set(after.sections()))
added = sorted(set(after.sections()) - set(before.sections()))
print('Removed sections:', removed)
print('Added sections:', added)
assert added == ['gcode_macro _PRINT_START_REQUIRE_T1_MOUNTED', 'gcode_macro _PRINT_START_SELECT_PROBE_TOOL']
for name in ('tool T0', 'extruder1', 'tool T2', 'tool T3', 'tool T4'):
    assert name not in after, name
for name in ('tool T1', 'extruder', 'toolchanger', 'cartographer'):
    assert name in after, name
assert after.get('tool T1', 'extruder') == 'extruder'
assert after.get('heater_fan T1_hotend_fan', 'heater') == 'extruder'
assert after.get('tmc2209 extruder', 'uart_pin')
for section in after.sections():
    if section.startswith('gcode_macro ') or section.startswith('delayed_gcode '):
        if after.has_option(section, 'gcode'):
            Environment('{%', '%}', '{', '}').parse(after.get(section, 'gcode'))
print('Parsed', len(after.sections()), 'sections and all G-code templates')
a, b = saved(live), saved(root / 'printer.cfg')
print('SAVE_CONFIG removed:', sorted(set(a) - set(b)))
print('SAVE_CONFIG changed:', sorted(x for x in set(a) & set(b) if a[x] != b[x]))
assert set(a) - set(b) == {'extruder1', 'extruder2', 'extruder3', 'extruder4', 'tool T2', 'tool T3', 'tool T4'}
assert b['extruder'][2:5] == a['extruder1'][2:5]
assert b['tool T1'][-1] == '#*# gcode_z_offset = 0.0'
print('PASS')
