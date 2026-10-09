"""Read Klipper logs and summarize reported temperatures, without printer I/O.

Use ordered files: oldest rotated log first, current log last. A wall-clock
anchor comes only from 'Start printer at' (epoch minus monotonic). Samples
before the first anchor or after an unexplained uptime reset stay undated.
Zero startup temperatures are ignored. This does not measure physical heat.
"""
from datetime import datetime, timezone, timedelta
from collections import defaultdict
import glob
import json
from pathlib import Path
import re
import statistics
import sys

ZONE = timezone(timedelta(hours=7))
START = re.compile(r'^Start printer at .*\(([\d.]+) ([\d.]+)\)')
STATS = re.compile(r'^Stats ([\d.]+):')
HEATER = re.compile(r'(extruder\d*|heater_bed): target=(\S+) temp=(\S+) pwm=(\S+)')
TOOLS = ['extruder', 'extruder1', 'extruder2', 'extruder3', 'extruder4']


def stamp(epoch):
    return datetime.fromtimestamp(epoch, ZONE).strftime('%Y-%m-%d %H:%M:%S')


def brief(row):
    return dict(file=row['file'], line=row['line'], time=stamp(row['epoch'])
                if row['epoch'] is not None else None,
                mono=row['mono'], temperatures=[v[1] for v in row['tools']],
                targets=[v[0] for v in row['tools']],
                pwm=[v[2] for v in row['tools']],
                t1_off_observed_seconds=round(row['off_age'], 1))


paths = sys.argv[1:]
if not paths:
    rotated = sorted(glob.glob('/home/voron/printer_data/logs/klippy.log.*'))
    paths = rotated + ['/home/voron/printer_data/logs/klippy.log']
offset = None
previous_mono = None
off_start = None
rows = []
sessions = []
inventory = []
session = None
for filename in paths:
    path = Path(filename)
    valid_count = 0
    undated_count = 0
    with path.open(errors='replace') as source:
        for number, line in enumerate(source, 1):
            start = START.match(line)
            if start:
                epoch, mono = map(float, start.groups())
                offset = epoch - mono
                previous_mono = mono
                off_start = None
                session = dict(file=path.name, line=number, start=stamp(epoch),
                               epoch=epoch, first=None, samples_first_10min=[],
                               first_high=None, first_high_after_30min_off=None)
                sessions.append(session)
            stats = STATS.match(line)
            if not stats:
                continue
            mono = float(stats[1])
            heaters = {name: tuple(map(float, (target, temp, pwm)))
                       for name, target, temp, pwm in HEATER.findall(
                           line[line.find('heater_bed:'):] if 'heater_bed:' in line else line)}
            if any(name not in heaters or heaters[name][1] <= 0 for name in TOOLS):
                continue
            if previous_mono is not None and mono < previous_mono - 2:
                offset = None
                off_start = None
                session = None
            previous_mono = mono
            epoch = mono + offset if offset is not None else None
            tool_values = [heaters[name] for name in TOOLS]
            t1 = tool_values[1]
            if t1[0] != 0 or t1[2] != 0:
                off_start = None
            elif off_start is None:
                off_start = mono
            off_age = mono - off_start if off_start is not None else 0
            row = dict(file=path.name, line=number, mono=mono, epoch=epoch,
                       tools=tool_values, off_age=off_age)
            rows.append(row)
            valid_count += 1
            if epoch is None:
                undated_count += 1
            others = [v[1] for i, v in enumerate(tool_values) if i != 1]
            high = (t1[0] == 0 and t1[2] == 0 and t1[1] >= 40
                    and max(others) <= 40 and t1[1] - statistics.median(others) >= 10)
            if session is not None:
                if session['first'] is None:
                    session['first'] = brief(row)
                age = epoch - session['epoch']
                if 0 <= age <= 600:
                    points = session['samples_first_10min']
                    if not points or epoch - points[-1]['epoch'] >= 60:
                        points.append(dict(epoch=epoch, **brief(row)))
                if high and session['first_high'] is None:
                    session['first_high'] = brief(row)
                if high and off_age >= 1800 and session['first_high_after_30min_off'] is None:
                    session['first_high_after_30min_off'] = brief(row)
    inventory.append(dict(file=str(path), bytes=path.stat().st_size,
                          valid_stats=valid_count, undated_stats=undated_count))

daily = []
by_day = defaultdict(list)
for row in rows:
    if row['epoch'] is not None:
        by_day[stamp(row['epoch'])[:10]].append(row)
for day, dated in sorted(by_day.items()):
    idle = [row for row in dated if all(v[0] == 0 and v[2] == 0 for v in row['tools'])
            and max(v[1] for i, v in enumerate(row['tools']) if i != 1) <= 40]
    prolonged = [row for row in idle if row['off_age'] >= 1800]
    def describe(group):
        if not group:
            return None
        temperatures = [row['tools'][1][1] for row in group]
        high = [row for row in group if row['tools'][1][1] >= 40 and
                row['tools'][1][1] - statistics.median(
                    v[1] for i, v in enumerate(row['tools']) if i != 1) >= 10]
        return dict(samples=len(group), t1_min=min(temperatures), t1_max=max(temperatures),
                    t1_median=statistics.median(temperatures), high_samples=len(high),
                    first=brief(group[0]), last=brief(group[-1]),
                    first_high=brief(high[0]) if high else None,
                    coolest=brief(min(group, key=lambda row: row['tools'][1][1])))
    daily.append(dict(day=day, samples=len(dated), all_heaters_off_others_below_40=describe(idle),
                      same_after_30min_t1_off=describe(prolonged)))

print(json.dumps(dict(inventory=inventory, daily=daily, sessions=sessions,
                     latest=brief(rows[-1]) if rows else None,
                     method='Observed target/PWM zero does not prove physical heater power is zero. '
                     'Off age is elapsed time since the first observed off sample after the last '
                     'observed heating or restart; unlogged gaps cannot exclude intervening heating.'), indent=2))
