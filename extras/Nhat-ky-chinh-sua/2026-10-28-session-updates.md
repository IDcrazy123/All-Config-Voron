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

## 2. Phân tích log bàn nhiệt gián đoạn

### Bằng chứng
- Đọc `klippy.log.2026-10-26`, `klippy.log.2026-10-27` và `klippy.log` ngày 28/10 trực tiếp trên máy qua SSH; đối chiếu Moonraker: máy đang in `ZAssembly_ABS_4h16m.gcode`, bàn 100/100°C tại thời điểm đọc. Không gửi lệnh nhiệt, chuyển động hoặc restart.
- Ngày 27/10 có hai lần `MCU shutdown: ADC out of range`; ngay trước khi dừng, mẫu bàn lần lượt nhảy 99,4→120,3°C và 87,1→127,5°C trong khoảng một giây. Các lần `Heater heater_bed not heating at expected rate` đi kèm tín hiệu bàn sụt/tăng bất thường khi PWM đáp ứng đến 100%.
- Ngày 28/10, khi target và PWM đều bằng 0 liên tục hơn 15 phút, mẫu bàn đi 49,7→4,4→49,8°C trong hai giây. Sự kiện khi tắt heater loại trừ thiếu công suất gia nhiệt hay riêng xung đóng ngắt SSR là nguyên nhân duy nhất. Thay đổi hàng chục độ trong một giây không thể là nhiệt thật của bàn 350 mm.
- Cấu hình live: NTC `NTC 100K MGB18-104F39050L32` trên PB0; `verify_heater` max_error=200, check_gain_time=240, hysteresis=5, heating_gain=1; smooth_time=3.0. Khác biệt max_temp Git 120°C/live 150°C vẫn tồn tại.

### Kết luận và việc còn chờ
- Xác nhận đường đo NTC bị chập chờn. Tiếp xúc hở gián đoạn ở cảm biến, dây hoặc giắc là giả thuyết ưu tiên; log chưa phân biệt được các bộ phận này, ngõ PB0 hoặc nhiễu điện khác. Không có bằng chứng để quy riêng lỗi cho SSR hoặc sai đường cong NTC; việc nới `verify_heater` sẽ che lỗi đo.
- Sau khi bản in kết thúc: ngắt điện lưới, để bàn nguội, kiểm tra gắn cảm biến và đường dây/giắc; đo điện trở NTC ở đầu controller trong lúc uốn nhẹ dây, rồi đo gần cảm biến để khoanh vùng. Chỉ sau sửa phần lỗi mới chạy thử gia nhiệt có giám sát và đối chiếu nhiệt kế độc lập.
- Chỉ cập nhật `KNOWN_ISSUES.md` và nhật ký. Không sửa CFG, không triển khai lên máy đang in.

## 3. Ẩn macro thử nghiệm và sắp lại printer.cfg

### Bằng chứng
- `printer.cfg` live và bản Git trước sửa có cùng SHA256 `672E57BC2F4243F38D150C0B902519E961ED5D7FE70E19FF0CF85F9DE3FDDA3B`; máy vẫn đang in `ZAssembly_ABS_4h16m.gcode`. Các giới hạn `[printer]` live trùng Git: XY 350/7000, Z 80/1000, square corner velocity 5.
- `test-speed.cfg` chỉ cấp `TEST_SPEED`, `TEST_Z_SPEED`; `tool-temp-bench.cfg` cấp ba lệnh đo nhiệt và biến/timer riêng; `oxplow_runtime.cfg` chỉ cấp `_OXPLOW_CHECK` cho G-code hiệu chuẩn tạo sẵn. Các file này không nằm trong luồng in thường ngày.
- Trước khi tắt benchmark, `_REQUIRE_MOTION_PREPARATION` và hai macro hiệu chuẩn PF2 đọc trực tiếp `_TOOL_HEATUP_VARS`, nên phải cho phép biến này vắng mặt. Những chỗ còn lại đã kiểm tra điều kiện tồn tại. Installer cho phép trạng thái benchmark vắng mặt khi truy vấn Moonraker.

### Thay đổi
- `config/printer.cfg`: gom chú thích theo include vận hành, module tùy chọn và giới hạn máy; comment ba include Oxplow, test tốc độ và benchmark nhiệt. Không đổi thứ tự các include còn hoạt động, giá trị `[printer]` hoặc khối `SAVE_CONFIG`.
- `config/Printer-Setup/print-macros.cfg` và `calibration-probe.cfg`: chỉ kiểm tra trạng thái benchmark khi module được nạp; khi bật lại benchmark, chặn chuyển động/hiệu chuẩn như trước.
- `extras/tests/Test-ProductionCfg.ps1`: kiểm tra các macro tùy chọn không được nạp trong cấu hình mặc định, guard hoạt động cả khi module có/vắng mặt và chỉ so khối `SAVE_CONFIG` thay vì hash toàn bộ `printer.cfg`. Các bài test benchmark độc lập vẫn chạy bằng cách nạp module tạm trong test.
- Đồng bộ hướng dẫn Oxplow và danh sách include trong README dự án, `config/README*` và `extras/Printables-Package/README.md`.

