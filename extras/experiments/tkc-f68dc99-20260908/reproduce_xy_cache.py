"""Offline reproduction only: no printer connections or hardware motion."""
import json
from unittest.mock import MagicMock
from klippy.extras.tool_calibrator import ToolCalibrator

def check(cached):
    c=object.__new__(ToolCalibrator)
    c.reference_tool=0
    c.z_backend_type='cartographer'
    c.allow_shuttle_z=False
    c.cached_offsets=cached
    c.navigator=MagicMock(carto_speedup=True)
    c.z_backend=MagicMock(measurement_reference='nozzle')
    c.printer=MagicMock()
    c.printer.lookup_object.return_value.parse_tool_offsets.return_value={2:{'x':0.82,'y':0.24}}
    th=MagicMock()
    th.get_position.return_value=[174,168,5,0]
    c.z_backend.probe_secondary_tool.return_value={'suggested_z_offset':-0.316}
    reference={'probe_xy':(174,168),'contact_z':0,'source':'cartographer_touch_reference'}
    # Return the commanded point so the independent same-point gate passes.
    def probe(*args):
        p=th.manual_move.call_args.args[0]
        return {'suggested_z_offset':-0.316,'probe_xy':p[:2]}
    c.z_backend.probe_secondary_tool.side_effect=probe
    gcmd=MagicMock()
    gcmd.get_int.return_value=0
    c._execute_z_calibration(2,th,MagicMock(),gcmd,reference,{})
    return th.manual_move.call_args.args[0][:2]

first=check({})
repeat=check({2:{'z':-0.316}})
print(json.dumps({'first_run_xy':first,'after_z_only_cache_xy':repeat,'lost_compensation_mm':[first[i]-repeat[i] for i in range(2)]},indent=2))
assert first==[174.82,168.24]
assert repeat==[174.0,168.0]
