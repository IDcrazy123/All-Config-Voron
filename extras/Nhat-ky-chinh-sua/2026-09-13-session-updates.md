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
- Hệ thống kTAMV sẵn sàng thực hiện chu trình đo tự động XY an toàn tại `X170 Y0 Z40`.
