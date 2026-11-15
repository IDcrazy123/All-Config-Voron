# 2026-11-15 — Tạm tắt T4 để bảo trì cảm biến nhựa

## Trạng thái trước sửa

- Người vận hành yêu cầu tắt T4 để bảo trì cảm biến nhựa; không có dữ liệu xác định lỗi cụ thể của cảm biến.
- Moonraker `192.168.1.43:7125`: Klipper `ready`, `print_stats=standby`, không pause, `idle_timeout=Ready`, `_PRINT_STATE=idle`, không sấy/benchmark, shuttle active/detected rỗng, chưa home, mọi heater target bằng 0; registry `[0,1,2,3,4]`, không cảnh báo cấu hình.
- Live `printer.cfg` và `T4.cfg` khớp Git. Macro `PRINT_START` hiện hữu chặn `TOOL=4` hoặc `T4_TEMP` dương khi T4 không đăng ký.

## Sao lưu, thay đổi và kiểm tra

- Sao lưu bản Git/live giống nhau vào `extras/backups/pre-t4-filament-sensor-maintenance-20261115-091735/` và bản live trên máy ở `/home/voron/printer_data/config_backups/pre-t4-filament-sensor-maintenance-20261115-091735/`; SHA-256 `a5bf84212ee4dde36a001ad9f7d401d5c67d7d3a21c26fc21e1ee09bab83d6ad`.
- Khôi phục đúng cấu hình T0–T3 đã thử ngày 14/11 trong `config/printer.cfg`: include KTC core và T0–T3 riêng; bỏ tạm SAVE_CONFIG PID `[extruder4]` và offset `[tool T4]`. Không sửa T4.cfg, macro hoặc readonly KTC.
- Parser Klipper trên máy: 201 → 190 section, đúng 11 section của T4 bị loại, không thêm/đổi option section khác. SAVE_CONFIG chỉ bỏ hai section T4. File mới có SHA-256 `af24a88f0ec9aa5272b3b96b3b52cc7c944b749eddc2e43b090a8cf9e547e656`.

## Triển khai và khôi phục

- Kiểm tra lại máy idle, shuttle rỗng, target 0 và hash live trước khi ghi atomically một file `printer.cfg`. Moonraker `RESTART` trả `ok`. Sau restart Klipper `ready`, registry `[0,1,2,3]`, không còn `tool T4`, `extruder4` hay `filament_sensor_T4`, `configfile.warnings=[]`, `print_stats=standby`, target bàn/T0–T3 đều 0. File live khớp Git.
- Chưa gắp tool, gia nhiệt hoặc in thử sau reload. Khi bảo trì xong, xác nhận CAN T4, đối chiếu calibration mới rồi khôi phục include KTC tổng và hai section SAVE_CONFIG T4 từ backup. Chỉ reload lúc máy idle; kiểm tra cảm biến nhựa T4 và gắp/thả có giám sát trước bản in T4.
