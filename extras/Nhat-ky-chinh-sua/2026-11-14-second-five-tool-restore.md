# 2026-11-14 — Bật lại T2–T4 sau lần bảo trì thứ hai

## Bằng chứng trước sửa

- Người vận hành yêu cầu bật lại T2–T4. Máy `ready`, `print_stats=standby`, không pause, `idle_timeout=Ready`, `_PRINT_STATE=idle`, không sấy/benchmark, chưa home, shuttle active/detected rỗng, target bàn/T0/T1 đều 0; registry `[0,1]`, không cảnh báo cấu hình.
- File `printer.cfg`, T2.cfg, T3.cfg, T4.cfg live khớp Git. `can0` ở trạng thái `ERROR-ACTIVE` với bộ đếm bus-off/bus-error bằng 0; truy vấn CAN thấy UUID T2 `4ad9d622a836`, T3 `c2465b7c36f8`, T4 `28650279df58` đúng với file tool.
- `printer.cfg` live khớp bản T0/T1 đã lưu, SHA-256 `9f620f3cfc1226d12de5e7ff0e0634351deb6ae9395e3589e27a5e3dc05cf534`; không có calibration mới trong file này từ lúc tắt.

## Sao lưu và thay đổi

- Sao lưu bản T0/T1 trước sửa vào `extras/backups/pre-five-tool-restore-20261114-124428/` và `/home/voron/printer_data/config_backups/pre-five-tool-restore-20261114-124428/`.
- Khôi phục `config/printer.cfg` từ `extras/backups/pre-second-t2-t4-maintenance-20261114-122627/printer.live.cfg`: include KTC tổng T0–T4, PID `extruder2`–`extruder4` và offset `tool T2`–`tool T4`. Không đổi macro, file tool, readonly KTC hoặc calibration còn lại.
- Parser Klipper trên máy: 168 → 201 section, đúng 33 section T2–T4 được thêm, không bỏ/đổi section cũ. SAVE_CONFIG chỉ thêm đúng 6 section PID/offset T2–T4.

## Triển khai và xác minh

- Sau khi kiểm tra lại máy idle và hash live, ghi atomically một file `printer.cfg`. Moonraker `RESTART` trả `ok` nhưng Cartographer còn shutdown khi cấu hình; `FIRMWARE_RESTART` tiếp theo đưa Klipper về `ready`.
- Sau restart: registry `[0,1,2,3,4]`, T2–T4 và `extruder2`–`extruder4` có mặt, `configfile.warnings=[]`, `print_stats=standby`, shuttle rỗng, chưa home, mọi heater target bằng 0. File live khớp Git.
- Chưa thử G28, gắp/thả, gia nhiệt hoặc in T2 sau bảo trì. Người vận hành cần quan sát dock/ngàm/detection_pin T2 và thử gắp/thả cùng bản in đầu có giám sát. Lưu ý dock T1 từ nhật ký 13/11 vẫn còn hiệu lực.
