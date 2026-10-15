# T0 silicone cleaner: measured contact and supported purge

Date: 2026-10-15. Scope: the T0 station in `config/Printer-Setup/nozzle-clean.cfg`.

## Observed problem and reasons for the change

The operator reported limited silicone contact and a purge blob dropping before
the wipe could remove it. The previous routine used a default contact height of
Z1.0, partially traversed the pad through its midpoint, and purged over the bucket.

The operator selected Z0.2 as the next trial height after finding Z1.0 too high
for this setup's intended contact. The old midpoint tracks did
not sweep the complete X span on every silicone row. Purging without a supporting
surface allowed the extruded material to hang freely and fall before the intended
breakoff. These are the reasons for the revised geometry and sequence; they are
not a claim that physical cleaning effectiveness has already been confirmed.

## Latest operator-specified geometry and sequence

All coordinates below are T0 nozzle coordinates with zero live offsets and no
active bed mesh.

| Feature | Coordinates or behavior |
| --- | --- |
| Supported purge point | X315, Y5, Z5 on the PEI surface |
| Direct purge-to-entry corridor | X315/Y5/Z5 to X315/Y-5/Z5 |
| Descent at the entry | X315/Y-5, through Z3 to contact Z0.2 |
| First breakoff stroke | X315/Y-5/Z0.2 to X278/Y-5/Z0.2 |
| First silicone contact from the right | Approximately X313; X315 starts outside it |
| Raster X span | X278 to X311, full-width strokes |
| Three silicone rows | Y-2, Y-5 and Y-8; overall pad range Y-10 to Y0 |
| Default DEEP cleaning | Three raster passes, alternating row order |
| Default TOUCH cleaning | One raster pass; no purge |
| Other station transfers | Z15 or higher before XY travel |
| Existing bucket/benchmark point | X315/Y1/Z6; preserved separately |

The X315 purge/entry alignment avoids an intermediate X move. After a purge, the
direct Y corridor remains at Z5, followed by the descent and first leftward strike;
there is no Z15 lift between the purge and that strike. This exception requires
`BREAKOFF=1` and a runtime check that the starting position matches the configured
purge plate. Ordinary wipes and other station transfers retain Z15 clearance.

When a DEEP call actually purges, it requests the breakoff once: during the warm
wipe stage if more than one pass was requested, or during the final wipe if only
one pass was requested. Calls without a purge do not use the low corridor. The
final wipe remains at or below 150 C before Cartographer Touch.

## Primary references and adaptation limits

