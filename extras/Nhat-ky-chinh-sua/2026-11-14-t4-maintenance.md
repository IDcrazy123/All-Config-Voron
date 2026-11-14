# 2026-11-14 — Tạm tắt riêng T4 để bảo trì

## Bằng chứng trước sửa

- Người vận hành yêu cầu tắt T4 để bảo trì, giữ T0–T3.
- Moonraker `192.168.1.43:7125`: Klipper `ready`, bản in trước `complete`, không pause, `idle_timeout=Ready`, `_PRINT_STATE=idle`, không sấy/benchmark, shuttle active/detected rỗng, máy đã home `xyz`, target bàn/T0–T4 đều 0; registry `[0,1,2,3,4]`, không cảnh báo cấu hình.
- Live `printer.cfg` và `T4.cfg` khớp Git. Include KTC tổng dùng glob `../tools/T*.cfg`; cần thay include này để Klipper không tiếp tục nạp MCU EBB4 khi T4 được tháo.

## Sao lưu và thay đổi

- Sao lưu bản Git/live giống nhau vào `extras/backups/pre-t4-maintenance-20261114-200533/`, SHA-256 `a5bf84212ee4dde36a001ad9f7d401d5c67d7d3a21c26fc21e1ee09bab83d6ad`; bản live cũng được lưu trên máy tại `/home/voron/printer_data/config_backups/pre-t4-maintenance-20261114-200533/printer.cfg`.
- `config/printer.cfg`: thay include KTC tổng bằng các include core theo thứ tự cũ, include riêng T0–T3 và `toolchanger-config.cfg`. Bỏ tạm hai section SAVE_CONFIG `[extruder4]` PID và `[tool T4]` offset; các giá trị gốc ở backup. Không sửa T4.cfg, macro hoặc readonly KTC.
- Parser Klipper trên máy: 201 → 190 section, đúng 11 section T4 bị loại, không thêm section hoặc đổi option của section còn lại. SAVE_CONFIG chỉ bỏ `[extruder4]` và `[tool T4]`. File mới có SHA-256 `af24a88f0ec9aa5272b3b96b3b52cc7c944b749eddc2e43b090a8cf9e547e656`.

## Triển khai và khôi phục

- Kiểm tra lại máy idle, shuttle rỗng, target 0 và hash live trước khi ghi atomically một file `printer.cfg`. Moonraker `RESTART` trả `ok`; sau restart Klipper `ready`, registry `[0,1,2,3]`, không còn `tool T4`/`extruder4`, `configfile.warnings=[]`, `print_stats=standby`, chưa home, target bàn/T0–T3 đều 0. File live khớp Git.
- Chưa gắp tool, gia nhiệt hoặc in thử sau reload. Macro `PRINT_START` hiện hữu chặn `TOOL=4` hoặc `T4_TEMP` dương khi T4 không đăng ký; G-code dùng T4 cần slice lại cho tool còn hoạt động.
- Khi bảo trì xong, xác nhận CAN T4, đối chiếu calibration mới rồi khôi phục include KTC tổng và hai section SAVE_CONFIG từ backup. Chỉ reload lúc máy idle; thử detection, dock/ngàm và gắp/thả T4 có giám sát trước khi in T4.
