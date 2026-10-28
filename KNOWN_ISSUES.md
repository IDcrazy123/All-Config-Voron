# Current production issues

Updated: 2026-10-28. This file records the active state of the printer. Older
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
