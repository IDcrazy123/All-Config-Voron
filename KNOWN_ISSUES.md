# Current production issues

Updated: 2026-11-13. This file records the active state of the printer. Older
entries in the parent workspace's `.agents/KNOWN_ISSUES.md` are historical.

## Cartographer adaptive mesh failed during T0 print (2026-11-13)

The T0-only job `A4T Stealthchanger_ABS_17m48s.gcode` was cancelled at 15:21:21
while `PRINT_START` ran `BED_MESH_CALIBRATE ADAPTIVE=1`. The live error was
`Mesh scan failed: 195/195 grid points have no valid samples`; the scan did
collect 2880 raw samples, and 1237 were assigned to the grid. QGL and Touch
completed beforehand. The scan model converted no grid point to a finite
distance, so this is a Cartographer scan/model problem, not a T1–T4 include or
Orca tool-selection rejection. The coil reported about -25 C during the failed
scan, versus about -21.9 C during a previous successful mesh. Its reference
temperature is -21.41 C and no coil compensation calibration is saved. The
negative coil reading warrants a physical probe inspection; the exact cause of
this single failed scan cannot be proved without raw scan frequencies.

No scan-height, model, or temperature limits were changed. After cancellation,
Klipper was `ready` but toolchanger state was `uninitialized`, active tool was
`None` and T0 was detected on the shuttle. Do not resume or command automatic
pickup/mesh from that state. Power off and inspect the Cartographer coil and
connectors, then validate scan readings/calibration with an attended test before
retrying a print. See `extras/diagnostics/2026-11-13-t0-print-mesh-failure/REPORT.vi.md`.

## T1 sensor fault and temporary T0-only mode (2026-11-13)

The operator reported a T1 sensor fault and requested T1–T4 be disconnected
for maintenance while T0 remains printable. Before the change, all heater
targets were zero and the machine was idle with an empty shuttle; T1 reported
about 114 C, which cannot be trusted as a physical temperature because of the
reported sensor fault. The live `printer.cfg` now explicitly includes only the
T0 tool file alongside the KTC core. T1–T4 extruder/tool SAVE_CONFIG sections
were omitted from the active file, with the original file backed up. A
`PRINT_START` guard rejects nonzero T1–T4 temperature requests before motion.

One idle RESTART returned Klipper `ready` without warnings. The live tool
registry is `[0]`; T1–T4 MCU, extruder, sensor and macro sections are absent.
No homing, pickup, heat or print was run afterward. Reslice every maintenance
job for T0 only; old multicolor G-code must not be reused. Confirm the physical
tool/CAN state and an attended first-layer test before claiming print readiness.
Restore five-tool includes and saved calibrations only after T1–T4 hardware is
reconnected and verified. See the November 13 maintenance journal.

Later on November 13, the operator reported replacing the T1 sensor with the
same `Generic 3950` type and moving its dock. All four EBB1–EBB4 CAN UUIDs were
visible. The five-tool include and stored PID/offset sections were restored;
`FIRMWARE_RESTART` brought Klipper to `ready` with tool registry `[0,1,2,3,4]`,
no warnings and T1 reading about 39 C with its target off. T1 dock is
provisionally X104 Y0 Z330 based on the operator's observed trigger at Z327–330.
An attended T1 pickup and `PID_CALIBRATE` at 250 C completed. The saved T1 PID
is 28.787/9.596/21.590; Klipper restarted `ready`, with all five tools listed
and no warnings. T1 dropoff/repickup and a print remain to be validated before
the new dock coordinates are considered calibrated.

## Mainsail Estimate and ETA during printing (2026-11-04)

Read-only observation reproduced Estimate changing from 23:55:17 to 21:42:35
in 78 seconds on Voron Skirt_ABS_2h45m.gcode, with ETA moving from 09:42 +1
to 08:15 +1. Slicer metadata is 2:44:30. Live Mainsail v2.19.0 defaults
average file/filament extrapolations for Estimate and file/filament/slicer
for ETA. PRINT_START purges T0 before bed waiting, a 90-second soak, QGL,
Touch and mesh; print_duration includes this time after initial extrusion
while virtual-SD file progress barely advances. Fine QGL needed eight
retries in this job. Nonuniform bytes/extrusion per second and macro purge
further destabilize extrapolation. Twenty-four samples reproduced this
while T3 remained active; a tool switch is not required.

