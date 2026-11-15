# 2026-11-15 — Bật lại T3/T4 để thử nghiệm

## Bằng chứng trước sửa

- Người vận hành yêu cầu bật lại T3/T4 để thử nghiệm. Máy `ready`, bản in trước `complete`, không pause, `idle_timeout=Ready`, `_PRINT_STATE=idle`, không sấy/benchmark, đã home `xyz`, shuttle active/detected rỗng, target bàn/T0–T2 đều 0; registry `[0,1,2]`, không cảnh báo.
- Live `printer.cfg`, T3.cfg và T4.cfg khớp Git. `can0` ở `ERROR-ACTIVE` với bus-off/bus-error bằng 0; truy vấn CAN thấy lại UUID T3 `c2465b7c36f8` và T4 `28650279df58` đúng file tool.
- File `printer.cfg` live khớp bản T0–T2 tạm thời, SHA-256 `000c9a1ee7d1570bd4c105721e41df27988a264872ab04e87f6f824fae72fe52`, nên không có calibration mới trong file này từ lúc tắt T3/T4.

## Sao lưu và thay đổi

- Sao lưu bản T0–T2 Git/live vào `extras/backups/pre-t3-t4-test-restore-20261115-194214/` và `/home/voron/printer_data/config_backups/pre-t3-t4-test-restore-20261115-194214/`.
- Khôi phục `config/printer.cfg` từ `extras/backups/pre-t4-filament-sensor-maintenance-20261115-091735/printer.live.cfg`: include KTC tổng T0–T4, PID `[extruder3]`/`[extruder4]` và offset `[tool T3]`/`[tool T4]`. Không sửa file tool, macro, readonly KTC hoặc calibration khác.
- Parser Klipper trên máy: 179 → 201 section, đúng 22 section T3/T4 được thêm, không xóa/đổi option section còn lại. SAVE_CONFIG chỉ thêm bốn section T3/T4.

## Triển khai và kiểm tra sau nạp

- Kiểm tra lại máy idle và hash live, ghi atomically một file `printer.cfg`. Moonraker `RESTART` trả `ok`; lúc chuyển trạng thái, Klipper báo Cartographer còn shutdown. Yêu cầu `FIRMWARE_RESTART` ngay sau đó trả HTTP 503 vì host chưa kết nối; vài giây sau Klipper tự lên `ready`. Không xác định được yêu cầu firmware restart có thực thi hay không.
- Sau đó registry `[0,1,2,3,4]`, `configfile.warnings=[]`, `print_stats=standby`, shuttle rỗng, chưa home, mọi heater target bằng 0; file live khớp Git. PID/offset T3/T4 đúng bản sao lưu. Cảm biến nhựa T3 `enabled=true, filament_detected=true`; T4 `enabled=true, filament_detected=false`. Người vận hành xác nhận T4 chưa nạp nhựa, nên trạng thái `false` phù hợp.
- Chưa thử tín hiệu T4 đổi sang `true` khi nạp nhựa, G28, gắp/thả, gia nhiệt hoặc in T3/T4. Cần nạp nhựa T4 rồi xác nhận tín hiệu sau debounce; quan sát ngàm/dock/detection_pin và bản in đầu trước khi coi thử nghiệm cơ khí hoàn tất.
