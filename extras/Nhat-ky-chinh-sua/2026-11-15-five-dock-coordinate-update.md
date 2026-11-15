# 2026-11-15 — cập nhật tọa độ dock T0–T4

## Dữ liệu đầu vào

Người vận hành cung cấp tọa độ dock theo thứ tự X/Y/Z (mm): T0 30,2/0/333; T1 104/0/330; T2 176/0/331; T3 249,5/0/331; T4 321,5/0/332. Dấu phẩy ở X T0/T3 được hiểu là dấu thập phân.

Trước sửa: Klipper `ready`, registry `[0,1,2,3,4]`, KTC `ready`, shuttle trống, print_stats `standby`, không pause, không sấy, heater targets bằng 0. Các file tool T0–T4 live trùng Git. Bản sao trước thay đổi ở `extras/backups/pre-five-dock-coordinates-20261115-221710/`.

## Thay đổi cấu hình

| Tool | Trước X/Y/Z | Sau X/Y/Z |
| --- | --- | --- |
| T0 | 30.20 / 1.3 / 343 | 30.2 / 0 / 333 |
| T1 | 104 / 0 / 330 | Không đổi |
| T2 | 176 / 1.6 / 343 | 176 / 0 / 331 |
| T3 | 249.5 / 2.5 / 343 | 249.5 / 0 / 331 |
| T4 | 321.5 / 3.1 / 343 | 321.5 / 0 / 332 |

Chỉ sửa `params_park_y/z` trong `config/toolchanger/tools/T0.cfg`, `T2.cfg`, `T3.cfg`, `T4.cfg` và chú thích liên quan. PID, offset tool, đường pickup/dropoff và các pin không đổi.

## Kiểm tra

Preflight trên Pi: tập section không đổi; chỉ bốn section `tool T0/T2/T3/T4` khác live; cả năm tọa độ candidate đúng dữ liệu người vận hành và các điểm trong đường pickup/dropoff nằm trong giới hạn X/Y/Z cấu hình. Chưa thử chuyển động thực tế.

Khi chuẩn bị, `print_stats=standby` nhưng `idle_timeout=Printing` và vị trí toolhead đang thay đổi vì thao tác jog. Người vận hành xác nhận đã dừng; ngay trước triển khai, `idle_timeout=Ready`, shuttle trống, mọi target nhiệt bằng 0, không pause/sấy và cả năm file live vẫn trùng bản sao trước sửa. Đã sao lưu năm file trên Pi tại `/home/voron/printer_data/config-backups/five-dock-coordinates-20261115-221710/`.

Sau khi nạp bốn file và `RESTART`, Klipper `ready`, registry `[0,1,2,3,4]`, không cảnh báo. `INITIALIZE_TOOLCHANGER` xác nhận KTC `ready`, shuttle trống, không di chuyển. Configfile hiệu lực đọc lại đúng năm tọa độ trong bảng. Mọi trục mất trạng thái home sau restart.

## Còn cần xác minh

Kiểm tra lần đầu từng đường gắp/thả có người quan sát; điều kiện giới hạn tọa độ không chứng minh dock không va chạm. Không coi Klipper `ready` là đã kiểm định cơ khí. Sau restart cần home lại trước khi dùng macro đòi hỏi XYZ homed.