On the operator's workaround request, Mainsail GUI preferences were changed
to ETA=Slicer only and Estimate=no selected sources (displaying --).
Estimate's average only supports File and Filament; this disables misleading
extrapolation rather than correcting that algorithm. Moonraker DB readback
confirmed only these two preferences changed. No Python, CFG, macro or
printer-control changes were made. The printer had returned to standby
before the preference changes, so live-print verification awaits the next
job. Slicer-based ETA can still be inaccurate when actual time differs.
Rollback and backup details are recorded in
extras/Nhat-ky-chinh-sua/2026-11-04-mainsail-time-display-workaround.md.
See extras/Nhat-ky-chinh-sua/2026-11-04-estimate-eta-readonly-diagnosis.md and
extras/diagnostics/20261104-time-estimate/ for evidence and limitations.

## Tool pickup and recovery

At 19:03, T0 pickup returned `No tool detected` and `Expected tool tool T0 but
active is None`. The operator found that the dock had shifted. The live T0 dock
Y value of 1.3 mm restored pickup; the repository previously specified 1.8 mm.
The live T2 dock Y value is 1.6 mm, rather than the old repository value of
2.1 mm. Both values are now in the repository. An authorized October 30 trial
verified 12 alternating T0/T2 tool changes without a pickup detection failure.
This does not establish long-term pickup reliability or nozzle Z repeatability.

The crash detector pauses the print and marks attachment as uncertain. After
inspecting the tool and dock, `RESUME` reinitializes KTC and verifies the
original tool; `CANCEL_PRINT` skips XYZ parking while the guard is set. Both
clear the temporary guard automatically. An idle sensor edge creates no guard.
`PRINT_START` and QGL check active/detected agreement before motion. A failed
verification means the dock or detection input still needs repair.

## Intermittent bed temperature input

The October 26–28 Klipper logs show recurrent implausible jumps in the bed
reading. On October 27, two shutdowns reported `ADC out of range`; just before
them the reported bed temperature jumped 99.4→120.3 °C and 87.1→127.5 °C in
about one second. Other episodes dropped tens of degrees and triggered `Heater
heater_bed not heating at expected rate`. On October 28, with the heater target
and PWM at zero for over 15 minutes, the reading went 49.7→4.4→49.8 °C in two
seconds. SSR switching or inadequate heater power alone cannot explain that
heater-off reading. The NTC measurement path is intermittently faulty; logs
cannot isolate the NTC element from its lead, crimps, connector, or PB0 input.
An intermittent open contact is a leading hypothesis, but electrical noise or
an input fault has not been ruled out.

The fault recurred during the October 30 motion/QGL trial while raising the
bed target from 70 to 100 C, before any ABS motion/QGL measurements. Klipper
logged 85.6 -> 65.5 -> 86.4 C in two seconds and 68.9 -> 101.0 C in one second.
The independent trial monitor deliberately sent emergency_stop at about
18:47:40 client local time; the shutdown reason is consequently a webhooks
request, not a native ADC or QGL error. Heater outputs report power=0, although
cached targets initially remained nonzero. Cleanup G-code was rejected after
shutdown. On the operator's subsequent reset request, one FIRMWARE_RESTART
returned Klipper to Ready at 18:52:17, with all heater targets/power zero and
unchanged settings. No homing, movement or heating followed this reset. Keep
heaters off pending inspection and repair of the temperature input. Data is in
extras/docs/qgl-motion-trial-2026-10-30-bed-fault.csv.

Before heating again, disconnect mains power and let the bed cool.
Inspect the sensor attachment, cable, crimps, PB0 connector and routing near
AC/SSR wiring. With power off, measure the cold NTC resistance at the controller
end while gently flexing the cable and connectors; repeat closer to the sensor
if the reading jumps or opens. Repair or replace the faulty part, then verify
stable readings and a supervised heat cycle before another long heated print.
Do not relax `verify_heater`, PID, or smoothing to mask the fault.

