# Current production issues

Updated: 2026-10-27. This file records the active state of the printer. Older
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

At about 19:22, the bed reading fell from approximately 104 to 71.7 °C in
seconds and then rebounded toward 100 °C with heater power at 100%. Klipper
stopped with `Heater heater_bed not heating at expected rate`. That measurement
change is implausible for the bed's thermal mass. The specific faulty component
has not been isolated. Inspect the NTC attachment, wiring, crimps, PB0 input,
and routing near AC/SSR wiring with power disconnected. Check for unstable
resistance while gently flexing the cold sensor lead. Replace a defective
sensor, cable, or connector and verify stable readings before another long
heated print. Do not relax `verify_heater`, PID, or smoothing to mask the fault.

The seller labels the sensor `NTC 100k MBG18-104F39050L32`; the installed
Klipper type is `NTC 100K MGB18-104F39050L32`. Confirm the actual component
specification before changing the thermistor curve. The 120 °C repository
`heater_bed.max_temp` and 150 °C live value also remain unresolved; do not
raise the repository limit without a verified hardware rating.
