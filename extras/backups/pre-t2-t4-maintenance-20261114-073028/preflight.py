from pathlib import Path
from configfile import ConfigFileReader

live = Path('/home/voron/printer_data/config/printer.cfg')
trial = Path('/tmp/t2-t4-preflight-20261114-073028/printer.cfg')
reader = ConfigFileReader()

def parsed(path):
    body = path.read_text().partition('#*# <')[0]
    return reader.build_fileconfig_with_includes(body, str(path))

a, b = parsed(live), parsed(trial)
before, after = set(a.sections()), set(b.sections())
removed = before - after
added = after - before
expected = {s for s in before if s.startswith((
    'mcu EBB2', 'mcu EBB3', 'mcu EBB4', 'adxl345 T2', 'adxl345 T3',
    'adxl345 T4', 'extruder2', 'extruder3', 'extruder4',
    'tmc2209 extruder2', 'tmc2209 extruder3', 'tmc2209 extruder4',
    'heater_fan T2_', 'heater_fan T3_', 'heater_fan T4_',
    'fan_generic T2_', 'fan_generic T3_', 'fan_generic T4_',
    'tool T2', 'tool T3', 'tool T4', 'neopixel T2_', 'neopixel T3_',
    'neopixel T4_', 'gcode_macro T2', 'gcode_macro T3', 'gcode_macro T4',
    'filament_switch_sensor filament_sensor_T2',
    'filament_switch_sensor filament_sensor_T3',
    'filament_switch_sensor filament_sensor_T4',
    'delayed_gcode _FILTER_RUNOUT_T2',
    'delayed_gcode _FILTER_RUNOUT_T3',
    'delayed_gcode _FILTER_RUNOUT_T4',
))}
changed = [s for s in before & after if dict(a.items(s)) != dict(b.items(s))]
print('sections:', len(before), '->', len(after))
print('removed:', sorted(removed))
print('added:', sorted(added))
print('changed:', sorted(changed))
assert removed == expected, 'unexpected removed sections'
assert not added and not changed, 'unexpected added/changed sections'
assert {'tool T0', 'tool T1', 'extruder', 'extruder1'} <= after
assert not any(s in after for s in ('tool T2', 'tool T3', 'tool T4'))
print('PASS')
