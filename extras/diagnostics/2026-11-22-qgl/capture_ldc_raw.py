"""Capture stationary Klipper LDC samples for offline time-series analysis."""

import csv
import json
import socket
import sys
import time


socket_path, output_path, duration = sys.argv[1], sys.argv[2], float(sys.argv[3])
deadline = time.monotonic() + duration
buffer = b""
count = 0
with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as conn, open(
    output_path, "w", newline="", encoding="utf-8"
) as output:
    writer = csv.writer(output)
    writer.writerow(("print_time", "frequency_hz", "model_z_mm", "batch_errors"))
    conn.settimeout(1.0)
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
    while time.monotonic() < deadline:
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
                writer.writerow((*sample, payload.get("errors", 0)))
                count += 1
print(f"wrote {count} samples to {output_path}")
