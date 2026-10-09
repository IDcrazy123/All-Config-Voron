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

## 2. Đề xuất chia sẻ độc lập từng file CFG cho StealthChanger khác

### Mục tiêu
Lập đề xuất thay đổi toàn diện để người khác dùng riêng từng tính năng trên StealthChanger có số tool/vị trí khác, chỉnh ít nhất có thể và đọc hướng dẫn ngay trong file tải về. Phiên này chỉ lập thiết kế, không triển khai cấu trúc CFG mới.

### Phân tích
- Kiểm tra include graph, section/macro và các lời gọi giữa các file active. Benchmark đang đọc cleaner/dryer/private print state kể cả khi bỏ park; dryer gọi LED; fans-leds chứa cả hardware, trạng thái, RESUME/cancel; print-macros chứa QGL/Cartographer/T0 và các policy khác.
- KTC readonly include glob nạp `tools/T*.cfg`: số tool phải lấy từ định nghĩa thực tế; một biến tool_count riêng có thể lệch với registry. Số tool không đủ mô tả vị trí/đường dock/clearance.
- Tham khảo tài liệu Klipper chính thức về macro variables, G-code state, template evaluation và configuration sections. Đây là cơ sở ngăn thiết kế biến macro thay thế trái phép pin/UUID hoặc đọc trạng thái mới ngay trong cùng template.
- Không kết nối hoặc thay đổi máy in trong tác vụ đề xuất này. Sử dụng source/config đã đọc và bằng chứng đối chiếu của mục 1.

### File đã sửa đổi
- Thêm `extras/docs/stealthchanger-sharing-proposal.md`: mục tiêu, kiến trúc, hợp đồng đầu vào, phụ thuộc, kế hoạch theo từng file, mẫu comment, test matrix và sáu giai đoạn triển khai.
- Cập nhật hai chỉ mục docs Anh/Việt, ghi rõ đây là đề xuất chưa thực hiện.
- Bổ sung mục 2 vào nhật ký hôm nay; không sửa CFG/CONF/SH production, thông số máy hay các thay đổi Printables/G-code tồn tại trước.

### Sao lưu
- [Bản gốc chỉ mục và nhật ký trước đề xuất](</D:/Desktop/All-Config-Voron-main/Voron 5 Tool/extras/backups/pre-sharing-proposal-20261009-190456/README.md>).

### Nội dung đề xuất
- Mỗi tính năng độc lập có file CFG gồm khối EDIT HERE, macro public, helper/callback riêng, CHECK/HELP chỉ đọc; không bắt buộc một file profile chung khi chỉ tải một tính năng.
- Người lấy cả bộ có thể dùng variable overrides riêng; phần cứng/UUID/PID/offset/SAVE_CONFIG vẫn ở chủ sở hữu thật, không sao chép calibration máy hiện tại.
- Tách LED/fan khỏi Mainsail recovery; PRINT_START/M109/RESUME và các override chỉ ở integration được chọn rõ ràng. Prefix SC cho API thư viện tương lai; giữ tên production qua wrapper.
- Phân loại DISCOVERED / USER_REQUIRED / USER_OPTIONAL; geometry chưa nhập bị chặn, park mặc định tắt ở benchmark/dryer chia sẻ. Tool mapping qua registry, không giả định T0–T4/extruderN.
- Reference tool chỉ đổi khi backend hỗ trợ: Axiscope/luồng T0-only phải giữ giới hạn hoặc được adapter riêng, không hứa chỉ thay chuỗi T0 là đủ.
- Xuất một file từ source thống nhất, khai báo version/schema/dependency/conflict; update chỉ file được chọn và giữ thông số local. Mẫu board `.cfg.example` nằm ngoài include globs.
- Lộ trình sáu bước: hợp đồng/scaffold → benchmark/prime độc lập → hardware/UI → station/dryer → lifecycle/calibration/shaper/recovery → đóng gói và migration có kiểm chứng.

