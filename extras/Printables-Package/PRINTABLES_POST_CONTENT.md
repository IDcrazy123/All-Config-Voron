# PRINTABLES MODEL UPLOAD DETAILS
# (Sử dụng nội dung này để điền vào form "Create a model" trên Printables)

---

## 1. Title (Tiêu đề dự án)
```text
Universal Oxplow First-Layer Z-Offset Calibration (Single-Tool & Multi-Toolchanger)
```

## 2. Category
```text
3D Printers > 3D Printer Calibration
```

## 3. Short Summary (Tóm tắt ngắn gọn - max 200 ký tự)
```text
Fast 60-second continuous ramp test to dial in perfect first-layer nozzle Z-offset visually with zero guesswork. Works for Ender 3, Prusa MK3/4, Prusa XL, Bambu Lab, and Voron StealthChanger.
```

## 4. Tags
```text
z-offset, calibration, first layer, toolchanger, stealthchanger, voron, prusa xl, klipper, bed leveling, oxplow
```

## 5. Description (Nội dung chi tiết - Hỗ trợ Markdown trên Printables)

```markdown
# Universal Oxplow First-Layer Z-Offset Calibration
### The Ultra-Fast, Visual, Zero-Guesswork Nozzle Height Tuner

Tired of wasting 15 minutes printing traditional flat square patches (Ellis style) only to scratch them with your fingernails trying to guess which one is smoothest?

The **Oxplow Continuous Gradient Ramp** calibration solves this once and for all. By printing a micro-stepped incline ramp instead of flat squares, you can **visually locate the exact transition between over-squish, perfect adhesion, and under-squish in under 60 seconds.**

---

### 🌟 Key Advantages
* **Ultra-Fast & Filament Saving:** Takes under 1 minute and less than 0.3g of filament per toolhead.
* **Continuous Incline ($0.150 \rightarrow 0.350\text{ mm}$):** Covers a full $\pm 0.10\text{ mm}$ range around nominal height ($0.25\text{ mm}$) with $0.004\text{ mm}$ ($4\text{ \mu m}$) micro-steps per hatch line.
* **Integrated Scale & Center Ticks:** Prominent center tick mark indicates nominal $0.00\text{ mm}$ error.
* **Direct Ruler Measurement:** Measure with any simple caliper or ruler from the front edge to calculate your exact offset in seconds.
* **Universal Compatibility:** Includes ready-to-run G-codes and an interactive Python generator supporting:
  - **Single-Tool:** Ender 3, Prusa MK3/MK4, Bambu Lab, Voron 2.4/Trident
  - **Multi-Tool / Toolchanger:** Voron StealthChanger (4-5 tools), Prusa XL (5 tools), Jubilee, IDEX

---

### 📐 How It Works

The test patch is a $20 \times 20\text{ mm}$ square where the Z-height continuously rises from front to back:

```
               SIDE-PROFILE CROSS SECTION OF THE TEST RAMP

  Z-Height (mm)
      ^
0.350 |                                            / (Back Edge: Y = 20mm) -> Under-squish (Gaps)
      |                                          /
      |                                        /
0.250 | ----------------- [ CENTER MARK ] --- / (Center: Y = 10mm) -> Ideal Nominal Target
      |                                     /
      |                                   /
0.150 | (Front Edge: Y = 0mm) -----------/  -> Over-squish (Plowing / Ridges)
      +----------------------------------------------------> Y Position (mm)
      0mm               5mm              10mm              15mm              20mm
