# Quy tắc làm việc hiện hành — Voron 5 Tool

Cập nhật: 2026-11-14. File này là điểm vào duy nhất cho công việc trong Git repository này. Các ghi chép ở thư mục ../.agents và extras là tài liệu tham khảo theo thời điểm, không tự động ghi đè trạng thái máy hoặc yêu cầu mới của người dùng.

## Máy và nguồn sự thật

- Git repository nằm tại thư mục Voron 5 Tool. Cấu hình triển khai nằm trong config; profile Orca đang dùng nằm trong Orca Config. Các bản sao CFG ở workspace cha và extras/backups là lịch sử.
- Máy production truy cập qua Moonraker tại 192.168.1.43:7125. Trước khi sửa hoặc triển khai, đọc trạng thái print_stats, toolchanger, homing và configfile trên máy; so với file trong repository. Một bản commit hoặc thông báo Klipper ready không chứng minh đã thử cơ khí.
- Thứ tự dùng bằng chứng: log và trạng thái live đúng thời điểm; cấu hình live; cấu hình Git hiện tại; nhật ký/báo cáo theo ngày; backup và cấu hình retired. Ghi rõ khi các nguồn khác nhau.
- Không coi các con số Z được Cartographer in ra trước khi home là tọa độ cơ khí đã chuẩn hóa. Đối chiếu chu trình G28, QGL và trạng thái sau home.

## Kiến trúc đang chạy

- Voron 2.4 350 mm, 5 tool T0–T4; Manta M8P V2, CM4, EBB36 qua CAN.
- Từ lần khôi phục thứ hai ngày 2026-11-14: production lại nạp T0–T4 cùng PID/offset T2–T4. Klipper `ready`, registry `[0,1,2,3,4]`, không cảnh báo; chưa thử cơ khí, gia nhiệt hoặc in T2 sau bảo trì. Xem `extras/Nhat-ky-chinh-sua/2026-11-14-second-five-tool-restore.md` trước khi coi T2 đã được xác minh.
- Từ 2026-11-13: sau bảo trì, Klipper production đã nạp lại T0–T4 và các PID/offset lưu trước chế độ T0-only. Người vận hành báo T1 thay cảm biến cùng loại `Generic 3950` và chuyển dock sang X104 Y0 Z330; Z330 là giá trị tạm từ điểm kích hoạt khoảng Z327–330. T1 đã gắp có người quan sát và PID_CALIBRATE ở 250°C được lưu với Kp/Ki/Kd 28,787/9,596/21,590. Cần xác minh thả/gắp lại và bản in đầu trước khi coi dock đã căn xong.
- KTC-Easy quản lý dock, chọn tool và detection_pin. Cartographer gắn vào shuttle quản lý home Z, Touch và mesh. Axiscope quản lý XY và đo Z tương đối sơ bộ qua PF2; Z production do first-layer quyết định.
- printer.cfg là entrypoint. print-macros.cfg sở hữu PRINT_START, PRINT_END, PAUSE, RESUME, CANCEL_PRINT, G32 và QGL. tool-crash.cfg sở hữu latch phục hồi. toolchanger-config.cfg và tools/T*.cfg chứa đường đổi tool, cảm biến và dock.
- toolchanger/readonly-configs do KTC-Easy cài đặt quản lý. Không sửa các file đó trong repository. Không sửa runtime .py cho tác vụ 2026-10-27.
- Script config/scripts/install.sh chỉ triển khai khi Moonraker xác nhận máy idle; nó kiểm tra SAVE_CONFIG khác biệt và backup. Push Git không tương đương triển khai; cần kiểm tra trạng thái máy trước khi reload.

## Luồng in và phục hồi

- PRINT_START kiểm tra nhiệt/filament, khởi tạo toolchanger, heat, G28, lấy T0 để vệ sinh, ổn định nhiệt bàn, QGL, Touch, mesh rồi prime tool dùng để in. T0 phải gắp chính xác vì chu trình làm sạch/Touch cần nó ngay cả khi bản in dùng T1–T4.
- Khi Tn không được nhận diện sau pickup, kiểm tra vị trí dock và detection_pin trước. Expected tool Tn but active is None mô tả lỗi xác thực gắp tool; lỗi recovery và preparation tiếp theo là hệ quả.
- `tool_crash.py` chỉ phát hiện và gọi macro pause; KTC xác thực tool. Không cần lệnh `RECOVER_TOOL` hoặc xác nhận thủ công riêng: sau khi kiểm tra ngàm/dock, `RESUME` tự khởi tạo và xác thực lại tool gốc; `CANCEL_PRINT` bỏ chuyển động park nếu đang có crash rồi xóa chốt tạm. Nếu không biết tool gốc, phải hủy bản in.
- Chốt crash nội bộ chỉ tồn tại trong bản in đang chạy hoặc pause để tránh chuyển động khi hủy. Sự kiện cảm biến lúc idle không được giữ chốt. Sau hủy, `PRINT_START` khởi tạo KTC và kiểm tra active/detected trước khi home; QGL kiểm tra lại trước probe.
- Nếu shuttle rỗng hoặc tool nằm sai vị trí sau sự cố, người vận hành cần quan sát và thu dọn trước khi chạy lệnh có chuyển động. Không tự động di chuyển để gắp lại khi không chắc tool đang ở dock hay kẹt trên shuttle.
- T0 dock Y đã chỉnh trên máy thành 1.3 mm và T2 thành 1.6 mm, đồng bộ vào repository ngày 2026-10-27. Tọa độ dock khác chỉ đổi khi có số đo live xác nhận.

