# OrcaSlicer Production Profiles

[English](README.md) | [Tiếng Việt](README.vi.md) | [Project overview](../README.md)

This directory mirrors the active OrcaSlicer user profile selected from `%APPDATA%\OrcaSlicer\user`. On 2026-09-27 the selected profile ID was `838ce884-12ee-416b-9e1b-1c7503cf6b5f`; 19 JSON files were validated and synchronized.

## Active inventory

Machine profile:

- `Voron Stealthchanger.json`

Process profiles:

- `0.20mm ABS.json`
- `0.20mm Multicolor PetG.json`
- `0.20mm PETG.json`

Filament profiles:

- `ABS Tpoimns Black.json`
- `ABS Tpoimns Pink.json`
- `ABS-Pro Tinmory Black.json`
- `PETG Bambu Basic Black.json`
- `PETG Bambu Basic White.json`
- `PETG Kabber Blue.json`
- `PETG Noname Antums.json`
- `PETG Tinmory Black.json`
- `PETG Tinmory.json`
- `PETG TPoimns Black.json`
- `PETG TPoimns Gray.json`
- `PETG TPoimns Orange.json`
- `PETG TPoimns Red.json`
- `PETG TPoimns White.json`
- `PETG TPoimns Yellow.json`

Six repository-only legacy presets were removed during the 2026-09-20 audit after confirming that no active profile inherited from them. Their original bytes remain in the dated pre-audit backup and Git history.

## Latest synchronized changes

- Synchronized the complete active profile state changed on 2026-09-26, including the 0.15 mm Spiral Lift setup, retraction/tool-change values, process overrides, and the new `PETG Bambu Basic White.json` preset.
- `Voron Stealthchanger.json`: reset all five `retract_restart_extra` values from 0.2 mm to 0, and enabled 0.5 s overhang-only fan lead time.
- `PETG Kabber Blue.json`: changed the no-cooling window from three inherited layers to two, allowing overhang cooling on physical layer 3.
- `0.20mm Multicolor PetG.json`: enabled small-perimeter handling with a 5 mm threshold and 30 mm/s speed.
- An isolated OrcaSlicer 2.4.2 reslice of `RoboOctopus_4Color.3mf` confirmed all 88 Arm1–Arm8 layer-3 restarts now use `E0.5` instead of `E0.7`, with T1 cooling active at 10%/90%.
- Analysis aliases under `extras/Orcasilcer setting/` mirror `Voron Stealthchanger.json` and `0.20mm Multicolor PetG.json`.

## Synchronization

Review-only sync (updates files and writes a journal entry, but does not commit or push):

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass `
  -File ".\Orca Config\Sync-OrcaProfiles.ps1"
```

One-click sync, scoped commit, and push:

```text
Orca Config\Sync-OrcaProfiles.cmd
```

The script selects the most recently edited Orca user profile unless `-ProfileId` is supplied. It parses every machine/process/filament JSON, rejects duplicate flat destination names, copies only changed bytes, backs up replaced files, refreshes the two analysis aliases, and records the operation in the daily journal.

Useful switches:

| Switch | Behavior |
| --- | --- |
| `-ProfileId <id>` | Select an explicit Orca user directory |
| `-SkipAnalysisAliases` | Do not update the two files under `extras/Orcasilcer setting/` |
| `-IncludeDiagnostics` | Include changed G-code/log diagnostics in the scoped commit |
| `-Commit` | Stage only synchronization-owned paths and commit |
| `-Push` | Implies `-Commit`, then pushes the current branch |

The synchronizer intentionally does not delete repository JSON files that disappear from AppData. Review inheritance and references before manually retiring a preset.

## Restore to OrcaSlicer

Close OrcaSlicer. Copy the machine JSON into `machine`, process JSON into `process`, and filament JSON into `filament` under the intended profile ID:

```powershell
$profile = Join-Path $env:APPDATA 'OrcaSlicer\user\<profile-id>'
Copy-Item '.\Orca Config\Voron Stealthchanger.json' (Join-Path $profile 'machine')
Copy-Item '.\Orca Config\0.20mm Multicolor PetG.json' (Join-Path $profile 'process')
Copy-Item '.\Orca Config\PETG Bambu Basic Black.json' (Join-Path $profile 'filament')
```

After opening OrcaSlicer, verify the printer, process, five filament assignments, tool count, start G-code, and prime-tower settings before slicing a production job.