### Kiểm tra và kết quả
- Rà liên kết tài liệu, cú pháp snippet settings và whitespace Git; đối chiếu mọi file production trong bảng chuyển đổi với inventory hiện có.
- Không chạy test phần cứng hoặc tuyên bố kiến trúc mới đã đạt 14 ca hồi quy cũ. Các tên SC, include, CHECK/HELP là thiết kế dự kiến, chưa có release thực thi.
- Tiêu chí nghiệm thu được đề xuất cho 2/5/6 tool, registry không liên tục, tính năng tùy chọn thiếu, offset/mesh/Z max, xung đột operation, recovery, update và người dùng độc lập.
- [Đề xuất chi tiết](</D:/Desktop/All-Config-Voron-main/Voron 5 Tool/extras/docs/stealthchanger-sharing-proposal.md>).

### Vấn đề còn lại
- Cần thực hiện từng module theo các completion gate trong đề xuất; code production hiện hành vẫn giữ cấu trúc cũ.
- Những workflow có motion/recovery chỉ được công bố sau khi xử lý finding A04–A07 và diagnostic defects cùng thử nghiệm có giám sát; EXCLUDE_OBJECT nhiều tool vẫn mở. CAN T1 đã sửa theo xác nhận người vận hành.

## 3. Điều chỉnh đề xuất đúng mục tiêu chia sẻ file CFG hiện có

### Mục tiêu và yêu cầu đã làm rõ
Người dùng không chấp nhận gom thông số vào EDIT HERE; mục tiêu là gửi riêng từng CFG cho người có dự án StealthChanger tương tự, dùng ngay khi thông số phù hợp hoặc chỉnh vài thông số tại đúng chỗ đang sở hữu chúng. Không yêu cầu người nhận lấy cả dự án hoặc dùng kiến trúc/profile/framework mới.

### Thay đổi
- Viết lại đề xuất hiện hành theo yêu cầu vừa làm rõ; mục 2 giữ nguyên như lịch sử thiết kế đã được thay thế.
- Giữ tên file/macro hiện có, giữ tham số trong section/macro đang sử dụng; comment cạnh dòng cần sửa nêu đơn vị, hệ tọa độ, cách đo/chọn và những chỗ phải đồng bộ.
- Đề xuất sửa nhỏ các giả định số/tên tool và phụ thuộc chéo không cần thiết. Helper/callback thiết yếu thuộc cùng file; LED/status tùy chọn được kiểm tra trước truy cập. Giữ đầy đủ các kiểm tra an toàn cần thiết.
- Bỏ chiến lược global profile/override hierarchy/EDIT HERE, namespace SC, generator/manifest/package và yêu cầu installer cả dự án.
- Lập bảng từng file: phần cần làm độc lập, chỗ người nhận phải chỉnh và phụ thuộc thật. File gộp hardware/recovery hoặc cần backend/calibration cụ thể được mô tả đúng là integration/reference, không hứa một include là đủ.
- Ưu tiên prime-lines và benchmark, tiếp đến dryer/cleaner; không công bố các luồng diagnostic/lifecycle/calibration đang có lỗi là sẵn dùng.
- Cập nhật cả hai chỉ mục tài liệu; không sửa CFG/CONF/SH production hay kết nối máy in trong tác vụ này.

### Sao lưu
- [Bản đề xuất/chỉ mục/nhật ký trước điều chỉnh](</D:/Desktop/All-Config-Voron-main/Voron 5 Tool/extras/backups/pre-sharing-proposal-correction-20261009-191616/README.md>).

### Kiểm tra và kết quả
- Kiểm tra liên kết tài liệu, phạm vi diff, comment ví dụ khớp tham số hiện có và whitespace Git.
- Không chạy lại kiểm thử motion/heater vì đây chỉ là sửa tài liệu; không tuyên bố các CFG hiện tại đã đạt tính độc lập.
- [Đề xuất hiện hành](</D:/Desktop/All-Config-Voron-main/Voron 5 Tool/extras/docs/stealthchanger-sharing-proposal.md>).

### Việc còn lại
Áp dụng các thay đổi nhỏ theo từng CFG và kiểm tra file đó trong fixture chỉ có phụ thuộc được công bố, thay vì nạp cả repository. Các issue production của mục 1 vẫn giữ nguyên; CAN T1 đã sửa, EXCLUDE_OBJECT nhiều tool chưa sửa.

