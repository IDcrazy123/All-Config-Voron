# 2026-11-02 — Điều tra lớp đầu sau đổi tool và QGL

## Cập nhật nguyên nhân từ người vận hành

- Người vận hành xác nhận đã tìm ra nguyên nhân: thay nhầm một part đệm. Cập nhật kết luận trong báo cáo và KNOWN_ISSUES; bảng tỷ lệ ban đầu được đánh dấu là lịch sử trước phát hiện này.
- Chưa có vị trí/mã part, cơ chế gây lệch hoặc kết quả QGL/first layer sau thay đúng. Không tự kết luận pulley trượt, GE5C bó, mất bước hoặc đã sửa hoàn toàn. Không thay cấu hình production; các bất thường coil/NTC vẫn chưa được xác nhận xử lý.

## Thu thập và nhận định ban đầu

- Theo yêu cầu người vận hành, đọc hướng dẫn hiện hành và đối chiếu repository với Moonraker/SSH 192.168.1.43, log, G-code và phiên OrcaSlicer đang mở. Chỉ đọc; không phát G-code, chuyển động, gia nhiệt, restart hoặc thay production/profile slicer.
- Phân nhánh PRINT_START/PRIME_LINES cho thấy T0 đơn giữ tool sau Touch/mesh; nhiều tool bắt đầu T0 phải prime tool khác rồi gắp T0 lại. T3/T4 đơn cũng đổi khỏi T0 sau Touch. Luồng này phù hợp lỗi mốc Z hoặc gá/tool sau hành trình dock, chưa chứng minh macro tính sai.
- QGL console 18:45 bắt đầu 0,981970 mm trên shuttle rỗng; 18:49 sau lấy T0 và bốn vòng T0/T4 bắt đầu 2,026687 mm nhưng nhiệt bàn bất thường; 18:54 sau năm vòng bắt đầu 1,179902 mm khi số đo bàn 79,9–80,1°C. Cả ba có Z2 nhận lệnh bù lớn nhất. Chưa có đồng hồ so nên không khẳng định độ lệch cơ khí thật hoặc linh kiện hỏng.
- Giới hạn Z live 80 mm/s, 1.000 mm/s²; dock Z343, đỉnh đường Z346, max347. Khoanh vùng cơ khí Z2/GE5C, pulley/đai, mất bước/bó/cạ ở hành trình cao; chưa tự giảm tốc hoặc sửa dock.
- Coil ~−20°C; Touch bản T4 có ngoại lai toàn chuỗi 0,454 mm trước cụm ba mẫu trùng. Raw NTC bàn tiếp tục nhảy 84,1→38,8→25,8→86,8°C. Không lấy adjusted z by làm độ lún nozzle; không xem target nhiệt ổn định là mặt bàn ổn định.
- G-code mới T0 đơn/nhiều tool/T3/T4 đều lớp đầu 0,20 mm, z_offset=0, không có SET_GCODE_OFFSET/G92 Z trong phần chạy. Profile/filename hiện tại không chứng minh nội dung những lần upload trước cùng tên.
- Báo cáo tiếng Việt có phân bổ nghi ngờ theo hai triệu chứng, các phép đo tách nguyên nhân và giới hạn bằng chứng: `extras/diagnostics/2026-11-02-first-layer-qgl/REPORT.vi.md`. Không commit/push; các lần đọc mạng cuối bị timeout, chưa xác minh trạng thái mới sau mất kết nối.
