# Quy tắc làm việc hiện hành — Voron 5 Tool

Cập nhật: 2026-10-27. File này là điểm vào duy nhất cho công việc trong Git repository này. Các ghi chép ở thư mục ../.agents và extras là tài liệu tham khảo theo thời điểm, không tự động ghi đè trạng thái máy hoặc yêu cầu mới của người dùng.

## Máy và nguồn sự thật

- Git repository nằm tại thư mục Voron 5 Tool. Cấu hình triển khai nằm trong config; profile Orca đang dùng nằm trong Orca Config. Các bản sao CFG ở workspace cha và extras/backups là lịch sử.
- Máy production truy cập qua Moonraker tại 192.168.1.43:7125. Trước khi sửa hoặc triển khai, đọc trạng thái print_stats, toolchanger, homing và configfile trên máy; so với file trong repository. Một bản commit hoặc thông báo Klipper ready không chứng minh đã thử cơ khí.
- Thứ tự dùng bằng chứng: log và trạng thái live đúng thời điểm; cấu hình live; cấu hình Git hiện tại; nhật ký/báo cáo theo ngày; backup và cấu hình retired. Ghi rõ khi các nguồn khác nhau.
- Không coi các con số Z được Cartographer in ra trước khi home là tọa độ cơ khí đã chuẩn hóa. Đối chiếu chu trình G28, QGL và trạng thái sau home.

## Kiến trúc đang chạy

- Voron 2.4 350 mm, 5 tool T0–T4; Manta M8P V2, CM4, EBB36 qua CAN.
- KTC-Easy quản lý dock, chọn tool và detection_pin. Cartographer gắn vào shuttle quản lý home Z, Touch và mesh. Axiscope quản lý XY và đo Z tương đối sơ bộ qua PF2; Z production do first-layer quyết định.
- printer.cfg là entrypoint. print-macros.cfg sở hữu PRINT_START, PRINT_END, PAUSE, RESUME, CANCEL_PRINT, G32 và QGL. tool-crash.cfg sở hữu latch phục hồi. toolchanger-config.cfg và tools/T*.cfg chứa đường đổi tool, cảm biến và dock.
- toolchanger/readonly-configs do KTC-Easy cài đặt quản lý. Không sửa các file đó trong repository. Không sửa runtime .py cho tác vụ 2026-10-27.
- Script config/scripts/install.sh chỉ triển khai khi Moonraker xác nhận máy idle; nó kiểm tra SAVE_CONFIG khác biệt và backup. Push Git không tương đương triển khai; cần kiểm tra trạng thái máy trước khi reload.

## Luồng in và phục hồi

- PRINT_START kiểm tra nhiệt/filament, khởi tạo toolchanger, heat, G28, lấy T0 để vệ sinh, ổn định nhiệt bàn, QGL, Touch, mesh rồi prime tool dùng để in. T0 phải gắp chính xác vì chu trình làm sạch/Touch cần nó ngay cả khi bản in dùng T1–T4.
- Khi Tn không được nhận diện sau pickup, kiểm tra vị trí dock và detection_pin trước. Expected tool Tn but active is None mô tả lỗi xác thực gắp tool; lỗi recovery và preparation tiếp theo là hệ quả.
- Sau khi kiểm tra ngàm/dock trực tiếp, dùng RECOVER_TOOL một lần. Macro phải INITIALIZE_TOOLCHANGER trước, rồi so tool active với tool detected và VERIFY_TOOL_DETECTED nếu có tool. QGL không chứng minh ngàm đã an toàn và không được tự xóa latch.
- Nếu shuttle rỗng, một lần xác nhận attended qua RECOVER_TOOL có thể xác nhận trạng thái rỗng sau khi KTC đọc lại cảm biến. Không tự động di chuyển để gắp lại khi không chắc tool đang ở dock hay kẹt trên shuttle.
- Trước QGL, khởi tạo lại KTC và yêu cầu active/detected khớp. Không bỏ qua lỗi cảm biến để tiếp tục in. Một lần xác nhận phục hồi đủ; không thêm yêu cầu lặp nếu trạng thái được xác thực.
- T0 dock Y đã chỉnh trên máy thành 1.3 mm và T2 thành 1.6 mm, đồng bộ vào repository ngày 2026-10-27. Tọa độ dock khác chỉ đổi khi có số đo live xác nhận.

## Bàn nhiệt và giới hạn

- Bàn AC 1000 W qua SSR PA1, NTC trên PB0. Klipper nhận sensor_type NTC 100K MGB18-104F39050L32; tên người bán ghi MBG18-104F39050L32 cần kiểm tra với linh kiện thật trước khi đổi đường cong nhiệt.
- Log ngày 2026-10-27 khoảng 19:22 ghi số đo bàn nhảy từ khoảng 104°C xuống 71,7°C trong vài giây rồi tăng lại, khi target 105°C. Cần kiểm tra đầu nối, dây NTC, điểm gắn cảm biến và nhiễu điện trước khi kết luận heater hoặc SSR hỏng. Không nới verify_heater hay tăng smooth_time để che tín hiệu sai.
- Có drift chưa giải quyết: max_temp của heater_bed là 120°C trong Git nhưng 150°C trên máy. Không tự đồng bộ giá trị cao hơn khi chưa có giới hạn phần cứng được xác nhận. Triển khai nguyên config có thể thay đổi giới hạn live này; review riêng trước.

## Cách sửa và báo cáo

1. Xác định file active và đọc nguyên section liên quan; so cấu hình live nếu máy có kết nối. Kiểm tra log trước khi quy lỗi cho macro hay phần cứng.
2. Sao lưu file CFG/CONF/SH sắp sửa vào extras/backups với timestamp và README. Chỉ sửa phần có bằng chứng, giữ comment/section không liên quan.
3. Kiểm tra cú pháp/template và những trường hợp ranh giới có liên quan. Test offline chỉ chứng minh logic, không chứng minh pickup, probe, nhiệt hay đường di chuyển.
4. Ghi mục tiếng Việt vào extras/Nhat-ky-chinh-sua, nêu bằng chứng, file, giá trị cũ/mới, điều đã xác minh và việc còn chờ phần cứng. Cập nhật KNOWN_ISSUES khi sự cố lặp lại.
5. Stage đúng file liên quan. Commit message tiếng Anh. Push sau khi thay đổi đã được xem lại; không tự động reload hoặc triển khai lúc máy đang in, pause, đổi tool hay sấy.
6. Khi dữ liệu vật lý còn thiếu, hoàn tất phần phân tích và chỉnh sửa chắc chắn được trước; nêu chính xác phép kiểm tra cần người vận hành thực hiện. Không tuyên bố sửa hoàn toàn chỉ vì Klipper ready hoặc test offline đạt.

Chat và nhật ký dùng tiếng Việt; comment cấu hình, README và commit message dùng tiếng Anh. Ưu tiên yêu cầu mới của người dùng khi nó thay đổi quy trình cũ.
