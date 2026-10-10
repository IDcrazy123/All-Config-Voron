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
