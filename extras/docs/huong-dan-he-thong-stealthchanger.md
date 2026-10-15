# Hướng dẫn Vận hành StealthChanger Production

[English](huong-dan-he-thong-stealthchanger.en.md) | [Tiếng Việt](huong-dan-he-thong-stealthchanger.md)

## Quyền sở hữu backend

- KTC-Easy quản lý gắp/thả tool, trạng thái tool active, đường dock và macro readonly.
- Axiscope quản lý đo XY bằng camera và đo Z tương đối sơ bộ qua microswitch `^PF2`.
- Cartographer quản lý home Z, chuẩn Touch, adaptive bed mesh và đo rung.
- OrcaSlicer quản lý lựa chọn theo filament/process như pressure advance và prime tower.

Không trộn quy trình kTAMV, ToolVision, TKC/KCC hoặc cấu hình SexBolt cũ với workflow Axiscope active.

## Trước khi in

1. Xác nhận Klipper ready và không có lỗi MCU/CAN.
2. Kiểm tra cả năm dock, không có tool nào gài nửa chừng.
3. Đối chiếu tool KTC báo active với tool đang gắn vật lý.
4. Làm sạch nozzle chuẩn nếu sắp chạy Cartographer Touch hoặc đo Z bằng công tắc.
5. Kiểm tra Orca đã chọn đúng machine năm tool, process và mapping filament.
6. Tháo đế công tắc giữa bàn trước khi home, Cartographer Touch, mesh hoặc in.

## Luồng in bình thường

`PRINT_START` nhận tool đầu tiên, nhiệt từng tool, nhiệt bàn và vật liệu từ OrcaSlicer. Macro nhận quyền từ dryer nếu cần, home an toàn, chọn T0 sau homing, gia nhiệt/ngâm nhiệt, chạy QGL và Cartographer, vệ sinh nozzle, prime đúng các tool được dùng và để tool in đầu tiên ở trạng thái active.

`PRINT_END` retract, nâng Z, trả tool vào dock, đỗ shuttle rỗng, tắt heater/quạt part, xóa offset/mesh và hẹn tắt quạt buồng sau cooldown.

Dùng `PAUSE`/`RESUME` thay vì tự di chuyển tool. `RESUME` khởi tạo KTC và xác nhận tool hiện diện trước khi tiếp tục.

## Hiệu chuẩn tool

Phân quyền production là: Axiscope camera đo XY; công tắc PF2 tại `(80, -8)` đo Z tương đối sơ bộ; test first-layer quyết định Z cuối. Vùng chạm quan sát là Z0–2, Axiscope bắt đầu tại Z3 và dùng Z15 để di chuyển XY/đổi tool an toàn. Không cấu hình `config_file_path`, vì vậy Axiscope không được tự ghi offset production.

1. Tháo đế và để mặt bàn thông thoáng khi chạy `G28`, QGL, bed mesh và Cartographer Touch. Home Z của KTC đi quanh `(174, 168)` ở Z10; Touch cũng dùng tâm này và mesh đi qua vùng giữa bàn ở Z thấp. Không chạy các thao tác này khi còn lắp đế.
2. Home XYZ, hoàn tất các bước cân gantry/Touch cần thiết, khởi tạo toolchanger, xác nhận tool detection đúng và vệ sinh nozzle khi chưa lắp đế.
3. Đưa đầu in tới khoảng hở Z15 và tránh đường lắp, rồi lắp đế. Giữ các trục ở trạng thái đã home.
4. Kiểm tra `CALIBRATION_STATUS`, rồi chạy `CALIBRATE_MOVE_OVER_PROBE` có người giám sát để tới X80/Y-8 ở Z15 mà không dò chạm.
5. Chạy `QUERY_ENDSTOPS` khi nhả và khi nhấn tay công tắc; chỉ tiếp tục khi dòng `Axiscope` lần lượt là `open` và `TRIGGERED`.
6. Khi đã xác nhận khoảng hở an toàn và cả hai trạng thái công tắc, chạy `CALIBRATE_COARSE_Z_OFFSETS CONFIRM=1` có người giám sát và sẵn E-stop. Không có `CONFIRM=1`, macro sẽ từ chối trước mọi chuyển động/gia nhiệt. Chu trình gia nhiệt từng nozzle đến 150 °C, bắt đầu dò tại Z3, dùng năm mẫu và chỉ báo kết quả Z tương đối sơ bộ.
7. Dùng giao diện Axiscope port 3000 để đo XY, nhập kết quả đã xem xét vào cấu hình sau khi sao lưu. Không dùng nút lưu tự động cho Z. Chốt từng Z bằng test first-layer, rồi chạy `CHECK_OFFSETS` để đối chiếu. Tháo đế trước mọi lần home, cân gantry, mesh, Touch hoặc in tiếp theo.

