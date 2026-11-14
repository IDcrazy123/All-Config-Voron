# 2026-11-14 — Tạm tắt T2–T4 để bảo trì T2

## Bằng chứng trước sửa

- Người vận hành yêu cầu tắt T2–T4, giữ khả năng in T0, sau đó báo đã tháo T2.
- Ban đầu Moonraker `192.168.1.43:7125` báo `print_stats=standby`, không pause, chưa home, toolchanger chưa khởi tạo, active/detected đều rỗng, heater target T0–T4 và bàn đều 0. Registry còn `[0,1,2,3,4]`.
- `printer.cfg`, `print-macros.cfg`, `T0.cfg`, `T1.cfg` trên máy khớp repository. Include KTC tổng dùng glob `../tools/T*.cfg`, sẽ tiếp tục đòi MCU EBB2 nếu giữ nguyên khi T2 đã tháo.
- Sau khi T2 được tháo, Klipper báo `startup` do đang kết nối lại; máy vẫn standby, không pause, `_PRINT_STATE=idle`, không sấy/benchmark, heater target đều 0. Không chạy lệnh chuyển động.

## Thay đổi và sao lưu

- Sao lưu `printer.cfg` Git/live giống nhau vào `extras/backups/pre-t2-t4-maintenance-20261114-073028/`, SHA-256 `a5bf84212ee4dde36a001ad9f7d401d5c67d7d3a21c26fc21e1ee09bab83d6ad`. Bản live cũng được sao lưu trên máy ở `/home/voron/printer_data/config_backups/pre-t2-t4-maintenance-20261114-073028/printer.cfg`.
- `config/printer.cfg`: thay include KTC tổng bằng các include core theo đúng thứ tự cũ, rồi include riêng T0/T1 và `toolchanger-config.cfg`. Không sửa file KTC readonly hoặc T2–T4.cfg.
- Bỏ tạm 6 section SAVE_CONFIG của PID `extruder2`–`extruder4` và offset `tool T2`–`tool T4`; giá trị gốc giữ trong backup. PID/offset T0/T1, bàn, mesh và Cartographer giữ nguyên.
- Macro `PRINT_START` hiện hữu đã chặn `TOOL=2..4` hoặc `T2_TEMP`–`T4_TEMP` dương trước nhiệt/chuyển động khi các tool không đăng ký, nên không cần sửa macro.

## Kiểm tra và triển khai

- Parser Klipper trên máy đọc bản thử: 201 → 168 section; đúng 33 section của T2–T4 bị loại, không thêm section và không đổi option của các section còn lại. `git diff --check` sạch.
- Sau khi xác nhận hash live vẫn đúng backup, ghi atomically một file `printer.cfg`, gửi Moonraker `RESTART` trả `ok`.
- Sau restart: Klipper `ready`, `print_stats=standby`, `tool_numbers=[0,1]`, không có `tool T2`–`T4` hoặc `extruder2`–`extruder4`, `configfile.warnings=[]`, target bàn/T0/T1 đều 0. File live khớp repository. Không home, gắp tool, gia nhiệt hay in thử trong bước này.

## Vận hành và khôi phục

- In T0 bằng G-code được slice cho `TOOL=0`, không có nhiệt hoặc lệnh T2–T4. Kiểm tra vị trí tool và đường đi trước bản in đầu sau restart; T1 vẫn đăng ký nhưng dock T1 còn cần xác minh cơ khí theo nhật ký 13/11.
- Khi bảo trì xong, nối lại và xác nhận CAN T2–T4, rồi khôi phục include KTC tổng và 6 section SAVE_CONFIG đã bỏ từ backup. Đối chiếu calibration mới phát sinh, chỉ reload lúc máy idle; xác minh registry và từng tool trước khi in nhiều tool.
