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
6. Tháo đế SexBolt giữa bàn trước khi home, Cartographer Touch, mesh hoặc in.

## Luồng in bình thường

`PRINT_START` nhận tool đầu tiên, nhiệt từng tool, nhiệt bàn và vật liệu từ OrcaSlicer. Macro nhận quyền từ dryer nếu cần, home an toàn, chọn T0 sau homing, gia nhiệt/ngâm nhiệt, chạy QGL và Cartographer, vệ sinh nozzle, prime đúng các tool được dùng và để tool in đầu tiên ở trạng thái active.

`PRINT_END` retract, nâng Z, trả tool vào dock, đỗ shuttle rỗng, tắt heater/quạt part, xóa offset/mesh và hẹn tắt quạt buồng sau cooldown.

Dùng `PAUSE`/`RESUME` thay vì tự di chuyển tool. `RESUME` khởi tạo KTC và xác nhận tool hiện diện trước khi tiếp tục.

## Hiệu chuẩn tool

Đế SexBolt tháo rời hiện dùng tọa độ tâm bàn cấu hình `(174, 168)`, với giá trị mặc định upstream `spread: 5.0` và `lower_z: 0.5`. Cần xác nhận tâm bi thực tế bằng nozzle T0; XY cấu hình chưa phải kết quả đo vật lý mới. Người vận hành đã xác nhận Z55 là khoảng hở di chuyển an toàn, được lưu tại `_CALIBRATION_SWITCH.z`. Chiều cao tiếp xúc và bắt đầu dò mới chưa được đo: `contact_z: -1` và `probe_z: -1` là giá trị đánh dấu chưa sẵn sàng, không phải tọa độ di chuyển. Mặc định `CALIBRATE_MOVE_OVER_PROBE` cho phép đi ở Z55 hoặc cao hơn mà không dò chạm. `CALIBRATE_ALL_OFFSETS` từ chối trước khi chọn tool, gia nhiệt hoặc di chuyển cho đến khi cấu hình Z tiếp xúc/bắt đầu dò hợp lệ; chế độ tiếp cận nội bộ `PROBE=1` kiểm tra các chiều cao này trước khi hạ xuống.

1. Tháo đế và để mặt bàn thông thoáng khi chạy `G28`, QGL, bed mesh và Cartographer Touch. Home Z của KTC đi quanh `(174, 168)` ở Z10; Touch cũng dùng tâm này và mesh đi qua vùng giữa bàn ở Z thấp. Không chạy các thao tác này khi còn lắp đế.
2. Home XYZ, hoàn tất các bước cân gantry/Touch cần thiết, khởi tạo toolchanger, xác nhận tool detection đúng và vệ sinh nozzle khi chưa lắp đế.
3. Đưa đầu in tới khoảng hở Z55 đã xác nhận và tránh đường lắp, rồi lắp đế. Giữ các trục ở trạng thái đã home. Không tái sử dụng Z12/Z18 của vị trí cũ cho đế mới.
4. Kiểm tra `CALIBRATION_STATUS`, lệnh báo các biến hiện tại. Chạy `CALIBRATE_MOVE_OVER_PROBE` có người giám sát và không truyền `PROBE=1` để tới tâm cấu hình ở Z55 hoặc cao hơn, không hạ tới bi.
5. Chạy `SEXBOLT_QUERY` khi nhả và khi nhấn tay công tắc; chỉ tiếp tục khi kết quả lần lượt là `open` và `TRIGGERED`. Có người giám sát khi xác nhận XY của nozzle T0 trên tâm bi và đo Z tiếp xúc mới. Đặt `_CALIBRATION_SWITCH.contact_z` theo số đo này và `.probe_z` theo chiều cao bắt đầu dò đã kiểm tra nằm trên điểm tiếp xúc, không cao hơn Z55 di chuyển. Giữ `.z: 55` cho di chuyển XY. Kiểm tra lại bằng `CALIBRATION_STATUS` trước khi dò tự động.
6. Khi đã xác nhận khoảng hở an toàn, chạy `CALIBRATE_ALL_OFFSETS` có người giám sát. Chu trình gia nhiệt từng nozzle đến 150 °C và dùng năm mẫu median. Trước mỗi lần đổi tool, chu trình nâng thẳng lên ít nhất Z55 di chuyển rồi mới rời vùng đế tới dock.
7. Chạy `CHECK_OFFSETS`, so sánh các lượt đo đầy đủ lặp lại với baseline đã lưu và chỉ `SAVE_CONFIG` khi kết quả ổn định, hợp lý. Tháo đế trước mọi lần home, cân gantry, mesh, Touch hoặc in tiếp theo.

`CALIBRATE_NOZZLE_PROBE_OFFSET` vẫn bị chặn để lần thử không thay đổi offset Cartographer.

## Vệ sinh nozzle

`CLEAN_NOZZLE` chỉ chạy với T0 đã được cảm biến xác nhận, KTC ở trạng thái `ready`, XYZ đã home, offset bằng 0 và mesh đã clear. Điểm xả là `X315 Y1 Z6`; đường vệ sinh nằm trong vùng đệm an toàn `X278–311`, `Y-9…-1` của miếng silicone đo được `X277–312`, `Y-10…0`. Z tiếp xúc mặc định là `1.0 mm` và macro chỉ chấp nhận `0.5–1.0 mm`.

`MODE=DEEP` có thể purge nóng rồi lau nhiều track/hai hướng, sau đó hoàn tất lượt cuối ở tối đa 150 °C. `PRINT_START` tự purge T0 `40 mm` tại nhiệt độ vật liệu khi slicer cung cấp `T0_TEMP`; lượng này bù `10 mm` retract của `PRINT_END` và còn khoảng `30 mm` nhựa thực tạo cục. Nếu job không dùng T0 thì không tự đoán nhiệt purge. `MODE=TOUCH` cấm purge, yêu cầu QGL đã áp dụng và thực hiện một lượt lau ngắn ở tối đa 150 °C ngay trước `CARTOGRAPHER_TOUCH_HOME`.

Lệnh thủ công cần truyền nhiệt vật liệu rõ ràng, ví dụ `PURGE_AND_CLEAN PURGE_TEMP=250`. Lần chạy đầu ở tọa độ mới phải có người giám sát; bắt đầu với `CLEAN_Z=1.0` và chỉ hạ dần sau khi xác nhận tiếp xúc thực tế.

## Quy tắc phục hồi

- Tool mismatch: dừng, kiểm tra gá cơ khí và detection pin, sau đó initialize KTC.
- Chưa home: không yêu cầu thả tool hoặc chạy đường dock.
- Lỗi điện TMC: tắt nguồn, kiểm tra dây; không clear lỗi rồi chạy tiếp.
- Kết quả calibration bất thường: giữ raw data, đối chiếu nhiệt, độ sạch nozzle và độ gài tool trước khi đổi offset.

Xem [nhận diện lỗi calibration cũ](legacy-calibration-troubleshooting.md) để tra các dấu hiệu của hệ thống retired.
