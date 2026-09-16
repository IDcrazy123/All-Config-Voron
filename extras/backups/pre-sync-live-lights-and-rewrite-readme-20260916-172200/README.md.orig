# Voron 2.4 StealthChanger — 5-Tool Production Configuration

[English](README.md) | [Tiếng Việt](README.vi.md) | [Active Config Reference](config/README.md) | [Documentation Index](extras/docs/README.md)

Production Klipper configuration, deployment scripts, and OrcaSlicer profiles for a **Voron 2.4 350 mm CoreXY** 3D printer equipped with a **five-tool StealthChanger** (KTC-Easy).

Supervised camera-based XY tool alignment is performed using **kTAMV** with dynamic camera-origin resolution.
The automated multi-tool macro `KTAMV_AUTO_CALIBRATE_ALL_TOOLS` sequentially aligns and stages XY offsets for T1–T4 against the learned T0 camera center at safe Z (Z=40).
Existing production Z offsets remain authoritative via Cartographer Touch.

---

## 1. System Specifications & Hardware Map

| Subsystem | Hardware Specification | Configuration & Pinout |
| :--- | :--- | :--- |
| **Controller & Host** | BTT Manta M8P V2.0 + BTT CM4 | CANbus interface `can0` (1 Mbps), UUID `19b203d75137` |
| **Toolchanger Mechanism**| StealthChanger via KTC-Easy | 5 rear docks (T0–T4), shuttle carriage with OptoTap crash sensing |
| **Toolboards** | 5x BTT EBB36 V1.2 over CAN | Individual tool CAN UUIDs, hotend fans (`PA0`), part fans (`PA1`) |
| **Extruders & Hotends** | 5x WW BMG (TMC2209 @ 0.6A) + TZ V6 2.0 | 0.4 mm nozzles, 50W 24V heaters, NTC 100K thermistors |
| **CoreXY Motion** | 0.9° 400-step motors (TMC2209 @ 0.8A) | X: `PE6`/`PE5`, endstop `PF0` (348 mm); Y: `PE2`/`PE1`, endstop `PF1` (336 mm, min -10 mm) |
| **Quad Z Gantry (QGL)** | 4x Belted Z (GT2 16T / 80:16 gear ratio) | Z0: `PG9`, Z1: `PB4`, Z2: `PG13`, Z3: `PB8` (TMC2209 @ 0.8A) |
| **Operating Limits** | Factory Production Limits | Max Vel: `350 mm/s` (tested `500`), Accel: `7000 mm/s²` (tested `15k`), Z Vel: `70 mm/s` (tested `80`), Z Accel: `900 mm/s²` (tested `1k`) |
| **Probe & Z Homing** | Cartographer V3 CAN (`da13d909ce34`) | Touch homing at bed center (174, 168) + 55×55 Scan adaptive bed mesh |
| **Input Shaper** | Unified Shuttle Shaper (Cartographer ADXL345) | Filter X: `mzv` @ 43.6 Hz ($\zeta = 0.124$); Filter Y: `mzv` @ 33.4 Hz ($\zeta = 0.080$) |
| **Heated Bed** | 1000W 220V AC Silicone Pad + SSR | Heater `PA1`, Sensor `PB0` (NTC 100K MGB18), max 120 °C |
| **Chamber & Cooling** | Chamber Sensor `PB1` (Generic 3950) | Bed fan `PF8`, CM4 fan `PF7`, Enclosure fan `PF9`, Chamber LEDs `PD15` |
| **Nozzle Service** | Purge Bucket & Bambu A1 Silicone Brush | Bucket at X=320, Y=-8.0; Silicone scrub pad at X=277..320, Y=-8.0 |

---

## 2. Five-Tool StealthChanger & Offset Map

Production dock coordinates and mechanical XYZ offsets (stored in `config/printer.cfg` `#*# <SAVE_CONFIG>`):

| Tool | CANbus UUID | Park Coordinates (X, Y, Z) | Mechanical Offset (X, Y, Z) | Role & Status |
| :---: | :---: | :---: | :---: | :--- |
| **T0** | `441e1484ac41` | `(30.2, 1.3, 343.0)` | `(0.000, 0.000, 0.0000)` | **Reference Tool** (Base zero for all offsets) |
| **T1** | `6475b5b9e028` | `(104.0, 1.1, 343.0)` | `(-0.354, -0.174, 0.1691)` | Calibrated production toolhead |
| **T2** | `4ad9d622a836` | `(176.0, 1.6, 343.0)` | `(1.068, -0.028, -0.3142)` | Calibrated production toolhead |
| **T3** | `c2465b7c36f8` | `(249.5, 2.5, 343.0)` | `(0.090, 0.424, -0.2575)` | Calibrated production toolhead |
| **T4** | `28650279df58` | `(321.5, 2.6, 343.0)` | `(0.211, -0.075, 0.0285)` | Calibrated production toolhead |

> [!TIP]
> **First-Layer Squish Factor:** Z offsets above incorporate both raw Cartographer Touch contact measurements (at 70 °C bed & 150 °C nozzle) and an empirical first-layer squish compensation (-0.04 mm for T1–T3, -0.03 mm for T4). This guarantees consistent, high-adhesion first-layer extrusion on textured PEI without requiring manual per-tool babystepping.

