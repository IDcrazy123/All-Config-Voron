# Nhật ký — 2026-10-13

## 1. Đồng bộ retract sau đường mồi cho tool về dock

### Mục tiêu
Người dùng quan sát tool để lâu trên dock có một ít nhựa thừa lúc bắt đầu dùng. Kiểm tra retract sau đường mồi và chỉnh macro dựa trên mức retract đã có trong profile máy.

### File đã sửa đổi
- `config/Printer-Setup/prime-lines.cfg` — tăng retract của tool không phải tool bắt đầu in; thêm comment về nguồn giá trị và trách nhiệm nạp lại của slicer.

### Sao lưu
- [prime-lines.cfg (Backup)](</D:/Desktop/All-Config-Voron-main/Voron 5 Tool/extras/backups/pre-prime-line-dock-retract-20261013-191807/prime-lines.cfg>)
- Backup trước ghi lúc 19:18:07 (Asia/Saigon); SHA-256 bản sao khớp file gốc.

### Phân tích nhật ký và cấu hình
- Đọc log live `/home/voron/printer_data/logs/klippy.log` qua SSH; phần cuối hiện tại không có bằng chứng giải thích nhựa rỉ trong lần in người dùng quan sát. Dòng đăng ký remote method `shutdown_machine` là thông tin đăng ký API, không phải lỗi shutdown.
- [Log excerpt chỉ đọc](</D:/Desktop/All-Config-Voron-main/Voron 5 Tool/extras/logs/2026-10-13-prime-retract-klippy-excerpt.log>) được lưu local và bỏ qua bởi Git theo quy tắc log.
- Moonraker báo `print_stats.state=standby`, toolchanger `uninitialized`, tool_number=-1 tại thời điểm kiểm tra. Không gửi G-code hay chạy heater/motion.
- Bản `prime-lines.cfg` live khớp local trước sửa (chuẩn hóa CRLF/LF).
- Macro đã có `M83` và `G1 E-{retract}` sau lượt vẽ cuối, rồi `G92 E0`, hạ target standby của tool không phải tool đầu tiên, lau ngang và nâng Z.
- `G92 E0` chỉ đặt lại tọa độ E, không nạp lại nhựa. KTC runtime và hooks hiện tại không thêm lệnh extrusion khi đổi tool; `RESTORE_GCODE_STATE MOVE=0` không hoàn tác retract vật lý. Đối chiếu [Klipper G-Codes](https://www.klipper3d.org/G-Codes.html#restore_gcode_state) và [gcode_move.py](https://raw.githubusercontent.com/Klipper3d/klipper/master/klippy/extras/gcode_move.py).

### Chi tiết thay đổi
- `variable_retract_amount: 1.8` → `5.0` mm cho tool sẽ về dock sau prime.
- Nguồn giá trị: `Orca Config/Voron Stealthchanger.json` đã đặt `retract_length_toolchange=5` và `retract_restart_extra_toolchange=0` cho cả năm tool. Đây là baseline profile hiện có, không phải kết quả calibration mới.
- Giữ `variable_final_retract_amount: 0.6` mm cho tool bắt đầu in ngay; feedrate retract vẫn `3600` mm/min.
- Tool primed về dock cần slicer nạp lại theo retract toolchange khi được chọn in; không thêm prime/unretract vào hook đổi tool để tránh cộng nhựa với lệnh slicer.

### Lý do
Retract về dock sau đường mồi thấp hơn mức toolchange đang dùng trong profile. Đồng bộ về 5 mm nhằm giảm áp suất nhựa còn lại lúc chờ trên dock. Chưa xác nhận đây là nguyên nhân duy nhất của nhựa thừa; log không đo được lượng nhựa rỉ thực tế.

### Kiểm tra
- CFG và Jinja theo delimiter Klipper: đạt.
- Đối chiếu baseline retract/restart của cả năm tool trong Orca: đạt.
- 16 trường hợp render: một/nhiều tool, số tool không liên tục, tool đầu/cuối làm INITIAL_TOOL, 2/3 lượt lau. Thứ tự prime đúng; retract đứng trước lau và nâng Z; so với backup chỉ lệnh retract tool về dock đổi từ E-1.8 sang E-5.0.
- `git diff --check` cho file sửa: đạt.
- Khởi động lại Klipper: chưa thực hiện.
- Thử in: chưa thực hiện.

### Kết quả
Đã sửa và kiểm tra offline macro trong repo, có backup và nhật ký. Bản trên máy in vẫn giữ retract 1.8 mm cho tới khi triển khai cấu hình mới.

### Vấn đề còn lại
- Sau triển khai, thử job multi-tool có người giám sát: quan sát nhựa rỉ khi tool chờ dock và đoạn in đầu tiên của từng tool; xác nhận G-code slicer nạp lại 5 mm cho tool đã primed trước khi in.
- Nếu còn nhựa thừa, cần dữ liệu vật liệu, nhiệt độ và thời gian chờ dock để tách ooze nhiệt khỏi lượng nhựa nạp lại; không tự tăng retract thêm.
