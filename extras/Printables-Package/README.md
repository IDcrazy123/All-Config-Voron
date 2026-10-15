# Oxplow 2.3.2 — Voron production integration

Source: [Universal Oxplow First-Layer Z-Offset Calibration by Công Dương](https://www.printables.com/model/1846885-universal-oxplow-first-layer-z-offset-calibration).
Method credit: Maxim7745. The exact published toolkit is preserved under
`upstream-2.3.2/`, including its SHA256 manifest, attribution and upstream
Vietnamese documentation. The root Python file launches that toolkit unchanged.

## Installed runtime and machine contract

`../../config/Printer-Setup/oxplow_runtime.cfg` is included once by `printer.cfg`.
It retains the published runtime logic and adds a local purpose/loading/usage guide
in its leading comments. Check installation without motion or heating:

```gcode
_OXPLOW_CHECK VERSION=2.3.2 STAGE=install
```

`profiles/` contains seven profiles for this repository's exact machine: PETG
T0–T4 together, ABS T0–T4 together, and each PETG tool separately. PETG uses
230/70 C; ABS uses 250/100 C, from the existing repository material baseline.
`reviewed=true` records the reviewed machine/macro contract, not a new physical
calibration or a promise of compatibility with other machines.

PRINT_START owns home, QGL, Cartographer mesh and prime. Its initial printing
tool retains 0.6 mm retract; other primed tools retain 5 mm. The generator
recovers exactly that amount once after pickup at the first printed point.
PRINT_END owns the last tool's retract and lift. Intermediate patch retract
remains 0.6 mm. Saved tool offsets are reference guards and are never applied
twice. No offset, PID, motor current or motion limit is changed by this package.

## Use

From this directory, validate the exact profile against your printer:

```bash
python generate_oxplow_gcode.py validate --profile profiles/voron-350-petg-T0.json --url http://YOUR_PRINTER:7125
python generate_oxplow_gcode.py generate --profile profiles/voron-350-petg-T0.json -o local/T0-new.gcode
python generate_oxplow_gcode.py calculate --report local/T0-new.report.json --tool 0 --row 35
```

The generator refuses to overwrite output. `local/` and `*.local.json` are
ignored by Git; keep private discovery snapshots and measurements there.
Checked-in `output/` files are machine-specific examples generated from the
tracked profiles, accompanied by SVG previews and reports. Start with a single
tool and supervise the print. Regenerate after changing the prime contract,
stored tool offsets, nozzle, material or start/end macros.

## Read the patch

Patches have no printed text, ticks or extra purge line. Tool IDs increase from
left to right. Row 0 is the lowest Y/front edge. For these profiles Z decreases
from 0.280 to 0.200 mm over 51 rows; row 25 is nominal Z0.240.
Use the report belonging to that exact G-code. The historical
`(distance - 10) * 0.010` formula does not apply to these files.
See [the current method](Oxplow-Z-Offset-Comprehensive-Method.md) and the
[upstream guide](upstream-2.3.2/README.md).

## Source and verification

Published ZIP SHA256:
`65d3eb72920723a4897ae9612641962c117fa14992b111b98c8097ab8d8b484d`.
The vendor manifest covers 22 original files; project profiles/outputs are
outside that upstream release. The live runtime was already 2.3.2 before this
integration. All pre-integration working files are retained in `legacy-v2.0.0/`
and the timestamped backup; they are not current print files.

To run upstream software tests, change into `upstream-2.3.2/` and run
`python -m unittest discover -s tests`. The optional dispatcher tests require
`OXPLOW_KLIPPER_SOURCE` pointing to the reviewed Klipper `klippy` source directory.
Published licensing/attribution statements remain in
`upstream-2.3.2/docs/PROVENANCE.md`; no new license is asserted here.

Every integration change and its cause is recorded in [INTEGRATION.md](INTEGRATION.md), including the source documentation reference that still names runtime 2.1.0.
