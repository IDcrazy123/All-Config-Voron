# Proposal: sharing existing CFG files individually

Date: 2026-10-09. Status: revised proposal; this task changes documentation only.

## Agreed scope

Prepare existing CFG files so someone with a similar, working StealthChanger can receive one file, add its include and change the few parameters that differ on their machine. They should not need our repository, hardware profile, installer or a new configuration framework.

The user's clarification supersedes the earlier design: **keep parameters in their actual owning sections or points of use and explain changes beside those lines**. Do not collect parameters into an EDIT HERE block, global profile, new configuration macro or override hierarchy. Existing macro variables stay in their existing macro; native pins, tool definitions and calibration stay in native sections. This is the agreed ownership/layout requirement, not a claim that every existing macro-variable block is inherently unsafe.

Keep file names and public macro names where practical. Limit logic changes to real tool-count/name assumptions, accidental project dependencies and confirmed defects. There is no need for a generated library, SC namespace, manifest framework or package installation.

The receiver reads the header, compares the annotated machine-specific settings, includes the file and calls the existing macro. Matching settings can remain after comparison. Measured values do not become universal defaults merely because a CFG is easy to download.

## Changes inside each file

1. Add a short header: purpose, supported Klipper/KTC/probe/runtime setup, existing macros, include line, whether the file heats/moves/changes tools, genuine dependencies and conflicts.
2. Add comments beside each machine-specific setting: units, coordinate frame, function, how to obtain a replacement and which other settings must agree.
3. Enumerate the actual KTC tools and configured extruder/fan associations. Do not require editing five-element lists or introduce another tool_count owner.
4. Keep essential feature helpers/callbacks in the file. Remove accidental dependencies on our project and guard optional visual/status calls before object access.
5. Preserve attachment, homing, temperature, contact, mesh/offset and operation-state checks. Missing enabled safety equipment must not silently become a no-op.
6. Explain the call site: whether the include enables the feature or the receiver adds a macro call to their own start/end/slicer sequence.

Comments alone suffice for already independent files. Logic changes are necessary for unconditional missing-object reads, inferred tool names and actual defects. Review these as focused changes, not a whole-project redesign.

## Comment examples at the actual owner

Illustrative excerpts only; these are not complete CFGs or new parameters. Shown values already exist on our machine.

```ini
# Inside the existing CLEAN_NOZZLE macro:
# This machine uses G-code Z15 for XY transfers over the silicone station.
# Verify the complete transfer route and approach/contact clearance on your printer.
variable_safe_z: 15.0

# This machine's purge X in G-code mm, paired with purge_y and purge_z.
# Replace with your measured bucket point and check nozzle/dock clearance.
variable_purge_x: 315.0
```

```ini
# Inside the existing toolchanger settings:
# Absolute G-code Y in mm for this machine's initial dock approach.
# Replace after checking your dock entrance and every pickup-path point.
# This is not a distance from safe_y or park_y.
params_close_y: 30
```

The cleaner's contact range is checked in both CLEAN_NOZZLE and _CLEAN_NOZZLE_WIPE_PATH. Comments at the contact setting and both guards must identify this relationship. Changing default_clean_z alone must not bypass those checks. A different brush mechanism requires a reviewed contact contract.

Prefer “Replace with your measured X/Y; also verify these checks” over “change for your printer”. Distinguish mm/s from G-code mm/min, filament length from volume, physical position from G-code position and board pins from MCU section names. Label comment numbers as examples/current-machine values; do not create duplicate editable owners.

## File-by-file proposal

Each row concerns an existing file. Eligibility is conditional on completing its changes and tests; these files are not all standalone today.