## 4. Chuẩn bị các CFG hiện có để chia sẻ riêng từng file

### Mục tiêu
Thực hiện yêu cầu chia sẻ một CFG cho người có dự án StealthChanger tương tự. Giữ tên file/macro và thông số tại section/macro đang sử dụng; không tạo khối EDIT HERE, global profile hay framework mới.

### Sao lưu
- [Bản gốc 18 CFG, test, chỉ mục và nhật ký trước sửa](</D:/Desktop/All-Config-Voron-main/Voron 5 Tool/extras/backups/pre-individual-cfg-sharing-20261009-193324/README.md>).
- Tất cả CFG được sao lưu trước khi sửa. Bản sao lưu cũ giữ nguyên; không sửa KTC readonly hoặc upstream mainsail.cfg.

### File đã sửa đổi và chi tiết
- Cả 18 CFG do người dùng sở hữu: `printer.cfg`, 11 file `Printer-Setup/*.cfg`, `toolchanger/toolchanger-config.cfg`, `tools/T0.cfg` đến `T4.cfg`. Thêm comment tiếng Anh về phạm vi chia sẻ, phụ thuộc thật, include/xung đột, chỗ cần chỉnh, đơn vị/hệ tọa độ, thông số cần đồng bộ và dữ liệu calibration thuộc máy nhận.
- `tool-temp-bench.cfg`: cleaner/LED/dryer/private state tùy chọn; không có cleaner thì không park mặc định. Hỗ trợ PARK_X/Y/Z ngay tại lời gọi; yêu cầu đủ ba tọa độ, tool đang mounted, XYZ homed, offset zero và bounds hợp lệ. Đánh dấu đang chạy trước chờ nhiệt; thêm `_TOOL_HEATUP_START_TIMER` kiểm tra lại sau bước chuẩn bị. Callback/STOP nhường heater khi có print/pause hoặc state không chắc chắn; timer hủy khi heater target đổi. STOP không xóa được lệnh đã queue trong Klipper. Timer vẫn đếm tick, không hứa thời gian monotonic tuyệt đối.
- `prime-lines.cfg`: giữ registry tool động và geometry hiện có; kiểm tra heater/temperature của mọi tool được dùng trước khi phát lệnh. Comment giải thích first-layer/travel/line/extrusion owners.
- `nozzle-clean.cfg`: giữ hạn chế T0/extruder, pad/contact/thermal/offset/mesh/QGL; fan được tìm theo tool registry thay vì khóa tên T0_part_fan. LED/private operation state tùy chọn; native print/pause luôn cần. STARTING=1 dành cho lời gọi pre-extrusion của PRINT_START bên nhận và được truyền xuống helper; nếu có _PRINT_STATE thì state đó luôn ưu tiên.
- `filament-dryer.cfg`: LED/benchmark/private state/bed_fan_off_delay tùy chọn; callback delayed được kiểm tra qua configfile.config, không giả định có get_status. Yêu cầu fan thật và sensor thật khi đặt target chamber/humidity; CHAMBER=0 cho bed-only, FAN=0 được giữ cả lúc start và timer. Kiểm tra max_temp bed theo máy nhận; overheat không nâng một BED custom thấp lên 45. PARK=1 phải homed/zero offsets/bounds hợp lệ, giữ Z200 + KTC docking + X175/Y310; dùng PARK=0 khi chưa xác minh đường đi. Không auto-home từ snapshot stale. Native pause/unknown state khiến callback nhường nhiệt/quạt cho print.
- `test-speed.cfg`: thêm preflight idle/unpaused, homed/QGL nếu có, zero offsets, positive parameters và pattern bounds; phép thử không vượt caps cấu hình. Bỏ lệnh chủ động tắt crash detector vì plugin không công bố trạng thái enable để khôi phục chính xác. TEST_Z_SPEED bỏ Z_VELOCITY/Z_ACCEL không được Klipper hỗ trợ, dùng VELOCITY/ACCEL hợp lệ cho pure-Z cycle; native Z caps vẫn áp dụng. Khôi phục giới hạn runtime tại entry khi hoàn tất bình thường, không lấy defaults từ config. Interruption/error vẫn có thể bỏ qua restore và cần kiểm tra trước tiếp tục.
- `tool-crash.cfg`: kiểm tra hợp đồng Mainsail RESUME variables và PAUSE rename_existing trước khi handler phát lệnh. Giữ detector values/no-XYZ crash pause; CANCEL_PRINT bên nhận vẫn phải review riêng.
- `toolchanger-config.cfg`: change hooks không bắt buộc LED, _PRINT_STATE hoặc biến color trong macro Tn của người nhận; trạng thái print/pause native là fallback. Không sửa đường dock hoặc shaper tuning.
- `tools/T0..T4.cfg`: delayed runout giữ project handler khi có; nếu thiếu, fallback PAUSE tại chỗ chỉ cho tool đang active, còn hết filament sau debounce, đang printing và chưa paused. Giữ nguyên pins, UUID, PID/current/offset/docks. Comment input-shaper sửa lời hứa sai rằng bỏ frequency override là giữ được global damping.
- Thêm [hướng dẫn chia sẻ thực tế từng file](</D:/Desktop/All-Config-Voron-main/Voron 5 Tool/extras/docs/sharing-cfg-files.md>), cập nhật cặp README config/docs Anh–Việt. File hardware/lifecycle/calibration được công bố là reference/integration với phụ thuộc thật, không quảng bá tất cả là một include dùng ngay.
- Thêm `extras/tests/test_individual_cfg.py`; cập nhật regression benchmark trong `test_portability.py` theo continuation mới. Các thay đổi Printables/G-code có sẵn trước tác vụ không được stage/commit.

