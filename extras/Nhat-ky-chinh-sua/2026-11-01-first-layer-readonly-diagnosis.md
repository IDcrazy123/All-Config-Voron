# 2026-11-01 — Điều tra lớp đầu T0 sát bàn

- Theo yêu cầu người vận hành, truy cập Moonraker/SSH máy 192.168.1.43 để đối chiếu `Hinh tru_ABS_52m32s.gcode` hoàn tất 10:36 với các bản Belt-Clam lỗi từ trưa. Chỉ đọc, không thay cấu hình hoặc phát lệnh chuyển động/gia nhiệt/restart.
- Xác nhận lỗi 12:13 là gắp T2 thất bại trước in; lỗi sát bàn người vận hành xác nhận trên T0 ngay nét đầu, kể cả sau calib.
- Cấu hình được nạp buổi sáng và đầu trưa giống nhau. Các chỉnh QGL và calib Scan/Touch xảy ra sau lỗi đầu tiên. Calib mới đã SAVE_CONFIG và nạp thật; Touch threshold 1504 -> 1379, z_offset vẫn -0.05.
- Sau calib, Touch trong bản 15:17 có 7 mẫu trải 0.542 mm trước khi chọn cụm 3 mẫu cuối; người dùng nâng tổng +0.20 mm trong bản đó. Có một sự kiện watchdog T0 lúc 14:45.
- Khác biệt cần kiểm tra vật lý: hình trụ chỉ T0, trong khi các bản nhiều tool có T0 -> T3 -> T0 sau Touch/mesh để prime. Chưa chứng minh độ ngồi lại T0 hoặc mất bước Z; không kết luận cảm biến hỏng cụ thể từ log.
- Lỗi nhiệt coil âm và tín hiệu NTC bàn bất thường vẫn tồn tại; bản sáng tốt cũng có bất thường nên chưa chứng minh là nguyên nhân duy nhất của sát bàn.
- Báo cáo, hạn chế kết luận và các phép kiểm tra tách nguyên nhân: `extras/diagnostics/20261101-first-layer/README.md`. Dữ liệu cũ/mới được giữ trong thư mục đó; không đổi giá trị production, không đồng bộ đè drift live/repository, không commit/push.

## Bổ sung: file khác in tốt, kiểm tra CAD/G-code

- Bản `Khoi lap phuong_ABS_26s.gcode` hoàn tất khoảng15:49, cùng first layer0,25 và flow0,96. Touch của bản tốt cũng báo adjusted z by+0,489 mm; không được dùng riêng số này để quy lỗi cảm biến.
- Kiểm tra thư mục Belt Clam: STL gốc có18 cặp tam giác trùng ngược mặt và45 cạnh không manifold, ở1,2 mm dưới cùng. STEP-derived meshes trong3MF hiện tại gồm4 khối kín, không chồng thể tích tại các mặt cắt kiểm tra, đáy Z0; lỗi STL không chứng minh nguyên nhân của bản STEP/3MF mới.
- Belt G-code có bước hạ Z0,25 trước XY vào mẫu, khác hình trụ/khối lập phương. Đồng thời luồng nhiều tool vẫn đổi T0->T3->T0 sau Touch.
- Tạo bản STL union kín, project T0-only và G-code safe-entry (chỉ comment một dòng hạ Z sớm) trong thư mục con Kiem-tra-Codex-20261101; nguồn giữ nguyên. Kiểm tra topology sau xuất, zip/mesh/project diff và G-code diff đạt; chưa slice project và chưa in các bản đối chứng. CLI Orca WindowsApps bị Access denied, không tác động phiên GUI đang mở.
- Báo cáo bổ sung: `extras/diagnostics/20261101-belt-clam-files/README.md`. Chưa xác định duy nhất nguyên nhân vật lý, chưa sửa production.
