"""Summarize read-only Klipper logs for bed-temperature jumps and QGL retries."""

import csv
import json
import re
import sys
from pathlib import Path


RETRY = re.compile(r"^Retries: (\d+)/(\d+) Probed points range: ([\d.]+) tolerance: ([\d.]+)")
PROBE = re.compile(r"^\[cartographer\] probe at ([\d.]+),([\d.]+) is z=([-\d.]+)")
STATS = re.compile(r"^Stats ([\d.]+):")
BED = re.compile(r"heater_bed: target=([-\d.]+) temp=([-\d.]+) pwm=([-\d.]+)")
COIL = re.compile(r"cartographer_coil: temp=([-\d.]+)")


def analyze(path):
    runs, jumps, errors = [], [], []
    probes = []
    run = None
    prev = None
    state = None
    for line_no, line in enumerate(path.open(encoding="utf-8", errors="replace"), 1):
        sm = STATS.match(line)
        if sm:
            bm = BED.search(line)
            if bm:
                state = {
                    "line": line_no, "t": float(sm[1]), "target": float(bm[1]),
                    "temp": float(bm[2]), "pwm": float(bm[3]),
                    "coil": float(COIL.search(line)[1]) if COIL.search(line) else None,
                }
                if (prev and 0 < state["t"] - prev["t"] < 3
                    and state["target"] > 0 and prev["target"] > 0
                    and abs(state["temp"] - prev["temp"]) >= 2):
                    jumps.append({"before": prev, "after": state, "delta": round(state["temp"] - prev["temp"], 2)})
                prev = state
            continue
        pm = PROBE.match(line)
        if pm:
            probes.append({"x": float(pm[1]), "y": float(pm[2]), "z": float(pm[3]), "line": line_no})
            probes = probes[-4:]
            continue
        rm = RETRY.match(line)
        if rm:
            n, limit, value, tol = int(rm[1]), int(rm[2]), float(rm[3]), float(rm[4])
            if n == 0:
                if run:
                    runs.append(run)
                run = {"line": line_no, "start_state": state, "tolerance": tol, "limit": limit, "rounds": [], "outcome": "incomplete"}
            if run:
                run["rounds"].append({"retry": n, "range": value, "probes": probes.copy(), "line": line_no, "state": state})
                if value <= tol:
                    run["outcome"] = "pass"
            continue
        if line.startswith("Retries aborting:") or line.startswith("Too many retries"):
            if run:
                run["outcome"] = "fail"
                run["error"] = line.strip()
                runs.append(run)
                run = None
            errors.append({"line": line_no, "message": line.strip(), "state": state})
    if run:
        runs.append(run)
    return {"file": path.name, "runs": runs, "jumps": jumps, "errors": errors}


def main():
    dest = Path(__file__).parent
    data = [analyze(Path(p)) for p in sys.argv[1:]]
    (dest / "summary.json").write_text(json.dumps(data, indent=2), encoding="utf-8")
    with (dest / "qgl-runs.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["file", "line", "t", "bed_c", "target_c", "coil_c", "tolerance_mm", "outcome", "first_range_mm", "last_range_mm", "last_retry", "rounds", "error"])
        for group in data:
            for run in group["runs"]:
                rounds = run["rounds"]
                if not rounds:
                    continue
                state = run["start_state"] or {}
                w.writerow([group["file"], run["line"], state.get("t"), state.get("temp"), state.get("target"), state.get("coil"), run["tolerance"], run["outcome"], rounds[0]["range"], rounds[-1]["range"], rounds[-1]["retry"], len(rounds), run.get("error", "")])
    for group in data:
        runs = group["runs"]
        fine = [r for r in runs if r["tolerance"] < 0.01]
        print(group["file"], "runs", len(runs), "fine", len(fine), "pass", sum(r["outcome"] == "pass" for r in fine), "fail", sum(r["outcome"] == "fail" for r in fine), "jumps", len(group["jumps"]))
        for jump in group["jumps"][-12:]:
            a, b = jump["before"], jump["after"]
            print(" JUMP", a["line"], a["t"], a["temp"], "->", b["temp"], "target", b["target"], "pwm", b["pwm"])
        for run in fine[-12:]:
            first, last = run["rounds"][0], run["rounds"][-1]
            print(" QGL", run["line"], (run["start_state"] or {}).get("t"), (run["start_state"] or {}).get("temp"), run["outcome"], first["range"], "->", last["range"], "retry", last["retry"])


if __name__ == "__main__":
    main()
