# 2026-11-15 — khôi phục T0–T4 để đo lại dock

## Yêu cầu và trạng thái trước khi đổi

Người vận hành yêu cầu bật lại tất cả tool, khôi phục cấu hình để đo lại vị trí dock toàn bộ. Trước triển khai: Klipper `ready`, print_stats `cancelled` nhưng máy idle, không pause/sấy, mọi target nhiệt bằng 0, KTC `ready` với registry `[1]`, shuttle trống (`active=detected=-1`), XYZ đã home từ thao tác trước. Ba file production `printer.cfg`, `print-macros.cfg`, `T1.cfg` trùng Git chế độ T1-only. Cảm biến nhựa T1 hiện là `true`.

Lệnh `canbus_query.py can0` thấy bốn UUID EBB0/EBB2/EBB3/EBB4 chưa được cấu hình trong chế độ T1-only; EBB1 và Cartographer đang hoạt động với Klipper. So sánh live/Git của các file khác thấy T3 live dùng `switch_pin: ^EBB3:PB8`, Git còn PB9; `hardware.cfg` chỉ khác hai dòng chú thích về smooth_time/pwm_cycle_time (không bật các tùy chọn đó). Giữ file live T3/hardware và đồng bộ Git theo chúng.

## Thay đổi

- Khôi phục `config/printer.cfg`, `config/Printer-Setup/print-macros.cfg`, `config/toolchanger/tools/T1.cfg` đúng bản năm-tool trong `extras/backups/pre-t0-removal-t1-only-20261115-195358/`. Các tool T0–T4, PID và offset trước chế độ T1-only được nạp lại; T1 trở về `extruder1`, Z offset 0,1665.
- Đồng bộ `config/toolchanger/tools/T3.cfg` theo live: chân cảm biến PB9 → PB8. Đồng bộ chú thích `config/Printer-Setup/hardware.cfg` theo live; không đổi thông số runtime của bàn nhiệt.
- Backup trước thao tác trong `extras/backups/pre-five-tool-dock-survey-20261115-214942/` và trên Pi tại `/home/voron/printer_data/config-backups/five-tool-dock-survey-20261115-214942/`.

## Xác minh

- Preflight trên Pi: candidate có 201 section, đủ T0–T4, T1 ánh xạ `extruder1`, T3 dùng PB8; mọi G-code template parse được và SAVE_CONFIG thêm lại các PID/offset cần thiết.
- `RESTART` đầu báo `Can not update MCU 'EBB1' config as it is shutdown`. Một `FIRMWARE_RESTART` sau đó đưa Klipper về `ready`.
- Sau reload: registry `[0,1,2,3,4]`, KTC `ready`, shuttle trống, không có cảnh báo, mọi target nhiệt 0. PID T0 23,911/7,971/17,933; PID T1 28,787/9,596/21,590; offset T1 -0,139/-0,341/0,1665; T3 sensor pin live `^EBB3:PB8`. Cảm biến nhựa lần lượt T0–T4 là true/true/false/false/false.

## Chờ đo tại máy

Không chạy home, gắp/thả, gia nhiệt hoặc in trong lượt khôi phục này. Cấu hình in chuẩn đã trở lại, bao gồm đường tự thả tool khi kết thúc/hủy in; **không bắt đầu in trước khi dock đã được đo và kiểm tra có người quan sát**, đặc biệt T1 hiện vẫn dùng tọa độ tạm X104 Y0 Z330. Trước mỗi lần thử gắp/thả, xác nhận tool đang ở đúng dock hoặc shuttle và đường đi không vướng. `ready` chỉ xác nhận cấu hình/MCU, chưa xác nhận cơ khí.
