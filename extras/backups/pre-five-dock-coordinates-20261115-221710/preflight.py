from pathlib import Path
from configfile import ConfigFileReader
import ast

live = Path('/home/voron/printer_data/config/printer.cfg')
trial = Path('/tmp/five-dock-coordinates-20261115-221710/printer.cfg')
reader = ConfigFileReader()

def parsed(path):
    body = path.read_text().partition('#*# <')[0]
    return reader.build_fileconfig_with_includes(body, str(path))

before, after = parsed(live), parsed(trial)
assert set(before.sections()) == set(after.sections())
changed = sorted(s for s in before.sections() if dict(before.items(s)) != dict(after.items(s)))
print('Changed Klipper sections:', changed)
assert changed == ['tool T0', 'tool T2', 'tool T3', 'tool T4']
expected = {0: (30.2, 0.0, 333.0), 1: (104.0, 0.0, 330.0), 2: (176.0, 0.0, 331.0), 3: (249.5, 0.0, 331.0), 4: (321.5, 0.0, 332.0)}
x_max = float(after.get('stepper_x', 'position_max'))
y_max = float(after.get('stepper_y', 'position_max'))
z_max = float(after.get('stepper_z', 'position_max'))
path = ast.literal_eval(after.get('toolchanger', 'params_dropoff_path')) + ast.literal_eval(after.get('toolchanger', 'params_pickup_path'))
for n, coords in expected.items():
    actual = tuple(float(after.get(f'tool T{n}', f'params_park_{axis}')) for axis in 'xyz')
    print(f'T{n}: {actual}')
    assert actual == coords
    x, y, z = actual
    assert 0 <= x <= x_max
    for waypoint in path:
        assert 0 <= y + float(waypoint.get('y', 0)) <= y_max
        assert 0 <= z + float(waypoint.get('z', 0)) <= z_max
print('All candidate path coordinates within configured travel limits: PASS')
