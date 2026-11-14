from pathlib import Path
import re
from configfile import ConfigFileReader

live = Path('/home/voron/printer_data/config/printer.cfg')
trial = Path('/tmp/t4-maintenance-20261114-200533/printer.cfg')
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

a, b = parsed(live), parsed(trial)
before, after = set(a.sections()), set(b.sections())
removed, added = before - after, after - before
expected = {
    'mcu EBB4', 'adxl345 T4', 'extruder4', 'tmc2209 extruder4',
    'heater_fan T4_hotend_fan', 'fan_generic T4_part_fan', 'tool T4',
    'neopixel T4_LED', 'gcode_macro T4',
    'filament_switch_sensor filament_sensor_T4',
    'delayed_gcode _FILTER_RUNOUT_T4',
}
changed = [s for s in before & after if dict(a.items(s)) != dict(b.items(s))]
print('sections:', len(before), '->', len(after))
print('removed:', sorted(removed))
print('added:', sorted(added), 'changed:', sorted(changed))
assert removed == expected and not added and not changed
assert {'tool T0', 'tool T1', 'tool T2', 'tool T3'} <= after

x, y = saved(live), saved(trial)
saved_removed = set(x) - set(y)
saved_added = set(y) - set(x)
saved_changed = [s for s in set(x) & set(y) if x[s] != y[s]]
print('SAVE_CONFIG removed:', sorted(saved_removed))
print('SAVE_CONFIG added:', sorted(saved_added), 'changed:', sorted(saved_changed))
assert saved_removed == {'extruder4', 'tool T4'}
assert not saved_added and not saved_changed
print('PASS')
