# 2026-11-22 — Quét bàn theo vùng in của từng bản

## Yêu cầu và trạng thái trước sửa

- Người vận hành yêu cầu dừng hiệu chuẩn trôi nhiệt, ưu tiên gọi `BED_MESH_CALIBRATE ADAPTIVE=1` trong `PRINT_START` như trước với Cartographer.
- Klipper live `ready`, `print_stats=standby`, XYZ đã home, T0 được nhận, heater target 0. `PRINT_START` live đã có `ADAPTIVE=1` nhưng còn chỉ định `METHOD=rapid_scan PROBE_COUNT=25,25 SCAN_SPEED=180 PROFILE=print_adaptive`. `[bed_mesh]` live có `adaptive_margin=10`, lưới tham chiếu 55×55, Z2 và tốc độ 150 mm/s. Macro bọc `BED_MESH_CALIBRATE` tự chọn `METHOD=rapid_scan` khi lệnh không chỉ định phương pháp.
- Một file Orca cũ (`Z belt clamp_ABS_31m13s.gcode`) có bốn `EXCLUDE_OBJECT_DEFINE` trước `PRINT_START`. Preset `0.20mm ABS no hole` đã bật cả hai cờ nhãn; preset ABS và PETG thường để kế thừa không rõ giá trị, preset `0.20mm Multicolor PetG` tắt cả hai.
- Dùng bốn polygon của file thật để kiểm tra endpoint `bed_mesh/dump_mesh` trên máy, không gia nhiệt hoặc di chuyển: với lệnh cũ 25×25 tham chiếu, Klipper tính vùng X152..196/Y138,485..201,126 và lưới thực 4×6. Sau thử đã `EXCLUDE_OBJECT_DEFINE RESET=1`, xác nhận danh sách vật thể trở lại rỗng.

## Thay đổi

- `config/Printer-Setup/print-macros.cfg`: rút lệnh trong `PRINT_START` còn `BED_MESH_CALIBRATE ADAPTIVE=1`. Rapid scan, Z2 và tốc độ mặc định lấy từ macro bọc và `[bed_mesh]`; số điểm tự co từ lưới tham chiếu 55×55. Giữ kiểm tra có object labels trước gia nhiệt.
- `Orca Config/0.20mm ABS.json`, `0.20mm PETG.json`, `0.20mm Multicolor PetG.json`: đặt tường minh `exclude_object=1` và `gcode_label_objects=1`. Preset `0.20mm ABS no hole` đã có giá trị 1 nên không sửa. Ba file live trong `%APPDATA%/OrcaSlicer/user/838ce884-12ee-416b-9e1b-1c7503cf6b5f/process/` khớp từng byte với bản cũ và Orca không chạy, nên đã sao lưu rồi đồng bộ bản mới vào đó. File G-code cũ không có nhãn phải slice lại.
- Backup trước sửa: `extras/backups/pre-adaptive-only-20261122/`.

## Kiểm tra và giới hạn

- Kiểm tra JSON, cú pháp Jinja, trạng thái live và đường quét giả lập không di chuyển. Chưa chạy bản in nóng hay mesh cơ khí mới vì đầu dò thay thế chưa có tap threshold và lỗi MCU digital output chưa xử lý.
- Với vùng in gần toàn bàn, native adaptive có thể dùng gần đủ 55×55 điểm; đây là mật độ tham chiếu của `[bed_mesh]`, không còn giới hạn 25×25 trong lệnh `PRINT_START`.
