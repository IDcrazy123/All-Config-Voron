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

## 2. Tích hợp Oxplow 2.3.2 và đồng bộ máy in/GitHub

### Mục tiêu
Người dùng yêu cầu tích hợp dự án riêng đã đăng Printables vào repo Voron, đồng bộ máy in và GitHub; sau đó yêu cầu đặt runtime trong Printer-Setup và chỉ rõ nguyên nhân từng sửa đổi để bảo trì nguồn Printables.

### Nguồn và nguyên nhân
- Đọc trang [Universal Oxplow của Công Dương](https://www.printables.com/model/1846885-universal-oxplow-first-layer-z-offset-calibration) qua trình duyệt: phiên bản ZIP 2.3.2, patch-only, profile máy riêng, SVG/report, runtime bắt buộc. Công cụ web không fetch được trang; browser đọc được và tải ZIP.
- ZIP SHA-256: `65d3eb72920723a4897ae9612641962c117fa14992b111b98c8097ab8d8b484d`; kiểm manifest 22 file đạt.
- Source tại `D:/Desktop/Klipper Code/First Layer Test/generate_oxplow_gcode.py` khớp byte với ZIP. Không sửa logic generator hoặc runtime và không chỉnh dự án nguồn riêng.
- Report `Voron_Oxplow_T0-T4_2026-10-13_07.report.json` được đối chiếu SHA-256 G-code đang trên máy `36ca288c906181496c1c83bf006d3824b2b0f60e92107bc19fddca7f90cfe29f`. Dùng lại contract và hình học; loại discovery/evidence/ghi chú ủy quyền cũ khỏi profile xuất bản.
- Profile của tool đã park đổi `initial_retract: 1.8 -> 5.0` vì PRIME_LINES vừa đổi retract dock; KTC không unretract. Tool ban đầu/single-tool giữ 0.6 mm. Profile ví dụ upstream 1.8 mm không phải lỗi chung.
- Ví dụ `profiles/ktc-prime-lines.example.json` trong nguồn còn note dùng runtime 2.1.0 dù release/runtime là 2.3.2. Đã chỉ ra nguyên nhân và đề xuất sửa note dùng runtime cùng release trong INTEGRATION.md; giữ upstream nguyên bản.

### File đã sửa đổi
- `config/printer.cfg`: include một lần `Printer-Setup/oxplow_runtime.cfg`, theo vị trí người dùng yêu cầu. Tất cả nội dung cấu hình cũ và SAVE_CONFIG giữ nguyên.
- `config/Printer-Setup/oxplow_runtime.cfg`: copy byte-identical runtime 2.3.2 đã có trên máy vào payload Git.
- `extras/Printables-Package/upstream-2.3.2/`: nguyên bản release, tài liệu, tests và manifest. Launcher root trỏ tới source này.
- `extras/Printables-Package/profiles/`: bảy profile máy theo nhiệt PETG 230/70 và ABS 250/100 đã có; không chứa host/API key/raw discovery.
- `extras/Printables-Package/output/`: bảy bộ G-code/SVG/report, PETG T0–T4 riêng và PETG/ABS đủ năm tool.
- `extras/Printables-Package/legacy-v2.0.0/`: chuyển nguyên trạng file working tree cũ, gồm chỉnh sửa trước phiên chưa commit; không mất dữ liệu.
- README Anh/Việt, config/docs index và hướng dẫn Oxplow: cập nhật nguồn, vị trí runtime, file hiện hành và công thức theo report; INTEGRATION.md ghi từng thay đổi/nguyên nhân.
- `.gitattributes`: giữ byte upstream, legacy và output/report có hash. `.gitignore`: bỏ local discovery/evidence khỏi Git.

### Sao lưu
- [Snapshot trước tích hợp](</D:/Desktop/All-Config-Voron-main/Voron 5 Tool/extras/backups/pre-oxplow-232-integration-20261013-192849/README.md>) chứa working tree trước sửa và ba file config live.
- [Snapshot trước chuyển runtime](</D:/Desktop/All-Config-Voron-main/Voron 5 Tool/extras/backups/pre-relocate-oxplow-runtime-20261013-193611/README.md>) chứa printer.cfg và runtime root trước di chuyển theo chỉ thị mới.
- Sao lưu đầy đủ trên máy do installer tạo sẽ được ghi ở phần xác minh triển khai bên dưới.

### Kiểm tra
- 96/96 tests upstream đạt, không skip; gồm bốn integration test dispatcher với source Klipper commit `7bc4d0946`.
- Cả bảy profile đạt static/live GET validation; audit G-code theo limits/E/nominal area/bounds đạt, report hash khớp code.
- Bù retract đúng một lần/tool: multi-tool 0.6/5/5/5/5 mm, single nonzero tool vẫn 0.6 mm; end macro sở hữu retract và lift cuối bài.
- Giữ hình học từ report hiện hành: 51 row, X20 mm, tâm X174/Y168, nominal Z0.240, range +/-0.040, high-to-low Z0.280 -> Z0.200. Row 25 tính Delta=0; row 35 tính Delta=-0.016 mm.
- Kiểm SVG trong trình duyệt: năm patch tách biệt, trái sang phải T0 -> T4.
- Runtime copy khớp live cũ; include duy nhất; không thay offset, PID, pins, dòng motor, limits, dock, readonly KTC hay nguồn độc lập.
- Trước triển khai: printer standby, unpaused, idle, heater targets 0, dryer/benchmark dừng. Triển khai/restart sẽ recheck trước ghi.

### Kết quả và công việc còn lại
Đã hoàn tất tích hợp và kiểm tra offline. Tiếp theo: push source, cập nhật checkout máy in, chạy installer backup-first, chuyển runtime root cũ ra config_backups, nạp lại Klipper và kiểm macro/version/files. Không tự bắt đầu in hay lưu offset; phần xác minh triển khai sẽ ghi kết quả thực tế.
