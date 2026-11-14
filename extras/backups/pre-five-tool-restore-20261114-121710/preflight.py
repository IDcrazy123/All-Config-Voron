from pathlib import Path
import re
from configfile import ConfigFileReader

live = Path('/home/voron/printer_data/config/printer.cfg')
trial = Path('/tmp/five-tool-restore-20261114-121710/printer.cfg')
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
changed = [s for s in before & after if dict(a.items(s)) != dict(b.items(s))]
expected = {s for s in after if re.match(r'(?:mcu EBB[234]|adxl345 T[234]|extruder[234]|tmc2209 extruder[234]|heater_fan T[234]_|fan_generic T[234]_|tool T[234]|neopixel T[234]_|gcode_macro T[234]$|filament_switch_sensor filament_sensor_T[234]|delayed_gcode _FILTER_RUNOUT_T[234])', s)}
print('sections:', len(before), '->', len(after))
print('added:', sorted(added))
print('removed:', sorted(removed), 'changed:', sorted(changed))
assert len(added) == 33 and added == expected and not removed and not changed

x, y = saved(live), saved(trial)
saved_added = set(y) - set(x)
saved_removed = set(x) - set(y)
saved_changed = [s for s in set(x) & set(y) if x[s] != y[s]]
print('SAVE_CONFIG added:', sorted(saved_added))
print('SAVE_CONFIG removed:', sorted(saved_removed), 'changed:', sorted(saved_changed))
assert saved_added == {f'extruder{n}' for n in (2, 3, 4)} | {f'tool T{n}' for n in (2, 3, 4)}
assert not saved_removed and not saved_changed
print('PASS')
