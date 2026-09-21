# Hướng dẫn Vận hành StealthChanger Production

[English](huong-dan-he-thong-stealthchanger.en.md) | [Tiếng Việt](huong-dan-he-thong-stealthchanger.md)

## Quyền sở hữu backend

- KTC-Easy quản lý gắp/thả tool, trạng thái tool active, đường dock và macro readonly.
- Axiscope quản lý hiệu chuẩn XY/Z có người giám sát qua Web UI cổng 3000 và microswitch `^PF2`.
- Cartographer quản lý home Z, chuẩn Touch, adaptive bed mesh và đo rung.
- OrcaSlicer quản lý lựa chọn theo filament/process như pressure advance và prime tower.

Không trộn quy trình kTAMV, ToolVision, TKC/KCC hoặc SexBolt đã retired với stack active.

## Trước khi in

1. Xác nhận Klipper ready và không có lỗi MCU/CAN.
2. Kiểm tra cả năm dock, không có tool nào gài nửa chừng.
3. Đối chiếu tool KTC báo active với tool đang gắn vật lý.
4. Làm sạch nozzle chuẩn nếu sắp chạy Cartographer Touch hoặc Axiscope Z.
5. Kiểm tra Orca đã chọn đúng machine năm tool, process và mapping filament.

## Luồng in bình thường

`PRINT_START` nhận tool đầu tiên, nhiệt từng tool, nhiệt bàn và vật liệu từ OrcaSlicer. Macro nhận quyền từ dryer nếu cần, home an toàn, chọn T0 sau homing, gia nhiệt/ngâm nhiệt, chạy QGL và Cartographer, vệ sinh nozzle, prime đúng các tool được dùng và để tool in đầu tiên ở trạng thái active.

`PRINT_END` retract, nâng Z, trả tool vào dock, đỗ shuttle rỗng, tắt heater/quạt part, xóa offset/mesh và hẹn tắt quạt buồng sau cooldown.

Dùng `PAUSE`/`RESUME` thay vì tự di chuyển tool. `RESUME` khởi tạo KTC và xác nhận tool hiện diện trước khi tiếp tục.

## Hiệu chuẩn tool

1. Mở Axiscope tại cổng 3000.
2. Dùng camera crosshair để căn XY có giám sát.
3. Dùng microswitch PF2 để đo Z; tọa độ production là `(80, -5, 8)`, 10 mẫu.
4. Workflow gia nhiệt toàn bộ tool tới 150 °C, chờ tool đang chọn và nâng Z tối thiểu 15 mm trước pickup.
5. Review offset, lưu bằng đường Axiscope/Klipper được hỗ trợ và chạy `CHECK_OFFSETS` trước bản in thử.

Không gọi `CALIBRATE_ALL_OFFSETS` hoặc `CALIBRATE_MOVE_OVER_PROBE` cũ; các macro này bị chặn có chủ đích.

## Vệ sinh nozzle

`CLEAN_NOZZLE` yêu cầu KTC có tool active. Macro dùng bucket `(320, -8)`, cọ silicone X 277–309 và Z vệ sinh 1.2 mm. `PURGE_AND_CLEAN` đùn nhựa ở nhiệt vật liệu rồi hạ về nhiệt vệ sinh.

## Quy tắc phục hồi

- Tool mismatch: dừng, kiểm tra gá cơ khí và detection pin, sau đó initialize KTC.
- Chưa home: không yêu cầu thả tool hoặc chạy đường dock.
- Lỗi điện TMC: tắt nguồn, kiểm tra dây; không clear lỗi rồi chạy tiếp.
- Kết quả calibration bất thường: giữ raw data, đối chiếu nhiệt, độ sạch nozzle và độ gài tool trước khi đổi offset.

Xem [nhận diện lỗi calibration cũ](legacy-calibration-troubleshooting.md) để tra các dấu hiệu của hệ thống retired.
