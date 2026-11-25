"""Compare raw LDC frequency of the original and replacement boards.

Usage: python analyze_replacement.py
No old Z calibration is applied to the replacement board.
"""

import gzip
from pathlib import Path

import numpy as np


ROOT = Path(__file__).parent.parent
FILES = [('old, fan on', ROOT / 'stationary-90s.csv.gz'),
         ('old, fan off', ROOT / 'stationary-tmcfan-off-90s.csv.gz'),
         ('replacement', ROOT / 'replacement-board' / 'new-board-stationary-90s.csv.gz')]


def fit_period(t, frequency):
    residual = frequency - np.polyval(np.polyfit(t, frequency, 3), t)
    periods = np.linspace(8, 25, 1701)
    fits = []
    for period in periods:
        phase = 2 * np.pi * t / period
        basis = np.column_stack((np.sin(phase), np.cos(phase)))
        coefficients = np.linalg.lstsq(basis, residual, rcond=None)[0]
        error = residual - basis @ coefficients
        fits.append((1 - np.dot(error, error) / np.dot(residual, residual),
                     np.linalg.norm(coefficients)))
    idx = int(np.argmax(np.asarray(fits)[:, 0]))
    return periods[idx], fits[idx]


for label, path in FILES:
    with gzip.open(path, 'rt', encoding='utf-8-sig') as source:
        data = np.genfromtxt(source, delimiter=',', names=True)
    bins = np.floor(data['time'] - data['time'][0]).astype(int)
    frequency = np.asarray([np.median(data['frequency_hz'][bins == i])
                            for i in range(bins[-1] + 1)])
    t = np.arange(len(frequency))
    period, (r2, amplitude) = fit_period(t, frequency)
    print(f'{label}: n={len(data)}, period={period:.2f}s, '
          f'amplitude={amplitude:.1f}Hz, R2={r2:.3f}, '
          f'errors={int(max(data["errors"]))}, '
          f'overflows={int(max(data["overflows"]))}')
    if label == 'replacement':
        for start, stop in ((0, 45), (45, 90)):
            x = t[start:stop]
            y = frequency[start:stop]
            phase = 2 * np.pi * x / period
            basis = np.column_stack((np.ones(len(x)), x, x*x,
                                     np.sin(phase), np.cos(phase)))
            coefficients = np.linalg.lstsq(basis, y, rcond=None)[0]
            print(f'  seconds {start}-{stop}: '
                  f'amplitude={np.linalg.norm(coefficients[-2:]):.1f}Hz')
