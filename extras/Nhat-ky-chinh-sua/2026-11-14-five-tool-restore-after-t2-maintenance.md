# 2026-11-14 — Khôi phục T2–T4 sau bảo trì T2

## Bằng chứng trước sửa

- Người vận hành báo đã bảo trì xong T2 và yêu cầu bật lại T2–T4.
- Moonraker `192.168.1.43:7125`: Klipper `ready`, bản in trước `complete`, không pause, `idle_timeout=Idle`, `_PRINT_STATE=idle`, không sấy/benchmark, shuttle rỗng (active/detected `None`), chưa home, target bàn/T0/T1 đều 0; registry `[0,1]`, không có cảnh báo cấu hình.
- Live `printer.cfg`, `T2.cfg`, `T3.cfg`, `T4.cfg` khớp repository. `can0` ở `ERROR-ACTIVE`, bộ đếm bus-off/bus-error bằng 0; truy vấn CAN bằng Klipper venv thấy lại UUID T2 `4ad9d622a836`, T3 `c2465b7c36f8`, T4 `28650279df58` đúng với các file tool.
- Không có thay đổi calibration trong `printer.cfg` kể từ khi tắt T2–T4: file live khớp Git, các section SAVE_CONFIG còn nạp giữ nguyên so với bản sao lưu trước bảo trì.

## Sao lưu và thay đổi

- Sao lưu `printer.cfg` chế độ T0/T1 vào `extras/backups/pre-five-tool-restore-20261114-121710/` và `/home/voron/printer_data/config_backups/pre-five-tool-restore-20261114-121710/`; SHA-256 `9f620f3cfc1226d12de5e7ff0e0634351deb6ae9395e3589e27a5e3dc05cf534`.
- Khôi phục `config/printer.cfg` từ `extras/backups/pre-t2-t4-maintenance-20261114-073028/printer.live.cfg`: include KTC tổng với glob T0–T4 và 6 section SAVE_CONFIG PID `extruder2`–`extruder4`/offset `tool T2`–`tool T4`. Không đổi file tool, macro, readonly KTC hay calibration khác.
- Bản thử qua parser Klipper: 168 → 201 section; đúng 33 section T2–T4 được thêm, không xóa hoặc đổi option của section còn lại. Trong SAVE_CONFIG đúng 6 section kể trên được thêm, không đổi section giữ lại.

## Triển khai và giới hạn xác minh

- Kiểm tra lại máy idle và hash live, ghi atomically đúng một file `printer.cfg`. Moonraker `RESTART` trả `ok` nhưng lần khởi động đầu báo Cartographer còn shutdown; `FIRMWARE_RESTART` tiếp theo đưa Klipper về `ready`.
- Sau khởi động: `tool_numbers=[0,1,2,3,4]`, T2–T4 và `extruder2`–`extruder4` có mặt trong cấu hình nạp, `configfile.warnings=[]`, `print_stats=standby`, shuttle rỗng, chưa home, mọi heater target bằng 0. File live khớp Git. T2 đọc khoảng 25°C, T3/T4 khoảng 35°C khi target 0; không dùng các số này để xác nhận độ chính xác cảm biến.
- Chưa chạy G28, gắp/thả, gia nhiệt, PID hoặc in thử. Người vận hành cần quan sát dock/ngàm/detection_pin T2 và thực hiện lượt gắp/thả cùng bản in đầu có giám sát trước khi coi T2 đã kiểm chứng cơ khí. T1 vẫn còn các lưu ý căn dock từ nhật ký 13/11.
