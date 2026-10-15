# Integration changes and their causes

Source: the published Oxplow 2.3.2 ZIP from [Printables](https://www.printables.com/model/1846885-universal-oxplow-first-layer-z-offset-calibration).

No generator or runtime algorithm was modified. All 22 files covered by the
upstream manifest remain byte-identical under `upstream-2.3.2/`.
`config/Printer-Setup/oxplow_runtime.cfg` retains the published executable
content and adds a local usage guide in its leading comments (2026-10-15).
The standalone source project has not been edited.

| Change in this repository | Cause | Action in the original project |
| --- | --- | --- |
| Add separate `T0_PURGE_TEMP=230 T0_MATERIAL=PETG` to the single T1-T4 machine profiles and regenerate their matching artifacts | PRINT_START now purges/cleans T0 for every print; an unused T0 needs its own loaded-filament metadata without joining the printing/prime mask. The operator confirmed PETG in T0 at 230 C | None to generator/runtime logic; update the local machine profile's start-macro arguments when that printer contract or loaded T0 filament changes |
| Add production CFG file guides | User requested purpose/loading/usage/setup help when opening each file; Oxplow also documents each runtime stage | Optional documentation improvement in the source CFG; runtime/generator logic and version are unchanged |
| Install runtime under `config/Printer-Setup/`; include that path once | User preference and this repository's macro directory layout | None to runtime code; its install documentation may show that any included config directory works |
| Recover 5 mm for primed/parked tools, 0.6 mm for the initial printing tool | PRIME_LINES dock retract changed from 1.8 to 5 mm; KTC pickup does not unretract | Update the machine's own profile after its macro changes. Do not change the toolkit's universal/default assumptions or every example to 5 mm |
| Keep seven machine profiles separate from the upstream examples | Bed region, temperatures, macro arguments and saved offsets are specific to this Voron | None; examples must remain `reviewed=false` |
| Preserve the existing Z0.280 -> Z0.200 patch-only geometry and PRINT_END ownership | The machine's latest 2.3.2 report already defines the tested-file geometry and final retract/lift contract | None; generator already supports this contract |
| Use a root launcher for the unchanged vendored CLI | Makes the repository entry point easy to find while keeping published checksums verifiable | None to upstream CLI |
| Retire 2.0.0 files and update old reading guides | Old files had annotations, the opposite ramp direction and a different formula | Update any old links/documentation still pointing to that retired version; do not use its formula on a 2.3.2 report |

## Source documentation finding

`upstream-2.3.2/profiles/ktc-prime-lines.example.json` still says
`Use oxplow_runtime.cfg 2.1.0 ...` in its notes. The actual release and runtime
are 2.3.2, and generated G-code requires a matching runtime version. Update
that note in the original source to the current version, or use wording such
as "Use the runtime from the same toolkit release" to avoid stale version text.
This is an outdated documentation reference, not a defect in the runtime.

The example's `initial_retract=1.8` is an explicitly unreviewed contract example;
it is valid for a machine that leaves 1.8 mm retracted. Its mismatch with this
machine's new 5 mm setting is solved in the Voron profile, not by hardcoding
5 mm into the original generator.

## Evidence

- ZIP SHA256: `65d3eb72920723a4897ae9612641962c117fa14992b111b98c8097ab8d8b484d`.
- The standalone source Python matches the published ZIP byte-for-byte.
- 96 upstream tests pass, including four dispatcher tests against reviewed
  Klipper commit `7bc4d0946`; no skipped tests in the completed run.
- All seven profiles pass static and live read-only prerequisite validation;
  generated G-code is audited for limits, geometry and extrusion.
- Each tool has exactly one initial-retract recovery; T0–T4 multi-tool recovery
  is 0.6/5/5/5/5 mm. Single-tool files recover 0.6 mm even for T1–T4.
- SVG inspection confirms five separate patches ordered T0 to T4.
- No physical calibration print or persistent offset change is performed by
  this integration.

## 2026-10-15 start-macro contract update

The four PETG single-tool T1-T4 profiles now include separate cleaning metadata
for the operator-confirmed T0 PETG at 230 C. Their model/printing-tool material
does not determine unused T0 filament. Changing the loaded T0 requires updating
`T0_PURGE_TEMP` and `T0_MATERIAL` in these machine profiles and regenerating the
matching G-code, SVG and report. No T0 printing tool or `T0_TEMP` was added.
The all-tool ABS profile still expects ABS loaded in T0-T4 at 250 C; a machine
with PETG in T0 does not match that profile's printing-material contract.

The upstream generator already supports arbitrary reviewed `start_gcode` macro
arguments. A missing machine-specific argument is a local integration mismatch,
not a defect requiring a source-project or toolkit-version change. Static and
live prerequisite checks do not execute PRINT_START or infer filament identity.

Regenerate with the unchanged launcher, choosing a new output directory because
the CLI refuses to overwrite an existing artifact set. For example, from this
directory:

```bash
python generate_oxplow_gcode.py validate --profile profiles/voron-350-petg-T1.json
python generate_oxplow_gcode.py generate --profile profiles/voron-350-petg-T1.json -o local/contract-20261015/Voron_Oxplow_2.3.2_PETG_T1.gcode
```

Repeat for T2, T3 and T4, review the generated audit and paired report hashes,
then replace the owned `output/` files only after backing up the previous set.
The regenerated four patches retain the same geometry, Z rows, extrusion,
tool selection, 0.6 mm initial recovery and PRINT_END ownership. Only their
start-macro contract, profile digest and embedded report metadata change.
