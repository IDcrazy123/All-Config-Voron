"""30-second stationary LDC A/B/A test with all tool LEDs off in phase B.

Run from a workstation with ssh access to voron@192.168.1.43. Restores every
tool LED color in finally. Sends no motion or heater command. Captures are
written to a specified local directory for later analysis.
"""

import gzip
import json
import subprocess
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path


HOST = 'http://192.168.1.43:7125'
LED_NAMES = [f'neopixel T{i}_LED' for i in range(5)]
OBJECTS = ['print_stats', 'toolhead', 'stepper_enable', 'heater_bed',
           'controller_fan tmc_fan'] + LED_NAMES
CAPTURE = Path(__file__).with_name('capture_ldc.py').read_bytes()
OUT = Path(sys.argv[1])
OUT.mkdir(parents=True, exist_ok=True)


def query():
    url = HOST + '/printer/objects/query?' + '&'.join(
        urllib.parse.quote(name) for name in OBJECTS)
    with urllib.request.urlopen(url, timeout=5) as response:
        return json.load(response)['result']['status']


def guard(status):
    if status['print_stats']['state'] != 'standby':
        raise RuntimeError('Print is no longer standby')
    if status['heater_bed']['target'] != 0:
        raise RuntimeError('Bed heater target changed')
    if any(status['stepper_enable']['steppers'].values()):
        raise RuntimeError('A stepper became enabled')


def gcode(script):
    payload = json.dumps({'script': script}).encode()
    request = urllib.request.Request(
        HOST + '/printer/gcode/script', payload,
        headers={'Content-Type': 'application/json'}, method='POST')
    with urllib.request.urlopen(request, timeout=10) as response:
        result = json.load(response)
    if 'error' in result:
        raise RuntimeError(result['error'])


def turn_off():
    for i in range(5):
        gcode(f'SET_LED LED=T{i}_LED RED=0 GREEN=0 BLUE=0 WHITE=0 SYNC=0')


def restore(colors):
    for i, pixels in enumerate(colors):
        for index, color in enumerate(pixels, start=1):
            r, g, b, w = color
            gcode(f'SET_LED LED=T{i}_LED INDEX={index} RED={r} GREEN={g} '
                  f'BLUE={b} WHITE={w} TRANSMIT={int(index == len(pixels))} SYNC=0')


def capture(label):
    before = query()
    guard(before)
    command = ['ssh', '-o', 'BatchMode=yes', '-o', 'ConnectTimeout=5',
               'voron@192.168.1.43', 'python3 - 30']
    result = subprocess.run(command, input=CAPTURE, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE, timeout=45, check=True)
    if not result.stdout.startswith(b'time,frequency_hz,z_mm,errors,overflows'):
        raise RuntimeError(f'Bad capture: {result.stderr.decode(errors="replace")}')
    (OUT / f'{label}.csv.gz').write_bytes(gzip.compress(result.stdout, 9, mtime=0))
    after = query()
    guard(after)
    record = {'before': before, 'after': after, 'bytes': len(result.stdout)}
    (OUT / f'{label}.status.json').write_text(json.dumps(record, indent=2))
    print(f'{label}: {len(result.stdout)} bytes', flush=True)


def main():
    initial = query()
    guard(initial)
    colors = [initial[name]['color_data'] for name in LED_NAMES]
    (OUT / 'led-colors-before.json').write_text(json.dumps(colors, indent=2))
    try:
        capture('leds-on-before-30s')
        turn_off()
        status = query()
        if any(any(any(pixel) for pixel in status[name]['color_data'])
               for name in LED_NAMES):
            raise RuntimeError('LED off state did not take effect')
        capture('leds-off-30s')
    finally:
        restore(colors)
    status = query()
    if [status[name]['color_data'] for name in LED_NAMES] != colors:
        raise RuntimeError('LED colors did not restore')
    capture('leds-on-after-30s')


if __name__ == '__main__':
    main()
