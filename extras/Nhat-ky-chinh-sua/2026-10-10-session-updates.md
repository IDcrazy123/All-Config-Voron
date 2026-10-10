# Nhật ký — 2026-10-10

## 1. Liệt kê nguyên nhân có thể gây số đọc nhiệt độ T1 sai

### Yêu cầu và phạm vi
Người dùng yêu cầu liệt kê nguyên nhân. Đối chiếu cấu hình/log cũ và tài liệu chính thức; không sửa cấu hình, gửi G-code, gia nhiệt, motion, restart hay thử phần cứng.

### Kiểm tra
- Đọc T1.cfg và so sánh năm tool; API configfile.settings xác nhận runtime T1: Generic3950, EBB1:PA3, pullup4700, inline0, heaterEBB1:PB13. Pin khớp mẫu EBB36/42 V1.2 của BTT; không thấy typo cấu hình khác riêng T1. Loại cảm biến/board/wiring thực tế chưa được xác minh bằng đo.
- Đọc thermistor.py đang cài, đối chiếu upstream đúng commit và Klipper config reference. NTC có R thấp → T cao; tăng series resistance/hở mạch thường báo lạnh, không phải cơ chế trực tiếp của warm bias.
- Đọc BTT guide phân biệt NTC/PT1000/pullup/jumper và board variants. Không giả định jumper PT1000 tự gây báo nóng; pullup thực nhỏ hơn giá trị software thường làm NTC báo lạnh.
- Minh họa tính toán model100k-at25/B3950: R30≈80.4k, R55≈29.8k, R69≈18.2k. Không dùng ví dụ để suy ra nhiệt thực hay thay calibration.

### Kết quả và giả thuyết
- Liệt kê tám nhóm: cáp chạm/rò; connector/PCB có contamination dẫn điện; thermistor/insulation hỏng; ADC/input EBB1 hỏng; pullup thực sai/hỏng; sensor thực khác model; nhiễu/ground; đấu nhầm sensor/channel/MCU.
- Xếp hướng kiểm tra rò/thermistor/input EBB1 trước theo pattern biến thiên warm bias, chỉ là suy luận, chưa có phần nào được xác nhận hỏng.
- Tách hotend/sensor nóng thật: nhiệt dư/nguồn nhiệt xung quanh/vị trí sensor và heater vẫn có công suất do MOSFET/wiring. PWM0 không phải phép đo dòng điện.
- PID không hiệu chỉnh conversion ADC; patch response không chạm conversion; không có bằng chứng CAN gây offset nhiệt.

### Tài liệu và việc còn lại
- [Danh sách và cách phân biệt](</D:/Desktop/All-Config-Voron-main/Voron 5 Tool/extras/docs/t1-temperature-error-causes-2026-10-10.md>) có nguồn Klipper/BTT và giới hạn suy luận.
- Cần đo nhiệt độc lập khi nguội để chọn nhánh sensor/board hay nhiệt thật. Đo điện trở phải cắt nguồn/rút sensor khỏi PCB; không thực hiện các bước phần cứng trong lượt này.
- Chỉ thêm tài liệu/nhật ký mới, không có file cấu hình bị sửa để cần backup; giữ nguyên log/backup/journal cũ. Không chạy test motion/heating cho thay đổi tài liệu.

## 2. Người vận hành xác định cảm biến nhiệt T1 hỏng

### Xác nhận mới
Người dùng xác định cảm biến trên T1 hỏng và đang mua linh kiện mới về thay. Ghi nhận nguyên nhân theo kết luận người vận hành; không suy diễn cơ chế hỏng cụ thể hoặc thông số cảm biến thay thế.

### Cập nhật
- Workspace KNOWN_ISSUES đổi trạng thái thành cảm biến hỏng, chờ thay; chưa đánh dấu đã khắc phục khi chưa lắp và kiểm tra sau sửa.
- Bổ sung kết luận mới vào tài liệu nguyên nhân; giữ các giả thuyết/log trước đó làm lịch sử điều tra.
- Không kết nối máy in, sửa CFG/runtime, sensor_type, pullup, PID, gia nhiệt hoặc chạy phép thử. Cấu hình thay thế chỉ được xem xét khi biết đúng loại linh kiện.
- Sao lưu nhật ký/tài liệu/KNOWN_ISSUES trước cập nhật tại [backup](</D:/Desktop/All-Config-Voron-main/Voron 5 Tool/extras/backups/pre-t1-sensor-diagnosis-20261010-165242/README.md>).

### Việc còn lại
Chờ thay cảm biến, đối chiếu loại linh kiện với cấu hình và kiểm tra số đọc nguội/hoạt động sau thay trước khi đóng lỗi.

## 3. Đồng bộ chân Y endstop thành PF4 theo máy thực tế

### Mục tiêu
Cập nhật chân Y endstop trong dự án theo yêu cầu người vận hành, khớp với cấu hình máy đang sử dụng.

### File đã sửa đổi
- `config/Printer-Setup/hardware.cfg` — `[stepper_y] endstop_pin: PF1` → `PF4`; giữ nguyên các tham số khác và định dạng file.

### Sao lưu
- [hardware.cfg gốc](</D:/Desktop/All-Config-Voron-main/Voron 5 Tool/extras/backups/pre-y-endstop-pf4-20261010-201012/hardware.cfg>).
- Thư mục sao lưu chứa bản gốc nhật ký và README; tạo lúc 20:10:12 UTC+7 ngày 2026-10-10.

### Lý do
Người dùng xác nhận Y endstop nối PF4 trên máy thực tế. Kiểm tra chỉ đọc qua SSH cho thấy file máy in đã dùng PF4; Moonraker `configfile.settings.stepper_y.endstop_pin` cũng trả về PF4. Bản trong dự án vẫn dùng PF1 nên cần đồng bộ.

### Kiểm tra
- Parse cú pháp file cấu hình: đạt; xác nhận giá trị `[stepper_y] endstop_pin` bằng PF4.
- So sánh byte với bản sao lưu: chỉ thay giá trị PF1 thành PF4 tại Y endstop.
- Tìm trong toàn bộ CFG production: không có PF4 được dùng trước thay đổi; sau thay đổi chỉ có Y endstop dùng PF4.
- Không triển khai hoặc restart: file máy in và cấu hình Klipper đang nạp đã dùng PF4. Không chạy homing, chuyển động hoặc thử in.

### Kết quả và vấn đề còn lại
Cấu hình dự án khớp chân Y endstop thực tế theo thông tin người dùng và cấu hình đang nạp. Chưa thử nhấn/nhả công tắc để kiểm chứng tín hiệu vật lý trong lượt này.
