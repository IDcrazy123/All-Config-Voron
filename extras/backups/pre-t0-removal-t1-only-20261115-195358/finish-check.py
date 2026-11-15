from pathlib import Path
from configfile import ConfigFileReader
from jinja2 import Environment
p = Path('/tmp/t0-removal-t1-only-20261115-195358/printer.cfg')
c = ConfigFileReader().build_fileconfig_with_includes(p.read_text().partition('#*# <')[0], str(p))
t = Environment('{%', '%}', '{', '}').from_string(c.get('gcode_macro _PRINT_FINISH_DOCK_AND_PARK', 'gcode'))
s = t.render(printer={'gcode_macro _TOOL_RECOVERY': {'required': 0}, 'toolhead': {'homed_axes': 'xyz'}, 'toolchanger': {'status': 'ready', 'tool_number': 1, 'detected_tool_number': 1, 'tool_numbers': [1]}}, params={'MIN_Z': 20}, action_raise_error=lambda message: (_ for _ in ()).throw(RuntimeError(message)))
assert 'UNSELECT_TOOL' not in s and '_PRINT_FINISH_PARK' not in s and 'T1-only finish' in s
print('T1-only finish leaves mounted tool in place: PASS')