- [BambuStudio official A1 start G-code template](https://raw.githubusercontent.com/bambulab/BambuStudio/master/resources/profiles/BBL/machine/Bambu%20Lab%20A1%200.4%20nozzle%20template%20machine_start_gcode.json):
  its silicone brush routine sweeps X back and forth while shifting Y between
  rows, then repeats from the opposite direction. Its circular wiping sections
  are identified separately as wiping on exposed steel.
- [Bambu Lab A1 nozzle wiper replacement guide](https://wiki.bambulab.com/en/a1/maintenance/nozzle-wiper-replacement):
  documents silicone-bristle wear and inadequate cleaning as reasons to inspect
  or replace the wiper.
- [Bambu Lab purge-wiper troubleshooting](https://wiki.bambulab.com/en/a1-mini/troubleshooting/excess-purge-abnormality):
  describes purge waste on a support plate and the normal subsequent ejection.
  This supports the distinction between supporting the purge and wiping the
  nozzle; this Voron does not inherit Bambu's ejector mechanism.
- [Klipper command templates](https://www.klipper3d.org/Command_Templates.html#template-expansion):
  includes a `clean_nozzle` example with alternating X strokes and shifted Y rows,
  together with saving and restoring G-code state.
- [Klipper arc configuration](https://www.klipper3d.org/Config_Reference.html#gcode_arcs)
  and [arc implementation](https://raw.githubusercontent.com/Klipper3d/klipper/master/klippy/extras/gcode_arcs.py):
  arcs are segmented into G1 moves; the current implementation rejects relative
  G2/G3 moves. The cleaner uses G1 raster moves.

Full-width raster coverage and a supported-purge/breakoff sequence are adaptations
informed by these sources. Every coordinate, height, entry direction and feedrate
remains specific to this Voron's measured installation; Bambu values are not
treated as suitable Voron settings.

## Offline verification

From the repository root, with Python and Jinja2 available:

```console
python extras/experiments/t0-cleaner-20261015/test_nozzle_clean_v2.py
```

The harness reads the production CFG and renders its templates using Klipper's
Jinja delimiters. Its small interpreter records moves and executes helper renders
after simulated temperature waits. It never connects to a printer.

There are fourteen test groups, including 40 raster combinations: one through five
passes, both starting directions, breakoff enabled/disabled, and contact Z0.2/Z1.0.
Result on the revised production CFG: all fourteen groups passed, including all 40
raster combinations.
The other checks cover the measured geometry, DEEP/TOUCH/wrapper defaults, actual
purge position, cold/overtemperature refusal, mesh/offset/tool/state guards,
breakoff starting-pose checks, the single low corridor, safe transfers, one
breakoff per purging call, fan restoration and the final 150 C upper bound.
PRINT_START checks cover dedicated T0 temperature while T0 is unused, preservation
of the used-tool/prime list, legacy T0-temperature fallbacks, and refusal of missing
or invalid T0 purge temperatures before any commands are emitted.

These checks establish rendered behavior and software guards. They do not model
silicone deflection, nozzle/plate alignment, blob shape, adhesion or real heater
response. Cleaning effectiveness still requires the operator's observations.

## First attended physical trial (superseded purge Y/Z)

- Live backup: `/home/voron/printer_data/config_backups/pre-t0-plate-purge-raster-20261015-201838-1b7yyj4j`.
- Both live CFGs matched the previous source before replacement. Klipper reload
  succeeded; the loaded macro variables showed plate/entry X315, the three new
  rows and default contact Z0.2. Homing completed, with active/detected T0,
  zero offsets and a clear mesh.
- At 20:20:01 +07:00, sent exactly once through Moonraker port 7125:
  `PURGE_AND_CLEAN PURGE_TEMP=230 PURGE=40 TEMP=150 RETRACT=0.8`.
  CLEAN_Z and WIPES used the revised shared defaults, 0.2 and 3.
- At 20:20:23 the nozzle was at X315/Y10/Z6, 227.85 C with target230.
  At 20:20:41, E39.2 matched purge40 minus retract0.8, target150 and fan70%.
  At 20:21:09 the warm helper had returned to Z15 and fan100% was cooling
  for the final pass.
- The complete request, including M400, returned `ok` at 20:21:20 +07:00.
  T0 was parked at X315/Y1/Z6. The operator can assess actual contact and blob
  detachment; the API completion does not prove those physical outcomes.
- Turned off T0 heating after completion. Final snapshot: Klipper ready, print
  standby, active/detected T0, zero offsets, heater target0, bed target0 and
  part fan0. No additional purge, dock or retract was sent.

Compact API evidence is retained in `samples-v2.jsonl`, `after-v2.json`,
`clean-v2.gcode` and `clean-v2-result.json` beside this report.

## Per-print material integration and revised purge point

After the first trial, the operator requested X315/Y5/Z5 and hot purge before
every print, followed by cooldown to150 C. PRINT_START now always requests
PURGE40 and receives dedicated `T0_PURGE_TEMP` and `T0_MATERIAL` metadata from
Orca's T0 filament preset. `Tn_TEMP` still names only the tools used by the model;
the cleaning-only T0 metadata does not add T0 to prime lines.

The printer has neither a material sensor, a saved material registry nor Spoolman.
The physical spool must match the T0 preset selected in Orca, even for T1-only
prints. Temperature is read from that preset, rather than inferred from the
initial printing tool or from a fixed polymer temperature table. Missing T0
temperature in an older non-T0 job is rejected before heating or motion; reslice
with the updated machine start code. T0_TEMP and TOOL_TEMP for TOOL=0 remain
compatible fallbacks. The accepted purge temperature range remains170–280 C.

This use of the indexed T0 temperature follows the
[official OrcaSlicer placeholder documentation](https://www.orcaslicer.com/wiki/developer_reference/built_in_placeholders_variables).
The active AppData machine profile, repository profile and analysis alias are
synchronized. Existing G-code is not changed by editing a slicer preset.

The indexed values were also checked against the
[OrcaSlicer v2.4.2 source](https://github.com/OrcaSlicer/OrcaSlicer/blob/v2.4.2/src/libslic3r/GCode.cpp#L2813-L2815):
temperature vectors remain separate from the used-tool mask. A fresh T1-only
reslice was not completed because the available portable installation lacks its
runtime DLL. Source inspection and offline macro tests confirm the contract;
a new sliced job has not been physically printed during this change.

## Second attended trial: X315/Y5/Z5

- Live CFG backup: `/home/voron/printer_data/config_backups/pre-t0-per-print-material-purge-20261015-203044-q14dwjt1`.
- Both CFGs matched their expected previous hashes before replacement and their
  new hashes afterward. Reload and G28 succeeded; queried runtime geometry was
  X315/Y5/Z5, with active/detected T0, zero offsets and a clear mesh.
- At 20:31:37 +07:00, sent one `PURGE_AND_CLEAN` request with PETG230,
  PURGE40, TEMP150 and RETRACT0.8, using default Z0.2 and three passes.
- Samples show X315/Y5/Z5 during purge; at 20:32:13, E39.2 confirmed the
  purge/retract amount. At 20:32:22, target150/fan70% confirmed cooldown;
  at 20:32:41, the warm helper was completing its wipe/vertical departure.
- The request including M400 returned `ok` at 20:32:59 +07:00. Turned off
  T0 heating afterward. Final state: ready/standby, detected/active T0, bucket
  X315/Y1/Z6, heater target0 and fan0. No full PRINT_START/print job was run.
- `samples-v3.jsonl`, `after-v3.json`, `clean-v3.gcode` and
  `clean-v3-result.json` retain the API evidence. Actual silicone contact and
  blob detachment remain for the operator to assess.
- The four updated Oxplow PETG single-tool G-code/report pairs were also copied
  into the printer's `gcodes/Oxplow-2.3.2` directory after backup and drift checks;
  no calibration print or offset change was started.