The seller labels the sensor `NTC 100k MBG18-104F39050L32`; the installed
Klipper type is `NTC 100K MGB18-104F39050L32`. Confirm the actual component
specification before changing the thermistor curve. Since November 11,
`heater_bed.max_temp` is 120 °C both live and in the repository; do not
raise it without a verified hardware rating.

Read-only October 30 follow-up distinguished preparation from printing. The
17:08 start had 79.8 -> 116.4 C in one second at an unchanged 105 C target.
Printing later showed smaller isolated steps: 99.8 -> 101.5 C at 17:20:51,
99.2 -> 101.1 C at 19:28:29, and 100.3 -> 102.4 C at 19:28:54. The ZAssembly
job completed at 20:28:28. Its entire heated printing phase, 19:22:11-20:28:10,
has 3,956 raw Stats samples with no step >=3 C; maximum adjacent step is
2.1 C. The three steps >=0.8 C all occurred at 19:27:58-19:28:54. A separate
19:45:07-19:55:07
client-time monitor completed 600 GET-only API samples and 599 matching-boot
raw Stats samples: raw bed 99.9-100.1 C, largest adjacent step 0.1 C. API
temperature is smoothed for 3 seconds and must not substitute for raw Stats.
Nozzle PWM and part fan changed while this window stayed stable. Earlier
bed-only spikes did not coincide with PB1 chamber spikes, narrowing suspicion
to the bed NTC/wiring/TH0-PB0 input or interference local to that path; the
part or interference source remains unproven. Commanded PWM is not measured
SSR current. The operator retained the mainboard, bed wiring and SSR through
the StealthChanger upgrade. Per the manufacturer schematic, TH0 already has
C34=0.1 uF plus series filtering, so an added 104 capacitor is not a verified
repair. See extras/docs/bed-temperature-review-2026-10-30.md.

On November 11, the operator reported replacing the bed sensor and moving the
SSR control to `PA5`. The live config and loaded settings both confirm `PA5`;
`PB0` remains the bed sensor input. A supervised heat cycle to 100 °C produced
389 raw Klipper Stats samples over about 6.5 minutes, from 24.5 to 100.4 °C.
The largest adjacent rise was 0.8 °C and the largest fall was 0.1 °C; no step
reached 2 °C and no bed heater or ADC error appeared in that window. The bed
was held near 100 °C for only about two minutes before its target returned to
zero. This is encouraging but does not establish long-term stability or absolute
sensor accuracy. The live file was edited and reloaded during the session:
`max_temp` is now 120 °C, while commented `smooth_time` and `pwm_cycle_time`
use Klipper defaults 1.0 s and 0.1 s. The repository was synchronized to
these live defaults on November 13, after the QGL log review.
See `extras/diagnostics/2026-11-11-bed-sensor-monitor/raw-stats.csv`,
`extras/diagnostics/2026-11-11-bed-sensor-monitor/samples.csv` and
`extras/Nhat-ky-chinh-sua/2026-11-11-bed-sensor-ssr-pa5.md`.

## Cartographer coil temperature and QGL

Negative coil readings first appear in the October 29 log at approximately
20:11:35 local time, while plugin 1.9.0 was still installed. The upgrade to
1.10.1 occurred on October 30 at 09:32:54, after the fault was already present.
The temperature path needs inspection; a specific failed component has not
been established.

The operator disabled the saved coil temperature-compensation coefficients
and recalibrated the scan model on October 30. Live scan calibration now has
reference_temperature=-8.53 and software_version=1.10.1; the live touch model
has threshold=1504. Coil temperature is still reported but no longer enters
scan temperature compensation. These live calibrations differ from the
repository printer.cfg. Live QGL retries is 10, while the repository still
specifies 5. Do not overwrite these operator changes with a full deployment.