### Lý do
Loại phụ thuộc chéo không cần thiết và giả định tên/số tool, đồng thời giữ việc chỉnh thông số tại chủ sở hữu thực. Comment phải cho người nhận biết chính xác phần nào chỉ cần sửa thông số và phần nào cần backend/wiring/workflow tương đương, tránh hứa mức độc lập không có thật.

### Kiểm tra và kết quả
- `VORON_TEST_BASH="D:\App Installs\Git\bin\bash.exe"` cùng `python -m unittest discover -s extras/tests -v`: **32/32 đạt**, không skip (18 isolated-feature tests, 10 portability tests, 4 installer tests).
- Chuỗi include local gồm 25 file; biên dịch **126 Jinja templates**. Fixture riêng feature không nạp trạng thái/LED của cả dự án để che phụ thuộc.
- Kiểm tra 2/5/6 tool, số không liên tục 0/7, custom extruder/fan, thiếu helper/sensor/callback, park/offset/contact/print/pause, timer handoff/ownership, native runout fallback, motion cap và runtime restore.
- So sánh toàn bộ option cũ ngoài G-code hooks trên 18 CFG với bản backup: giá trị hardware, PID/current/limits/geometry/native options không đổi. SAVE_CONFIG giữ nguyên. Representative cleaner/prime/dryer motion/heat commands ở mặc định hợp lệ khớp backup.
- Kiểm tra 18/18 sharing headers, liên kết docs và Git whitespace. Test chỉ mô phỏng render/variable writes, không xác nhận firmware/plugin loading hoặc clearance/nhiệt/concurrency trên máy thật.
- Không SSH/deploy, restart Klipper, gửi G-code, chạy heater/motion hay test in trong tác vụ này. Các chỉnh sửa hiện có trong repository.

### Vấn đề còn lại
- EXCLUDE_OBJECT nhiều tool chưa sửa; CAN T1 đã sửa theo người vận hành.
- END/CANCEL lift tại max-Z và frame tọa độ, crash CANCEL parking, Axiscope return-to-T0, inherited damping KTC vẫn mở. Phần diagnostic đã sửa lệnh/guard/restore như mô tả, nhưng cần commissioning có người giám sát trước dùng trên máy khác.
- Calibration/hardware/lifecycle references vẫn có phụ thuộc được ghi rõ; không hứa mọi file chỉ sửa vài số là dùng trên mọi loại máy. Người nhận giữ PID, offsets, limits và đo dock/pad/mesh của máy họ.

