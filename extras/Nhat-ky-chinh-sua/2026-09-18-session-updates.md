# Nhật ký Cập nhật Hệ thống — 2026-09-18

**Mục tiêu chính trong phiên:**
- Gỡ bỏ hoàn toàn backend thị giác máy tính kTAMV khỏi máy in thực tế (`192.168.1.43`) và kho cấu hình do hiện tượng quang học phản xạ chóp nozzle gây sai lệch kết quả căn tâm tự động.
- Cài đặt và cấu hình hoàn chỉnh hệ thống Axiscope (Web Interface cổng 3000 + Klipper extension `axiscope.py`) để đo sai lệch bù trừ XYZ (Manual Crosshair Camera cho XY, công tắc microswitch tiếp xúc PF2 cho Z).

---

## 1. Gỡ bỏ Hoàn toàn kTAMV Khỏi Máy In Thật & Kho Cấu Hình Production

### Mục tiêu
- Loại bỏ triệt để runtime kTAMV, virtualenv, systemd service và các liên kết symlink Klipper khỏi máy in.
- Dọn dẹp các patch, shell script và macro kTAMV, chuyển toàn bộ sang lưu trữ tại `extras/retired-configs/2026-09-18-ktamv-removal/`.
- Loại bỏ ràng buộc preflight kTAMV trong `config/scripts/install.sh`.

### File đã sửa đổi
- `config/printer.cfg` — Xóa bỏ dòng `[include Printer-Setup/ktamv.cfg]`, cập nhật ghi chú hệ thống.
- `config/scripts/install.sh` — Gỡ bỏ khối kiểm tra bắt buộc kTAMV runtime/venv/service/patches.
- `config/Printer-Setup/ktamv.cfg` — Chuyển sang `extras/retired-configs/2026-09-18-ktamv-removal/ktamv.cfg`.
- `config/scripts/ktamv/` — Chuyển sang `extras/retired-configs/2026-09-18-ktamv-removal/ktamv-scripts/`.
- `config/scripts/patches/ktamv-*` — Chuyển sang `extras/retired-configs/2026-09-18-ktamv-removal/`.

