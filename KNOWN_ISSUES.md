# Current production issues

Updated: 2026-10-30. This file records the active state of the printer. Older
entries in the parent workspace's `.agents/KNOWN_ISSUES.md` are historical.

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
specification before changing the thermistor curve. The 120 °C repository
`heater_bed.max_temp` and 150 °C live value also remain unresolved; do not
raise the repository limit without a verified hardware rating.

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
