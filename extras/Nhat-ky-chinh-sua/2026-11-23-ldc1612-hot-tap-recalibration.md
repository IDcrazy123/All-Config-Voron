# 2026-11-23 — Đối chiếu hiệu chuẩn tap nóng của LDC1612 mới

## Điều kiện và nguồn bằng chứng

- Người vận hành chọn điều kiện bàn/T0 100/150°C như lần quét nóng, xác nhận vòi T0 và mặt bàn sạch, rồi tự hoàn tất hiệu chuẩn tap và restart trong lúc trợ lý đang chờ máy gia nhiệt. Trợ lý không gửi lệnh `PROBE_EDDY_CURRENT_TAP_CALIBRATE` hoặc lệnh tap khác trong lượt này.
- Log live `klippy.log.2026-11-22` gần các dòng 371043–371143 ghi bàn target 100°C, thực tế khoảng 100,1°C; T0 target 150°C, thực tế khoảng 149,4–151,3°C; nhiệt cuộn tăng khoảng 50,7→52,1°C. Nhiệt cuộn khác 73,565570°C lúc hiệu chuẩn bảng Z; tap dùng điểm tiếp xúc vòi nên không dùng trực tiếp bảng khoảng cách Z của scan.
- Chuỗi Klipper: `TAP=guess` chọn ngưỡng 26238,552 và trả Z−0,065015; `TAP=refine` chọn 19931,059 và trả Z−0,063790; `TAP=verify` năm lần chạm lần lượt Z−0,061286 / −0,060092 / −0,062718 / −0,059617 / −0,062311 mm. Dải năm lần là 0,003101 mm, kết quả trung bình Z−0,061205. Log ghi `tap_threshold: 19931.059`; sau restart live cũng có đúng giá trị đó và `save_config_pending_items={}`.
- Lúc hiệu chuẩn, log cấu hình còn `tap_z_offset=-0.1`. Sau đó người vận hành đổi live thành `-0.06` và hỏi về chiều tác động. Mã Klipper trả Z tap theo `z_contact - tap_z_offset`; macro live `_LDC_APPLY_TAP_Z` dùng kết quả đó để cập nhật gốc động học. Chuyển −0,10→−0,06 khiến vòi T0 đi xuống khoảng 0,04 mm ở cùng tọa độ Z in sau tap. Đây là tác động hình học dự kiến, chưa xác minh bằng lớp đầu.

## Cấu hình và trạng thái

- Trước khi sửa repository đã sao lưu live và bản Git cũ tại `extras/backups/pre-ldc1612-tap-recal-20261122/`. Chỉ đồng bộ hai giá trị từ live vào Git: `config/printer.cfg` `tap_threshold` 18555,665→19931,059 và `config/Printer-Setup/calibration-probe.cfg` `tap_z_offset` +0,10→−0,06. Không triển khai Git đè cấu hình live QGL hay offset T2 đang khác Git.
- Sau restart và một lần shutdown qua webhooks trong chu trình làm sạch T0 do thao tác ngoài lượt lệnh trợ lý, live tại mốc đầu kiểm tra `ready`, `print_stats=standby`, XYZ chưa home, QGL chưa applied, toolchanger `uninitialized` nhưng cảm biến nhận T0, mọi heater target 0. Về sau người vận hành tiếp tục thao tác: tại một mốc đọc khác `print_stats=complete`, XYZ homed, toolchanger ready, không phát hiện tool trên shuttle. Không gửi thêm lệnh di chuyển/gia nhiệt khi trạng thái còn thay đổi.
- Tap threshold mới đã vượt qua năm lần chạm tại 100/150°C. Chưa xác minh `LDC_TAP_HOME` sau đổi `tap_z_offset`, QGL nóng, hoặc lớp đầu T0/T2. Lỗi main MCU `Missed scheduling of next digital out event` từ lượt QGL nóng trước vẫn chưa có nguyên nhân pin/OID xác định.

Tài liệu tham chiếu: https://www.klipper3d.org/Eddy_Probe.html
