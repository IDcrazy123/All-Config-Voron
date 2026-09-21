# Hướng dẫn Vận hành StealthChanger Production

[English](huong-dan-he-thong-stealthchanger.en.md) | [Tiếng Việt](huong-dan-he-thong-stealthchanger.md)

## Quyền sở hữu backend

- KTC-Easy quản lý gắp/thả tool, trạng thái tool active, đường dock và macro readonly.
- KTC-Easy `tools_calibrate` quản lý thử nghiệm SexBolt XYZ có người giám sát qua microswitch `^PF2`.
- Cartographer quản lý home Z, chuẩn Touch, adaptive bed mesh và đo rung.
- OrcaSlicer quản lý lựa chọn theo filament/process như pressure advance và prime tower.

Không trộn quy trình kTAMV, ToolVision, TKC/KCC, Axiscope hoặc cấu hình SexBolt cũ với lần thử active.

## Trước khi in

1. Xác nhận Klipper ready và không có lỗi MCU/CAN.
2. Kiểm tra cả năm dock, không có tool nào gài nửa chừng.
3. Đối chiếu tool KTC báo active với tool đang gắn vật lý.
4. Làm sạch nozzle chuẩn nếu sắp chạy Cartographer Touch hoặc SexBolt.
5. Kiểm tra Orca đã chọn đúng machine năm tool, process và mapping filament.

## Luồng in bình thường

`PRINT_START` nhận tool đầu tiên, nhiệt từng tool, nhiệt bàn và vật liệu từ OrcaSlicer. Macro nhận quyền từ dryer nếu cần, home an toàn, chọn T0 sau homing, gia nhiệt/ngâm nhiệt, chạy QGL và Cartographer, vệ sinh nozzle, prime đúng các tool được dùng và để tool in đầu tiên ở trạng thái active.

`PRINT_END` retract, nâng Z, trả tool vào dock, đỗ shuttle rỗng, tắt heater/quạt part, xóa offset/mesh và hẹn tắt quạt buồng sau cooldown.

Dùng `PAUSE`/`RESUME` thay vì tự di chuyển tool. `RESUME` khởi tạo KTC và xác nhận tool hiện diện trước khi tiếp tục.

## Hiệu chuẩn tool

1. Sau restart, chạy `SEXBOLT_QUERY` khi nhả và khi nhấn tay công tắc; chỉ tiếp tục khi kết quả lần lượt là `open` và `TRIGGERED`.
2. Home XYZ, khởi tạo toolchanger, xác nhận tool detection đúng và vệ sinh nozzle.
3. Chạy `CALIBRATE_MOVE_OVER_PROBE`; macro chỉ tới Z18 rồi vào tâm `(80, -5.5)`, không chạm công tắc.
4. Khi vị trí an toàn đã đúng, chạy `CALIBRATE_ALL_OFFSETS` có người giám sát. Chu trình gia nhiệt từng nozzle đến 150 °C và dùng năm mẫu median.
5. Chạy `CHECK_OFFSETS`, so sánh với baseline và chỉ `SAVE_CONFIG` sau khi kết quả hợp lý.

`CALIBRATE_NOZZLE_PROBE_OFFSET` vẫn bị chặn để lần thử không thay đổi offset Cartographer.

## Vệ sinh nozzle

`CLEAN_NOZZLE` yêu cầu KTC có tool active. Macro dùng bucket `(320, -8)`, cọ silicone X 277–309 và Z vệ sinh 1.2 mm. `PURGE_AND_CLEAN` đùn nhựa ở nhiệt vật liệu rồi hạ về nhiệt vệ sinh.

## Quy tắc phục hồi

- Tool mismatch: dừng, kiểm tra gá cơ khí và detection pin, sau đó initialize KTC.
- Chưa home: không yêu cầu thả tool hoặc chạy đường dock.
- Lỗi điện TMC: tắt nguồn, kiểm tra dây; không clear lỗi rồi chạy tiếp.
- Kết quả calibration bất thường: giữ raw data, đối chiếu nhiệt, độ sạch nozzle và độ gài tool trước khi đổi offset.

Xem [nhận diện lỗi calibration cũ](legacy-calibration-troubleshooting.md) để tra các dấu hiệu của hệ thống retired.
