"""Read a short stationary LDC1612 sample stream from Klipper's local socket."""

import json
import math
import socket
import statistics
import sys
import time


def main(socket_path, seconds):
    samples = []
    batches = 0
    errors = []
    buffer = b""
    end = time.monotonic() + seconds
    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as conn:
        conn.settimeout(1.0)
        conn.connect(socket_path)
        request = {
            "id": 1,
            "method": "ldc1612/dump_ldc1612",
            "params": {
                "sensor": "ldc1612_eddy_coil",
                "response_template": {"method": "ldc_samples"},
            },
        }
        conn.sendall(json.dumps(request).encode() + b"\x03")
        while time.monotonic() < end:
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
                batches += 1
                errors.append(payload.get("errors", 0))
                samples.extend(payload.get("data", []))
    valid = [(float(t), float(f), float(z)) for t, f, z in samples
             if math.isfinite(z) and 0.0 <= z <= 4.1]
    if len(valid) < 2:
        print(json.dumps({"sample_count": len(samples), "valid_count": len(valid),
                          "batch_count": batches, "errors": errors[-2:]}, indent=2))
        return
    ts = [v[0] for v in valid]
    zs = [v[2] for v in valid]
    fs = [v[1] for v in valid]
    t_avg = statistics.mean(ts)
    z_avg = statistics.mean(zs)
    slope = sum((t - t_avg) * (z - z_avg) for t, z in zip(ts, zs)) / sum(
        (t - t_avg) ** 2 for t in ts)
    detrended = [z - z_avg - slope * (t - t_avg) for t, z in zip(ts, zs)]
    sorted_z = sorted(zs)
    result = {
        "sample_count": len(samples),
        "valid_count": len(valid),
        "batch_count": batches,
        "errors_first_last": errors[:1] + errors[-1:],
        "elapsed_sample_seconds": ts[-1] - ts[0],
        "mean_frequency_hz": statistics.mean(fs),
        "mean_z_mm": z_avg,
        "min_z_mm": min(zs),
        "max_z_mm": max(zs),
        "p05_to_p95_z_mm": [sorted_z[int(.05 * (len(zs) - 1))],
                              sorted_z[int(.95 * (len(zs) - 1))]],
        "z_stddev_mm": statistics.pstdev(zs),
        "z_detrended_stddev_mm": statistics.pstdev(detrended),
        "z_drift_mm_per_second": slope,
    }
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main(sys.argv[1], float(sys.argv[2]))