```

#### Slope Ratio:
Every **$1.0\text{ mm}$ along the Y axis corresponds to exactly $0.010\text{ mm}$ ($10\text{ \mu m}$) in Z-height change**.

---

### 🔍 How to Read Your Print

Inspect the printed patch under angled light:
1. **Front Section ($Y < 10\text{ mm}$):** Plastic is squished too hard, creating rough ridges/plowing marks from the nozzle.
2. **SWEET SPOT:** Completely flat, mirror-smooth sheen with seamless line bonding.
3. **Back Section ($Y > 10\text{ mm}$):** Separate round extruded lines with visible gaps between them.

Use calipers or a ruler to measure the distance from the **front edge ($Y=0$)** to the **center of the sweet spot ($Y_{measured}$)**:

#### Calculation Formula:
$$\Delta Z = (Y_{measured} - 10.0\text{ mm}) \times 0.010\text{ mm/mm}$$
$$Z_{new} = Z_{current} + \Delta Z$$

* **If the sweet spot is BEHIND the center ($Y > 10\text{ mm}$):** The nozzle was too close. **ADD (+)** $\Delta Z$ to raise the nozzle.
* **If the sweet spot is IN FRONT OF the center ($Y < 10\text{ mm}$):** The nozzle was too high. **SUBTRACT (-)** $\Delta Z$ to lower the nozzle.
* **If the sweet spot is AT the center mark ($Y = 10\text{ mm}$):** Your Z-offset is **100% PERFECT!**

---

### 📊 Quick Lookup Table

| Measured Sweet Spot ($Y$) | Relative to Center | Action | Adjust Offset ($\Delta Z$) |
| :---: | :---: | :---: | :---: |
| **0.0 mm** (Front edge) | $-10.0\text{ mm}$ | **LOWER (-)** | **$-0.100\text{ mm}$** |
| **4.0 mm** | $-6.0\text{ mm}$ | **LOWER (-)** | **$-0.060\text{ mm}$** |
| **8.0 mm** | $-2.0\text{ mm}$ | **LOWER (-)** | **$-0.020\text{ mm}$** |
| **10.0 mm (Center Mark)** | **$0.0\text{ mm}$** | **PERFECT** | **$0.000\text{ mm}$ (Keep)** |
| **12.0 mm** | $+2.0\text{ mm}$ | **RAISE (+)** | **$+0.020\text{ mm}$** |
| **14.0 mm** | $+4.0\text{ mm}$ | **RAISE (+)** | **$+0.040\text{ mm}$** |
| **16.0 mm** | $+6.0\text{ mm}$ | **RAISE (+)** | **$+0.060\text{ mm}$** |
| **20.0 mm** (Back edge) | $+10.0\text{ mm}$ | **RAISE (+)** | **$+0.100\text{ mm}$** |

---

### 🛠️ Python Generator (`generate_oxplow_gcode.py`)

Run the included Python script to instantly generate custom G-codes for your exact bed size, nozzle diameter (0.2, 0.4, 0.6, 0.8mm), and material:

```bash
# Interactive wizard:
python generate_oxplow_gcode.py -i

# One-click CLI presets:
python generate_oxplow_gcode.py --preset voron-350-5tool --material PETG
python generate_oxplow_gcode.py --preset ender3 --material PLA
python generate_oxplow_gcode.py --preset prusa-xl-5tool --material PETG
```

Features embedded in the generator:
- **Vector font strokes:** Prints crisp tool identifiers (`T0`, `T1`, `T2`...) directly on the bed.
- **Preheat & Standby Management:** Safely preheats docked tools before pickup and idles finished tools at 150°C to eliminate toolchange temperature drops and prevent nozzle oozing.
- **Bed Boundary Protection:** Automatically centers patches and prevents boundary collisions.

---

### 📦 Files Included
1. `generate_oxplow_gcode.py` — Multi-platform G-code generator script.
2. `Oxplow_5Tool_Z_Test_PETG.gcode` — Voron 2.4 350mm StealthChanger 5-Tool test (PETG).
3. `Oxplow_5Tool_Z_Test_ABS.gcode` — Voron 2.4 350mm StealthChanger 5-Tool test (ABS).
4. `Oxplow_T1_Z_Test_PETG.gcode` — Single-tool calibration test.
```
