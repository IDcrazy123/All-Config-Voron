# Voron 2.4 StealthChanger — Cấu hình Vận hành 5 Tool

[English](README.md) | [Tiếng Việt](README.vi.md) | [Tài liệu cấu hình](config/README.vi.md) | [Chỉ mục tài liệu](extras/docs/README.vi.md)

Tài liệu cấu hình firmware Klipper, kịch bản triển khai tự động và profile OrcaSlicer đa vật liệu cho máy in 3D **Voron 2.4 350 mm CoreXY** trang bị hệ thống đổi đầu in **StealthChanger 5 tool** (vận hành qua KTC-Easy).

Kho lưu trữ này chứa **toàn bộ cấu hình thực tế đang vận hành (production)** trên máy in thật. Hệ thống tích hợp quét lưới bàn in cảm ứng dòng xoáy tốc độ cao qua **Cartographer V3**, cân chỉnh bù trừ tọa độ XY đầu in bằng thị giác máy tính qua **kTAMV**, sấy cuộn nhựa tự động điều tiết luồng khí buồng in, watchdog chống rơi tool và quy trình vòng đời in tối ưu cho nhiều đầu in.

---

## Mục lục
1. [Thông số Kỹ thuật & Kiến trúc Phần cứng](#1-thông-số-kỹ-thuật--kiến-trúc-phần-cứng)
2. [Sơ đồ 5 Tool StealthChanger & Bản đồ Offset](#2-sơ-đồ-5-tool-stealthchanger--bản-đồ-offset)
3. [Hướng dẫn Cài đặt & Triển khai](#3-hướng-dẫn-cài-đặt--triển-khai)
4. [Hướng dẫn Vận hành & Sử dụng](#4-hướng-dẫn-vận-hành--sử-dụng)
5. [Hướng dẫn Gỡ cài đặt, Hoàn tác & Bảo trì](#5-hướng-dẫn-gỡ-cài-đặt-hoàn-tác--bảo-trì)
6. [Ghi công & Lời cảm ơn](#6-ghi-công--lời-cảm-ơn)
7. [Phân tích Chuyên sâu Thuật toán & Logic Vận hành](#7-phân-tích-chuyên-sâu-thuật-toán--logic-vận-hành)

---

## 1. Thông số Kỹ thuật & Kiến trúc Phần cứng

### 1.1 Thông số Phần cứng Chi tiết

| Hệ thống | Thông số phần cứng thực tế | Cấu hình & Chân Pin |
| :--- | :--- | :--- |
| **Bo mạch chính & Máy chủ** | BTT Manta M8P V2.0 + BTT CM4 (MainsailOS) | Giao diện CANbus `can0` (1 Mbps), UUID `19b203d75137` |
| **Cơ cấu Toolchanger** | StealthChanger qua KTC-Easy (`v0.0.0-258`) | 5 dock phía sau (T0–T4), carriage shuttle có cảm biến rơi tool OptoTap |
| **Bo mạch Toolhead** | 5x BTT EBB36 V1.2 qua mạng CANbus | CAN UUID độc lập từng tool, quạt hotend (`PA0`), quạt part (`PA1`), LED Neopixel (`PD3`) |
| **Extruder & Hotend** | 5x WW BMG (TMC2209 dòng 0.6A) + TZ V6 2.0 | Đầu phun 0.40 mm, thanh nhiệt 50W 24V, cảm biến nhiệt NTC 100K Generic 3950 |
| **Chuyển động CoreXY** | Động cơ 0.9° 400 bước (TMC2209 dòng 0.8A) | X: `PE6`/`PE5`, endstop `PF0` (348 mm); Y: `PE2`/`PE1`, endstop `PF1` (336 mm, min -10 mm) |
| **Khung nâng Z 4 góc (QGL)**| 4 động cơ dẫn động đai (GT2 16T / tỉ số 80:16) | Z0: `PG9`, Z1: `PB4`, Z2: `PG13`, Z3: `PB8` (TMC2209 dòng 0.8A, Z tối đa 347 mm) |
| **Giới hạn Động học** | Giới hạn vận hành an toàn trong cấu hình | Vận tốc tối đa: `350 mm/s` (đã test `500`), Gia tốc: `7000 mm/s²` (đã test `15k`), Z Vel: `80 mm/s`, Z Accel: `1000 mm/s²` |
| **Đầu dò & Homing Z** | Cartographer V3 CAN (`da13d909ce34`, fw 6.1.0) | Touch homing tại tâm bàn (174, 168) + Bed Mesh quét adaptive 55×55 dòng xoáy siêu tốc |
| **Cân chỉnh Tool XY** | Camera MF-500 2K hướng lên + kTAMV (Port 8086)| Đo tự động tuần tự T1–T4 tại Z an toàn (`Z=40`); lọc phân tán 3 mẫu $\le 0.12$ mm |
| **Công tắc Z-Offset** | Công tắc vi mô vật lý trên chân `^PF2` (Axiscope) | Tọa độ X: 68.0, Y: -8.0, Z: 2.0 (Nâng Z: 2.0 mm, Z tiếp cận an toàn: 15.0 mm) |
| **Mâm nhiệt Bàn in** | Tấm nhiệt silicon 220V 1000W + Rơ-le bán dẫn SSR| Heater `PA1`, Cảm biến `PB0` (NTC 100K MGB18), max 120 °C, `check_gain_time: 240s` |
| **Vỏ máy & Làm mát** | Cảm biến buồng in `PB1` (Generic 3950) | Quạt bed `PF8`, Quạt CM4 `PF6` (50 °C), Quạt MCU `PF7` (55 °C), Quạt TMC `PF9` (cooldown 3600s) |
| **Đèn chiếu sáng Buồng** | Dải 40 đèn LED Neopixel WS2812B | Chân dữ liệu `PD15`, mặc định tắt khi khởi động, macro `LIGHTS_ON` bật 100% độ sáng |
| **Vệ sinh Đầu phun** | Khay xả phôi & Cọ chà silicon Bambu A1 | Khay xả tại X: 320.0, Y: -8.0; Cọ chà tại X: 277.0..309.0, Y: -8.0, độ cao chà Z: 1.2 mm |

---

## 2. Sơ đồ 5 Tool StealthChanger & Bản đồ Offset

Tọa độ dock và offset cơ khí XYZ (được lưu trữ có thẩm quyền tại khối `#*# <SAVE_CONFIG>` trong `config/printer.cfg`):

| Tool | CANbus UUID | Tọa độ Dock (X, Y, Z) | Offset cơ khí (X, Y, Z) | Vai trò & Trạng thái |
| :---: | :---: | :---: | :---: | :--- |
| **T0** | `441e1484ac41` | `(30.2, 1.3, 343.0)` | `(0.000, 0.000, 0.0000)` | **Tool tham chiếu chuẩn** (Gốc 0 cho toàn bộ offset) |
| **T1** | `6475b5b9e028` | `(104.0, 1.1, 343.0)` | `(-0.354, -0.174, 0.1691)` | Đầu in vận hành sản xuất đã hiệu chuẩn |
| **T2** | `4ad9d622a836` | `(176.0, 1.6, 343.0)` | `(1.068, -0.028, -0.3142)` | Đầu in vận hành sản xuất đã hiệu chuẩn |
| **T3** | `c2465b7c36f8` | `(249.5, 2.5, 343.0)` | `(0.090, 0.424, -0.2575)` | Đầu in vận hành sản xuất đã hiệu chuẩn |
| **T4** | `28650279df58` | `(321.5, 2.6, 343.0)` | `(0.211, -0.075, 0.0285)` | Đầu in vận hành sản xuất đã hiệu chuẩn |

> [!TIP]
> **Hệ số Nén nhựa Lớp đầu tiên (Squish Factor):** Các giá trị Z-offset ở trên là sự kết hợp giữa số đo tiếp xúc cơ học từ Cartographer Touch (đo ở nhiệt độ bàn 70 °C & đầu phun 150 °C) cùng với hệ số bù nén nhựa thực nghiệm (-0.04 mm cho T1–T3, -0.03 mm cho T4). Điều này đảm bảo độ bám dính hoàn hảo và phẳng mịn cho lớp in đầu tiên trên bề mặt PEI sần mà không cần phải babystep thủ công từng đầu in.

> [!NOTE]
> **Chống rỉ nhựa tại Dock:** Trong suốt quá trình đổi đầu in, lệnh `pickup_gcode` của KTC giữ đầu phun tì trên đệm silicon của dock trong lúc nung nhiệt (`M109`) để chống trào nhựa trước khi hạ Z. Để rút ngắn thời gian chờ tại dock, hãy cài đặt **Pre-heating time** trong OrcaSlicer khoảng 15–20 giây.

---

## 3. Hướng dẫn Cài đặt & Triển khai

### 3.1 Triển khai Tinh gọn qua Sparse Checkout (Lean Deployment)
Kho mã nguồn trên GitHub chứa đầy đủ lịch sử sao lưu, biểu đồ chẩn đoán phân tích cộng hưởng và file thử nghiệm. Để tránh làm tốn dung lượng bộ nhớ flash trên bo mạch CM4 của máy in, hãy triển khai bằng Git sparse checkout:

```bash
# Sao chép kho lưu trữ về bo mạch máy in:
git clone --depth=1 --filter=blob:none --sparse https://github.com/IDcrazy123/All-Config-Voron.git ~/All-Config-Voron
cd ~/All-Config-Voron
git sparse-checkout set config
bash config/scripts/install.sh
sudo systemctl restart moonraker
```
*Kết quả: Dung lượng lưu trữ trên máy in giảm từ **610 MB xuống chỉ còn 14 MB (tiết kiệm 97.7% bộ nhớ)**.*

### 3.2 Quy trình Kiểm tra & Kiến trúc Bộ cài đặt (`install.sh`)
Khi thực thi, `config/scripts/install.sh` tự động thực hiện quy trình kiểm tra nghiêm ngặt trước khi can thiệp vào file cấu hình:
1. **Kiểm tra Liên kết KTC-Easy:** Xác thực toàn bộ 6 liên kết symlink chỉ đọc (`calibrate-offsets.cfg`, `crash-detection.cfg`, `homing.cfg`, `toolchanger-include.cfg`, `toolchanger-macros.cfg`, `toolchanger.cfg`) tồn tại và trỏ đúng vào plugin `klipper-toolchanger-easy`.
2. **Xác thực kTAMV Runtime & Dịch vụ:** Kiểm tra repo kTAMV nằm đúng commit đã duyệt `72421f2`, môi trường ảo `~/ktamv-env`, service `ktamv-server.service` và các bản vá thuật toán thị giác máy tính đã được tích hợp đầy đủ.
3. **Vá lỗi Tự động cho Watchdog Rơi Tool:** Kiểm tra file `~/klipper/klippy/extras/tool_crash.py`. Nếu chưa được vá, script tự động áp dụng bản vá `config/scripts/patches/tool_crash-active-tool-validation.patch` để ngăn chặn việc ngắt xung giả từ các tool đang đỗ trong dock gây sập máy in.
4. **Tự động Sao lưu Nguyên tử có Dấu thời gian:** Tạo bản sao lưu toàn bộ thư mục cấu hình hiện tại vào `~/printer_data/config_backups/config-install-<YYYYMMDD-HHmmss>/`.
5. **Đồng bộ Rsync Bảo vệ Dữ liệu:** Đồng bộ cấu hình mới vào `~/printer_data/config/`, loại trừ và bảo vệ nguyên vẹn các thư mục dữ liệu cục bộ (`Generated-Data/`, `ShakeTune_results/`, `Nhat-ky-chinh-sua/`, `toolchanger/readonly-configs/`) và tự động dọn sạch các file tài liệu `.md`.
6. **Tự động Dọn dẹp Bản sao lưu Cũ:** Tự động quét và chỉ giữ lại 5 bản sao lưu gần nhất trong `config_backups/`, ngăn ngừa việc đầy thẻ nhớ theo thời gian.

### 3.3 Cập nhật 1-Click qua Giao diện Web Mainsail
1. Đẩy các thay đổi đã kiểm thử lên GitHub từ máy tính: `git push origin main`.
2. Trên giao diện Mainsail, vào **Cài đặt (Settings) > Máy in (Machine) > Update Manager**.
3. Tìm mục **`All-Config-Voron`** và bấm **Update**.
4. Moonraker sẽ tự động kéo code mới về, thực thi `config/scripts/install.sh`, tạo bản sao lưu an toàn, cập nhật cấu hình và yêu cầu khởi động lại Klipper.

### 3.4 Cập nhật Tạm thời Không cần Git (`update.sh`)
Dành cho trường hợp cập nhật nhanh mà không muốn giữ thư mục git trên host:
```bash
curl -fsSL https://raw.githubusercontent.com/IDcrazy123/All-Config-Voron/main/config/scripts/update.sh | bash
```
Script sẽ tải gói nén tạm thời về `/tmp`, chạy bộ cài đặt và tự động xóa sạch file nén khi hoàn tất.

---

## 4. Hướng dẫn Vận hành & Sử dụng

### 4.1 Cấu hình Start G-code trong OrcaSlicer
Trong OrcaSlicer, cấu hình tại **Printer Settings > Custom G-code > Machine start G-code**:
```gcode
PRINT_START TOOL_TEMP={first_layer_temperature[initial_tool]} {if is_extruder_used[0]}T0_TEMP={first_layer_temperature[0]}{endif} {if is_extruder_used[1]}T1_TEMP={first_layer_temperature[1]}{endif} {if is_extruder_used[2]}T2_TEMP={first_layer_temperature[2]}{endif} {if is_extruder_used[3]}T3_TEMP={first_layer_temperature[3]}{endif} {if is_extruder_used[4]}T4_TEMP={first_layer_temperature[4]}{endif} BED_TEMP=[first_layer_bed_temperature] TOOL=[initial_tool] MATERIAL={filament_type[initial_tool]}
```

### 4.2 Bảng Tra cứu Macro Vận hành

| Nhóm chức năng | Lệnh Macro | Tham số & Mô tả Chi tiết |
| :--- | :--- | :--- |
| **Quy trình In** | `PRINT_START` | `BED_TEMP=.. TOOL=.. [SOAK=..] [MATERIAL=..] [AUTO_SOAK=1] [Tn_TEMP=..]`<br>Home trục với Cartographer trên shuttle, gia nhiệt bất đồng bộ, lau T0, ngâm nhiệt bàn in thông minh, cân bàn QGL ở nhiệt độ ổn định, Touch home Z, quét lưới adaptive, mồi nhựa pipelined. |
| | `PRINT_END` | Nâng Z an toàn ($\ge 50$ mm), rút sợi 2 nấc (-10 mm), trả tool về dock, đỗ shuttle rỗng ở phía sau ($Y_{\max}-20$), tắt thanh nhiệt/quạt part, kích hoạt hẹn giờ 180s lọc khí buồng in. |
| | `PAUSE` | Đỗ đầu in an toàn, giữ nhiệt độ chờ, chuyển LED sang màu tím magenta. |
| | `RESUME` | Chạy `INITIALIZE_TOOLCHANGER`, kiểm tra cảm biến nhận diện tool qua `VERIFY_TOOL_DETECTED`, phục hồi nhiệt độ, bù nhựa đùn, tiếp tục in. |
| | `CANCEL_PRINT` | Dọn dẹp toolchanger, trả tool về dock an toàn, nâng Z và đỗ carriage rỗng. |
| | `G32` | Xóa mesh, home toàn bộ trục XYZ, cân mặt bàn QGL, đưa đầu in về tâm bàn. |
| **Sấy Cuộn nhựa** | `START_DRYER` | `MATERIAL=[PLA\|TPU\|PETG\|ABS\|ASA\|NYLON\|PC\|CUSTOM] [BED=..] [CHAMBER=..] [TIME=..] [FAN=..]`<br>Tự động nâng Z $\ge 200$ mm, trả tool về dock, kích hoạt điều tiết nhiệt 4 vùng và xung xả ẩm định kỳ. |
| | `STOP_DRYER` | Dừng chu trình sấy, ngắt nhiệt bàn in, đưa quạt buồng về chế độ nghỉ. |
| | `DRYER_STATUS` | Hiển thị thời gian đã sấy, thời gian còn lại, nhiệt độ bàn/buồng và độ ẩm RH. |
| **Bảo trì Đầu phun** | `CLEAN_NOZZLE` | `[WIPES=5] [TEMP=150] [PURGE=0] [PURGE_TEMP=0]`<br>Di chuyển tới khay xả (X:320, Y:-8.0), gia nhiệt tới 150 °C, gạt phôi nhựa vào khay, chà xoay tròn G2/G3 trên cọ silicon ở độ cao Z:1.2 mm. |
| | `PURGE_AND_CLEAN` | `[PURGE=15] [PURGE_TEMP=200] [TEMP=150]`<br>Xả phôi nhựa thừa ở nhiệt độ cao, bật quạt làm nguội nhanh để đông cứng sợi nhựa thừa, gạt phôi và chà sạch đầu phun. |
| | `PRIME_LINES` | `INITIAL_TOOL=.. [Tn_TEMP=..]`<br>Tính toán phân bổ slot không chồng lấn trên mép bàn, nung trước tool tiếp theo song song, vẽ đường mồi 3 đường kèm gạt ngang ở Z thấp, giữ lại tool in ban đầu trên đầu in. |
| **Cân chỉnh Tool** | `KTAMV_AUTO_CALIBRATE_ALL_TOOLS` | `[SAMPLES=3] [MAX_SPREAD=0.12] [Z=40]`<br>Quy trình đo tự động tuần tự bù trừ XY cho T1–T4 dựa trên tọa độ camera đã học từ T0 tại Z an toàn (Z=40 mm). |
| | `KTAMV_STATUS` | Báo cáo trạng thái calib camera, tỉ lệ mm/pixel và tọa độ gốc camera đã học. |
| | `CHECK_OFFSETS` | In ra toàn bộ offset XYZ hiện tại của cả 5 tool mà không di chuyển máy. |
| | `CALIBRATION_STATUS` | Báo cáo backend cân chỉnh đang hoạt động và cấu hình chân switch. |
| | `MEASURE_TOOL_HEATUP` | `TOOL=[0..4] [START=150] [TARGET=220] [TIMEOUT=180]`<br>Đo thời gian gia nhiệt và tốc độ tăng nhiệt (°C/s) của từng tool qua bộ đếm thời gian thực 0.5s. |
| **Kiểm tra Động cơ** | `TEST_SPEED` | `[SPEED=..] [ACCEL=..] [ITERATIONS=5]`<br>Kiểm tra tốc độ và gia tốc CoreXY ở Z thấp (Z=30 mm) bên dưới các dock; kiểm tra mất bước qua `GET_POSITION`. |
| | `TEST_Z_SPEED` | `[SPEED=..] [ACCEL=..] [ITERATIONS=5]`<br>Kiểm tra chu trình nâng hạ trục Z đa vòng (Z:10 đến 320 mm); kiểm chứng đồng bộ của 4 động cơ dẫn động đai Z. |
| **Đèn & Quạt** | `LIGHTS_ON` / `OFF` | Bật/tắt dải đèn LED buồng in 40 bóng ở 100% độ sáng (`RED=1 GREEN=1 BLUE=1`). |
| | `BED_FAN_ON` / `OFF` | Điều khiển quạt tuần hoàn buồng in dưới đáy bàn nhiệt (tốc độ 0.0–1.0). |

---

## 5. Hướng dẫn Gỡ cài đặt, Hoàn tác & Bảo trì

### 5.1 Dọn dẹp Hệ thống Tinh gọn (`cleanup-voron.sh`)
Để dọn sạch các bản backup thừa và file rác trên máy in:
```bash
# Xem trước danh sách các file sẽ xóa (dry-run):
bash config/scripts/cleanup-voron.sh

# Thực hiện xóa thực tế:
bash config/scripts/cleanup-voron.sh --apply
```
Script sẽ xóa các file `config.update-backup-*`, `axiscope.bak`, các file markdown nằm lẫn trong config, và các thư mục backup cũ vượt quá 5 bản gần nhất.

### 5.2 Hoàn tác về Bản Cấu hình Trước đó (Rollback)
Mỗi lần chạy `install.sh`, hệ thống tự động tạo một snapshot có dấu thời gian. Nếu cấu hình mới gặp sự cố:
```bash
# 1. Liệt kê các bản sao lưu hiện có:
ls -la ~/printer_data/config_backups/

# 2. Khôi phục từ bản sao lưu mong muốn:
cp -a ~/printer_data/config_backups/config-install-YYYYMMDD-HHmmss/* ~/printer_data/config/

# 3. Khởi động lại Klipper:
sudo systemctl restart klipper
```

### 5.3 Gỡ cài đặt Hoàn toàn (Decoupling)
Để gỡ bỏ hoàn toàn liên kết cấu hình khỏi máy in:
1. **Xóa tích hợp Moonraker Update Manager:** Xóa khối `[update_manager All-Config-Voron]` trong `~/printer_data/config/moonraker.conf`.
2. **Vô hiệu hóa Dịch vụ kTAMV:**
   ```bash
   systemctl --user stop ktamv-server.service
   systemctl --user disable ktamv-server.service
   rm -f ~/.config/systemd/user/ktamv-server.service
   ```
3. **Khôi phục các File Mã nguồn Klipper:**
   ```bash
   # Hoàn tác bản vá tool_crash:
   patch -R -d ~/klipper/klippy/extras -p1 < ~/All-Config-Voron/config/scripts/patches/tool_crash-active-tool-validation.patch
   # Xóa symlink kTAMV:
   rm -f ~/klipper/klippy/extras/ktamv.py ~/klipper/klippy/extras/ktamv_utl.py
   ```
4. **Xóa Thư mục Kho lưu trữ:** `rm -rf ~/All-Config-Voron`.

---

## 6. Ghi công & Lời cảm ơn

Dự án cấu hình sản xuất này được phát triển dựa trên nền tảng của các dự án mã nguồn mở và sáng kiến kỹ thuật xuất sắc từ cộng đồng:

- **[StealthChanger](https://stealthchanger.com/)** bởi *draftsauce* và cộng đồng StealthChanger: Nền tảng cơ khí đổi đầu in đa năng cho dòng máy Voron.
- **[klipper-toolchanger-easy (KTC-Easy)](https://github.com/jwellman80/klipper-toolchanger-easy)** bởi *jwellman80*: Đơn giản hóa động học chuyển động, quỹ đạo dock và quản lý trạng thái toolhead.
- **[kTAMV (Klipper Tool Alignment with Machine Vision)](https://github.com/TypQxQ/kTAMV)** bởi *TypQxQ*: Cân chỉnh tâm đầu phun và tính toán bù trừ sai số XY qua camera nhìn lên.
- **[tool_crash](https://github.com/cekim-git/tool_crash)** bởi *cekim-git*: Giám sát sự hiện diện của tool và cơ chế an toàn chống rơi đầu in.
- **[Cartographer 3D](https://cartographer3d.com/)**: Cảm biến dòng xoáy tốc độ cao và công nghệ dò mặt phẳng chạm đầu phun Touch.
- **[Mainsail](https://mainsail.xyz/)** & **[Mainsail Crew](https://github.com/mainsail-crew)**: Giao diện web điều khiển, streaming Crowsnest, Sonar và hệ thống macro client.
- **[Klippain Shake&Tune](https://github.com/Frix-x/klippain-shaketune)** bởi *Frix-x*: Bộ công cụ đo đạc cộng hưởng cơ khí và tối ưu hóa Input Shaper chuyên nghiệp.
- **[Andrew Ellis Print Tuning Guide](https://ellis3dp.com/)**: Phương pháp luận kiểm thử và tối ưu hóa động học CoreXY.
- **[Voron Design](https://vorondesign.com/)**: Thiết kế máy in 3D CoreXY Voron 2.4.

---

## 7. Phân tích Chuyên sâu Thuật toán & Logic Vận hành

### 7.1 Thuật toán Ngâm nhiệt Co giãn Động (`_PRINT_START_HEAT_SOAK`)
Thay vì áp dụng thời gian ngâm nhiệt cố định gây lãng phí thời gian, hệ thống tính toán thời gian ngâm nhiệt dựa trên chênh lệch nhiệt độ thực tế của bàn in ($\Delta T = T_{\text{bed,target}} - T_{\text{bed,start}}$):

$$\text{Thời gian ngâm} = \begin{cases} 
T_{\text{preset}} & \text{khi } \Delta T > 15^\circ\text{C} \quad (\text{Bàn in nguội hoàn toàn}) \\
\text{làm tròn}(0.20 \times T_{\text{preset}}) & \text{khi } 5^\circ\text{C} < \Delta T \le 15^\circ\text{C} \quad (\text{Bàn in đã ấm sẵn}) \\
0 & \text{khi } \Delta T \le 5^\circ\text{C} \quad (\text{Bàn in đã nóng đủ, bỏ qua ngâm nhiệt})
\end{cases}$$

- **Hằng số theo Vật liệu ($T_{\text{preset}}$):** PLA/TPU: 30s; PETG: 60s; ABS/ASA/PC/NYLON: 90s.
- **Mức độ ưu tiên:** Lệnh thủ công `SOAK=<giây>` có mức ưu tiên cao nhất; tham số `AUTO_SOAK=0` sẽ tắt hoàn toàn ngâm nhiệt tự động.

### 7.2 Logic Bảo vệ Đầu dò Z và Khử Gờ nhựa 2 Giai đoạn
Đối với cơ cấu đổi đầu in dùng đầu phun làm điểm chạm, phôi nhựa mềm bám trên đầu phun là nguyên nhân hàng đầu gây sai lệch Z:
1. **Giai đoạn 1 (Lúc nung bàn):** T0 được đưa tới khay xả và chà sạch trên cọ silicon ở 150 °C trong lúc mâm nhiệt 1000W tiếp tục gia nhiệt.
2. **Giai đoạn 2 (Ngay trước khi Touch Home):** Sau khi hoàn tất ngâm nhiệt và cân bàn QGL, T0 được làm sạch *lần thứ hai* ở 150 °C ngay trước khi thực thi `CARTOGRAPHER_TOUCH_HOME`.
- **Cơ chế Vật lý:** Trong 60–90 giây ngâm nhiệt, nhựa thừa trong buồng nung sẽ rỉ ra một đốm nhỏ. Đốm nhựa mềm này đóng vai trò như một lớp đệm đàn hồi; khi ép chạm vào mặt bàn, nó sẽ bị nén lại và làm biến dạng ngàm khóa của StealthChanger shuttle, dẫn đến sai lệch gốc $Z=0$ từ 0.05–0.15 mm. Việc lau sạch ở 150 °C ngay sát thời điểm chạm đảm bảo sự tiếp xúc trực tiếp giữa kim loại đầu phun và mặt bàn in mà không làm nhựa chảy loang ra.

### 7.3 Nguyên tắc Bất biến Homing An toàn
Cartographer V3 được bắt cố định trực tiếp trên carriage shuttle chứ không gắn trên từng toolhead. Điều này tạo ra một nguyên tắc bất biến sống còn:
- **Tuyệt đối không bao giờ thực hiện đổi tool, trả dock hoặc di chuyển khay xả trước khi hoàn thành lệnh `G28` đầy đủ.** Nếu máy in bị dừng đột ngột khi đang giữ T1..T4, quỹ đạo trả tool về dock bắt buộc phải có một bước nâng Z an toàn (Z-hop). `PRINT_START` thực thi full G28 với bất kỳ toolhead nào đang gắn trên shuttle, nâng Z lên độ cao an toàn ($Z=10$ mm), rồi mới kích hoạt đổi về T0.

### 7.4 Thuật toán Điều tiết Nhiệt & Quạt Sấy Nhựa 4 Vùng (4-Zone Adaptive Drying)
Macro sấy cuộn nhựa (`filament-dryer.cfg`) chạy vòng lặp kín 10 giây một lần, kết hợp mâm nhiệt AC 1000W và quạt tuần hoàn đáy bàn:

```
                  Nhiệt độ Buồng in So với Ngưỡng Mục tiêu
  < (Target - 2°C)      [Target - 2°C .. +3.5°C]      (+3.5°C .. +6°C]      > (Target + 6°C)
┌────────────────────┬─────────────────────────────┬───────────────────┬──────────────────────┐
│  VÙNG 1: GIA NHIỆT │   VÙNG 2: SẤY TỐI ƯU        │  VÙNG 3: GIẢM GIÓ │  VÙNG 4: BẢO VỆ NHIỆT│
│  Tăng quạt (+25%)  │   Quạt cơ bản (40-70%)      │  Hạ quạt (-10%)   │  Hạ quạt (-20%)      │
│  Tối đa: 85% gió   │   + Xung Xả ẩm Định kỳ      │  Tối thiểu: 30%   │  Hạ target bàn -4°C  │
└────────────────────┴─────────────────────────────┴───────────────────┴──────────────────────┘
```

- **Xung Xả ẩm Định kỳ (Periodic Moisture Flush Pulse):** Cứ mỗi 20 phút (1200 giây) sau 15 phút đầu tiên, quạt buồng in tự động tăng tốc thêm +25% (giới hạn 70%) trong vòng 30 giây để đẩy toàn bộ luồng khí ẩm tích tụ ra khỏi buồng in qua khe thoát khí.
- **Bảo vệ Chống Quá nhiệt (Overheat Guard):** Nếu nhiệt độ buồng vượt ngưỡng mục tiêu $>6^\circ\text{C}$, nhiệt độ bàn in sẽ tự động bị bóp giảm $-4^\circ\text{C}$ (không thấp hơn 45 °C) để tránh hiện tượng sợi nhựa trong cuộn bị mềm biến dạng do nhiệt độ chuyển thủy tinh ($T_g$).
- **Chuyển tiếp Quyền sở hữu Tài nguyên (`_DRYER_HANDOFF_TO_PRINT`):** Nếu lệnh in được phát khi máy đang sấy, timer sấy sẽ dừng ngay lập tức mà không ngắt mâm nhiệt hay quạt, giữ nguyên nhiệt độ bàn in cho `PRINT_START` mà không bị gián đoạn.

### 7.5 Thuật toán Thị giác Máy tính & Lọc Phân tán 3 Mẫu kTAMV
Để đạt được độ chính xác quang học dưới 0.02 mm trong điều kiện ánh sáng đa dạng:
- **Thuật toán Nhận diện Đốm sáng Tâm (`find_center_highlight_keypoint`):** Được tích hợp qua bản vá runtime. Khi bộ nhận diện blob mặc định bị phân vân do phản xạ, thuật toán chuyển ảnh sang thang xám, nhị phân hóa ở ngưỡng 245 (`cv2.threshold`), trích xuất các thành phần liên thông (`cv2.connectedComponentsWithStats`) và lọc theo các tiêu chí hình học: diện tích $30 \le A \le 1200\text{ px}$, tỉ lệ co $0.35 \le W/H \le 2.8$, khoảng cách tới tâm quang học $(320, 240) \le 120\text{ px}$. Sau đó chọn ứng viên tối thiểu hóa bộ $(\text{khoảng cách}, -\text{diện tích})$.
- **Lọc Phân tán 3 Mẫu lặp lại (`KTAMV_MEASURE_TOOL_XY`):** Thực hiện 3 chu trình căn tâm độc lập từ Z an toàn ($Z=40$ mm). Tính toán độ phân tán:

$$\Delta X = X_{\max} - X_{\min}, \quad \Delta Y = Y_{\max} - Y_{\min}$$

Nếu $\max(\Delta X, \Delta Y) > 0.12\text{ mm}$, lượt đo sẽ bị hủy bỏ với thông báo lỗi, ngăn chặn hoàn toàn việc nạp sai số quang học vào cấu hình tool.
- **Tắt LED Đầu in khi Đo:** Tự động tắt LED đầu in (`SET_LED ... RED=0 GREEN=0 BLUE=0`) trong lúc camera chụp để loại bỏ hiện tượng lóa sáng trên bề mặt vát của đầu phun.

### 7.6 Thuật toán Mồi Nhựa Đa Tool Dạng Pipeline (`PRIME_LINES`)
- **Tự động Phân chia Tọa độ Slot:** Chia khoảng trống mép bàn khả dụng ($X_{\min} + 30\text{ mm}$ đến $X_{\max} - 30\text{ mm}$) thành các vị trí mồi nhựa riêng biệt không chồng lấn, căn đều theo số lượng tool thực tế được sử dụng trong file in.
- **Gia nhiệt Song song Dạng Đường ống (Pipeline Preheating):** Trong lúc tool $T_n$ đang đùn đường mồi 3 lượt, macro tự động phát lệnh `M104 T{next_t} S{next_temp}` để nung nóng trước tool tiếp theo, triệt tiêu thời gian chờ đợi gia nhiệt tại dock.
- **Đảo ngược Thứ tự Mồi:** Các tool phụ được mồi trước và hạ về nhiệt độ chờ; riêng tool in đầu tiên được mồi sau cùng và giữ nguyên nhiệt độ in, sẵn sàng di chuyển thẳng vào vị trí in lớp đầu tiên.

### 7.7 Watchdog Chống Rơi Tool & Tạm dừng Không Di chuyển (`tool_crash`)
- **Bản vá Khử Xung Ngắt Transients:** Bản gốc của `tool_crash.py` kích hoạt shutdown ngay khi có bất kỳ cạnh xung nào từ chân sensor. Bản vá chuyển hướng ngắt sang hàm `self._sync_expected()`, lọc bỏ hoàn toàn các xung rung cơ học trên các tool đang đỗ trong dock.
- **Cơ chế Xác nhận 2 Chu kỳ:** Thăm dò trạng thái mỗi 0.5 giây và yêu cầu 2 lần thất bại liên tiếp (`watchdog_threshold: 2`) trước khi xác nhận có sự cố rơi tool.
- **Tạm dừng An toàn Tuyệt đối Không Di chuyển (`_TOOL_CRASH_SAFE_PAUSE`):** Khi phát hiện rơi tool trong lúc in, macro thực thi `PAUSE_BASE` và rút nhẹ sợi nhựa *mà tuyệt đối không di chuyển trục X, Y hoặc Z*. Nếu đầu in đã bị tuột ngàm hoặc nghiêng lệch, bất kỳ chuyển động di chuyển nào cũng sẽ gây va quẹt gãy hỏng cơ khí.

### 7.8 Thuật toán Rút Sợi 2 Nấc & Nâng Z An toàn (`PRINT_END`)
- **Nấc 1:** Rút nhanh $-2.0\text{ mm}$ ở tốc độ $F=2700$ để giải phóng áp suất tức thời trong buồng nung.
- **Nấc 2:** Rút tốc độ cao $-8.0\text{ mm}$ kết hợp nâng Z $+5.0\text{ mm}$ đồng thời ở tốc độ $F=12000$ (tổng cộng rút $-10.0\text{ mm}$) để cắt đứt hoàn toàn tơ nhựa kéo dài.
- **Nâng Z An toàn Động:** Luôn nâng Z lên $Z_{\text{safe}} = \min(\max(Z_{\text{hiện tại}} + 10, 50), Z_{\max})$ trước khi tiếp cận dock, tránh va chạm với các vật thể in cao trên bàn.
- **Làm nguội Trước khi Trả Tool:** Hạ nhiệt độ hotend về $0^\circ\text{C}$ *trước* khi gọi `UNSELECT_TOOL`, đảm bảo KTC không bị kẹt lại chờ đợi nhiệt độ tại dock.

### 7.9 Máy Trạng thái LED 10 Mức Ưu tiên & Điều tiết Bus CAN (`fans-leds.cfg`)
- **Phân cấp Ưu tiên Hướng sự kiện:**
  `error` > `toolchange` > `leveling` > `calibrating` > `cleaning` > `heating` > `printing` > `pause` > `complete` > `ready` > `standby`
- **Độ tương phản Trực quan:** Đầu in đang hoạt động phát sáng mạnh; các đầu in đang đỗ trong dock tự động mờ về màu xanh dương đậm (`_SYNC_INACTIVE_LEDS`).
- **Gom Khung Truyền SPI:** Cập nhật LED 1 và 2 với `TRANSMIT=0`, và LED 3 với `TRANSMIT=1`, truyền toàn bộ dữ liệu màu trong một frame duy nhất để chống chớp nháy.
- **Chống Nghẽn Băng thông Bus CAN:** Trong các vòng lặp cập nhật LED qua cả 5 tool, hệ thống chèn lệnh `G4 P10` (nghỉ 10 ms) giữa các tool để tránh làm tràn hàng đợi gói tin CANbus.

### 7.10 Bộ đệm Tham số Input Shaper Động (`_ACTIVE_INPUT_SHAPER`)
Trong hệ thống đổi đầu in, việc gọi lệnh `SET_INPUT_SHAPER` liên tục mỗi khi đổi tool sẽ gây tràn log bảng điều khiển và cơ sở dữ liệu Moonraker. Hệ thống duy trì một biến đệm trong RAM (`_ACTIVE_INPUT_SHAPER`); lệnh `after_change_gcode` chỉ thực thi `SET_INPUT_SHAPER` khi các tham số tần số và bộ lọc thực sự có sự thay đổi so với giá trị hiện hành.