## Bàn nhiệt và giới hạn

- Bàn AC 1000 W qua SSR PA5, NTC trên PB0. Klipper nhận sensor_type NTC 100K MGB18-104F39050L32; tên người bán ghi MBG18-104F39050L32 cần kiểm tra với linh kiện thật trước khi đổi đường cong nhiệt.
- Log ngày 2026-10-27 khoảng 19:22 ghi số đo bàn nhảy từ khoảng 104°C xuống 71,7°C trong vài giây rồi tăng lại, khi target 105°C. Cần kiểm tra đầu nối, dây NTC, điểm gắn cảm biến và nhiễu điện trước khi kết luận heater hoặc SSR hỏng. Không nới verify_heater hay tăng smooth_time để che tín hiệu sai.
- Ngày 2026-11-11 người vận hành báo đã thay cảm biến bàn. Một lượt gia nhiệt 24,5→100,4°C có 389 mẫu Stats 1 Hz, không có bước nhiệt từ 2°C trở lên; thời gian giữ gần 100°C chỉ khoảng hai phút, chưa xác nhận hết lỗi gián đoạn lâu dài hay độ chính xác nhiệt tuyệt đối.
- Sau reload 2026-11-11, max_temp live và Git cùng 120°C. `smooth_time` và `pwm_cycle_time` live dùng mặc định 1,0/0,1; Git đã đồng bộ ngày 13/11. Không nâng giới hạn nhiệt nếu thiếu thông số phần cứng.
- Đánh giá log đến 13/11: người vận hành xác nhận cảm biến cũ có dấu hiệu hỏng khi dùng và đã thay. Log cũ có lỗi lúc gia nhiệt, nhưng 28/10 còn ghi 49,7→4,4→49,8°C khi target/PWM bằng 0, nên không kết luận lỗi chỉ lúc bật heater. Sau thay chưa thấy bước >=2°C trong Stats có target >0 của log 11 và 13/11. PID bàn hiện 64,710/2,713/385,835.
- QGL vẫn không ổn định sau thay NTC và Scan model mới: 4/7 lượt tinh ở target 105°C đạt 0,0075 mm, 3/7 hủy. Bản Cube 13/11 hoàn tất sau lượt đạt 0,003413 mm ở retry 2; lượt trước đó hủy dù bàn báo 105,1–105,2°C. Python đang chạy lấy nhiệt coil từ MCU Cartographer, không lấy NTC bàn; không có hệ số bù nhiệt coil đang nạp. Xem `extras/diagnostics/2026-11-13-qgl/REPORT.vi.md` trước khi điều chỉnh QGL hoặc quy lỗi motor.

## Cách sửa và báo cáo

1. Xác định file active và đọc nguyên section liên quan; so cấu hình live nếu máy có kết nối. Kiểm tra log trước khi quy lỗi cho macro hay phần cứng.
2. Sao lưu file CFG/CONF/SH sắp sửa vào extras/backups với timestamp và README. Chỉ sửa phần có bằng chứng, giữ comment/section không liên quan.
3. Kiểm tra cú pháp/template và những trường hợp ranh giới có liên quan. Test offline chỉ chứng minh logic, không chứng minh pickup, probe, nhiệt hay đường di chuyển.
4. Ghi mục tiếng Việt vào extras/Nhat-ky-chinh-sua, nêu bằng chứng, file, giá trị cũ/mới, điều đã xác minh và việc còn chờ phần cứng. Cập nhật KNOWN_ISSUES khi sự cố lặp lại.
5. Stage đúng file liên quan. Commit message tiếng Anh. Push sau khi thay đổi đã được xem lại; không tự động reload hoặc triển khai lúc máy đang in, pause, đổi tool hay sấy.
6. Khi dữ liệu vật lý còn thiếu, hoàn tất phần phân tích và chỉnh sửa chắc chắn được trước; nêu chính xác phép kiểm tra cần người vận hành thực hiện. Không tuyên bố sửa hoàn toàn chỉ vì Klipper ready hoặc test offline đạt.

Chat và nhật ký dùng tiếng Việt; comment cấu hình, README và commit message dùng tiếng Anh. Ưu tiên yêu cầu mới của người dùng khi nó thay đổi quy trình cũ.
