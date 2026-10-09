# Proposal: independently reusable StealthChanger CFG modules

Date: 2026-10-09. Status: design proposal; the module layout, names, settings and commands below are not implemented interfaces.

## Intended result

A user with a working StealthChanger should be able to select a feature, download its CFG, edit one clearly marked settings block, add one include, run a read-only check, and commission that feature. Changing from five tools to two or six must not require editing macro loops. A user adopting only a heat benchmark must not also install our cleaner, dryer, LEDs, Cartographer, Axiscope or complete print workflow.

This requires both a software refactor and a distribution/documentation contract. More comments alone cannot remove required printer objects, macro overrides or assumptions about physical contact. Conversely, extracting every setting into one mandatory global profile would make individual files harder to share.

The proposed first supported backend is **KTC-Easy**, matching this repository. StealthChanger describes the mechanism; it does not establish that every installation has the same Klipper plugin/API, homing routine or calibration backend. Other backends should receive explicit adapters and a tested compatibility statement, not a claim of universal support.

The existing `config/` remains the measured production profile during development. New designs belong outside that deployment payload until validated. This proposal changes documentation only.

## What currently prevents individual-file reuse

These examples come from the current code, including the changes in the [2026-10-09 audit](project-audit-2026-10-09.md):

| Current coupling | Why a downloaded CFG is insufficient | Proposed boundary |
| --- | --- | --- |
| `tool-temp-bench.cfg` reads `CLEAN_NOZZLE`, `_DRYER_STATUS`, `_PRINT_STATE` and LED helpers | Even `PARK_BUCKET=0` currently reads the cleaner station before the branch; those other files are still required | Benchmark owns its optional park inputs and local state. An explicitly enabled integration can reuse cleaner geometry. LED/dryer interaction is optional and checked before lookup. |
| `filament-dryer.cfg` reads benchmark/private state and calls drying LEDs | Sharing the dryer alone leaves missing objects/commands | Local dryer state and native print/pause checks are required; optional integrations are presence-checked. No toolchanger motion is enabled merely because the object exists. |
| `fans-leds.cfg` contains pins, fans, LEDs, `_PRINT_STATE`, RESUME and cancel cleanup | Installing LED support can replace recovery behavior and import unrelated hardware | Separate hardware definitions, LED behavior, fan behavior, operation state and Mainsail integration. |
| `print-macros.cfg` contains QGL geometry, idle policy, exclude-object registration and a Cartographer/T0 workflow | A different bed/probe/reference tool requires changes throughout the file | Lifecycle orchestration calls explicitly selected leveling/probe/clean/prime adapters; hardware geometry and host policies remain owned elsewhere. |
| Cleaner requires T0/`extruder`, zero offsets, no mesh and a measured silicone contact envelope | A name change alone does not transfer the mechanical/thermal contract | Reference-tool mapping plus a separately commissioned station profile; retain contact/offset/mesh checks. Provide a distinct silicone-pad implementation first. |
| KTC include glob loads `tools/T*.cfg`; tool files also contain MCU, heater, fans, LEDs and runout | Copying all five files registers five tools, even if the receiver has fewer | User owns the active tool definitions. Share board templates and a per-tool worksheet; generic features enumerate the actual registry. |
| `toolchanger-config.cfg` supplies hook overrides for motion, calibration, shaper and recovery | One dock setting file brings unrelated integration choices and ordering requirements | Keep measured dock/path settings apart from feature hooks and backend-specific calibration/recovery adapters. |
| `input-shaper.cfg` includes resonance testing and ShakeTune | A user wanting shaper selection inherits optional analysis plugins | Separate measured shaper values, profile selection and optional resonance/ShakeTune setup. |

## Architecture and distribution

Use feature-local configuration for independent files and optional machine-local overrides for users who adopt the whole package. Hardware definitions are not replaced by macro variables.

Proposed repository layout, outside production `config/` initially:

```text
extras/reusable-stealthchanger/
  src/                         Authoritative feature source and export fragments
  modules/                     Generated, individually includable feature CFGs
    sc-prime-lines.cfg
    sc-tool-temp-bench.cfg
    sc-silicone-clean.cfg
    sc-filament-dryer.cfg
    sc-bed-fan.cfg
    sc-status-leds.cfg
    sc-shaper-selection.cfg
    sc-motion-diagnostics.cfg
  integrations/                Explicit macro/backend ownership
    sc-print-lifecycle.cfg
    sc-mainsail-hooks.cfg
    sc-tool-crash-ktc.cfg
    sc-calibration-axiscope.cfg
    sc-probe-cartographer.cfg
  templates/                   Hardware templates, not ready-to-run defaults
    tool-ebb36-v1.2.cfg.example
    manta-m8p-v2.cfg.example
  examples/                    Annotated 2-tool / 5-tool / 6-tool include layouts
  docs/                        Per-module install and commissioning guides
  manifest.json                Version, exports, conflicts and dependency contracts
  tools/                       Export/check scripts; not needed to run a CFG
```

One exported feature CFG contains its settings, public macro, private helpers and delayed callbacks. It must not require an undocumented common CFG or Python generator at runtime. Klipper/KTC and stated native sections remain legitimate dependencies. Larger integrations can be distributed as a small documented set; hardware templates must be labelled as templates.

Small validation/mapping fragments may be shared at build time and emitted with module-specific private names. Exported files are generated from one authoritative source; CI rejects differences from regeneration. Do not maintain a standalone copy and a package copy by hand. Keep any module license/source notices and verify redistribution permission for third-party code before embedding it; prefer declaring external runtimes instead of copying them.

Offer two adoption paths:

| Path | User edits | Includes and updates |
| --- | --- | --- |
| One feature | The CFG's top settings block | Include that CFG once. Preserve the block when updating; show a settings migration diff if its schema changes. |
| Multiple features | A machine-local variable override file for the selected modules, plus hardware owners | Include modules, then the documented overrides. Validate effective options and include order. Updates replace only selected library files, retaining local overrides. |

Variable-only override sections need tests against the supported Klipper config reader. They must not repeat `gcode`, `rename_existing`, hardware pins or `SAVE_CONFIG` values. Never ship two active copies of the same module or combine a flattened bundle with its individual modules. The checker should report duplicate public/private names, repeated delayed IDs and override chains before restart.

## Tool count and tool identity

1. Derive tool count from KTC's paired `tool_numbers`/`tool_names` registry. Do not introduce a second `tool_count` setting that can disagree with included tool definitions.
2. Map a registered number to its corresponding section, then read that tool's configured extruder/fan. Never infer these from `extruderN` or `Tn_part_fan`. Validate against actual Klipper objects; mapping does not permit arbitrary unsupported heater-section names.
3. Permit a sparse registry in generic helpers. Every selectable number must have a working selection entry point in the supported backend. Reject an empty registry or unknown tool before emitting commands.
4. Add an explicit `reference_tool` setting only to workflows needing a reference nozzle. Default it to an unset value in a distributable profile. T0 remains required where an installed external runtime hardcodes T0; reject incompatible settings until that backend is adapted.
5. Read used tools/temperatures from the job and the actual registry. Preserve the existing `Tn_TEMP` interface through a compatibility adapter; do not emit fixed T0–T4 slicer clauses in the generic implementation.
6. For a two-tool machine, only its two tool definitions belong in the active KTC include glob. Unused examples use `.cfg.example` and stay outside active globs. Adding a sixth tool requires a real hardware/tool definition and slicer array entry, but no change to reusable macro loops.
7. Tool-specific LED/sensor/standby inputs are optional metadata with their own owner. Do not duplicate UUIDs, detection pins, heater limits or calibrated offsets in a second macro dictionary.

First release should retain the current backend's reference-T0 limitation where necessary. Removing every T0 restriction is a separate backend integration task, not a string replacement.

## Settings and motion contracts

Use three input categories, marked consistently in comments:

| Category | Examples | Default and validation policy |
| --- | --- | --- |
| DISCOVERED | Registered tools, heater `max_temp`, actual axis limits, active extruder | Read the authoritative runtime/config owner. Missing or inconsistent required data is an error. |
| USER_REQUIRED | Prime rectangle, cleaning contact area, reference tool, safe transfer route, park clearance | Use an unset sentinel and `configured: False`; no motion until complete. Validate against travel and module-specific constraints, then commission physically. |
| USER_OPTIONAL | Wipe count, status LEDs, measured soak duration, optional park use | Provide a documented behavior default, type/range and disable method. A default must not silently enable unmeasured travel or heating. |

