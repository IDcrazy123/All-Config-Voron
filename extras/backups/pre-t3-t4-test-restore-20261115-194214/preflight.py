from pathlib import Path
import re
from configfile import ConfigFileReader

live = Path('/home/voron/printer_data/config/printer.cfg')
trial = Path('/tmp/t3-t4-test-restore-20261115-194214/printer.cfg')
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
added, removed = after - before, before - after
expected = set()
for n in (3, 4):
    expected.update({
        f'mcu EBB{n}', f'adxl345 T{n}', f'extruder{n}',
        f'tmc2209 extruder{n}', f'heater_fan T{n}_hotend_fan',
        f'fan_generic T{n}_part_fan', f'tool T{n}',
        f'neopixel T{n}_LED', f'gcode_macro T{n}',
        f'filament_switch_sensor filament_sensor_T{n}',
        f'delayed_gcode _FILTER_RUNOUT_T{n}',
    })
changed = [s for s in before & after if dict(a.items(s)) != dict(b.items(s))]
print('sections:', len(before), '->', len(after))
print('added:', sorted(added))
print('removed:', sorted(removed), 'changed:', sorted(changed))
assert added == expected and not removed and not changed

x, y = saved(live), saved(trial)
saved_added = set(y) - set(x)
saved_removed = set(x) - set(y)
saved_changed = [s for s in set(x) & set(y) if x[s] != y[s]]
print('SAVE_CONFIG added:', sorted(saved_added))
print('SAVE_CONFIG removed:', sorted(saved_removed), 'changed:', sorted(saved_changed))
assert saved_added == {'extruder3', 'tool T3', 'extruder4', 'tool T4'}
assert not saved_removed and not saved_changed
print('PASS')
