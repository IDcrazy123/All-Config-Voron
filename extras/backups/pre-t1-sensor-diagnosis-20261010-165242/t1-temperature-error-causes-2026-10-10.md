# Possible causes of T1 temperature reading error — 2026-10-10

## Verified facts and limits

The loaded T1 configuration was checked read-only through Moonraker:
`sensor_type=Generic 3950`, `sensor_pin=EBB1:PA3`, `pullup_resistor=4700`,
`inline_resistor=0`, `heater_pin=EBB1:PB13`. The five repository tool files use
the same sensor model and corresponding PA3 inputs. The pins match the
[manufacturer's V1.2 example](https://github.com/bigtreetech/EBB/blob/master/EBB%20CAN%20V1.1%20and%20V1.2%20%28STM32G0B1%29/sample-bigtreetech-ebb-canbus-v1.2.cfg).
This verifies software settings, not the actual thermistor model, wiring or PCB.

The [previous log investigation](../experiments/t1-temperature-history-20261009/README.md)
shows variable reported T1 temperatures, sometimes substantially above peer
tools with target/PWM zero. No independent temperature or resistance measurement
has established a sensor fault. The following is a diagnostic shortlist, not a
list of confirmed failures or numerical probabilities.

## Electrical interpretation

For this NTC model, lower inferred resistance produces a higher temperature.
Installed [Klipper thermistor conversion](https://github.com/Klipper3d/klipper/blob/7bc4d09465d31cd30fc0822e8d0abe02cc8c547f/klippy/extras/thermistor.py)
uses `R = pullup * ADC / (1 - ADC)` before applying the temperature curve.
Thus a leakage path toward ground or between sensor wires can mimic a hot sensor.
An open circuit or increased series/contact resistance normally produces a
colder reading; an intermittent connector can produce several different faults.

Illustration only: for a 100 kOhm-at-25 C, beta3950 NTC, expected resistance is
approximately 80.4 kOhm at 30 C, 29.8 kOhm at 55 C and 18.2 kOhm at 69 C.
If the sensor were physically 30 C while reporting 55 C, that would require a
large measurement/model error, not merely normal small component tolerance.
The actual physical temperature has not been measured, so this is not an estimate
of the installed sensor's resistance or a replacement configuration value.

## Candidate causes and discriminating evidence

| Candidate | Mechanism / fit to the observed high reading | Evidence to seek |
| --- | --- | --- |
| Sensor cable insulation damage or partial short | The two leads touch, or signal leaks to ground. Effective resistance falls; bending or tool position can change the error. | Inspect worn/flattened insulation and strain points. Compare disconnected resistance while gently flexing the cold, unpowered cable. |
| Conductive contamination in a connector or on the PCB | Moisture, conductive dust, contamination or solder bridges can create a shunt leakage path. Not every residue or loose contact is conductive. | Inspect/clean appropriately; compare sensor resistance directly with the entire disconnected cable/connector path. |
| Damaged thermistor element or its insulation | Mechanical crushing, damaged leads, heat cycling or internal leakage can change resistance or make it unstable. | Check disconnected resistance at a known physical temperature; compare with a verified same-model sensor. |
| EBB1 input circuit or ADC damage | Leakage in the protection/input/filter circuit or a damaged ADC input can pull the measured voltage down. Board temperature may change the fault. | Use a known sensor or precision resistor at the input; compare with a good board using the same verified model/settings. Matching board behavior under temperature/load helps isolate this hypothesis. |
| Wrong or damaged pull-up circuit | If actual pull-up is larger than the configured value, inferred NTC resistance is too low and temperature too high. Small ordinary tolerance is insufficient for the illustrative large offset above. | Identify exact PCB variant and thermistor jumper state; verify resistance against that variant's schematic. A lower pull-up with software still set to 4.7 kOhm generally biases this NTC colder, not hotter. |
| Actual sensor does not match Generic 3950 | Different resistance-at-25 C, beta/curve, or a sensor of a different family gives a wrong conversion. Identical CFG settings do not prove identical sensors. | Verify the installed part specification and measure resistance at known temperatures. A modest beta difference between otherwise 100 kOhm-at-25 C sensors alone is less convincing for a large near-ambient offset. |
| Electrical interference or ground differences | Heater/fan/motor switching and poor ground connections may disturb the analog measurement. A uniform supply change does not automatically bias a ratiometric ADC divider. | Look for repeatable correlation with fan/motor/load changes or cable routing. Measure signal/ground with suitable equipment; do not infer EMI just from past CAN errors. |
| Wrong physical input, MCU association or sensor routing | The configured channel may be attached to a different sensor/board, or the cable may use the wrong connector. | Verify EBB1 identity and trace the sensor cable to TH0/PA3. Software pins currently match the V1.2 example, so there is no demonstrated pin typo. |

The prioritization of leakage/thermistor/EBB1 input checks is an **inference** from
the variable, sometimes warm-biased reports. It is not a finding that any of
those parts is defective.

The [BTT thermistor setup guide](https://github.com/bigtreetech/docs/blob/master/docs/EBB%2036%20CAN.md#100k-ntc-or-pt1000-settings)
distinguishes NTC and PT1000 arrangements and board variants. It documents
4.7 kOhm for the NTC arrangement without the PT1000 jumper in the described
non-MAX31865 variant. Do not transfer jumper instructions or pull-up values
to an unidentified variant. [Klipper's reference](https://www.klipper3d.org/Config_Reference.html#common-thermistors)
defines the configurable sensor curve and pull-up/inline resistor parameters.

## Real heat that can resemble a reading error

Residual heat, radiation/conduction from nearby hot tools or the bed, and sensor
placement near a hotter region can make the sensor physically warmer. A faulty
heater output, leakage MOSFET or incorrect heater wiring can also deliver actual
power even when commanded PWM is zero. These are separate hypotheses: PWM/API
power is a command, not an independent current measurement.

First compare the cold T1 sensor region with an independent physical temperature
measurement. If physically warm, investigate heat/power sources; if physically
cold but reporting warm, isolate sensor/cable versus board input. Resistance
measurements require power off and the sensor disconnected from the PCB. Any
cross-check should use verified compatible parts and remain cold, without
heater drive or motion. No physical test was performed in this task.

PID controls heater output; it does not change the ADC-to-temperature curve.
The startup serial-response patch also does not touch this conversion. No
evidence here establishes CAN transport as the cause of a numerical offset.
No sensor, PID, offset, jumper, firmware or runtime change was made.