Do not scale docks, brush/contact Z, probe locations or Z clearance from nominal bed dimensions. Axis travel limits include docks and off-bed areas; they are not the printable rectangle. Prime limits must describe a reserved printable region and its mesh coverage. Validate nozzle/probe coordinates with offsets and check the entire path, including sideways wipes and intermediate dock points.

Choose and document the coordinate frame for each operation. Convert/clamp in one frame; distinguish `toolhead.position`, G-code position and offsets. Every motion helper explicitly owns XYZ/E mode, feedrate, state save/restore and whether restore moves. Helpers that home, heat or change tools call a later-rendered helper to inspect the resulting state. A caller cannot read a command's new state in the same Jinja evaluation.

Provide a read-only `SC_<FEATURE>_CHECK` and `SC_<FEATURE>_HELP` in each export. CHECK reports effective inputs, detected tools, bounds, missing prerequisites and conflicts; it must not home, heat, probe, select tools or move. Do not call an execution with zero extrusion a dry run if it still moves. A separate, explicitly attended commissioning guide can describe movements after validation.

Do not declare success by silently clamping an impossible station/prime path. Report the setting, supplied value, allowed range and how to fix it. Known contact limits remain enforced; a different brush gets a different commissioned profile/implementation.

## Optional features and operational ownership

Optional features should be optional throughout the caller chain, not only at the include:

- **LEDs:** no LED object/helper lookup unless enabled and installed. Missing disabled LEDs have no effect on heating/motion; missing enabled LED mappings receive a clear check result. LED support never replaces RESUME.
- **Bed fan/chamber sensor:** name fields are explicit. A dryer requiring chamber feedback refuses operation when the selected sensor is missing. Never pretend a missing humidity field measures filament dryness.
- **Cleaner:** benchmark parking is off by default. Standalone benchmark has no cleaner dependency. Reusing cleaner coordinates requires explicit configuration, validates that provider, and reads it only in that enabled branch.
- **Dryer/benchmark state:** each module owns and exposes its own local status. Presence-checked interoperability refuses conflicting installed operations without requiring the other module. The full print integration checks these providers before heating. Operation ownership begins before the first preheat/wait and covers callbacks and cancellation.
- **Crash detection:** an enabled protection provider missing its runtime/patch is a hard error. Do not turn a missing safety dependency into a silent no-op. A crash flag directs pause/cancel to a reviewed no-XYZ recovery path until attachment is confirmed.
- **Calibration/probe/leveling:** select one implemented adapter explicitly. A feature using QGL requires QGL; it does not assume every StealthChanger is a Voron 2.4. Axiscope and other conflicting calibration owners must not be loaded together.

Guard native print/pause state in standalone diagnostics. Advanced coordination with other plugins is an integration contract: a CFG cannot prevent arbitrary manual G-code or guarantee cancellation cleanup after every interpreter error. Define stop/recovery commands and use guarded callbacks that cannot later switch off heaters owned by a different operation. State release/restoration must be tested on normal completion, abort and delayed callbacks.

## Names, overrides and compatibility

Export new library entry points with a `SC_` prefix and helpers with a feature-specific `_SC_` prefix. Keep delayed IDs/state names equally specific. A standalone file should not define or wrap `PRINT_START`, `PRINT_END`, `RESUME`, `CANCEL_PRINT`, `M104`, `M109`, QGL or the user's homing routine implicitly.

Preserve existing production/slicer names through explicit integration wrappers. List every wrapper's previous command, `rename_existing` chain and required include order. A user should be able to install prime lines without replacing print start. Existing Mainsail `_CLIENT_VARIABLE` options must be merged deliberately: hook conflicts should be reported, not overwritten by another shipped full client-variable block.

KTC's readonly configurations remain owned by KTC. Settings can be overridden only through supported user-owned includes/hooks. Selection, startup, shutdown and detector behavior should each have one active owner. Document the effective include graph and option precedence, including options supplied by later modules.

Each distribution includes a module version, settings schema, compatibility matrix, tested runtime revisions, required sections/commands, optional providers, public macros, hook/conflict list and migration notes. Initially use the inspected runtime revisions as the compatibility baseline and expand after tests. Do not describe an untested upstream version as compatible simply because it is newer.