QGL remains sensitive to thermal settling. A manual run after SAVE_CONFIG,
with bed target zero and the bed cooling, aborted at retry 6 as the measured
range increased. During the subsequent print start at a maintained 105 C bed
target, QGL passed at retry 7 with a 0.005290 mm range. The requested belt
tensioner file then passed Touch/mesh and began printing with T2.

After the requested print completed, scan samples=200 (previous default 20)
was selectively deployed and verified on October 30 at 17:41 local time.
Klipper is ready, and all other effective configuration settings match the
pre-restart snapshot. The scan/touch models, disabled coil compensation, QGL
retries=10 and heater limits are preserved. The one-time deployment heartbeat
was removed afterward. A later authorized thermal trial completed 10 QGLs:
three at 100 C after a 90-second initial soak (retries 8/6/3), three at 105 C
after a 90-second initial soak (6/4/3), and four with a PETG target of 70 C
(2/3/1/3). All met the 0.0075 mm tolerance, but the first PETG run was still
at 71.89-74.83 C and must be treated as a thermal transition. The last PETG
control followed 60.9 seconds continuously within the target band and passed
at 0.007201 mm. Some passes remain marginal and need many retries; this does
not establish a repaired sensor or reliable cold starts. No runtime Python
or configuration changes were made during the trial. See
extras/docs/qgl-thermal-trial-2026-10-30.md for measured temperatures and data.

A subsequent motion trial applied three T0->T2->T0 round trips and three
Z20->Z200->Z20 cycles before EACH QGL. Both PETG 70 C trials passed at
0.002764/0.005048 mm, retries 3/1, after 12 verified tool changes and six Z
cycles in total. Apparent center Z shifted -0.038139/-0.173363 mm; consecutive
center probes already varied by 0.010838-0.027926 mm. These measurements mix
thermal/probe drift with mechanical effects and do not establish lost Z steps
or tool nozzle reseating accuracy. The ABS 100/105 C motion trials remain
unperformed because of the bed input fault above. All effective settings
remain unchanged. See extras/docs/qgl-motion-trial-2026-10-30.md.

At the later read-only review, live scan samples was 20, while the repository
probe file still specifies 200; no synchronization was performed. The scan
and touch models remain unchanged. A 19:18 print-start QGL aborted as range
increased 0.075379 -> 0.076728 -> 0.092545 mm despite bed 104.7-105.3 C without
a large step. The retrying print start passed at 0.006676 mm, retry 2, around
19:21:08. Both starts skipped automatic heat soak. This does not establish a
controlled 20-versus-200 comparison or prove the bed input caused this QGL
failure. The ZAssembly job subsequently completed; no intervention was made.

## November 2 first-layer and post-docking QGL follow-up

Operator follow-up on November 2 identifies an incorrectly substituted spacer
part as the cause. This supersedes the provisional cause ranking below and in
the diagnostic report. The exact part/location, failure mechanism and results
after fitting the correct spacer have not yet been supplied. Do not mark the
first-layer/QGL issue mechanically verified as resolved, or infer pulley slip,
joint binding or lost motor steps from this report alone. The independently
observed coil-temperature and bed-input faults remain unverified as repaired.

A read-only review found large QGL ranges recurring after dock travel. At
18:45 the empty shuttle measured 0.981970 mm after the T4 print ended. After
an initial T0 pickup and four T0/T4 round trips, the 18:49 run started at
2.026687 mm, but bed readings were faulty and thermally transitioning. After
five further round trips ending on T0, the 18:54 run started at 1.179902 mm
while raw bed readings stayed at 79.9-80.1 C. All three requested their largest
initial correction on Z2. These are probe measurements and commanded motor
corrections, not independent proof of mechanical displacement or lost steps.

Live Z limits are 80 mm/s and 1000 mm/s2. Native dock paths reach Z346 with
position_max=347. Inspect the rebuilt Z/GE5C assembly, especially the Z2 drive,
pulley retention, belts, joint freedom and actual upper clearance. The loaded
PRINT_START/PRIME_LINES sequence keeps T0 mounted after Touch/mesh for a
T0-only print, but changes T0 to the other tool and back before a multicolor
print starting on T0. A T3/T4-only print also changes tools after T0 Touch.
This provides a plausible trigger for losing the reference; no physical
before/after measurement or reduced-speed comparison has yet isolated it.

