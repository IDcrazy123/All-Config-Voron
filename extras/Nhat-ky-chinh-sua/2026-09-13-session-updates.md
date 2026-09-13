# Nhật ký — 2026-09-13

## 1. Dọn dẹp KCC/TKC, đồng bộ cấu hình máy in và tích hợp macro tự động đo kTAMV XY

### Mục tiêu
- Dọn dẹp sạch toàn bộ các dịch vụ, file tạm, thư mục thử nghiệm của KCC (Klipper-Camera-Calibration) và TKC (Tool-Klipper-Calibration) trên máy in thực tế `192.168.1.43`.
- Nghỉ hưu module `tool_calibrator` khỏi cây cấu hình active và đưa vào `extras/retired-configs/2026-09-13-tkc-removal/`.
- Đồng bộ thông số PID thực tế mới nhất của `extruder1` đến `extruder4` và các giá trị offset của 4 tool (`T1`–`T4`) từ máy thật về repository.
- Chuẩn hóa cấu hình, làm sạch comment và xây dựng macro đo tự động tuần tự 5 tool `KTAMV_AUTO_CALIBRATE_ALL_TOOLS` tại tọa độ an toàn `X: 170, Y: 0, Z: 40`.
- Cập nhật Git repository lên `origin/main`.

### File đã sửa đổi
- `config/printer.cfg` — Đồng bộ PID extruder 1–4, cập nhật tool offsets T1–T4 thực tế, gỡ bỏ include và comment liên quan tới TKC/KCC.
- `config/moonraker.conf` — Gỡ bỏ update_manager `tool_calibrator` và include KCC.
- `config/Printer-Setup/calibration-probe.cfg` — Làm sạch các tham chiếu tới TKC, làm sạch comment và tập trung vào kTAMV.
- `config/Printer-Setup/ktamv.cfg` — Bổ sung macro `_KTAMV_CALIBRATE_TOOL` và `KTAMV_AUTO_CALIBRATE_ALL_TOOLS` với tọa độ an toàn `X: 170, Y: 0, Z: 40`.
- `config/scripts/install.sh` — Gỡ bỏ các bước preflight check và exclude rule của TKC.
- `config/tool_calibrator/` — Chuyển toàn bộ vào `extras/retired-configs/2026-09-13-tkc-removal/`.

