# Voron 2.4 StealthChanger — 5-Tool Production Configuration

[English](README.md) | [Tiếng Việt](README.vi.md) | [Active Config Reference](config/README.md) | [Documentation Index](extras/docs/README.md)

Production Klipper firmware configuration, automated deployment scripts, and OrcaSlicer multi-material profiles for a **Voron 2.4 350 mm CoreXY** 3D printer equipped with a **five-tool StealthChanger** (driven by KTC-Easy).

This repository represents the **live, battle-tested production codebase** operating on the physical machine (`192.168.1.43`). It integrates high-speed eddy-current bed scanning via **Cartographer V3**, machine vision toolhead XY offset calibration via **kTAMV**, automated filament drying with active chamber airflow regulation, an active-tool crash watchdog, and an optimized multi-tool print lifecycle.

---

## Table of Contents
1. [System Specifications & Hardware Architecture](#1-system-specifications--hardware-architecture)
2. [Five-Tool StealthChanger & Calibration Map](#2-five-tool-stealthchanger--calibration-map)
3. [Installation & Deployment Guide](#3-installation--deployment-guide)
4. [Operator & Usage Guide](#4-operator--usage-guide)
5. [Uninstallation, Rollback & Maintenance](#5-uninstallation-rollback--maintenance)
6. [Credits & Attributions](#6-credits--attributions)
7. [Algorithms & Operational Logic Deep Dive](#7-algorithms--operational-logic-deep-dive)

---

## 1. System Specifications & Hardware Architecture

### 1.1 Hardware Specifications

| Subsystem | Hardware Specification | Configuration & Pinout |
| :--- | :--- | :--- |
| **Controller & Host** | BTT Manta M8P V2.0 + BTT CM4 (MainsailOS) | CANbus interface `can0` (1 Mbps), UUID `19b203d75137` |
| **Toolchanger Mechanism** | StealthChanger via KTC-Easy (`v0.0.0-258`) | 5 rear docks (T0–T4), carriage shuttle with OptoTap presence sensing |
| **Toolhead MCUs** | 5x BTT EBB36 V1.2 over CANbus | Individual CAN UUIDs, hotend fans (`PA0`), part fans (`PA1`), Neopixels (`PD3`) |
| **Extruders & Hotends** | 5x WW BMG (TMC2209 @ 0.6A) + TZ V6 2.0 | 0.40 mm nozzles, 50W 24V heaters, NTC 100K Generic 3950 thermistors |
| **CoreXY Motion** | 0.9° 400-step motors (TMC2209 @ 0.8A) | X: `PE6`/`PE5`, endstop `PF0` (348 mm); Y: `PE2`/`PE1`, endstop `PF1` (336 mm, min -10 mm) |
| **Quad Z Gantry (QGL)** | 4x Belted Z (GT2 16T / 80:16 gear ratio) | Z0: `PG9`, Z1: `PB4`, Z2: `PG13`, Z3: `PB8` (TMC2209 @ 0.8A, max Z: 347 mm) |
| **Kinematic Limits** | Factory Production Limits | Max Vel: `350 mm/s` (tested `500`), Accel: `7000 mm/s²` (tested `15k`), Z Vel: `80 mm/s`, Z Accel: `1000 mm/s²` |
| **Probe & Z Homing** | Cartographer V3 CAN (`da13d909ce34`, fw 6.1.0) | Touch homing at bed center (174, 168) + 55×55 high-density eddy-current scan mesh |
| **XY Tool Calibration** | MF-500 2K Camera + kTAMV (Port 8086) | Supervised optical nozzle centering at safe Z (`Z=40`); 3-sample dispersion gating |
| **Z-Offset Switch** | Physical Microswitch on `^PF2` (Axiscope) | Centered at X: 68.0, Y: -8.0, Z: 2.0 (Lift Z: 2.0, Safe approach Z: 15.0) |
| **Heated Bed** | 1000W 220V AC Silicone Pad + SSR | Heater `PA1`, Sensor `PB0` (NTC 100K MGB18), max 120 °C, `check_gain_time: 240s` |
| **Chamber & Cooling** | Chamber Sensor `PB1` (Generic 3950) | Bed fan `PF8`, CM4 fan `PF6` (50 °C), MCU fan `PF7` (55 °C), TMC fan `PF9` (3600s idle timeout) |
| **Chamber Lighting** | 40x WS2812B Neopixel Strip | Data pin `PD15`, initial state off, full brightness macro `LIGHTS_ON` |
| **Nozzle Service** | Purge Bucket & Bambu A1 Silicone Brush | Bucket at X: 320.0, Y: -8.0; Silicone scrub pad at X: 277.0..309.0, Y: -8.0, clean Z: 1.2 mm |

---

## 2. Five-Tool StealthChanger & Calibration Map

Production dock coordinates and mechanical XYZ offsets (authoritatively preserved in `config/printer.cfg` `#*# <SAVE_CONFIG>`):

| Tool | CANbus UUID | Park Coordinates (X, Y, Z) | Mechanical Offset (X, Y, Z) | Role & Operational Status |
| :---: | :---: | :---: | :---: | :--- |
| **T0** | `441e1484ac41` | `(30.2, 1.3, 343.0)` | `(0.000, 0.000, 0.0000)` | **Reference Tool** (Base origin for all tool offsets) |
| **T1** | `6475b5b9e028` | `(104.0, 1.1, 343.0)` | `(-0.354, -0.174, 0.1691)` | Calibrated production toolhead |
| **T2** | `4ad9d622a836` | `(176.0, 1.6, 343.0)` | `(1.068, -0.028, -0.3142)` | Calibrated production toolhead |
| **T3** | `c2465b7c36f8` | `(249.5, 2.5, 343.0)` | `(0.090, 0.424, -0.2575)` | Calibrated production toolhead |
| **T4** | `28650279df58` | `(321.5, 2.6, 343.0)` | `(0.211, -0.075, 0.0285)` | Calibrated production toolhead |

> [!TIP]
> **First-Layer Squish Factor:** Z-offsets above combine physical contact measurements from Cartographer Touch (conducted at 70 °C bed & 150 °C nozzle) with an empirical first-layer squish compensation (-0.04 mm for T1–T3, -0.03 mm for T4). This delivers uniform first-layer adhesion across all 5 toolheads on textured PEI without requiring manual per-tool babystepping.

> [!NOTE]
> **Dock Seal & Ooze Prevention:** During tool changes, KTC's `pickup_gcode` holds the nozzle against the dock's silicone pad while heating to printing temperature (`M109`) to prevent ooze before lowering Z. To minimize toolchange delay during printing, configure OrcaSlicer **Pre-heating time** to 15–20s.

---

## 3. Installation & Deployment Guide

### 3.1 Lean Deployment via Sparse Checkout
The complete repository contains historical backups, high-resolution diagnostic graphs, and test artifacts. To avoid consuming hundreds of megabytes of flash memory on the printer's host CM4, deploy using Git sparse checkout:

```bash
# SSH into the printer host (voron@192.168.1.43)
git clone --depth=1 --filter=blob:none --sparse https://github.com/IDcrazy123/All-Config-Voron.git ~/All-Config-Voron
cd ~/All-Config-Voron
git sparse-checkout set config
bash config/scripts/install.sh
sudo systemctl restart moonraker
```
*Result: Disk usage on the printer is reduced from **610 MB to only 14 MB (97.7% space saved)**.*

### 3.2 Automated Preflight & Installer Architecture (`install.sh`)
When executed, `config/scripts/install.sh` enforces strict preflight validation before touching active configuration:
1. **KTC-Easy Symlink Integrity:** Verifies that all 6 readonly configuration links (`calibrate-offsets.cfg`, `crash-detection.cfg`, `homing.cfg`, `toolchanger-include.cfg`, `toolchanger-macros.cfg`, `toolchanger.cfg`) exist and point to valid targets managed by `klipper-toolchanger-easy`.
2. **kTAMV Runtime & Service Verification:** Confirms that the kTAMV repository is at reviewed commit `72421f2`, the isolated virtualenv `~/ktamv-env` exists, the user systemd service `ktamv-server.service` is present, and reviewed computer vision detector patches are active.
3. **Active-Tool Watchdog Patching:** Checks `~/klipper/klippy/extras/tool_crash.py`. If unpatched, idempotently applies `config/scripts/patches/tool_crash-active-tool-validation.patch` to prevent edge spikes on docked tools from triggering false shutdowns.
4. **Automated Timestamped Backup:** Copies the current `~/printer_data/config` into `~/printer_data/config_backups/config-install-<YYYYMMDD-HHmmss>/`.
5. **Protected Rsync Deployment:** Synchronizes repository configuration while preserving machine-local data (`Generated-Data/`, `ShakeTune_results/`, `Nhat-ky-chinh-sua/`, `toolchanger/readonly-configs/`) and purging markdown documentation.
6. **Automatic Backup Pruning:** Retains only the 5 most recent backups in `config_backups/`, preventing storage exhaustion over time.

### 3.3 Everyday 1-Click Update (Mainsail Web UI)
1. Push tested changes to GitHub: `git push origin main`.
2. In Mainsail, navigate to **Settings > Machine > Update Manager**.
3. Locate **`All-Config-Voron`** and click **Update**.
4. Moonraker pulls the latest commit, executes `config/scripts/install.sh`, creates a local backup, applies patches, deploys files, and prompts for a Klipper restart.

### 3.4 Non-Git Ephemeral Updater (`update.sh`)
For environments without a persistent Git repository on the host:
```bash
curl -fsSL https://raw.githubusercontent.com/IDcrazy123/All-Config-Voron/main/config/scripts/update.sh | bash
```
Downloads an ephemeral tarball to `/tmp`, deploys through `install.sh`, and automatically cleans up all temporary archives upon exit.

---

## 4. Operator & Usage Guide

### 4.1 OrcaSlicer Start G-code Integration
In OrcaSlicer, configure **Printer Settings > Custom G-code > Machine start G-code**:
```gcode
PRINT_START TOOL_TEMP={first_layer_temperature[initial_tool]} {if is_extruder_used[0]}T0_TEMP={first_layer_temperature[0]}{endif} {if is_extruder_used[1]}T1_TEMP={first_layer_temperature[1]}{endif} {if is_extruder_used[2]}T2_TEMP={first_layer_temperature[2]}{endif} {if is_extruder_used[3]}T3_TEMP={first_layer_temperature[3]}{endif} {if is_extruder_used[4]}T4_TEMP={first_layer_temperature[4]}{endif} BED_TEMP=[first_layer_bed_temperature] TOOL=[initial_tool] MATERIAL={filament_type[initial_tool]}
```

### 4.2 Operator Macro Reference

| Category | Macro Command | Parameters & Description |
| :--- | :--- | :--- |
| **Print Control** | `PRINT_START` | `BED_TEMP=.. TOOL=.. [SOAK=..] [MATERIAL=..] [AUTO_SOAK=1] [Tn_TEMP=..]`<br>Homing with Cartographer on shuttle, async bed/tool preheat, T0 cleaning, heat soak, stable-temp QGL, touch homing, adaptive scan mesh, pipelined prime lines. |
| | `PRINT_END` | Safe Z lift ($\ge 50$ mm), 2-stage string-break retract (-10 mm), drops tool to dock, parks empty shuttle at rear center ($Y_{\max}-20$), turns off heaters/part fans, schedules 180s chamber scrub. |
| | `PAUSE` | Parks carriage, maintains hotend standby, sets magenta LED. |
| | `RESUME` | Runs `INITIALIZE_TOOLCHANGER`, verifies physical tool presence with `VERIFY_TOOL_DETECTED`, restores temperature, unretracts, resumes print. |
| | `CANCEL_PRINT` | Cleans up toolchanger, drops mounted tool, lifts Z safely, parks empty carriage at rear. |
| | `G32` | Clears mesh, homes XYZ, runs Quad Gantry Leveling, moves to bed center. |
| **Filament Dryer** | `START_DRYER` | `MATERIAL=[PLA\|TPU\|PETG\|ABS\|ASA\|NYLON\|PC\|CUSTOM] [BED=..] [CHAMBER=..] [TIME=..] [FAN=..]`<br>Auto-parks toolhead at $Z \ge 200$ mm, docks tool, runs 4-zone thermal regulation with periodic moisture flush. |
| | `STOP_DRYER` | Halts drying cycle, cools bed, resets circulation fans. |
| | `DRYER_STATUS` | Displays elapsed/remaining time, bed/chamber temperature, and humidity telemetry. |
| **Nozzle Cleaning** | `CLEAN_NOZZLE` | `[WIPES=5] [TEMP=150] [PURGE=0] [PURGE_TEMP=0]`<br>Travels to bucket (X:320, Y:-8.0), heats to clean temp, flick wipes debris into bucket, executes G2/G3 circular scrub on silicone brush at Z:1.2 mm. |
| | `PURGE_AND_CLEAN` | `[PURGE=15] [PURGE_TEMP=200] [TEMP=150]`<br>Purges old filament into bucket, activates 100% part fan to solidify drool, flick wipes, and scrubs. |
| | `PRIME_LINES` | `INITIAL_TOOL=.. [Tn_TEMP=..]`<br>Calculates non-overlapping bed slots, preheats next tool in parallel, draws 3-pass purge line with sideways wipe, leaves initial print tool active. |
| **Tool Calibration** | `KTAMV_AUTO_CALIBRATE_ALL_TOOLS` | `[SAMPLES=3] [MAX_SPREAD=0.12] [Z=40]`<br>Fully automated sequential XY calibration of T1–T4 against learned T0 camera origin at safe Z=40 mm. |
| | `KTAMV_STATUS` | Reports camera calibration status, mm/pixel scale, and learned camera center. |
| | `CHECK_OFFSETS` | Prints current XYZ offsets for all 5 tools without motion. |
| | `CALIBRATION_STATUS` | Reports active calibration backend status and hardware assignments. |
| | `MEASURE_TOOL_HEATUP` | `TOOL=[0..4] [START=150] [TARGET=220] [TIMEOUT=180]`<br>Measures hotend heating elapsed time and heating rate (°C/s) via 0.5s reactor ticker. |
| **Kinematics Testing** | `TEST_SPEED` | `[SPEED=..] [ACCEL=..] [ITERATIONS=5]`<br>Tests CoreXY speed/acceleration at safe Z=30 mm below tool docks; verifies step loss via `GET_POSITION`. |
| | `TEST_Z_SPEED` | `[SPEED=..] [ACCEL=..] [ITERATIONS=5]`<br>Multi-cycle vertical travel test (Z:10 to 320 mm); validates 4-motor belted Z gantry synchronization. |
| **Lighting & Fans** | `LIGHTS_ON` / `OFF` | Toggles 40-LED chamber strip at 100% white (`RED=1 GREEN=1 BLUE=1`). |
| | `BED_FAN_ON` / `OFF` | Controls under-bed chamber circulation fan (0.0–1.0). |

---

## 5. Uninstallation, Rollback & Maintenance

### 5.1 System Cleanup (`cleanup-voron.sh`)
To remove obsolete backups and temporary files from the host:
```bash
# Preview candidates (dry-run):
bash config/scripts/cleanup-voron.sh

# Apply deletion:
bash config/scripts/cleanup-voron.sh --apply
```
Deletes `config.update-backup-*`, legacy `axiscope.bak`, root `*.md` files inside config, and older `config-install-*` backups beyond the 5 most recent.

### 5.2 Rollback to a Previous Configuration
Every run of `install.sh` creates an independent, timestamped snapshot. If a configuration change causes issues:
```bash
# 1. Identify desired backup directory:
ls -la ~/printer_data/config_backups/

# 2. Restore the backup:
cp -a ~/printer_data/config_backups/config-install-YYYYMMDD-HHmmss/* ~/printer_data/config/

# 3. Restart Klipper:
sudo systemctl restart klipper
```

### 5.3 Complete Uninstallation & Decoupling
To decouple the printer from this configuration repository:
1. **Remove Update Manager Integration:** Delete the `[update_manager All-Config-Voron]` section from `~/printer_data/config/moonraker.conf`.
2. **Disable kTAMV Service:**
   ```bash
   systemctl --user stop ktamv-server.service
   systemctl --user disable ktamv-server.service
   rm -f ~/.config/systemd/user/ktamv-server.service
   ```
3. **Revert Klippy Runtime Patches:**
   ```bash
   # Revert tool_crash patch:
   patch -R -d ~/klipper/klippy/extras -p1 < ~/All-Config-Voron/config/scripts/patches/tool_crash-active-tool-validation.patch
   # Remove kTAMV extension symlinks:
   rm -f ~/klipper/klippy/extras/ktamv.py ~/klipper/klippy/extras/ktamv_utl.py
   ```
4. **Remove Repository Checkout:** `rm -rf ~/All-Config-Voron`.

---

## 6. Credits & Attributions

This production configuration builds upon outstanding open-source projects and community innovations:

- **[StealthChanger](https://stealthchanger.com/)** by *draftsauce* and the StealthChanger community: The mechanical multi-tool changer platform for Voron printers.
- **[klipper-toolchanger-easy (KTC-Easy)](https://github.com/jwellman80/klipper-toolchanger-easy)** by *jwellman80*: Streamlined toolchanger motion kinematics, dock routing, and state tracking.
- **[kTAMV (Klipper Tool Alignment with Machine Vision)](https://github.com/TypQxQ/kTAMV)** by *TypQxQ*: Upward-looking camera tool centering and offset calibration.
- **[tool_crash](https://github.com/cekim-git/tool_crash)** by *cekim-git*: Tool presence detection and crash watchdog architecture.
- **[Cartographer 3D](https://cartographer3d.com/)**: High-speed eddy-current probe sensing and Touch nozzle contact homing.
- **[Mainsail](https://mainsail.xyz/)** & **[Mainsail Crew](https://github.com/mainsail-crew)**: Web interface, Crowsnest streaming, Sonar, and client macros.
- **[Klippain Shake&Tune](https://github.com/Frix-x/klippain-shaketune)** by *Frix-x*: Advanced input shaper and mechanical resonance analysis.
- **[Andrew Ellis Print Tuning Guide](https://ellis3dp.com/)**: CoreXY kinematics benchmarking and test methodology.
- **[Voron Design](https://vorondesign.com/)**: Voron 2.4 CoreXY 3D printer design.

---

## 7. Algorithms & Operational Logic Deep Dive

### 7.1 Dynamic Heat Soak Scaling (`_PRINT_START_HEAT_SOAK`)
Traditional print-start macros employ rigid soak timers regardless of the printer's thermal history. This system implements dynamic scaling based on the temperature delta between target and starting bed temperature ($\Delta T = T_{\text{bed,target}} - T_{\text{bed,start}}$):

$$\text{Soak Time} = \begin{cases} 
T_{\text{preset}} & \text{if } \Delta T > 15^\circ\text{C} \quad (\text{Cold bed}) \\
\text{round}(0.20 \times T_{\text{preset}}) & \text{if } 5^\circ\text{C} < \Delta T \le 15^\circ\text{C} \quad (\text{Warm bed}) \\
0 & \text{if } \Delta T \le 5^\circ\text{C} \quad (\text{Hot bed, soak bypassed})
\end{cases}$$

- **Material Presets ($T_{\text{preset}}$):** PLA/TPU: 30s; PETG: 60s; ABS/ASA/PC/NYLON: 90s.
- **Precedence:** Manual `SOAK=<seconds>` overrides all calculations; `AUTO_SOAK=0` disables automatic soaking entirely.

### 7.2 Two-Phase Nozzle De-Blobbing & Contact Protection Logic
In single-probe toolchangers, plastic ooze on nozzle contact probes introduces measurement error. This system executes a mandatory two-phase cleaning protocol:
1. **Phase 1 (Bed Warmup Phase):** T0 is cleaned at 150 °C while the 1000W AC bed continues heating.
2. **Phase 2 (Immediate Pre-Touch Phase):** After QGL and heat soak, T0 is cleaned *a second time* at 150 °C immediately prior to `CARTOGRAPHER_TOUCH_HOME`.
- **Physical Rationale:** Residual plastic drooled during the 60–90s soak acts as an elastic cushion during Touch probing. Under contact force, soft plastic compresses and flexes the StealthChanger shuttle latch, corrupting the $Z=0$ datum by 0.05–0.15 mm. Performing a 5-pass flick and scrub at 150 °C immediately before touch guarantees clean metal-to-bed contact without molten plastic flow.

### 7.3 Safe Homing & Tool Persistence Invariant
Cartographer V3 is mounted directly to the carriage shuttle, not to any individual tool. This enables a strict safety invariant:
- **Never attempt a toolchange, dock, or bucket move before full `G28`.** If the machine stopped holding T1..T4, the dropoff trajectory requires a valid Z-hop. `PRINT_START` executes full homing with whichever toolhead happens to be attached, raises Z to safe clearance ($Z=10$ mm), and only then performs tool switching to T0.

### 7.4 4-Zone Adaptive Filament Drying & Periodic Moisture Flush Pulse
The filament drying controller (`filament-dryer.cfg`) executes a 10-second closed-loop thermal and airflow regulation cycle using the 1000W AC bed and under-bed circulation fan:

```
                  Chamber Temperature Relative to Target
  < (Target - 2°C)      [Target - 2°C .. +3.5°C]      (+3.5°C .. +6°C]      > (Target + 6°C)
┌────────────────────┬─────────────────────────────┬───────────────────┬──────────────────────┐
│  ZONE 1: WARM-UP   │   ZONE 2: ACTIVE DRYING     │  ZONE 3: GENTLE   │  ZONE 4: OVERHEAT    │
│  Fan Boost (+25%)  │   Base Fan (40-70%)         │  Fan Cut (-10%)   │  Fan Cut (-20%)      │
│  Max: 85% Airflow  │   + Moisture Flush Pulse    │  Min: 30% Airflow │  Bed Target -4°C     │
└────────────────────┴─────────────────────────────┴───────────────────┴──────────────────────┘
```

- **Periodic Moisture Flush Pulse:** Every 20 minutes (1200 seconds) after the first 15 minutes, airflow increases by +25% (capped at 70%) for 30 seconds to evacuate humid air trapped in the enclosure.
- **Overheat Guard:** If chamber temperature exceeds target by $>6^\circ\text{C}$, the bed target temperature is actively throttled down by $-4^\circ\text{C}$ (floor 45 °C) to protect spools from glass transition softening.
- **Dryer-to-Print Handoff (`_DRYER_HANDOFF_TO_PRINT`):** If a print job is launched while drying, the dryer timer terminates immediately without cycling the bed heater or circulation fan off, preventing thermal shock.

### 7.5 Computer Vision Nozzle Centering & Dispersion Gating (`kTAMV`)
To achieve reliable sub-0.02 mm optical alignment under varied lighting and camera conditions:
- **Center Highlight Detection Fallback (`find_center_highlight_keypoint`):** Applied via runtime patch. When standard blob detection is ambiguous, it binarizes grayscale frames at threshold 245 (`cv2.threshold`), extracts connected components, and evaluates candidates against strict geometric gates: area $30 \le A \le 1200\text{ px}$, aspect ratio $0.35 \le W/H \le 2.8$, distance to optical center $(320, 240) \le 120\text{ px}$. It selects the candidate minimizing $(\text{distance}, -\text{area})$.
- **3-Sample Dispersion Gating (`KTAMV_MEASURE_TOOL_XY`):** Performs 3 independent centering cycles from safe $Z=40$ mm. Calculates mean offset and spread:

$$\Delta X = X_{\max} - X_{\min}, \quad \Delta Y = Y_{\max} - Y_{\min}$$

If $\max(\Delta X, \Delta Y) > 0.12\text{ mm}$, the calibration run is aborted with an error, preventing noisy optical measurements from corrupting tool parameters.
- **Specular Flare Blanking:** Automatically turns off toolhead LEDs (`SET_LED ... RED=0 GREEN=0 BLUE=0`) during vision acquisition to eliminate glare on the nozzle tip.

### 7.6 Pipelined Multi-Tool Priming & Slot Allocation (`PRIME_LINES`)
- **Dynamic Slot Geometry:** Divides available bed margin ($X_{\min} + 30\text{ mm}$ to $X_{\max} - 30\text{ mm}$) into evenly spaced, non-overlapping slots based on the number of tools used in the sliced model.
- **Parallel Heating Pipeline:** While tool $T_n$ is executing its 3-pass purge line, the macro issues `M104 T{next_t} S{next_temp}` to start heating the next tool in parallel, eliminating dock wait times.
- **Reverse Tool Scheduling:** Non-initial tools are primed first and cooled to standby; the initial printing tool is primed last and remains at printing temperature, ready for layer 1.

### 7.7 Active-Tool Crash Watchdog & Zero-Motion Safe Pause (`tool_crash`)
- **Edge Transient Validation Patch:** Upstream `tool_crash.py` triggered a shutdown on any detection pin edge. The downstream patch re-routes interrupts to `self._sync_expected()`, filtering out mechanical transients on docked/parked tools.
- **Watchdog Confirmation:** Polls every 0.5s and requires 2 consecutive inconsistent states (`watchdog_threshold: 2`) before declaring a crash.
- **Zero-Motion Safe Pause (`_TOOL_CRASH_SAFE_PAUSE`):** When a crash is confirmed during printing, executes `PAUSE_BASE` and filament retraction *without moving X, Y, or Z*. If a toolhead has detached or tilted, any XY or Z travel would risk colliding with the print or frame.

### 7.8 Two-Stage Anti-Stringing Retraction & Safe Z Hop (`PRINT_END`)
- **Stage 1:** Fast $-2.0\text{ mm}$ retraction at $F=2700$ to immediately release nozzle pressure.
- **Stage 2:** High-speed $-8.0\text{ mm}$ retraction coordinated with $+5.0\text{ mm}$ vertical Z-hop at $F=12000$ (total $-10.0\text{ mm}$ retract) to cleanly break the molten filament string.
- **Dynamic Safe Z Lift:** Lifts Z to $Z_{\text{safe}} = \min(\max(Z_{\text{current}} + 10, 50), Z_{\max})$ before dock approach, eliminating collisions with tall printed parts.
- **Pre-Dock Cooldown:** Sets hotend target to $0^\circ\text{C}$ *before* calling `UNSELECT_TOOL`, ensuring KTC does not pause at the dock waiting for cooldown.

### 7.9 10-State Toolhead LED State Machine & Bus Pacing (`fans-leds.cfg`)
- **Event-Driven Priority Hierarchy:**
  `error` > `toolchange` > `leveling` > `calibrating` > `cleaning` > `heating` > `printing` > `pause` > `complete` > `ready` > `standby`
- **Optical Contrast:** Active toolhead illuminates brightly; docked toolheads dim to dark blue standby (`_SYNC_INACTIVE_LEDS`).
- **SPI Frame Batching:** Updates Index 1 and 2 with `TRANSMIT=0`, and Index 3 with `TRANSMIT=1`, transmitting a single frame to prevent LED flicker.
- **CAN Bus Saturation Prevention:** In multi-tool iteration loops, inserts `G4 P10` (10 ms dwell) between toolhead LED commands to avoid CAN bus packet drops.

### 7.10 Dynamic Input Shaper Parameter Caching (`_ACTIVE_INPUT_SHAPER`)
In multi-tool systems where toolheads have individual resonance tunings, calling Klipper's `SET_INPUT_SHAPER` on every toolchange floods the console log and Moonraker database. The system maintains an in-memory cache variable (`_ACTIVE_INPUT_SHAPER`); `after_change_gcode` only invokes `SET_INPUT_SHAPER` when target shaper parameters differ from active values.