| Existing file | Focused changes for sharing | Receiver edits / remaining requirements |
| --- | --- | --- |
| prime-lines.cfg | Keep PRIME_LINES/helper together, enumerate real tools, preserve configured standby lookup; explain slot/wipe bounds and start-sequence call. | Existing prime geometry/extrusion variables; reserve printable space and mesh/wipe clearance. Compatible KTC selection/heating, tools and job temperatures. |
| tool-temp-bench.cfg | Keep state/timer/stop macro; remove unconditional cleaner/dryer/private-state reads and unguarded LEDs. Parking disabled must not read station geometry or move there. Retain equivalent operation guards; correct old T0–T4 header examples. | Temperature/time call parameters; positioning code only if station parking is used. KTC/heater mapping and native print/pause state; declare docked-tool heating restrictions. |
| nozzle-clean.cfg | Keep purge/wipe/park helpers; annotate geometry in place, guard visual calls and replace private-state coupling with equivalent safety checks. Resolve fan/heater association where valid; document [gcode_arcs] conflict. | Existing brush/purge/transit/contact settings and guards. Initially retain T0 silicone-pad, zero-offset/no-mesh and declared KTC/QGL/probe contract. Other brush types are not automatically compatible. |
| filament-dryer.cfg | Keep start/stop/status/timer; optional LEDs; remove mandatory benchmark/LED-state coupling while protecting present operations. Review bed_fan_off_delay ownership: essential callbacks belong here or get equivalent reviewed behavior. | Fan/sensor names at uses, material presets beside each branch, parking beside its code or existing PARK=0. Actual hardware and measured enclosure/spool limits; no fabricated safe feedback when required sensors are absent. |
| test-speed.cfg | Retain names; fix unsupported Z commands, restore prior runtime limits/detector state and add busy/input guards. Declare leveling/kinematics requirements. | Existing test envelope/clearance/request parameters within configured limits. Attended diagnostics; not ready as-is until defects are fixed. |
| tool-crash.cfg | Keep wrappers/handler; state required Python runtime/patch. Optional LEDs remain optional; detector failures are explicit. Describe integration with the receiver's recovery flow. | Detection inputs stay in their tools; review timings/pause/resume/cancel compatibility. Crash cancel must not implicitly park XYZ. |
| input-shaper.cfg | Comment measured native values in place; identify optional resonance_tester/ShakeTune dependencies. Explain effective KTC after-change selection and damping mismatch. | Own frequencies/types/damping and resonance setup. This CFG alone cannot fix a hook selecting another profile. |
| fans-leds.cfg | Label combined hardware/LED/state/RESUME/cancel integration accurately. For LED-only sharing, extract a reviewed ordinary CFG with the requested feature/helpers, without a global settings layer. | Hardware in native sections, LED names/indexes at uses. Recovery hooks only after compatibility review; full file is not harmless LED support. |
| print-macros.cfg | List dependencies/call order; keep QGL/probe/clean/prime choices at existing sections/call sites. Fix lifecycle Z/recovery issues before claiming portable use. | Own geometry/start/end calls and compatible feature setup. Share as integration/reference or selected macro excerpts until dependencies are reduced. |
| calibration-probe.cfg | Explain native probe/mesh/twist and Axiscope portions in place; document conflicting owners, duplicate switch inputs and final-T0 ordering. | Own probe geometry/pins/points/transit and calibration results. Same supported backend; final-toolchange issue blocks ready-to-use calibration claims. |
| toolchanger-config.cfg | Annotate docks/corridors/paths at their owners; list hook dependencies, later overrides and include order. Preserve managed readonly files. | Measured dock/path values and supported hooks. Similar mechanism does not imply identical coordinates. |
| tools/Tn.cfg | Explain native MCU/extruder/fan/tool/runout/LED sections and names that must agree. Generic features must not require all five of ours. | Own UUID/pins/tool number/names/dock/calibration. Matching board/wiring; include only physically installed tools. |
| hardware.cfg / printer.cfg | Retain as annotated machine references; do not require replacing working hardware to install a feature. | Own wiring/travel/drivers/heaters/calibration. These are not standalone convenience macros. |
| readonly-configs/*.cfg / mainsail.cfg | Preserve upstream ownership; document installed dependencies and supported user-owned hooks. | Compatible upstream runtime; these are not our files to redesign. |

## Real and accidental dependencies

Prime lines should not require our dryer/LED file. A benchmark should not require the whole cleaner just to render its template. Essential helpers belong with their feature; optional visual effects must not import the rest of our project.

Real dependencies remain explicit: tool_crash.cfg needs its Python plugin; Axiscope calibration needs Axiscope. If a file still genuinely needs another CFG, list it and classify it as an integration/reference until independent. Do not promise one-file use while silently requiring the rest of the repository.

Replacing private-state coupling requires a tested equivalent contract based on actual native state and present operation providers. Cover preparation, pause, conflicting heating/calibration and delayed callbacks. Required checks cannot disappear merely to allow an include. A CFG cannot automatically coordinate arbitrary unregistered third-party operations.

Keep names unless a real collision requires a change. Headers must identify overrides such as RESUME/M109 and warn against duplicate definitions. Installing a feature must not unexpectedly replace the receiver's homing, pause, cancel or lifecycle.

## Tool count and physical position differences

Generic helpers iterate two tools on a two-tool machine and six on a six-tool machine. Resolve names through the registry and reject unknown numbers/missing required heaters. Do not introduce another registry or infer a list index/object suffix from the number.

Physical positions remain where the consuming section/code owns them. Add local comments at the actual dock, cleaner, prime, probe and parking values. Do not scale brush Z or docks from bed dimensions. Axis travel includes off-bed areas; prime needs a verified reserved printable region, including sideways-wipe clearance.

T0 remains an explicit restriction where required by the backend/reference-nozzle contract. A six-tool machine retaining T0 may qualify; changing tool count does not make a no-T0 backend compatible. Generalizing that contract is a separate implementation and validation task.

## Acceptance before calling a file independently usable

- Load/render with only its declared native/KTC/runtime prerequisites, not the whole project.
- Test two/five/six-tool and alternate-name fixtures; distinguish simulated from physical checks.
- Remove optional LED/cleaner/dryer files and verify there are no unconditional reads/calls.
- Compare command sequences and measured settings on our machine; preserve behavior except reviewed fixes.
- Check busy states, missing required dependencies, offsets/mesh, near-max-Z and cancellation/callback ownership where applicable.
- Confirm every recipient edit is documented beside the actual parameter/name/call site; no hidden helper installation or loop editing.
- Validate header/include/call examples and comments; commission changed motion/thermal/recovery behavior while attended.

The earlier 14 tests validate audit changes, not the independence proposed here. This task edits documentation only.

## Implementation order

1. Add accurate headers/local comments and identify real prerequisites, conflicts and machine-specific edits. Preserve section order and production values.
2. Make prime-lines.cfg and tool-temp-bench.cfg independent with focused changes, existing macro names and required guards.
3. Reduce accidental dryer/cleaner dependencies; review callbacks, contact limits and operation ownership.
4. For combined files, share the integration with explicit requirements or extract just the requested feature into an ordinary self-contained CFG. No restructuring of the recipient's project is required.
5. Fix lifecycle/recovery/calibration/diagnostic defects before advertising those workflows as portable. Multi-tool EXCLUDE_OBJECT remains unfixed; CAN T1 is fixed according to the operator.

The deliverable is an ordinary CFG sent directly, with justified dependencies and comments at the few machine-specific edits. No central parameter block, global profile, new naming convention, generator or whole-project installer is required.

## Related evidence

- [Production audit](project-audit-2026-10-09.md): current defects and runtime/config evidence.
- [Machine adaptation worksheet](machine-adaptation.md): existing input owners, not a required profile.
- [Klipper command templates](https://www.klipper3d.org/Command_Templates.html): evaluation and command-state rules.
- [Klipper configuration reference](https://www.klipper3d.org/Config_Reference.html): native sections/options.