## 5. Triển khai cấu hình chia sẻ từng CFG lên máy in

### Mục tiêu
Thực hiện yêu cầu triển khai bộ cấu hình đã kiểm tra, source commit `4041d5ee90db9b1e55485d40402ef5ed0c82cad2`, tới `voron@192.168.1.43` và kiểm tra Klipper nạp lại.

### Kiểm tra trước ghi
- Moonraker/Klipper ready; job `panel-latch-2020-6_0mm-no-logo_ABS_1h39m.gcode` complete, Idle, không paused, toolchanger ready nhưng không tool mounted. XYZ chưa homed; tất cả bed/hotend target 0, dryer/benchmark không chạy, _PRINT_STATE idle.
- Đọc cấu hình live trước ghi: 28 file tương ứng payload, không có file thiếu. Native hardware/geometry/limits và SAVE_CONFIG khớp source; không thay đổi PID, current, UUID, pin, dock hay calibration thực tế.
- Soak variables mới ABS90/PETG60/hot-bed90/PLA30 phản ánh defaults đã review trong commit audit; không có chỉnh tuning mới trong tác vụ deploy.
- Source staging lấy từ git archive của commit đã push, không lấy Printables/G-code hoặc file untracked đang chỉnh. Chuỗi include dùng sáu readonly file live: 25 file, 126 template biên dịch thành công bằng Jinja 2.11.3 trong klippy-env thực tế.
- Installer dry-run xác nhận chỉ 18 CFG user-owned và `scripts/install.sh` khác nội dung. File không đổi được giữ timestamp/mode ở staging để không ghi thừa vào destination. mainsail.cfg/service config giữ nguyên.

### Sao lưu
- [Bản ghi triển khai và backup live local](</D:/Desktop/All-Config-Voron-main/Voron 5 Tool/extras/backups/pre-deploy-individual-cfg-20261009-210532/deployment-record.md>).
- `live-config-before.tar`: bản chính xác của 28 file payload live trước ghi; không tải secrets hoặc generated results vào Git.
- Backup đầy đủ trên máy in do installer tạo trước rsync: `/home/voron/printer_data/config_backups/config-install-20261009-210823-F2BuYW`.
- Backup giữ sáu readonly symlink và destination-only files; không xóa config/backup cũ. Sao lưu nhật ký và các docs trước cập nhật trạng thái deploy trong cùng thư mục local.

### Triển khai
- Chạy install.sh từ staging `/tmp/voron-deploy-4041d5e.9vXTYN` với Moonraker cùng máy `http://127.0.0.1:7125`. Idle được installer kiểm tra lại ngay trước ghi.
- Cập nhật 18 CFG và installer. Runtime tool_crash đã có patch active-tool-validation nên không phải patch lại; Axiscope/runtime/plugin và readonly KTC không bị sửa.
- So sánh sau ghi: 28/28 file payload khớp source, chín file không đổi giữ chính xác nội dung cũ; sáu symlink readonly nguyên target và còn hợp lệ.
- Kiểm tra lại Idle/print/pause/toolchanger/dryer/benchmark/heater targets trước gửi `POST /printer/restart`; RESTART trả ok. Không cần restart Moonraker vì service configuration không đổi.