Coil readings remain near -20 C. The latest T4 start had Touch samples
-0.6290/-0.1750/-0.6090/-0.6090/-0.6090 mm before accepting the final cluster.
The 0.454 mm spread warrants investigation, but the resulting Touch adjustment
is not the nozzle-to-bed error. Bed input faults also recurred, including
84.1 -> 38.8 -> 25.8 -> 86.8 C within a few seconds at approximately 18:47.
Inspect and verify that measurement path before further heated ABS trials.

Recent downloaded T0-only, T0/T3, T3-only and T4-only G-code files use a
0.20 mm first layer and zero slicer Z offset, without runtime SET_GCODE_OFFSET
or G92 Z commands. Live gantry_corners remain (-10,-10)/(350,350); their
relationship to the actual Z belt positions still needs measurement and may
contribute to slow convergence. No production settings or slicer profiles
were changed. Final SSH/API reads timed out, so later machine state is not
verified. Evidence and the provisional cause ranking are in
extras/diagnostics/2026-11-02-first-layer-qgl/REPORT.vi.md.

## November 7 QGL recurrence and calibration sync

QGL still aborted intermittently after the new Scan and Touch models were
saved. After a T0/T3 round trip, the 11:38 coarse pass measured 0.956585 mm
and requested +0.804969 mm at Z2. The fine pass reached 0.009511 mm at
retry 10 and failed against 0.0075 mm. Other runs passed in five or six
retries. A T0-only print completed at 11:59 after a 90-second heat soak and
a QGL pass at retry 2. Touch on that job needed nine attempts to accept its
three-sample cluster. The motor numbering error comes from the retry trend
check. The larger post-dock deviation makes Z2 a mechanical inspection
priority. The fine-pass variation still needs independent comparison against
Scan.

Coil temperature remains negative with no compensation coefficients loaded.
Bed telemetry jumped from 109.0 to 44.3 to 106.2 C in about two seconds at
a 100 C target. Verify the NTC input path before further heated trials.

The repository mirrored the November 7 SAVE_CONFIG block, QGL geometry and retry
count, and Scan sample configuration. The bed temperature limit was later
returned to 120 C on the printer; newer PID and Scan values were synchronized
on November 13.
See [the November 7 log](extras/Nhat-ky-chinh-sua/2026-11-07-qgl-live-calibration-sync.md).

The attended corner checks later that day confirmed motion in both directions
on all four Z drives. Z2 showed the smallest local Scan response and largest
return residual. Stationary Scan at Z2 also varied by up to 0.046 mm. The
two T3 round trips produced larger four-corner changes than the two T4 round
trips, and the largest change followed the first sampled corner when the
measurement order was reversed. The T0 and empty-shuttle confirmation QGLs
both passed. Independent measurement at Z2 is still needed to separate
physical motion from Scan drift. See [the corner test results](extras/Nhat-ky-chinh-sua/2026-11-07-z-corner-live-tests.md).

The operator then adjusted the lower Z motor drive GT2 belts. The repeated
checks found smaller Z200 and post-T3 four-corner changes, with no consistent
motor-specific failure. The colder test conditions also differed. Stationary
Scan still drifted after docking, and the last production QGL needed eight
retries. Fine QGL with 3 mm travel height passed in 0-2 retries in three cold
trials, including one after T3. The production height remains unchanged
pending an operating-temperature comparison. A timing shutdown during the
diagnostic's long sample stream did not recur after switching to short scans.
See [the alignment retest](extras/Nhat-ky-chinh-sua/2026-11-07-qgl-after-hardware-alignment.md).

