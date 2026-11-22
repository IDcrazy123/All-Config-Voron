"""Collect LDC data during short bed-power steps at a stationary probe point."""

import csv
import json
import socket
import sys
import time
import urllib.parse
import urllib.request


socket_path, output_path = sys.argv[1:3]
url = "http://127.0.0.1:7125/printer/gcode/script"
status_url = (
    "http://127.0.0.1:7125/printer/objects/query?print_stats&heater_bed"
    "&temperature_probe%20ldc1612_eddy_coil"
)


def status():
    with urllib.request.urlopen(status_url, timeout=5) as response:
        s = json.load(response)["result"]["status"]
    return (
        s["print_stats"]["state"],
        s["heater_bed"]["temperature"],
        s["heater_bed"]["target"],
        s["temperature_probe ldc1612_eddy_coil"]["temperature"],
    )


def bed(target):
    data = urllib.parse.urlencode({"script": f"M140 S{target}"}).encode()
    with urllib.request.urlopen(url, data=data, timeout=10) as response:
        json.load(response)


state, _, target, _ = status()
if state != "standby" or target != 100:
    raise SystemExit(f"Expected standby and bed target 100, got {state}/{target}")

buffer = b""
start = time.monotonic()
transitions = ((6, 0), (12, 100), (18, 0), (24, 100))
next_transition = 0
phase = 0
events = []
with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as conn, open(
    output_path, "w", newline="", encoding="utf-8"
) as output:
    writer = csv.writer(output)
    writer.writerow(("phase", "host_elapsed_s", "print_time", "frequency_hz", "model_z_mm", "batch_errors"))
    conn.settimeout(0.2)
    conn.connect(socket_path)
    conn.sendall(
        json.dumps(
            {
                "id": 1,
                "method": "ldc1612/dump_ldc1612",
                "params": {
                    "sensor": "ldc1612_eddy_coil",
                    "response_template": {"method": "ldc_samples"},
                },
            }
        ).encode()
        + b"\x03"
    )
    try:
        while time.monotonic() - start < 30:
            elapsed = time.monotonic() - start
            if next_transition < len(transitions) and elapsed >= transitions[next_transition][0]:
                requested_target = transitions[next_transition][1]
                bed(requested_target)
                phase += 1
                events.append((phase, round(elapsed, 3), requested_target, status()))
                next_transition += 1
            try:
                buffer += conn.recv(65536)
            except socket.timeout:
                continue
            while b"\x03" in buffer:
                raw, buffer = buffer.split(b"\x03", 1)
                if not raw:
                    continue
                message = json.loads(raw)
                if message.get("method") != "ldc_samples":
                    continue
                payload = message["params"]
                for sample in payload.get("data", []):
                    writer.writerow((phase, round(time.monotonic() - start, 4), *sample, payload.get("errors", 0)))
    finally:
        bed(100)

print(json.dumps({"events": events, "final_status": status(), "output_path": output_path}))
