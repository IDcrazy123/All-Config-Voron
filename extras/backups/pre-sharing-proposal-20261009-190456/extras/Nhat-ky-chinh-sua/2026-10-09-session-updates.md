# Nhật ký — 2026-10-09

## 1. Tổng duyệt cấu hình đang chạy và cải thiện khả năng chia sẻ

### Mục tiêu
Đọc logic theo từng module, đối chiếu với máy thật, sửa lỗi rõ ràng và comment sai; xác định thông số do từng máy sở hữu để người dùng khác dễ điều chỉnh. Người vận hành xác nhận CAN T1 đã sửa; lỗi EXCLUDE_OBJECT khi in nhiều tool chưa sửa.

### Đối chiếu máy thực tế
- Truy cập chỉ đọc Moonraker và SSH tại `192.168.1.43`, tài khoản `voron`. Mốc dữ liệu cấu hình: `2026-10-09T17:30:58.273140+07:00`.
- 32 file cấu hình/script/patch khớp nội dung trước sửa, sau chuẩn hóa xuống dòng; sáu symlink readonly KTC hợp lệ. Máy ready và đang thực hiện job ABS `panel-latch-2020-6_0mm-no-logo_ABS_1h39m.gcode`.
- Đọc source runtime thực tế: Klipper `7bc4d0946`, KTC `e881fe4`, Axiscope `9a1a9ef`; Moonraker `v0.11.0-3-g9e676eb`. Không suy diễn phiên bản checkout là source upstream nguyên bản vì máy có crash patch riêng.
- Mẫu EBB1 hiện tại: `rx_error=0`, `tx_error=0`, `tx_retries=0`; không dùng mẫu ngắn này để kết luận độ bền CAN. Không được cung cấp chi tiết phương pháp sửa T1.
- Bằng chứng gọn và hash: [audit evidence](</D:/Desktop/All-Config-Voron-main/Voron 5 Tool/extras/audits/2026-10-09/README.md>). Snapshot/source tải về để đọc nằm cục bộ, không đưa lên Git.

### File đã sửa đổi
- `config/Printer-Setup/tool-temp-bench.cfg`: mapping tool/heater theo cấu hình, dùng chung tọa độ station, kiểm tra giới hạn heater và quyền sở hữu nhiệt trong lúc in/sấy.
- `config/Printer-Setup/print-macros.cfg`: biến soak, guard benchmark, mapping standby/fan/extruder, sửa comment alias mesh.
- `config/Printer-Setup/prime-lines.cfg`: abort điều kiện đầu vào sai và bố trí X không đủ chỗ; mapping standby, hướng dẫn chỉnh vùng prime.
- `config/Printer-Setup/fans-leds.cfg`: mapping shutdown, sửa comment LED/trạng thái/scope/queue.
- `config/Printer-Setup/filament-dryer.cfg`: guard benchmark, hướng dẫn tùy chỉnh, mô tả chính xác RH và idle keepalive trên runtime hiện tại.
- `config/Printer-Setup/nozzle-clean.cfg`, `calibration-probe.cfg`, `test-speed.cfg`: sửa comment, chỉ rõ các đầu vào và giới hạn kiểm thử; thông báo purge lấy tọa độ cấu hình.
- `config/toolchanger/toolchanger-config.cfg`: override deadband trong file người dùng sở hữu, hỗ trợ số tool không liên tục; sửa mô tả tọa độ tiếp cận dock.
- `config/scripts/install.sh`: đường dẫn/URL/dry-run tùy chọn, kiểm tra trạng thái máy trước ghi, giữ file riêng và backup cũ, yêu cầu crash runtime/patch.
- README gốc, README config, README Orca, chỉ mục docs và hai tài liệu mới: báo cáo 20 finding theo module và worksheet chuyển sang máy khác.
- Hai script hồi quy mới dưới `extras/tests/`; evidence gọn dưới `extras/audits/2026-10-09/`.
- Quy tắc workspace `.agents/PROJECT.md`, `DIRECTORY.md`, `KNOWN_ISSUES.md`, `TODO.md`: cập nhật Axiscope/brush, CAN T1 đã sửa và lỗi còn mở. Thư mục `.agents` bên ngoài Git root; bản hiện hành chỉ lưu tại workspace, nội dung liên quan được ghi trong báo cáo/journal.

### Sao lưu
- [Bản gốc trước tổng duyệt](</D:/Desktop/All-Config-Voron-main/Voron 5 Tool/extras/backups/pre-project-audit-20261009-173322/BACKUP_RECORD.md>), tạo lúc `2026-10-09T17:33:22.454887+07:00`. Giữ đường dẫn gốc cho config/script/docs; quy tắc workspace lưu dưới `workspace-rules/`.
- Không ghi đè hoặc xóa backup trước đây. Các tài liệu bổ sung cũng được chép bản gốc trước khi sửa.

