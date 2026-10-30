# Current production issues

Updated: 2026-10-30. This file records the active state of the printer. Older
entries in the parent workspace's `.agents/KNOWN_ISSUES.md` are historical.

## Tool pickup and recovery

At 19:03, T0 pickup returned `No tool detected` and `Expected tool tool T0 but
active is None`. The operator found that the dock had shifted. The live T0 dock
Y value of 1.3 mm restored pickup; the repository previously specified 1.8 mm.
The live T2 dock Y value is 1.6 mm, rather than the old repository value of
2.1 mm. Both values are now in the repository. Mechanical verification of T2
after deployment remains open.

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

After the current print ends, disconnect mains power and let the bed cool.
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

The repository probe config now prepares scan samples=200 (previous default
20). This is separate from QGL retries. Deployment is pending completion of
the current print and a verified idle state; an authorized heartbeat in the
current chat will apply only this probe-config change and verify it after
RESTART. The 200-sample setting has not yet been mechanically validated with
the newly recalibrated, uncompensated model. No runtime Python changes are
planned.

## T2 false filament runout

The operator reports filament remained loaded when T2 paused. On October 30,
the T2 sensor triggered at 17:25:15 and the delayed handler paused at 17:25:17.
A second event at 17:29:01 recovered before confirmation and was filtered at
17:29:03. The operator then issued SET_FILAMENT_SENSOR for T2 with ENABLE=0.
The input currently reports filament present, but automatic T2 runout handling
is disabled for this session. A Klipper restart normally enables it again.

Live T2 uses ^EBB2:PB8 with event_delay=0.5 and a delayed state recheck after
0.5 seconds. This is not a continuous signal-stability filter. In the installed
Klipper, insert_gcode runs only outside the Printing idle-timeout state, so
its cancellation hook cannot be relied on to cancel noisy events while
printing. The installed filament switch/button code supports debounce_delay;
T2 currently omits it and therefore uses zero.

A targeted candidate is debounce_delay: 0.5 in the T2 filament-switch section,
retaining the existing delayed confirmation and active-tool checks. An
isolated replay of the installed DebounceButton class rejected short and
intermittent pulses while accepting persistent absence. This option has not
been deployed or physically tested. It cannot repair a sustained false input;
inspect the sensor's filament actuation, mounting, PTFE loading, connector,
signal and ground wiring before declaring the problem resolved. The exact
faulty component and raw pulse durations are not established by these logs.