## File-by-file transformation plan

All names in the target column are proposed exports, not files currently available to include.

| Current file | Proposed transformation / sharing unit | Minimum recipient inputs |
| --- | --- | --- |
| `printer.cfg` | Keep our complete production example separate; supply a short include-layout example for package adoption. Never distribute our SAVE_CONFIG as a generic profile. | Own hardware, kinematics, limits, include list and calibration; this is not a drop-in feature. |
| `hardware.cfg` | Board-specific annotated templates, separate from generic modules. Retain measured production owners. | MCU identity, wiring, directions, drivers, sensors, heater/verification, travel and measured currents. |
| `tools/T*.cfg` | One annotated board template and per-tool checklist. Separate optional LED/runout/accelerometer snippets; retain KTC tool/extruder ownership. | Registered number, supported object names, UUID/pins, extruder setup, detection, dock XYZ; own PID/offsets. |
| `toolchanger-config.cfg` | Separate dock/path settings from user-owned hooks, shaper selection, calibration and recovery integrations. | Measured dock paths/corridor, mechanism-specific clearances; selected integrations. |
| `readonly-configs/*.cfg` | Link to required upstream installation and document the user-owned include points. Do not refactor/vendor these managed files. | Compatible KTC installation and valid managed links. |
| `prime-lines.cfg` | First standalone candidate: `sc-prime-lines.cfg` with local geometry/check/help/helpers; neutral optional LED behavior. | Reserved prime rectangle, extrusion/retract recipe and safe transfer/first-layer contract. Tool count is discovered. |
| `tool-temp-bench.cfg` | `sc-tool-temp-bench.cfg`; remove unconditional cleaner/dryer/LED/private-state reads; default to no station travel; configure optional park independently. | Often no geometry input for a mounted tool measured in place; choose temperatures and confirm heating is permitted. Docked-tool heating requires an explicit safe-use policy. |
| `nozzle-clean.cfg` | `sc-silicone-clean.cfg`; explicit reference mapping, measured contact min/max and separate purge/transfer bounds. Move unrelated `[gcode_arcs]` to a package/native-config owner. | Brush/purge coordinates, contact envelope, allowed temperatures, transfer path, tool/offset/mesh contract. Generic brush types are separate later adapters. |
| `filament-dryer.cfg` | `sc-filament-dryer.cfg`; names/presets/parking exposed locally; default park off and material policy uncommissioned; no mandatory LED/benchmark file. | Bed/fan/sensor mapping, measured enclosure/spool limits and presets. Optional park coordinates only when enabled. |
| `fans-leds.cfg` | Split physical fans/lights into templates, `sc-bed-fan.cfg`, `sc-status-leds.cfg`, and `sc-mainsail-hooks.cfg`. Move print operation state into the lifecycle integration. | Real fan names or LED name/index map; native hardware definitions. Recovery hooks require a separate review. |
| `print-macros.cfg` | `sc-print-lifecycle.cfg` orchestrates existing modules through explicit adapters. Split idle policy, QGL geometry and exclude-object registration into owners. | Reference tool, probe/level/clean/prime choices, own bed/park settings and slicer temperatures. Full integration is a package, not a universal single file. |
| `calibration-probe.cfg` | Separate Cartographer setup, bed/QGL/twist geometry and Axiscope calibration integration. Correct final-T0 lift ordering before publishing its calibration workflow. | Installed probe/calibration backend, physical points/pins, safe routes and own measured results. |
| `input-shaper.cfg` | `sc-shaper-selection.cfg` plus separate native measured profile and optional resonance/ShakeTune setup. Select frequency/type/damping as one explicitly enabled profile. | Own shaper measurements; per-tool profile enablement if used. No copied 43.6/33.4 frequencies or damping defaults. |
| `tool-crash.cfg` | `sc-tool-crash-ktc.cfg` integration with explicit runtime/patch manifest and recovery contract. Sensor declarations stay with tools. | Compatible detector runtime, real detection inputs and chosen reviewed recovery routing. Detector timings must be commissioned. |
| `test-speed.cfg` | `sc-motion-diagnostics.cfg`; repair unsupported Z commands and restore actual prior limits/detector state; exclusive diagnostic mode. | Explicit test bounds/clearances, speed/acceleration within configured limits and attended operation. Not enabled as a startup task. |
| `mainsail.cfg` | Keep upstream-owned; distribute hooks separately, with conflicts and order documented. | Compatible native Mainsail macros and deliberately selected hooks. |
| Host `.conf` / installer / Orca | Host examples stay separate. Module installation selects explicit files instead of synchronizing our complete config. Slicer examples generate used-tool clauses from its tool list. | Own host paths/services, chosen modules and slicer printer/tool arrays. |

