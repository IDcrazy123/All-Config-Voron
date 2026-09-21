# OrcaSlicer Production Profiles

[English](README.md) | [Tiếng Việt](README.vi.md) | [Project overview](../README.md)

This directory mirrors the active OrcaSlicer user profile selected from `%APPDATA%\OrcaSlicer\user`. On 2026-09-20 the selected profile ID was `838ce884-12ee-416b-9e1b-1c7503cf6b5f`; 18 JSON files were validated and synchronized.

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

- `Voron Stealthchanger.json`: all five `z_hop` values changed from `0.6` to `0.4` mm, matching the active Orca profile.
- `0.20mm PETG.json`: synchronized the active Orca 2.4.0.2 process override, including painted brim, 6 s preheat, 10 mm tower brim, 40 mm prime tower, 40 mm³ prime volume, and 50 mm³/s maximum tower purge speed.
- Analysis aliases under `extras/Orcasilcer setting/` now mirror `Voron Stealthchanger.json` and `0.20mm Multicolor PetG.json`.

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