`CALIBRATE_NOZZLE_PROBE_OFFSET` vẫn bị chặn để lần thử không thay đổi offset Cartographer.

## Vệ sinh nozzle

`CLEAN_NOZZLE` chỉ chạy với T0 đã được cảm biến xác nhận, KTC ở trạng thái `ready`, XYZ đã home, offset bằng 0 và mesh đã clear. Xả có mặt bàn đỡ tại `X315 Y5 Z5`; điểm đỗ trên khay vẫn là `X315 Y1 Z6`. Khi đã nguội tới cửa sổ lau ấm, nozzle đi thẳng tới `X315 Y-5` ở Z5, hạ qua Z3 tới Z0,2 rồi gạt sang trái tới X278. Người vận hành xác nhận nozzle bắt đầu chạm silicone tại X313. Đoạn xả–gạt này không nâng Z15; các lần tiếp cận khác và rời chổi vẫn dùng Z15.

Mỗi lượt lau quét đủ chiều rộng X278–311 trên cả ba hàng silicone Y-8/-5/-2, đảo thứ tự hàng giữa các lượt. `MODE=DEEP` mặc định ba lượt: hai lượt ấm ở tối đa 170 °C và một lượt cuối ở tối đa 150 °C. Nếu có purge, macro thêm đúng một nhát gạt từ mép phải trước các lượt lau. `PRINT_START` luôn purge T0 `40 mm` ở mỗi bản in, kể cả job không in bằng T0, rồi đưa về 150 °C để lau và chuẩn bị dò bàn. `MODE=TOUCH` cấm purge, yêu cầu QGL đã áp dụng và thực hiện một lượt lau ở tối đa 150 °C ngay trước `CARTOGRAPHER_TOUCH_HOME`.

Orca gửi riêng `T0_PURGE_TEMP={first_layer_temperature[0]}` và `T0_MATERIAL="{filament_type[0]}"`, ngoài các tham số `Tn_TEMP` của tool thật sự dùng. Profile T0 phải khớp cuộn đang nạp, kể cả khi chỉ in bằng T1. Máy chưa có cảm biến nhận loại nhựa hoặc registry Spoolman; nhiệt được lấy từ profile, không đoán theo bảng vật liệu chung. G-code cũ vẫn dùng được `T0_TEMP`, hoặc `TOOL_TEMP` khi TOOL=0; nếu T0 không dùng và thiếu nhiệt riêng, macro dừng trước gia nhiệt/chuyển động. Cần nạp lại preset máy Orca và slice lại job cũ. Metadata vệ sinh riêng không làm T0 bị thêm vào prime lines.

Lệnh thủ công cần truyền nhiệt vật liệu rõ ràng, ví dụ `PURGE_AND_CLEAN PURGE_TEMP=230` với PETG của lượt thử này. Người vận hành chọn mặc định mới `CLEAN_Z=0.2` sau khi quan sát Z1,0 tiếp xúc chưa đủ; khoảng cho phép là 0,2–1,0 mm. Cần quan sát đường mới trước khi chạy không giám sát. Máy khác phải đo lại mặt bàn đỡ sợi, vị trí chổi và khoảng hở của chính máy đó.

## Quy tắc phục hồi

- Tool mismatch: dừng, kiểm tra gá cơ khí và detection pin, sau đó initialize KTC.
- Chưa home: không yêu cầu thả tool hoặc chạy đường dock.
- Lỗi điện TMC: tắt nguồn, kiểm tra dây; không clear lỗi rồi chạy tiếp.
- Kết quả calibration bất thường: giữ raw data, đối chiếu nhiệt, độ sạch nozzle và độ gài tool trước khi đổi offset.

Xem [nhận diện lỗi calibration cũ](legacy-calibration-troubleshooting.md) để tra các dấu hiệu của hệ thống retired.