### Sao lưu, kiểm tra và triển khai
- Bản trước sửa: `extras/backups/pre-optional-macro-cleanup-20261028-195546/` (ba CFG và runner PowerShell). So sánh byte xác nhận toàn bộ phần từ dấu `SAVE_CONFIG` trở xuống không đổi.
- `Test-ProductionCfg.ps1`: 83 bài chạy, 70 đạt và 13 bỏ qua vì giới hạn Bash/POSIX hoặc hợp đồng cũ đã được thay thế; `git diff --check` đạt. Đây là kiểm tra offline, chưa chứng minh Klipper đã nạp cấu hình mới trên máy.
- Máy đang in nên chưa upload/restart. Sau khi idle và xử lý rủi ro cảm biến bàn nhiệt, triển khai cấu hình có chọn lọc rồi kiểm tra các macro thử nghiệm đã biến mất trong Mainsail. Nếu dùng G-code Oxplow tạo sẵn, bật lại `oxplow_runtime.cfg` và restart khi idle trước khi chạy.

## 4. Rà chú thích cấu hình và triển khai khi máy idle

### Bằng chứng và thay đổi
- Rà các CFG do dự án sở hữu trong `config/Printer-Setup/`, `config/toolchanger/` và `config/printer.cfg`; không sửa `mainsail.cfg`, KTC readonly, Python runtime, khối `SAVE_CONFIG` hay tài liệu lịch sử. Moonraker xác nhận bản in `ZAssembly_ABS_4h16m.gcode` đã `complete`, không pause, toolchanger `ready`, pha in `idle`, dryer tắt, target bàn 0°C trước khi ghi lên máy.
- Sửa chú thích sai thời điểm: LED chỉ phản ánh trạng thái, không ghi `_PRINT_STATE`; hook toolchange bỏ qua damping KTC kế thừa khi chưa bật tần số riêng; Oxplow/test tốc độ/benchmark nhiệt là include tùy chọn; bỏ số dock cũ và nhãn BUG lịch sử. Gỡ các banner lặp, mô tả benchmark không còn khẳng định phép đo thời gian chứng minh wattage hoặc vị trí cảm biến lỗi. Bổ sung ghi chú smooth_time/SSR không sửa được đường NTC chập chờn.
- Chỉ đổi chú thích và một `description` LED. So sánh bản trước/sau của 18 file CFG bằng parser cho thấy không có thay đổi section/value/G-code ngoài `description`. Runner được sửa để kiểm tra chân heater PA1, NTC PB0, chamber PB1 thay cho so hash nguyên CFG; hash file readonly và Python vẫn được giữ.

### Kiểm tra và triển khai
- Sao lưu nguồn Git trước sửa tại `extras/backups/pre-comment-audit-20261028-200526/`. `Test-ProductionCfg.ps1`: 83 bài chạy, 70 đạt, 13 bỏ qua; `git diff --check` đạt. Commit chú thích `da76c29` đã push.
- Đối chiếu từng file live: đa số khớp Git trước sửa; `printer.cfg`, `print-macros.cfg`, `calibration-probe.cfg`, T0/T2 và `hardware.cfg` có drift đã biết. T0/T2 và calibration không khác giá trị cấu hình ngoài macro/chú thích. `hardware.cfg` chỉ khác `heater_bed.max_temp`: Git 120°C, live 150°C.
- Triển khai chọn lọc 18 CFG sau khi kiểm tra idle hai lần. Bản live trước ghi nằm tại `/home/voron/printer_data/config_backups/comment-audit-20261028-2015/backup/`, kèm manifest SHA256; bản stage nằm cùng thư mục. File hardware stage giữ nguyên `max_temp: 150` của máy, không chép giới hạn Git 120 lên production. Chép file bằng thay thế từng file và xác nhận hash, sau đó kiểm tra idle lần nữa rồi gọi Klipper restart.
- Sau restart, Moonraker báo Klipper `ready`, print `standby`, target bàn 0°C, `max_temp` live vẫn 150°C. `PRINT_START`/`PRINT_END` còn trong config; `_OXPLOW_CHECK`, `TEST_SPEED`, `TEST_Z_SPEED`, `MEASURE_TOOL_HEATUP`, `STOP_TOOL_HEATUP`, `BENCH_TOOL_TEMP` không còn được nạp. Toolchanger `uninitialized` ngay sau restart; PRINT_START sẽ khởi tạo lại, chưa thử pickup/QGL/Touch hoặc in thật.

### Còn mở
- Không coi Klipper ready là xác nhận cơ khí. Cần quan sát chu trình in đầu tiên sau deploy; lỗi đường NTC bàn đã xác nhận ở mục 2 vẫn phải xử lý trước khi tin cậy bản in gia nhiệt dài. Chênh lệch `max_temp` Git/live chưa được giải quyết.
