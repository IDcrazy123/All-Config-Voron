"""Stream stationary LDC1612 samples from Klipper's local Unix socket.

Run on the printer host: python3 capture_ldc.py [seconds]
Writes CSV to stdout. This sends no G-code and does not move the printer.
Closing the connection stops the sensor stream.
"""

import csv
import json
import socket
import sys
import time


duration = float(sys.argv[1]) if len(sys.argv) > 1 else 60.0
sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
sock.connect('/home/voron/printer_data/comms/klippy.sock')
request = {'id': 1, 'method': 'ldc1612/dump_ldc1612',
           'params': {'sensor': 'ldc1612_eddy_coil'}}
sock.sendall((json.dumps(request) + '\x03').encode())
sock.settimeout(2.0)
writer = csv.writer(sys.stdout, lineterminator='\n')
writer.writerow(['time', 'frequency_hz', 'z_mm', 'errors', 'overflows'])
buffer = b''
deadline = time.monotonic() + duration
try:
    while time.monotonic() < deadline:
        try:
            buffer += sock.recv(65536)
        except socket.timeout:
            continue
        while b'\x03' in buffer:
            msg, buffer = buffer.split(b'\x03', 1)
            packet = json.loads(msg)
            if 'error' in packet:
                raise RuntimeError(packet['error'])
            params = packet.get('params', {})
            for sample in params.get('data', []):
                writer.writerow([*sample, params.get('errors', 0),
                                 params.get('overflows', 0)])
finally:
    sock.close()