> [!NOTE]
> During tool changes, KTC's `pickup_gcode` holds the nozzle on the silicone dock seal while heating to printing temperature (`M109`) to prevent ooze before lowering Z. To minimize toolchange delay, configure OrcaSlicer **Pre-heating time** to 15–20s.

---

## 3. Essential Operator Macros

| Category | Macro Command | Description |
| :--- | :--- | :--- |
| **Print Lifecycle** | `PRINT_START [BED=..] [HOTEND=..]` | Homing, chamber soak, QGL, Cartographer Touch Z, adaptive mesh, nozzle wipe, T0 load. |
| | `PRINT_END` | Retract filament, safe Z hop, drop off tool, turn off heaters/fans, set idle LEDs. |
| | `PAUSE` / `RESUME` / `CANCEL_PRINT` | Standard print control with safe head parking and extrusion state management. |
| **Kinematics Testing** | `TEST_SPEED [SPEED=..] [ACCEL=..]` | CoreXY speed/accel test; verifies step integrity via `GET_POSITION` against endstops. |
| | `TEST_Z_SPEED [SPEED=..] [ACCEL=..]` | Multi-cycle Z gantry travel test (Z=10 to 320 mm); validates Z stepper synchronicity. |
| **Nozzle Maintenance**| `CLEAN_NOZZLE [WIPES=5] [TEMP=150]` | Heats nozzle, performs flick wipes and circular scrub on Bambu A1 silicone brush. |
| | `PRIME_LINES [TOOL=..]` | Purges a clean priming line along the bed margin for the selected tool. |
| **Filament Dryer** | `START_DRYER [TEMPERATURE=..] [TIME=..]` | Controlled bed-based drying (`DRY_PLA`, `DRY_PETG`, `DRY_ABS`). Auto-parks tools safely. |
| | `STOP_DRYER` / `DRYER_STATUS` | Stops bed drying timer and cools bed; displays remaining drying duration. |
| **Tool Calibration** | `KTAMV_AUTO_CALIBRATE_ALL_TOOLS` | Automated sequential XY calibration of T1–T4 using learned T0 camera origin at safe Z. |
| | `KTAMV_MEASURE_ACTIVE_TOOL_XY` | Centering and 3-sample average XY measurement of active tool; validates spread $\le 0.12$ mm. |
| | `KTAMV_APPLY_ACTIVE_TOOL_XY` | Stages measured XY residual into tool parameters (requires `SAVE_CONFIG`). |
| | `CHECK_OFFSETS` | Prints current XYZ offsets for all 5 tools without motion. |
| | `CALIBRATION_STATUS` | Displays active calibration backend status (supervised kTAMV camera XY alignment). |
| | `MEASURE_TOOL_HEATUP [TOOL=..] [START=150] [TARGET=220]` | Measures hotend heating rate and elapsed time from Temp A to B per tool; computes °C/s. |

---

## 4. Repository Layout

```text
All-Config-Voron/
├── config/                     # Production Klipper payload (synced to ~/printer_data/config)
│   ├── printer.cfg             # Root config, kinematics, includes, SAVE_CONFIG block
│   ├── moonraker.conf          # Moonraker API server & Update Manager integration
│   ├── crowsnest.conf          # WebRTC camera streamer configuration
│   ├── KlipperScreen.conf      # Touchscreen GUI configuration
│   ├── mainsail.cfg            # Mainsail UI macro overrides
│   ├── Printer-Setup/          # Modular subsystems (hardware, fans-leds, test-speed, dryer...)
│   ├── toolchanger/            # StealthChanger configs, tools/T0..T4.cfg, readonly symlinks
│   └── scripts/                # Deployment (install.sh), updater (update.sh), cleanup
├── Orca Config/                # Active OrcaSlicer printer, process, and filament user presets
└── extras/                     # Documentation, daily session journals, backups, and ShakeTune data
```

---

## 5. 1-Click Mainsail Update & Lean Deployment

### 5.1. One-Time Setup on Printer (Sparse Checkout)
To prevent downloading 600MB+ of PC backups and commit history to the printer's storage, run via SSH once:
```bash
git clone --depth=1 --filter=blob:none --sparse https://github.com/IDcrazy123/All-Config-Voron.git ~/All-Config-Voron
cd ~/All-Config-Voron
git sparse-checkout set config
sudo systemctl restart moonraker
```
*Result: Printer storage footprint is reduced from **610 MB to only 14 MB (97.7% space saved)**.*

### 5.2. Everyday 1-Click Update
1. Commit and push configuration changes from your PC (`git push origin main`).
2. In the **Mainsail Web UI** under **Settings > Machine / Update Manager**, click **Update** on **`All-Config-Voron`**.
3. Moonraker automatically runs `git pull`, invokes `config/scripts/install.sh` (validates KTC symlinks, purges markdown files, retains only the 5 most recent backups, deploys files), and restarts Klipper. No SSH required.

---

## 6. Safety Rules & Boundaries

1. **Never edit files in `config/toolchanger/readonly-configs/`:** These are symlinks owned exclusively by `klipper-toolchanger-easy`.
2. **Preserve `printer.cfg` `#*# <SAVE_CONFIG>`:** Contains live PID tuning and Cartographer calibration data. Always verify before pushing modifications.
3. **Emergency Stop:** Keep an emergency stop button ready during the first motion after hardware or dock coordinate adjustments.