### Chi tiết thay đổi
- Tool benchmark: giới hạn số `0..4` → danh sách `tool_numbers`; tên `extruderN` → `tool_names`/`tool.extruder`; ngưỡng `290 C` → nhiệt độ nhỏ hơn `max_temp` của heater được chọn.
- Tọa độ benchmark `315/1/15` → `CLEAN_NOZZLE.purge_x/purge_y/safe_z`; giá trị máy này vẫn giữ `315/1/15`.
- Soak hằng `30/60/90/90 s` → biến `pla_soak/petg_soak/abs_soak/hot_bed_soak` cùng giá trị mặc định; tham số `SOAK` của job vẫn ưu tiên cao nhất.
- Deadband mặc định vẫn `4 C` (±2 C); đổi cách tìm tool từ index trực tiếp sang cặp số/tên, không sửa readonly KTC.
- PRIME_LINES lỗi chỉ RESPOND → `action_raise_error`; từ chấp nhận slot X quá nhỏ → từ chối khi không thể bố trí ít nhất 5 mm/tool cùng gap.
- Installer `rsync --delete` → sync không xóa file riêng; bỏ tự động xóa Markdown/prune backup; backup timestamp cố định → thư mục `mktemp` duy nhất. Thêm `VORON_CONFIG_DIR`, `VORON_BACKUP_ROOT`, `VORON_MOONRAKER_URL`, `VORON_DEPLOY_DRY_RUN`.
- Installer chưa kiểm tra hoạt động → kiểm tra fail-closed print/pause/toolchange/idle và macro start/dryer/benchmark; trạng thái bắt buộc thiếu hoặc không nhận diện bị từ chối. Kiểm tra lại ngay trước lần ghi đầu tiên. Đây chưa phải khóa ngăn job mới bắt đầu.
- README dock Y cũ được cập nhật theo config đang chạy: T0 `1.8`, T1 `1.5`, T2 `2.1`, T3 `2.5`, T4 `3.1`; không thay đổi dock thực tế.

### Lý do
Loại bỏ một số giả định tên/số tool và tọa độ bị lặp; giúp thay thông số ở đúng chủ sở hữu, phát hiện điều kiện sai trước khi xuất lệnh và hạn chế triển khai vào máy đang hoạt động. Các thay đổi cần đo vật lý được ghi thành đề xuất cụ thể thay vì áp dụng giá trị phỏng đoán.

### Kiểm tra
- 25 file CFG trong include graph; 125 template Jinja được biên dịch thành công theo delimiter và cách merge cấu hình của Klipper đã đọc.
- 14 ca hồi quy offline đạt: tên tool riêng/số tool không liên tục, heater/station, soak mặc định/tùy chỉnh/thủ công, thứ tự prime/đầu vào lỗi, sở hữu benchmark; installer từ chối trạng thái bận/thiếu, runtime thiếu, dry-run, giữ backup và đường dẫn backup duy nhất.
- So sánh chuỗi lệnh mặc định của năm helper trước/sau: PRINT_END, custom cancel, prime helper, benchmark, soak khớp sau loại thông báo hiển thị.
- Giá trị phần cứng, pins, PID, dòng motor, giới hạn trục, dock và motion hooks giữ nguyên.
- `bash -n` install/update/cleanup và kiểm tra whitespace Git đạt. Fixture rsync chỉ kiểm tra đối số/điều kiện, không mô phỏng cơ chế copy của rsync.
- Không deploy, restart Klipper, gửi G-code, chạy heater/motion hoặc thử in cấu hình mới. Không đo trực tiếp dây điện, tiếp xúc brush hay clearance dock.

### Kết quả
- [Báo cáo tổng duyệt và đề xuất](</D:/Desktop/All-Config-Voron-main/Voron 5 Tool/extras/docs/project-audit-2026-10-09.md>).
- [Worksheet chuyển sang máy khác](</D:/Desktop/All-Config-Voron-main/Voron 5 Tool/extras/docs/machine-adaptation.md>).
- Các thay đổi có sẵn tại repository để review và triển khai khi máy idle. Thay đổi Printables/G-code/backup tồn tại trước phiên này không được đưa vào commit của tổng duyệt.

### Vấn đề còn lại
- P1: PRINT_END nâng tương đối Z5 trước khi clamp; tại Z345/max347 có thể yêu cầu Z350 và dừng trước shutdown. End/cancel còn trộn tọa độ vật lý/G-code khi offset hoạt động.
- P1: Axiscope gọi T0 cuối trước finish hook nâng Z; cancel Mainsail sau crash có thể park XYZ trước custom cleanup.
- EXCLUDE_OBJECT nhiều tool vẫn chưa sửa: cần state extrusion theo từng extruder, replay trường hợp lỗi và coupon có giám sát.
- Input shaper: damping cấu hình chung `0.124/0.080` nhưng mặc định tool KTC chọn `0.1/0.1`; cache runtime hiện tại xác nhận `0.1/0.1`. Đề xuất sửa lựa chọn profile sau khi kiểm chứng tuning.
- TEST_Z_SPEED dùng tham số Z không được runtime hỗ trợ; TEST_SPEED thiếu guard/restore crash detection. Comment đã chỉ rõ, logic chuyển động chưa thay.
- Worksheet chưa biến toàn bộ dự án thành một file profile; T0, cơ cấu dock, brush, probe, park, fan/LED và dữ liệu calibration vẫn cần đo/adapt. Phạm vi tổng duyệt tập trung code/config đang dùng, không khẳng định rà từng dòng toàn bộ archive/G-code lịch sử.
