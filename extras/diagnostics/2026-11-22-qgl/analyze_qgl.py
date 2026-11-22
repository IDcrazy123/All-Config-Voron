"""Summarize QGL iterations from a Klipper log without modifying the printer."""

import json
import re
import sys


POINTS = re.compile(r"0: ([\d.\-]+) 1: ([\d.\-]+) 2: ([\d.\-]+) 3: ([\d.\-]+)")
ACTUATORS = re.compile(r"z: ([\d.\-]+) z1: ([\d.\-]+) z2: ([\d.\-]+) z3: ([\d.\-]+)")
RETRY = re.compile(r"Retries: (\d+)/\d+ Probed points range: ([\d.]+) tolerance: ([\d.]+)")
STATS = re.compile(r"^Stats ([\d.]+):.*temperature_probe ldc1612_eddy_coil: temp=([\d.]+).*heater_bed: target=([\d.]+) temp=([\d.]+)")


def main(path):
    rounds = []
    latest_stats = None
    pending = {}
    want = None
    with open(path, encoding="utf-8", errors="replace") as log:
        for number, line in enumerate(log, 1):
            stats = STATS.search(line)
            if stats:
                latest_stats = tuple(float(v) for v in stats.groups())
            if want == "points":
                match = POINTS.search(line)
                if match:
                    pending["points"] = [float(v) for v in match.groups()]
                want = None
            elif want == "actuators":
                match = ACTUATORS.search(line)
                if match:
                    pending["actuators"] = [float(v) for v in match.groups()]
                want = None
            elif want == "adjustments":
                value = re.search(r"^stepper_z(?:[123])? = ([\d.\-]+)", line)
                if value:
                    pending.setdefault("adjustments", []).append(float(value[1]))
                if len(pending.get("adjustments", [])) == 4:
                    want = None
            if line.startswith("Gantry-relative probe points:"):
                pending = {"line": number, "stats": latest_stats}
                want = "points"
            elif line.startswith("Actuator Positions:"):
                want = "actuators"
            elif line.startswith("Making the following Z adjustments:"):
                want = "adjustments"
            else:
                match = RETRY.search(line)
                if match and "points" in pending:
                    pending.update(retry=int(match[1]), spread=float(match[2]), tolerance=float(match[3]))
                    rounds.append(pending)
                    pending = {}
    sessions = []
    for row in rounds:
        if not sessions or row["retry"] == 0:
            sessions.append([])
        sessions[-1].append(row)
    print(json.dumps({"rounds": len(rounds), "session_count": len(sessions), "sessions": sessions}, indent=2))


if __name__ == "__main__":
    main(sys.argv[1])