## Required comment format

Every exported CFG must contain, in this order:

1. Purpose, module/settings version and supported backend; whether it moves, heats or changes tools.
2. Required native sections/commands and optional integrations, with links and tested revisions.
3. Installation steps: files to copy, exact include line, include order, conflict checks, CHECK command and stop/rollback procedure.
4. A single **EDIT HERE** block: discovered inputs versus required/optional inputs; no additional undocumented edit points lower in the G-code.
5. For every setting: type, units, coordinate frame, role, allowed range, how to measure/select, default behavior and related fields to change together.
6. Public macro parameters, valid examples and expected outcome, including missing-tool/no-homing/busy behavior.
7. Numbered physical commissioning steps and a boundary checklist. Heating/motion examples are explicitly labelled.
8. Implementation comments explaining a non-obvious contract or timing constraint, with no unimplemented priority/recovery promises.

Comments and public technical docs stay in English. Use short numbered steps and a glossary for `tool number`, `reference tool`, `G-code coordinates`, `physical clearance`, `mm/s` versus `mm/min`, and `filament length` versus extrusion volume. A diagram can show the prime/brush/dock geometry, but the essential setup remains inside the downloadable file.

Example of a settings/header pattern only; it is valid macro-variable syntax but **does not implement prime behavior**:

```ini
# SC PRIME SETTINGS — proposed pattern, not an available release
# Required: working Klipper + supported KTC-Easy tool registry.
# EDIT HERE. No motion is enabled until the reserved area is commissioned.
[gcode_macro _SC_PRIME_CONFIG]
description: Report the proposed prime settings block; no motion or heating
variable_configured: False
# USER_REQUIRED. G-code XY in mm: [left, right, front, rear].
# Measure a printable strip reserved in the slicer; include final-wipe clearance.
# None means unset. This rectangle is not inferred from axis travel limits.
variable_area: [None, None, None, None]
# USER_REQUIRED. G-code Z in mm, with the documented first-layer offset contract.
variable_prime_z: None
# USER_OPTIONAL. 0 means no LED integration or LED helper dependency.
variable_use_status_leds: 0
gcode:
    {action_respond_info("Settings pattern only; no prime implementation installed")}
```

The implementation must reject unconfigured geometry before movement. `configured: True` means the user completed the commissioning checklist; it does not prove physical clearance and cannot substitute for value/path checks. Provide a separate fully annotated example carrying **our** measured values, rather than preloading them into the neutral export.

## Validation and release criteria

Expand existing offline checks into a per-module acceptance matrix. Compile templates, resolve actual includes/options and validate manifest dependencies; regex searches alone cannot prove conditional or dynamically named calls are valid.

| Scenario | Required result before publishing |
| --- | --- |
| Two tools, five tools, six tools; alternate names and sparse numbers | All loops, heater waits, shutdown and initial/final tool order resolve against the actual registry. No source-loop edits. |
| Only one feature installed | Include succeeds with only its documented native/runtime prerequisites. CHECK lists no hidden dependency on our production files. |
| LEDs/cleaner/dryer/benchmark absent or disabled | No missing-object Jinja reads or emitted calls. An enabled required provider missing is rejected clearly. |
| Different reference tool | Generic helpers respect the setting; an external T0-only backend is rejected or explicitly adapted. |
| Smaller/different bed and off-bed dock/brush | Validate reserved printable area separately from travel. Invalid/intermediate paths fail rather than silently entering the object area. |
| Unset, malformed or inconsistent settings | Clear error before heat/motion. No fallback to this printer's production coordinates. |
| Offset/mesh active, near max Z, different XYZ/E modes | Coordinate conversion, capped lift and state handling produce valid intended commands; restore does not introduce an unexpected move. |
| Print/pause/preparation/dryer/benchmark conflict | Refuse competing ownership before the first heater/motion command, including preparation waits and delayed callbacks. |
| Abort/cancel/crash/recovered tool | Shutdown and state/callback cleanup follow the selected recovery contract. A crash cancel never parks XYZ implicitly. |
| Existing PRINT_START/M109/RESUME/client hooks | Standalone feature leaves ownership intact; integration conflicts/override order are detected. |
| Update of one module | Machine-local inputs, hardware, SAVE_CONFIG and upstream readonly links are retained; settings-schema migrations are explicit. |
| CHECK/HELP invocation | Rendered command stream has no motion, heat, homing, tool selection, probing or state-changing setup command. |

