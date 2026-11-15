from pathlib import Path
import re
from configfile import ConfigFileReader

live = Path('/home/voron/printer_data/config/printer.cfg')
trial = Path('/tmp/t3-maintenance-20261115-163710/printer.cfg')
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
    'mcu EBB3', 'adxl345 T3', 'extruder3', 'tmc2209 extruder3',
    'heater_fan T3_hotend_fan', 'fan_generic T3_part_fan', 'tool T3',
    'neopixel T3_LED', 'gcode_macro T3',
    'filament_switch_sensor filament_sensor_T3',
    'delayed_gcode _FILTER_RUNOUT_T3',
}
changed = [s for s in before & after if dict(a.items(s)) != dict(b.items(s))]
print('sections:', len(before), '->', len(after))
print('removed:', sorted(removed))
print('added:', sorted(added), 'changed:', sorted(changed))
assert removed == expected and not added and not changed
assert {'tool T0', 'tool T1', 'tool T2'} <= after
assert 'tool T4' not in after

x, y = saved(live), saved(trial)
saved_removed = set(x) - set(y)
saved_added = set(y) - set(x)
saved_changed = [s for s in set(x) & set(y) if x[s] != y[s]]
print('SAVE_CONFIG removed:', sorted(saved_removed))
print('SAVE_CONFIG added:', sorted(saved_added), 'changed:', sorted(saved_changed))
assert saved_removed == {'extruder3', 'tool T3'}
assert not saved_added and not saved_changed
print('PASS')