The frame-derived trial corners `(-52, 1)` and `(417, 423)` exhausted all 10
fine QGL retries twice at about 33 C with the heaters off. The previous
corners passed all five scored cases at the same tolerance, including Z2
and Z0 perturbations. The machine was reverted to `(-10, -10)` and
`(350, 350)`. The trial alternated the calculated Z3 correction direction,
with the physical Z3 response still unverified. See [the corner comparison](extras/Nhat-ky-chinh-sua/2026-11-07-qgl-gantry-corners-ab.md).

## November 11–13 bed sensor replacement and QGL result

The operator confirmed the previous bed sensor showed failure in use and
replaced it, then recalibrated the bed PID and Cartographer Scan. Old logs
support intermittent large jumps while heating, but an October 28 episode
also occurred with heater target/PWM zero, so "only when heating" is not
established by the logs. The November 11 and 13 Klipper logs show no adjacent
bed-temperature jump >=2 C while the target was nonzero. The new sensor's
absolute accuracy and long-term reliability remain unmeasured.

After the last Scan model and Touch 792 were saved on November 11, seven hot
fine-QGL attempts at a 105 C target are identifiable across the November 11
and 13 logs: four met 0.0075 mm tolerance and three aborted. The short
November 13 cube print completed after QGL reached 0.003413 mm at retry 2;
an earlier attempt that day aborted after its range climbed from 0.013422
to 0.249438 and 0.353690 mm. Bed readings during that failed pass stayed
about 105.1–105.2 C. QGL convergence is therefore still unreliable.

The installed Cartographer Python reads temperature from the probe MCU, not
the bed thermistor. No coil temperature-compensation calibration is loaded,
so its negative coil reading is not used to correct scan frequency. The
Klipper motor-numbering message is a generic result of two increasing range
checks. Repeated Scan deviations, especially at the right-side points, need
independent dial-indicator comparison before assigning the cause to the probe
mount, thermal drift, or Z mechanics. Current live PID, Scan model, bed
smoothing/PWM defaults and disabled axis twist are now mirrored in Git; no
printer reload was performed. See the [November 13 analysis](extras/diagnostics/2026-11-13-qgl/REPORT.vi.md).

## T2 false filament runout

The operator reports filament remained loaded when T2 paused. On October 30,
the T2 sensor triggered at 17:25:15 and the delayed handler paused at 17:25:17.
A second event at 17:29:01 recovered before confirmation and was filtered at
17:29:03. The operator then issued SET_FILAMENT_SENSOR for T2 with ENABLE=0.
That session reported filament present with automatic T2 runout handling
disabled. The authorized samples=200 deployment restarted Klipper after print
completion; at 17:41 T2 again reports filament present and enabled=true, as
expected after restart. The T2 configuration file was unchanged at that point;
the later native-debounce deployment below now mitigates short false inputs.

Live T2 uses ^EBB2:PB8 with event_delay=0.5 and a delayed state recheck after
0.5 seconds. This is not a continuous signal-stability filter. In the installed
Klipper, insert_gcode runs only outside the Printing idle-timeout state, so
its cancellation hook cannot be relied on to cancel noisy events while
printing. The installed filament switch/button code supports debounce_delay;
all five sensors previously omitted it and therefore used zero.

On the operator's repair request, T2 received debounce_delay: 0.5 at 21:04.
The operator then expanded the scope to all five tools. T0/T1/T3/T4 received
the same option at 21:07; T2 was not rewritten. At 21:08:28, Klipper was Ready,
all five sensors were enabled and reported filament present, and effective
settings differed from the initial snapshot only in these five debounce
values (0 -> 0.5 seconds). Existing delayed confirmations, active-tool checks,
pins/polarities and runout pause behavior are preserved. Each stage used one
idle-checked RESTART; no motion, heat or print was started.

Replay of the installed DebounceButton class rejected a 125 ms false pulse
and intermittent chatter, while accepting persistent absence and insertion
after 500 ms. This verifies software filtering, not the physical switch or a
new T2 print. A sustained false input can still pause the active printing
tool; inspect filament actuation, mounting, PTFE loading, connector, signal
and ground wiring if the fault recurs. The exact failed component and raw
pulse durations are not established. See
extras/docs/filament-runout-debounce-2026-10-30.md for backups and verification.