### Kết quả kiểm tra sau restart
- Klipper `v0.13.0-777-g7bc4d0946-dirty`: **ready / Printer is ready**. Moonraker không failed component hoặc warning; registry nạp đủ T0–T4, `_TOOL_HEATUP_START_TIMER` mới đã có.
- Heater bed và năm hotend target 0; _PRINT_STATE idle, dryer/benchmark không chạy. Toolchanger uninitialized và XYZ chưa homed là trạng thái sau restart; không tự initialize/home để tránh chuyển động không được yêu cầu.
- Lệnh chỉ đọc `CALIBRATION_STATUS`, `CHECK_OFFSETS`, `QUERY_ENDSTOPS` trả ok. Axiscope active; endstop Axiscope/X/Y/Z open ở mẫu kiểm tra.
- Offset được báo: T0=(0,0,0); T1=(-0.139,-0.341,0.1665); T2=(1.095,-0.09,-0.3515); T3=(0.003,0.369,-0.3265); T4=(0.213,-0.007,0.0279), khớp calibration hiện hành.
- Mẫu CAN sau startup: mcu, EBB0–EBB4, cartographer đều active; rx_error/tx_error/tx_retries 0. Không có config-load error hoặc shutdown trong phần startup vừa kiểm tra.
- Có một traceback `Write g-code response / BlockingIOError: [Errno 11] Resource temporarily unavailable` tại `gcode.py:_respond_raw` khi khởi động. Đối chiếu runtime cho thấy handler catch os.error, ghi log và tắt output-pipe flag; không shutdown Klipper. API/read-only commands hoạt động sau đó. Không sửa runtime vì đây chưa phải bằng chứng lỗi CFG mới; lưu trace trong `verification-after-restart.json` để theo dõi kênh serial response nếu cần.
- Không homing, toolchange, gia nhiệt, calibration hoặc test in. Đây là xác nhận deploy/config loading và kiểm tra chỉ đọc, chưa là commissioning tính năng vật lý.

### Tài liệu và việc còn lại
- Cập nhật sharing guide và hai cặp README để phân biệt đã deploy máy hiện tại với chưa thử motion/heating/máy khác; source CFG không thay thêm trong tác vụ này.
- EXCLUDE_OBJECT nhiều tool, END/CANCEL max-Z/frame, crash cancel parking, Axiscope return-to-T0 và inherited KTC damping vẫn mở; triển khai không được hiểu là đã sửa các issue đó.

## 6. Kiểm tra sau vận hành và sửa phản hồi G-code lúc khởi động

### Yêu cầu và bằng chứng
- Người dùng báo đã chạy nhiều thao tác, máy ổn định; yêu cầu kiểm tra lỗi tiềm tàng và sửa lỗi response lúc startup.
- Console có G28, QGL và nhiều lượt đổi T0–T4 không response lỗi. Đây là thao tác người vận hành, không phải motion test do assistant chạy.
- Máy standby/unpaused, _PRINT_STATE idle, dryer/benchmark dừng, các heater target 0 trước ghi và trước restart. T0 đang mounted trước service restart.
- CAN T1 vẫn được xem là đã sửa theo người dùng; EXCLUDE_OBJECT nhiều tool còn mở.

### Nguyên nhân và thay đổi
- Runtime Klipper `7bc4d09465d31cd30fc0822e8d0abe02cc8c547f`: GCodeIO bật pipe lúc startup, ghi vào PTY nonblocking dù không có serial consumer quan sát được. Output tích lũy qua soft restart gây EAGAIN. Moonraker dùng Unix API socket nên vẫn nhận response.
- Thêm `config/scripts/patches/klipper-pty-client-gate.patch`: pipe khởi tạo inactive; input handler hiện có bật lại khi client gửi dữ liệu. Không thay command processor, exception handler, debug-file input hoặc API output subscription; không retry blocking hay chỉ che traceback.
- Đã áp dụng vào runtime thật `/home/voron/klipper/klippy/gcode.py` bằng thay file atomic sau SHA/context/syntax checks. Bản patch artifact mới cũng có tại `printer_data/config/scripts/patches/`; installer không tự áp dụng core patch này.
- Không thay CFG, PID, sensor_type, currents, limits, dock hoặc calibration. Không sửa mainsail.cfg/readonly KTC. Client legacy chờ banner tự phát phải gửi command trước; backpressure sau khi client active vẫn là giới hạn hiện có.
- Git attributes giữ LF cho riêng patch mới để khi checkout Windows rồi chuyển sang máy Linux vẫn giữ context; đã sao lưu attributes trước sửa.

