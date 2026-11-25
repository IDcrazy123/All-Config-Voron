"""Compare 30-second raw LDC captures with fixed 14.2-second harmonic.

Usage: python analyze_ebb_isolation.py CAPTURE.csv.gz [...]
The diagnostic Klipper profile has no Eddy Z calibration, so fit raw frequency.
"""

import gzip
import sys

import numpy as np


def analyze(path):
    with gzip.open(path, 'rt', encoding='utf-8-sig') as source:
        samples = np.genfromtxt(source, delimiter=',', names=True)
    # Quarter-second medians reduce raw quantization without filtering 14 s.
    bins = np.floor((samples['time'] - samples['time'][0]) * 4).astype(int)
    freq = np.asarray([np.median(samples['frequency_hz'][bins == i])
                       for i in range(bins[-1] + 1)])
    t = np.arange(len(freq)) / 4
    trend = np.column_stack((np.ones(len(t)), t, t * t))
    base = trend @ np.linalg.lstsq(trend, freq, rcond=None)[0]
    phase = 2 * np.pi * t / 14.2
    model = np.column_stack((trend, np.sin(phase), np.cos(phase)))
    coefficients = np.linalg.lstsq(model, freq, rcond=None)[0]
    residual = freq - model @ coefficients
    r2 = 1 - np.dot(residual, residual) / np.dot(freq - base, freq - base)
    amplitude = np.linalg.norm(coefficients[-2:])
    print(f'{path}: n={len(samples)}, duration={samples["time"][-1]-samples["time"][0]:.2f}s, '
          f'14.2s amplitude={amplitude:.1f}Hz, partial R2={r2:.3f}, '
          f'errors={int(max(samples["errors"]))}, overflows={int(max(samples["overflows"]))}')


if __name__ == '__main__':
    for file_name in sys.argv[1:]:
        analyze(file_name)