### Sao lưu
- [pre-remove-ktamv-install-axiscope-20260918-163000](file:///d:/Desktop/All-Config-Voron-main/Voron%205%20Tool/extras/backups/pre-remove-ktamv-install-axiscope-20260918-163000/)

### Thao tác trên máy in thật `192.168.1.43`:
1. Dừng và vô hiệu hóa user systemd service:
   ```bash
   systemctl --user stop ktamv-server.service
   systemctl --user disable ktamv-server.service
   rm -f ~/.config/systemd/user/ktamv-server.service
   systemctl --user daemon-reload
   ```
2. Xóa các symlink extension trong Klipper:
   ```bash
   rm -f ~/klipper/klippy/extras/ktamv.py ~/klipper/klippy/extras/ktamv_utl.py
   rm -rf ~/klipper/klippy/extras/__pycache__/ktamv*
   ```
3. Xóa thư mục runtime & virtual environment:
   ```bash
   rm -rf ~/kTAMV ~/ktamv-env
   ```
4. Xóa file config kTAMV trên máy in:
   ```bash
   rm -f ~/printer_data/config/Printer-Setup/ktamv.cfg
   ```

### Kết quả
- Toàn bộ tàn dư kTAMV đã được dọn sạch khỏi host BTT CM4 và kho cấu hình.

---

## 2. Cài đặt & Cấu hình Dịch vụ Web Axiscope (Port 3000) & Extension Klipper

### Mục tiêu
- Triển khai ứng dụng Axiscope (Upstream Nic335) để phục vụ việc căn chỉnh tọa độ XY đầu in bằng giao diện web trực quan, ngắm tâm thủ công qua crosshair (dấu chữ thập), loại bỏ hoàn toàn hiện tượng thuật toán quang học bị kéo lệch bởi quầng sáng nozzle.
- Tích hợp extension Klipper `axiscope.py` và cấu hình module `[axiscope]` trên chân microswitch `^PF2` tại tọa độ đo thực tế `(X: 80, Y: -7, Z: 2)` với cơ chế gia nhiệt 150°C và nâng Z an toàn $\ge 15\text{ mm}$.

### File đã sửa đổi
- `config/Printer-Setup/calibration-probe.cfg` — Thay thế section `[tools_calibrate]` và macro `CALIBRATE_ALL_Z_OFFSETS` cũ bằng section `[axiscope]`, cập nhật macro `CALIBRATION_STATUS`.
- `config/moonraker.conf` — Bổ sung section `[update_manager axiscope]`.

### Thao tác trên máy in thật `192.168.1.43`:
1. Clone mã nguồn Axiscope chính thức:
   ```bash
   git clone https://github.com/nic335/Axiscope.git ~/axiscope
   ```
2. Thiết lập Python Virtual Environment & cài đặt thư viện cần thiết:
   ```bash
   python3 -m venv ~/axiscope/axiscope-env
   ~/axiscope/axiscope-env/bin/pip install --upgrade pip
   ~/axiscope/axiscope-env/bin/pip install flask waitress
   ```
3. Thiết lập user systemd service `~/.config/systemd/user/axiscope.service` (không yêu cầu quyền sudo):
   - Chạy ứng dụng Flask trên `0.0.0.0:3000`.
   - Đã kích hoạt tự khởi động cùng hệ thống: `systemctl --user enable axiscope.service` và bật `loginctl enable-linger voron`.
4. Tạo symlink Klipper extension:
   ```bash
   ln -sf /home/voron/axiscope/klippy/extras/axiscope.py /home/voron/klipper/klippy/extras/axiscope.py
   ```
5. Đăng ký service với Moonraker trong `~/printer_data/moonraker.asvc`.

### Kiểm tra
- **Dịch vụ Web Axiscope:** Kiểm tra qua `curl -sI http://127.0.0.1:3000` trả về `HTTP/1.1 200 OK` (Server: Werkzeug/Python 3.11).
- **Moonraker Update Manager:** `machine/update/status` nhận diện thành công `axiscope` phiên bản `v1.1-31` ở trạng thái sạch (`pristine: true`).
- **Klipper Restart (`FIRMWARE_RESTART`):**
  - Klipper nạp cấu hình thành công và đạt trạng thái `Printer is ready`.
  - Không có xung đột `tools_calibrate` hay `probe_multi_axis`.
  - Đối tượng Moonraker `printer.objects.query?axiscope` phản hồi:
    `endstop_x: 80.0, endstop_y: -7.0, endstop_z: 2.0`.
  - Lệnh `QUERY_ENDSTOPS` phản hồi: `Axiscope:open stepper_x:open stepper_y:open stepper_z:open`.
  - Lệnh `CALIBRATION_STATUS` phản hồi đầy đủ thông tin backend:
    `echo: Calibration backends: Axiscope (Web UI port 3000 camera XY + PF2 microswitch Z); Cartographer Touch (Z)`.

---

## 3. Hướng Dẫn Sử Dụng Axiscope Đo Bù Trừ XYZ

### A. Quy trình đo lệch tâm XY (Camera Web Interface):
1. Đặt gá camera hướng lên trên bàn in tại vị trí nhìn rõ đầu phun.
2. Mở trình duyệt truy cập: `http://192.168.1.43:3000`.
3. Chọn máy in và chọn luồng camera Crowsnest.
4. Home máy in (`G28`), gắp Tool 0 (`T0`).
5. Dùng cụm phím Jog điều khiển đưa vòi phun T0 vào chính giữa tâm vòng ngắm (crosshair).
6. Nhấn nút **Capture Position** để khóa tọa độ gốc tham chiếu của T0.
7. Đổi sang tool cần đo (ví dụ `T1`), đưa nozzle T1 vào tâm vòng ngắm crosshair.
8. Nhấn các trục **X** và **Y** trên bảng điều hướng bên cạnh: Axiscope sẽ tự động tính toán ra giá trị chênh lệch và hiển thị offset mới.

### B. Quy trình đo lệch độ cao Z (Microswitch Switch PF2):
- Chạy lệnh G-code:
  ```gcode
  CALIBRATE_ALL_Z_OFFSETS
  ```
- Macro sẽ tự động:
  1. Gia nhiệt 150°C cho toàn bộ 5 đầu in và chờ T0 đạt 150°C.
  2. Nâng Z an toàn $\ge 15\text{ mm}$ trước khi gắp từng tool.
  3. Lần lượt gắp T0 $\rightarrow$ T4, tiếp cận công tắc microswitch tại `(X: 80, Y: -8, Z: 3)` và chạm 10 mẫu để lấy giá trị trung bình chính xác.
  4. Trả về T0, tắt toàn bộ nhiệt và in bảng kết quả `gcode_z_offset` của từng đầu in lên console Mainsail.

---

## 4. Gỡ bỏ Macro Đo Z Bằng Cartographer & Cập nhật Tọa độ Cữ Switch Axiscope (80 : -8 : 3)

### Mục tiêu
- **Gỡ bỏ macro `MEASURE_ALL_Z_CARTOGRAPHER`:** Do các đầu phun TZ V6 có chiều dài cơ học ngắn dài khác nhau, khoảng cách tương đối từ cuộn cảm ứng eddy-current coil của Cartographer cố định trên shuttle tới mặt bàn in khi các nozzle khác nhau chạm bàn dao động bất đối xứng (có nozzle làm coil cách bàn $>3.0\text{ mm}$, có nozzle làm coil sát bàn $<2.5\text{ mm}$), vượt ngoài dải tuyến tính tối ưu 2.5–3.0 mm của coil. Do đó phương pháp chạm bàn bằng Cartographer không hoàn hảo để đo tương quan giữa các tool.
- **Cập nhật tọa độ công tắc microswitch cữ Z của Axiscope:**
  - Tọa độ mới đo đạc chuẩn xác: **`X: 80.0, Y: -8.0, Z: 3.0`**.

### File đã sửa đổi
- `config/Printer-Setup/calibration-probe.cfg` — Xóa macro `[gcode_macro MEASURE_ALL_Z_CARTOGRAPHER]`, cập nhật section `[axiscope]` với `zswitch_x_pos: 80.0`, `zswitch_y_pos: -8.0`, `zswitch_z_pos: 3.0`, cập nhật `CALIBRATION_STATUS`.
- `config/toolchanger/toolchanger-config.cfg` — Cập nhật `_CALIBRATION_SWITCH` với `variable_x: 80`, `variable_y: -8`, `variable_z: 15`, `variable_contact_z: 3`.
- `.agents/PROJECT.md` — Đồng bộ bảng thông số phần cứng Z-offset switch.

### Sao lưu
- [pre-remove-cartographer-z-macro-update-switch-80-minus8-3-20260918-164800](file:///d:/Desktop/All-Config-Voron-main/Voron%205%20Tool/extras/backups/pre-remove-cartographer-z-macro-update-switch-80-minus8-3-20260918-164800/)

### Kiểm tra
- Triển khai file cấu hình sang máy in qua SCP.
- Gửi lệnh `FIRMWARE_RESTART`: Thành công (`Printer is ready`).
- Truy vấn Klipper objects:
  - `printer.objects.query?axiscope` trả về: `endstop_x: 80.0, endstop_y: -8.0, endstop_z: 3.0`.
  - `printer.objects.query?gcode_macro _CALIBRATION_SWITCH` trả về: `x: 80, y: -8, z: 15, contact_z: 3`.

---

## 5. Dọn Dẹp Toàn Diện Tài Liệu Thời Cũ Lỗi Thời & File Python Test Cũ Ra Khỏi Máy & Dự Án

### Mục tiêu
- Dọn dẹp sạch sẽ các file `.py` test thử nghiệm cũ thời TKC, các thư mục clone thử nghiệm và các bản sao config cũ ở thư mục gốc workspace để dự án tinh gọn, dễ quan sát, chỉnh sửa và cập nhật.
- Dọn dẹp trên máy in thật: xóa các file backup sinh ra từ `SAVE_CONFIG` trong `config/` và các patch kTAMV cũ trong `scripts/patches/`.

### File đã xử lý
1. **Lưu trữ bảo toàn (Archive Backup):**
   - Nén toàn bộ tàn dư `.tkc-*` vào [legacy-tkc-archive.zip](file:///d:/Desktop/All-Config-Voron-main/Voron%205%20Tool/extras/backups/pre-cleanup-legacy-test-files-20260918-165500/legacy-tkc-archive.zip).
   - Sao lưu `printer.cfg` và `print-macros.cfg` tàn dư ở root workspace.
2. **Dọn dẹp thư mục gốc workspace (`All-Config-Voron-main/`):**
   - Xóa toàn bộ các thư mục và file test: `.tkc-20260908`, `.tkc-latest`, `.tkc-review`, `.tkc-*.py`, `.tkc-*.json`.
   - Xóa các file bản sao cũ gây nhầm lẫn: `printer.cfg`, `print-macros.cfg`, `extras/`, `Voron`, `__pycache__`.
   - Thư mục gốc hiện chỉ còn đúng các thành phần quản trị AI (`.agents`, `.clinerules`, `.cursorrules`, `.github`, `.roo`, `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`) và thư mục Git repo chính duy nhất **`Voron 5 Tool/`**.
3. **Dọn dẹp trên máy in thật `192.168.1.43`:**
   - Xóa các file backup config rác: `~/printer_data/config/printer-20260917_*.cfg`.
   - Xóa các patch kTAMV cũ: `~/printer_data/config/scripts/patches/ktamv-*.patch`.

### Kết quả
- Toàn bộ máy in và kho dự án trở nên tinh gọn, sạch sẽ 100%, không còn bất kỳ tài liệu hay script test cũ nào gây rối mắt.