### Sao lưu
- [Backup local trước sửa](</D:/Desktop/All-Config-Voron-main/Voron 5 Tool/extras/backups/pre-startup-response-20261009-213009/README.md>): gcode.py live gốc, hai docs index, nhật ký và KNOWN_ISSUES.
- Backup runtime trên máy: `/home/voron/printer_data/config_backups/runtime-pty-20261009-213009/gcode.py`; không ghi đè backup cũ.
- SHA-256 gốc `a2bcd6949b4263f608eaa71ba1cdfb713553542b7b90de739241b624f06415ae`; sau patch `4ba80ab638b6fa49b92ea07906a198fd49ed08dff42fafebff64be55da600dc8`.

### Kiểm tra và kết quả
- `test_klipper_pty.py`: 6/6 test đạt trên Linux/klippy-env với source thật và PTY riêng; tái hiện baseline đầy buffer, patched startup/restart không ghi vào pipe chưa active, API vẫn đủ responses, M115 client-first hoạt động, error handler/recovery/debug input giữ nguyên. Không nối PTY fixture vào máy in.
- Windows: cả suite 38 tests chạy, 34 đạt và 4 PTY tests skip đúng nền tảng; 4 bài này đã đạt riêng trên Linux. 32 tests CFG/portability/installer trước đó vẫn đạt. Kiểm tra native options/macro templates và whitespace Git không lỗi.
- Service restart qua Moonraker thành công lúc 21:33:51; PID 767 → 8125 chứng minh core module được nạp mới. Soft RESTART lúc 21:34:42 cũng ready; Cartographer loaded ở cả hai startup, không Write g-code response/traceback/config-load failure/shutdown transition mới. Không sửa/xóa traceback lịch sử.
- M115 API trả firmware identity; M115 trên klippy.serial thật trả `ok FIRMWARE_NAME:Klipper ...`. Probe serial chỉ thực hiện sau kiểm tra không có client khác quan sát được; không gửi heater/motion command.
- Snapshot sau hai restart: ready, standby, unpaused, targets/power 0, dryer/bench dừng, registry T0–T4. XYZ unhomed, toolchanger uninitialized/T0 detected tại snapshot đó; người vận hành tiếp tục thao tác sau kiểm tra nên không suy diễn snapshot thành trạng thái cuối bất biến.
- Snapshot riêng từ 7 object `canbus_stats ...` có bus active và rx_error/tx_error/tx_retries 0; không lấy số mặc định từ MCU serial stats để khẳng định CAN sạch.
- Assistant không homing, toolchange, gia nhiệt, calibration hoặc test in. Các lệnh T1 heater xuất hiện sau kiểm tra là thao tác ngoài lệnh audit.

### Rủi ro còn mở và tài liệu
- [Báo cáo bổ sung và cách bảo trì/rollback patch](</D:/Desktop/All-Config-Voron-main/Voron 5 Tool/extras/docs/startup-response-and-risk-review-2026-10-09.md>) liệt kê trigger/hậu quả/đề xuất/test cho END max-Z/frame, crash cancel, Axiscope final T0, multi-tool exclusion, KTC damping, diagnostic interruption/timer và prime/mesh clearance.
- Xác minh lại SHA runtime Axiscope và exclude_object khớp source đã đọc trong audit; lỗi vẫn tồn tại. Không chạy calibration/exclusion để kích lỗi trên máy thật.
- Đính chính diễn đạt cũ: early park Mainsail khi CANCEL là có điều kiện park_at_cancel, máy hiện không bật. Nguy cơ hiện hữu vẫn nằm ở _CUSTOM_CANCEL_CLEANUP tự lift/UNSELECT/park khi XYZ homed dù tool có thể lệch/rơi sau crash.
- T1 ban đầu ~56°C so với tool khác ~32–33°C, target/power 0. Người dùng xác nhận lượt in trước chỉ T0/T4 và yêu cầu để kiểm tra sau. Không kết luận sensor hỏng hoặc tự chỉnh PID; cần nguội hoàn toàn/đo độc lập, vì console sau đó có thử T1 target100 rồi off làm history hiện tại không phù hợp làm baseline nguội.
- Cập nhật hai docs index và workspace KNOWN_ISSUES, giữ audit/backup/journal cũ làm lịch sử. Runtime patch phải được kiểm tra lại sau update Klipper; không bắt buộc người nhận CFG dùng nó.