Offline tests support the contract; they do not establish wiring or mechanical clearance. Physically moving features need attended commissioning on the existing five-tool printer and at least one genuinely different target before claiming cross-machine validation. Simulated two/six-tool fixtures must be labelled simulated until those machines are actually tested. The existing 14 tests are a starting point, not certification of this proposed architecture.

Definition of done for each release:

- One file for an eligible standalone feature; a manifest-declared minimal set for an integration; no hidden common-file dependency.
- One top input block; zero edits inside macro logic for a supported tool-count/layout variation.
- No personal IP/UUID/pin/calibration/dock value in generic feature logic. Board templates may show identifiers only as explicitly replaceable examples.
- CHECK/HELP, complete comments and dependency/conflict list accompany the file itself.
- All declared acceptance scenarios pass, changes to motion/heating have commissioning evidence, version/source license and rollback are documented.
- A first-time user can follow the instructions without reading our full production profile; record their feedback and any undocumented edits.

## Implementation sequence

| Stage | Concrete deliverable | Completion gate |
| --- | --- | --- |
| 1. Contract and scaffold | Manifest schema, comment template, module namespace and include validator outside `config/`; per-file dependency inventory | Distinguish runtime requirements, optional providers and conflicts; no production refactor yet. |
| 2. Independent pilot | Benchmark without mandatory cleaner/dryer/LED objects; prime feature with reserved-area settings; read-only CHECK/HELP | Standalone two/five/six-tool fixtures and missing-optional-feature cases pass; physical commissioning for enabled motions. |
| 3. Hardware/UI separation | Split fans/LEDs/operation state/Mainsail hooks; per-tool templates and mappings | Installing an LED feature cannot replace recovery or import unwanted hardware. |
| 4. Station and dryer | Measured silicone-clean settings/contract; independent dryer with explicit thermal policy and parking off by default | Contact/offset/mesh tests, timer/cancellation ownership and attended station/enclosure verification. |
| 5. Lifecycle and calibration | Explicit adapters, corrected end/cancel Z handling and crash recovery, safe Axiscope final toolchange, shaper profile selection | Resolve audit A04–A07 and diagnostic defects before advertising those workflows as reusable releases. |
| 6. Distribution and migration | Versioned exports, examples, selected-file installer/updater, preservation of local values; production profile consumes validated modules through compatibility wrappers | Current-machine before/after command/settings comparison, attended tests, rollback and independent-user acceptance. |

Release benchmark and prime independently as soon as each meets its gate; the calibration integration need not block those unrelated features. Keep multi-tool EXCLUDE_OBJECT unavailable in the shared lifecycle's supported workflow until its backend fix passes replay and physical testing. CAN T1 is already fixed according to the operator and is not an open prerequisite for this refactor.

Avoid a simultaneous move of all production files. Migrate one validated feature at a time and preserve current public names through the integration layer. Each motion/calibration change receives a concrete reviewed diff and commissioning plan; no hardware retuning is implied by this proposal.

## References and related documents

- [Current machine adaptation worksheet](machine-adaptation.md): where the existing production inputs live; still valid while implementing this plan.
- [Production audit and unresolved defects](project-audit-2026-10-09.md): release blockers and source/runtime evidence.
- [Klipper command templates](https://www.klipper3d.org/Command_Templates.html): macro variables, command state and whole-template evaluation.
- [Klipper configuration reference](https://www.klipper3d.org/Config_Reference.html): native configuration owners and supported sections.

Names beginning with SC in this document describe the proposed future API. Users must not add those includes/commands until the corresponding release actually exists.
