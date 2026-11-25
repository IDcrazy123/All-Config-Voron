"""Fit the stationary LDC1612 cycle in the saved 25 Nov 2026 captures.

Usage: python analyze_stationary.py
Requires NumPy; reads only files beside this script.
"""

import csv
import gzip
from pathlib import Path

import numpy as np


HERE = Path(__file__).parent


def fit_cycle(x, y, trend_degree=3, periods=None):
    if periods is None:
        periods = np.linspace(8, 25, 1701)
    trend = np.polyval(np.polyfit(x, y, trend_degree), x)
    residual = y - trend
    power = np.dot(residual, residual)
    fits = []
    for period in periods:
        phase = 2 * np.pi * x / period
        basis = np.column_stack((np.sin(phase), np.cos(phase)))
        coeff = np.linalg.lstsq(basis, residual, rcond=None)[0]
        delta = residual - basis @ coeff
        fits.append((1 - np.dot(delta, delta) / power, np.linalg.norm(coeff)))
    idx = int(np.argmax(np.asarray(fits)[:, 0]))
    return periods[idx], fits[idx]


def load_ldc(name):
    with gzip.open(HERE / name, 'rt', encoding='utf-8-sig') as source:
        data = np.genfromtxt(source, delimiter=',', names=True)
    t = data['time']
    seconds = np.floor(t - t[0]).astype(int)
    z = np.asarray([np.median(data['z_mm'][seconds == i])
                    for i in range(seconds[-1] + 1)])
    return data, z


def main():
    for name in ('stationary-90s.csv.gz', 'stationary-75s.csv.gz',
                 'stationary-tmcfan-off-90s.csv.gz'):
        data, z = load_ldc(name)
        x = np.arange(len(z))
        period, (r2, amplitude) = fit_cycle(x, z)
        print(f'{name}: samples={len(data)}, seconds={data["time"][-1]-data["time"][0]:.2f}, '
              f'rate={len(data)/(data["time"][-1]-data["time"][0]):.1f}/s, '
              f'errors={int(max(data["errors"]))}, overflows={int(max(data["overflows"]))}, '
              f'period={period:.2f}s, amplitude={amplitude*1000:.2f}um, R2={r2:.3f}')

    for name, fixed_period in (('stationary-context.csv', 13.85),
                               ('stationary-tmcfan-off-context.csv', 14.36)):
        with (HERE / name).open(newline='', encoding='utf-8') as source:
            rows = list(csv.DictReader(source))
        x = np.asarray([float(row['eventtime']) for row in rows])
        x -= x[0]
        print(name)
        for field in ('coil', 'bed'):
            y = np.asarray([float(row[field]) for row in rows])
            period, (r2, amplitude) = fit_cycle(x, y, trend_degree=2,
                                                 periods=np.asarray([fixed_period]))
            print(f'  {field}: start={y[0]:.3f}C, end={y[-1]:.3f}C, '
                  f'period={period:.2f}s, amplitude={amplitude:.5f}C, R2={r2:.3f}')
        for field in ('bed_power', 'tmc_fan', 'cm4_fan', 'enclosure_fan'):
            values = [float(row[field]) for row in rows]
            print(f'  {field}: min={min(values):.3f}, max={max(values):.3f}')

    for name in ('leds-on-before-30s.csv.gz', 'leds-off-30s.csv.gz',
                 'leds-on-after-30s.csv.gz'):
        with gzip.open(HERE / 'led-isolation' / name, 'rt', encoding='utf-8-sig') as source:
            data = np.genfromtxt(source, delimiter=',', names=True)
        bins = np.floor((data['time'] - data['time'][0]) * 4).astype(int)
        z = np.asarray([np.median(data['z_mm'][bins == i])
                        for i in range(bins[-1] + 1)])
        x = np.arange(len(z)) / 4
        trend = np.column_stack((np.ones(len(x)), x, x*x))
        base = trend @ np.linalg.lstsq(trend, z, rcond=None)[0]
        phase = 2*np.pi*x/14.2
        model = np.column_stack((trend, np.sin(phase), np.cos(phase)))
        coefficients = np.linalg.lstsq(model, z, rcond=None)[0]
        residual = z - model @ coefficients
        r2 = 1 - np.dot(residual, residual) / np.dot(z - base, z - base)
        print(f'{name}: amplitude={1000*np.linalg.norm(coefficients[-2:]):.2f}um, '
              f'partial R2={r2:.3f}, errors={int(max(data["errors"]))}, '
              f'overflows={int(max(data["overflows"]))}')


if __name__ == '__main__':
    main()