### Sao lưu
- [pre-cleanup-kcc-tkc-and-ktamv-autocalib-20260913-171300](file:///d:/Desktop/All-Config-Voron-main/Voron%205%20Tool/extras/backups/pre-cleanup-kcc-tkc-and-ktamv-autocalib-20260913-171300/)

### Chi tiết thay đổi
- **Trên máy chủ `voron@192.168.1.43`**:
  - Dừng và xóa `klipper-camera-calibration.service`.
  - Xóa 2 symlink KCC trong `/home/voron/klipper/klippy/extras/`.
  - Xóa sạch các thư mục và file bundle/log/tar.gz của KCC và TKC trong `/home/voron/`.
  - Xóa thư mục `camera_calibration/` và `tool_calibrator/` trong `printer_data/config/`.
  - Gỡ bỏ khối include KCC trong `printer.cfg` và `moonraker.conf`.
- **Trong cấu hình Klipper**:
  - Khởi tạo macro `KTAMV_AUTO_CALIBRATE_ALL_TOOLS` cho phép tự động chuyển tool tuần tự từ T1 đến T4, kiểm tra trạng thái toolchanger, tiếp cận tọa độ an toàn `X170 Y0 Z40`, tắt LED toolhead, lặp căn tâm kTAMV 3 lần, kiểm tra spread $\le 0.12\text{ mm}$ và tự động stage offset.

### Kiểm tra
- Khởi động lại firmware Klipper (`FIRMWARE_RESTART`): Thành công (`ready`).
- Khởi động lại Moonraker: Thành công (`klippy_connected: true`, không có failed component hay cảnh báo).
- Đăng ký macro Klipper: `gcode_macro KTAMV_AUTO_CALIBRATE_ALL_TOOLS` đã được nạp thành công.

### Kết quả
- Hệ thống máy in và kho mã nguồn đã được dọn dẹp sạch sẽ, không còn tàn dư của các dự án thử nghiệm KCC và TKC.
- Hệ thống kTAMV sẵn sàng thực hiện chu trình đo tự động XY an toàn.

---

## 2. Cập nhật Macro đo tự động kTAMV sử dụng tọa độ camera đã học (Learned Origin)

### Mục tiêu
- Thay thế việc hardcode tọa độ `X170 Y0` trong macro `_KTAMV_CALIBRATE_TOOL` và `KTAMV_AUTO_CALIBRATE_ALL_TOOLS` bằng tọa độ động đã học `printer.ktamv.camera_center_coordinates` từ bước thiết lập gốc quy chiếu T0 (`KTAMV_SET_ORIGIN`).

### File đã sửa đổi
- `config/Printer-Setup/ktamv.cfg` — Sử dụng `printer.ktamv.camera_center_coordinates` làm điểm đích tiếp cận tại độ cao `safe_z` (Z40).

### Sao lưu
- [pre-ktamv-learned-origin-20260913-172000](file:///d:/Desktop/All-Config-Voron-main/Voron%205%20Tool/extras/backups/pre-ktamv-learned-origin-20260913-172000/)

### Chi tiết thay đổi
- Macro `_KTAMV_CALIBRATE_TOOL`: Sau khi gắp tool từ dock, đầu in nâng lên `safe_z` ngay tại vị trí hiện tại để đảm bảo an toàn, sau đó bay tới tọa độ camera đã học `origin = printer.ktamv.camera_center_coordinates`.
- Không nhúng bất kỳ tọa độ XY tĩnh nào vào macro, giúp hệ thống hoàn toàn linh hoạt trước mọi thay đổi cơ khí camera.

### Kiểm tra
- Nạp lại firmware Klipper (`FIRMWARE_RESTART`): Thành công (`ready`).

---

## 3. Cập nhật tài liệu kỹ thuật Markdown và chuẩn hóa comment trong hệ thống

### Mục tiêu
- Cập nhật toàn bộ các file `.md` chính của dự án dựa trên việc đọc code thực tế, tuyệt đối không đoán mò.
- Đảm bảo các comment trong các file cấu hình `.cfg` và tài liệu khớp 100% với hiện trạng vận hành.

### File đã sửa đổi
- `README.md` & `README.vi.md` — Cập nhật bảng offset thực tế mới nhất, ghi nhận việc nghỉ hưu của TKC/KCC và macro tự động `KTAMV_AUTO_CALIBRATE_ALL_TOOLS`.
- `config/README.md` & `config/README.vi.md` — Cập nhật chuỗi include của `printer.cfg`, làm rõ vai trò kTAMV là backend cân chỉnh XY duy nhất hiện hành.
- `extras/docs/README.md` & `extras/docs/README.vi.md` — Thêm thư mục nghỉ hưu `extras/retired-configs/2026-09-13-tkc-removal/` và snapshot rollback mới.
- `.agents/PROJECT.md` — Cập nhật hiện trạng hệ thống cân chỉnh, bỏ các plugin cũ.
- `.agents/DIRECTORY.md` — Cập nhật cấu trúc thư mục, ghi nhận `retired-configs/2026-09-13-tkc-removal/` và bỏ `tool_calibrator/`.
- `.agents/KNOWN_ISSUES.md` — Khôi phục cấu trúc file sạch sẽ, ghi chú trạng thái nghỉ hưu của các issue TKC ngày 2026-09-13.
- `.agents/TODO.md` — Đánh dấu hoàn thành các hạng mục gỡ KCC/TKC, macro đo tự động và dọn dẹp tài liệu.
- `.agents/DECISIONS.md` — Bổ sung quyết định kỹ thuật ngày 2026-09-13 về việc chuẩn hóa kTAMV và cơ chế tọa độ học.
- `.agents/CHANGELOG.md` — Bổ sung phiên bản [1.7.0] — 2026-09-13.

### Kiểm tra
- Toàn bộ các file `.md` và `.cfg` đã được kiểm tra cú pháp, đường dẫn và tính nhất quán với code thực tế.

---

## 4. Cập nhật tọa độ công tắc Axiscope Z và rút gọn/ẩn các macro kTAMV phụ

### Mục tiêu
- Cập nhật tọa độ vật lý mới của công tắc vi mô đo Z (Axiscope switch): `X: 68.0, Y: -8.0, Z: 2.0`.
- Kích hoạt lại module `[axiscope]` trong `calibration-probe.cfg` để hỗ trợ đo tự động chênh lệch Z bằng lệnh `CALIBRATE_ALL_Z_OFFSETS`.
- Rút gọn bảng macro trên giao diện Mainsail: ẩn các macro phụ trợ kTAMV bằng tiền tố `_` (`_KTAMV_SETUP`, `_KTAMV_MEASURE_ACTIVE_TOOL_XY`, `_KTAMV_APPLY_ACTIVE_TOOL_XY`), chỉ giữ lại macro chính `KTAMV_AUTO_CALIBRATE_ALL_TOOLS` và macro kiểm tra `KTAMV_STATUS`.

### File đã sửa đổi
- `config/Printer-Setup/calibration-probe.cfg` — Kích hoạt `[axiscope]` với tọa độ `zswitch_x_pos: 68.0`, `zswitch_y_pos: -8.0`, `zswitch_z_pos: 2.0`.
- `config/Printer-Setup/ktamv.cfg` — Đổi tên các macro helper thành `_KTAMV_SETUP`, `_KTAMV_MEASURE_ACTIVE_TOOL_XY`, `_KTAMV_APPLY_ACTIVE_TOOL_XY`.

### Sao lưu
- [pre-axiscope-update-20260913-174800](file:///d:/Desktop/All-Config-Voron-main/Voron%205%20Tool/extras/backups/pre-axiscope-update-20260913-174800/)

### Kiểm tra
- Nạp cấu hình sang máy in `192.168.1.43` và khởi động lại firmware Klipper (`FIRMWARE_RESTART`): Thành công (`ready`).
- Lệnh Moonraker help xác nhận: các lệnh `CALIBRATE_ALL_Z_OFFSETS`, `MOVE_TO_ZSWITCH`, `PROBE_ZSWITCH` đã sẵn sàng; các macro helper kTAMV đã được ẩn khỏi bảng điều khiển Mainsail.

