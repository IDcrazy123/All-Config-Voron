# Nhật ký — 2026-10-28

## 1. Tổng duyệt và tinh gọn print-macros.cfg

### Bằng chứng
- Đọc toàn bộ `config/Printer-Setup/print-macros.cfg`, các macro KTC/Cartographer/cleaner/prime liên quan, profile Orca đang dùng và trạng thái Moonraker tại `192.168.1.43`. Trước sửa, hash SHA256 live và Git của print-macros.cfg cùng là `0B41780866B1E48063F41836E104E4DF39F8EB7A820521097AAF0F67B3994BF3`.
- Máy đang in `ZAssembly_ABS_4h16m.gcode`, `print_stats=printing`, T2 active/detected, không pause, Klipper ready; vì vậy không upload hoặc restart trong phiên rà này.
- `PRINT_START` kiểm tra thông số trước tác động và không tự động di chuyển khi bản in khác đang ở pha printing/paused. Kiểm tra ở PRINT_START và PRIME_LINES không thừa vì PRIME_LINES có thể gọi độc lập. Khởi tạo/xác thực KTC trước G28 và trước QGL ở hai thời điểm khác nhau vì có đổi tool và vệ sinh ở giữa. Tắt nhiệt trước và sau dock là có chủ đích vì KTC có thể đặt lại nhiệt standby.
- Các phần thật sự trùng: hai nhánh chọn T0 phát cùng lệnh; hai mệnh đề kiểm tra trạng thái của `_REQUIRE_MOTION_PREPARATION`; đường dock/park và vòng tắt từng heater/fan/stepper trong PRINT_END/CANCEL_PRINT; nhiều khối comment lịch sử và bản sao start G-code Orca trong CFG.
- Phát hiện thêm: đường park trước đây chỉ kiểm tra `tool_number=-1`. Nếu cảm biến vẫn nhận tool thì không nên park shuttle như đang rỗng.

### Thay đổi
- `config/Printer-Setup/print-macros.cfg`: gộp điều kiện chuẩn bị chuyển động thành một nhánh; gộp chọn T0 và xác thực lại T0 đã gắn sau G28; dùng `_PRINT_FINISH_DOCK_AND_PARK` và `_PRINT_FINISH_TOOL_SHUTDOWN` chung cho kết thúc/hủy. Bỏ lặp TURN_OFF_HEATERS/STOP_CRASH_DETECTION trong hook hủy vì wrapper đã chạy các lệnh đó trước hook. Yêu cầu active/detected khớp trước lift/dock/park; sau dock, park chỉ chạy khi cả active và detected đều rỗng. Giữ shutdown heater ở đầu và sau dock, bảo vệ crash guard, giới hạn Z, kiểm tra nhiệt/filament và các bước QGL/Touch/prime.
- Bỏ các chú thích BUG cũ và ví dụ Orca lặp trong CFG; luồng hiện tại và hợp đồng đầu vào được ghi gọn ở đầu file. File giảm từ 1026 xuống 866 dòng.
- `extras/tests/Test-ProductionCfg.ps1`: mô hình hóa `detected_tool_number`, kiểm tra helper chung, bất đồng cảm biến và xác thực T0 sau home. Giữ nguyên `extras/tests/test_portability.py` và mọi Python runtime; runner mở rộng helper khi chạy một hợp đồng test lịch sử vốn tìm lệnh tắt fan trực tiếp trong PRINT_END.
- `extras/docs/huong-dan-he-thong-stealthchanger.en.md` và `.md`: sửa thứ tự PRINT_START/END, trường hợp T0 trống chỉ lau khô, điều kiện RESUME và đường hủy khi crash. Không sửa các báo cáo audit có ngày cũ vì chúng là ghi chép lịch sử.

### Sao lưu và kiểm tra
- Bản trước sửa: [pre-print-macro-audit-20261028-185711](file:///D:/Desktop/All-Config-Voron-main/Voron%205%20Tool/extras/backups/pre-print-macro-audit-20261028-185711/).
- `Test-ProductionCfg.ps1`: 82 bài đạt, 13 bài bỏ qua vì Bash/POSIX không có trên Windows hoặc hợp đồng lịch sử đã được thay thế. Jinja CFG biên dịch; replay xác nhận end/cancel tắt nhiệt trước và không di chuyển khi crash, mất homing, KTC lỗi hoặc active/detected bất đồng. `git diff --check` đạt.

### Chưa xác minh trên phần cứng
- Chưa triển khai/reload vì job đang in; bản live vẫn là bản trước sửa. Khi máy idle cần triển khai chọn lọc print-macros.cfg, đối chiếu hash, restart và thử đường G28/T0/QGL/Touch/prime cùng PRINT_END/CANCEL_PRINT dưới quan sát trực tiếp.
- Không triển khai toàn bộ config vì `heater_bed.max_temp` trong Git là 120°C còn live là 150°C. Lỗi cảm biến bàn nhiệt gián đoạn vẫn cần kiểm tra riêng.
