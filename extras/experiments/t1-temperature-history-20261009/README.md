# T1 reported temperature history — 2026-10-09

## Finding

T1's reported temperature is repeatedly above the other tools when its recorded
target and PWM are zero. This predates today's CFG deployment and runtime patch.
There is clearer evidence by **2026-09-29**, about ten days before this review,
and an earlier difference on September 27 whose residual-heat history is not
sufficiently established. Neither date proves the exact physical fault onset.

At **21:53:15 on October 9**, the API reports T1 **47.19 C**, target/power zero;
T0/T2/T3/T4 are **31.52 / 31.82 / 31.83 / 31.92 C**. This latest snapshot is
affected by a separate console command setting T1 to 220 C at 21:48:23 and
turning heaters off at 21:49:17; do not treat it as a cold baseline.
Earlier in this review, at approximately 21:45, T1 was 55.95 C with target/power
zero and the other tools 31.78–32.18 C, also following earlier manual heating.

## Representative dated samples

All temperatures below are **reported readings**, not independent physical
measurements. At each historical row, all five hotend targets and PWM are zero.
Times use Asia/Saigon, UTC+7; log-derived seconds have the precision of the
recorded epoch/monotonic anchor.

| Time | T1 C | Other hotends C | Evidence |
| --- | ---: | --- | --- |
| 2026-09-27 03:13:07 | 42.1 | 31.7–33.8 | Older local log, line 7226; residual heat not excluded. |
| 2026-09-29 09:25:10 | 32.7 | 31.5–31.7 | Older local log, line 537377. |
| 2026-09-29 09:52:32 | 49.0 | 32.3–32.6 | Same session, line 537743; reported T1 rises about 16 C while peers remain near 32 C. |
| 2026-10-04 15:41:58 | 62.9 | 38.2–40.0 | Rotated live log, line 307297. T1 has 9,377.6 s since its first observed off sample without observed heating/reset. |
| 2026-10-08 23:59:59 | 69.0 | 30.5–31.3 | Rotated live log, line 253970. |
| 2026-10-09 06:24:36 | 51.0 | 27.8–28.2 | Current live log, line 29904, before today's edits. |
| 2026-10-09 21:09:18 | 57.2 | 33.2–34.5 | Current live log, line 116104, before the response runtime patch. |
| 2026-10-09 21:34:51 | 55.8 | 32.1–32.8 | Current live log, line 126330, after the response patch. |

The behavior is variable, not a fixed +24 C correction. For example, after the
October 7 20:47:02 restart, T1 reports 26.2 C at 20:47:14 and 38.6 C at 20:48:14;
T0 stays near 24.3–24.4 C and T1 target/PWM at the sampled points are zero.
At other startups T1 differs from peers by only about 2 C. These records do not
justify editing sensor type, adding a temperature offset, or changing PID.

## Data and method

- Read all six retained live Klipper logs: current log and rotated October 4–8
  files, about 536 MB (512 MiB) total. Collected source line numbers and compact summaries
  without downloading full live logs or changing the printer.
- Also read local September 27 and September 29 captures. September 29's second
  capture is nearly identical and was not counted twice.
- The parser reads only `Stats` lines and uses `Start printer at` to convert
  monotonic time to UTC+7 wall time. Zero startup sensor readings are ignored;
  samples without a usable anchor stay undated and are excluded from dated
  conclusions. Cached rollover prefixes and duplicated captures can contain
  samples from an earlier date than the filename.
- The optional "30 minutes off" grouping means elapsed time since the first
  observed target/PWM-zero sample after the last observed heating/restart. Gaps
  without log samples cannot rule out intervening commands. It is not a proof
  of continuous electrical power-off or thermal equilibrium.
- Representative source lines were fetched separately and checked against the
  summary and their startup anchors. Units and mappings: T1=`extruder1`, PWM is
  commanded heater output, API `power` is also commanded output.
- No G-code, heater command, movement, restart, calibration or CFG write was
  issued during this investigation. Later console heating belongs to separate
  operator activity and is retained only as context.

Files:

- `analyze_logs.py`: reproducible read-only parser; accepts ordered input paths.
- `recent-log-summary.json`: dated/session summaries of the retained live logs.
- `older-local-log-summary.json`: summaries of September 27/29 local captures.
- `selected-live-log-lines.jsonl` and `selected-older-log-lines.jsonl`: compact
  source evidence with file/line references.
- `live-snapshot.json`: API readings at 21:53:15, UTC+7.
- `recent-console-commands.json`: later manual T1 heat/off context.
- `log-inventory.jsonl`: source headers/anchors and first/last sample inventory.

The original September captures remain at `extras/logs/`; live log paths are
`/home/voron/printer_data/logs/klippy.log*`. Large raw logs are not added to Git.

## Interpretation and next check

The log confirms a longstanding **reported-temperature difference**, including
periods with no recorded heater drive. It cannot determine whether the sensor
reports incorrectly or the hotend is actually warmer. Commanded PWM zero does
not independently measure electrical heater power. After a full cool-down,
compare T1 with an independent temperature measurement before investigating
the thermistor/input circuit or heater hardware. The operator asked to defer
the physical investigation; this task only records the log evidence.
