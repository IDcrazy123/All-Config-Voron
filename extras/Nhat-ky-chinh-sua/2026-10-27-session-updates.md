# Nhật ký — 2026-10-27

## 1. Nới lỏng chốt an toàn và tinh gọn điều kiện di chuyển chuẩn bị (QGL / Motion Preparation Guard)

### Triệu chứng
- Người dùng gặp chuỗi lỗi liên hoàn sau khi gắp tool T0 thất bại lúc bắt đầu in:
  - `Expected tool tool T0 but active is None`
  - `Tool crash detected outside an active print; no shutdown or motion was requested`
  - Sau khi người dùng hủy in (`CANCEL_PRINT`) và thực hiện Home `G28` thành công bằng Cartographer trên shuttle rỗng, người dùng chạy `QUAD_GANTRY_LEVEL` thì bị chặn cứng:
    `Error evaluating 'gcode_macro _REQUIRE_MOTION_PREPARATION:gcode': gcode.CommandError: Preparation motion refused: tool recovery is required. Run CONFIRM_TOOL_RECOVERY CONFIRM=1 or select a tool`
  - Người dùng phải gõ `CONFIRM_TOOL_RECOVERY CONFIRM=1` mới có thể chạy tiếp QGL.

### Phân tích nguyên nhân gốc
1. **Lỗi gắp tool ban đầu:**
   - Trong `_PRINT_START_SELECT_T0`, lệnh `T0` nhặt toolhead 0. Tại tọa độ chốt ngàm dock T0, lệnh `VERIFY_TOOL_DETECTED T=0` đọc chân `detection_pin: ^!EBB0:PB6` nhưng công tắc chưa đóng dứt khoát. KTC kích hoạt `error_gcode: _TOOL_CRASH_SAFE_PAUSE`.
   - `_TOOL_CRASH_SAFE_PAUSE` đặt `_TOOL_RECOVERY.required = 1`.
2. **Khắt khe quá mức trong macro `_REQUIRE_MOTION_PREPARATION`:**
   - Cảm biến Cartographer gắn cố định trên shuttle (carriage), không nằm trên toolhead.
   - Khi shuttle rỗng (`active is None`) và máy đang `idle` (không in), việc cân gantry bằng `QUAD_GANTRY_LEVEL` hay `G32` là hoàn toàn an toàn và lý tưởng.
   - Việc `_REQUIRE_MOTION_PREPARATION` chặn cứng `QUAD_GANTRY_LEVEL` chỉ vì cờ `_TOOL_RECOVERY.required` cũ khiến người vận hành bị deadlock sau sự cố.

### File đã sửa đổi
- `config/Printer-Setup/print-macros.cfg`:
  - Trong `_REQUIRE_MOTION_PREPARATION`: Nới lỏng điều kiện chặn `recovery`. Chỉ chặn khi đang trong `PRINT_START` (`phase == "starting"`) hoặc khi đang gắp một tool chưa được xác minh (`is_active_tool == True`). Khi shuttle rỗng ở trạng thái `idle`, cho phép chạy `QUAD_GANTRY_LEVEL` / `G32` bình thường.
  - Trong `QUAD_GANTRY_LEVEL`: Khi QGL hoàn tất với shuttle rỗng, tự động xóa chốt `_TOOL_RECOVERY.required = 0` và thông báo `"Gantry leveled; recovery latch cleared for empty shuttle"`.
  - Tinh giản thông báo lỗi điều hướng: gợi ý rõ ràng `RECOVER_TOOL` (1-click) hoặc `CONFIRM_TOOL_RECOVERY`.

### Sao lưu
- [print-macros.cfg (Backup)](file:///d:/Desktop/All-Config-Voron-main/Voron%205%20Tool/extras/backups/pre-streamline-recovery-conditions-20261027-192500/print-macros.cfg)
- [tool-crash.cfg (Backup)](file:///d:/Desktop/All-Config-Voron-main/Voron%205%20Tool/extras/backups/pre-streamline-recovery-conditions-20261027-192500/tool-crash.cfg)
- [Thư mục sao lưu](file:///d:/Desktop/All-Config-Voron-main/Voron%205%20Tool/extras/backups/pre-streamline-recovery-conditions-20261027-192500/)

### Kiểm tra & Xác minh
- Bộ kiểm thử tự động `Test-ProductionCfg.ps1`: Đạt 78/78 tests (13 skip POSIX PTY/Bash), toàn bộ test suites đều pass (`OK`).
- Đã triển khai trực tiếp 2 file cấu hình lên máy in thực tế `192.168.1.43` qua Moonraker File Upload API.
- Thực hiện soft reload Klipper (`restart`): Trạng thái `ready` ("Printer is ready").

### Kết quả
- Loại bỏ hoàn toàn điều kiện chặn vô lý đối với `QUAD_GANTRY_LEVEL` khi shuttle rỗng.
- Người vận hành có thể tự do Home và QGL mà không bao giờ bị kẹt lỗi `Preparation motion refused: tool recovery is required`.
- Gantry cân bằng xong tự động giải phóng chốt an toàn cho shuttle rỗng.

### Vấn đề còn lại
- Không có.

---

## 2. Đồng bộ dock live, sửa phục hồi một bước và điều tra lỗi cảm biến bàn

### Triệu chứng và bằng chứng
- Console 19:03–19:06: khi gắp T0, KTC báo No tool detected và Expected tool tool T0 but active is None. Các lỗi recovery/QGL là hệ quả sau khi pickup không xác nhận được.
- Người vận hành xác nhận dock đã xê dịch; chỉnh tọa độ trên máy giúp T0 hoạt động, nhưng Git chưa được cập nhật.
- Đọc toàn bộ CFG/CONF live qua Moonraker 192.168.1.43 và so với repository: T0 dock Y live 1.3 so với Git 1.8; T2 dock Y live 1.6 so với Git 2.1. Chỉ hai file dock và heater_bed khác trước các sửa đổi của phiên này.
- Log Klipper khoảng 19:22: trong một lượt gia nhiệt target 105°C, số đo bàn từ 104,0°C xuống 86,9°C rồi 71,7°C trong khoảng sáu giây, sau đó nhảy lại gần 100°C. PWM lên 1.000 và Klipper shutdown với Heater heater_bed not heating at expected rate. Sự đổi nhiệt này không phù hợp quán tính của bàn 350 mm.
- Máy live dùng sensor_type NTC 100K MGB18-104F39050L32 tại PB0; người bán ghi MBG18-104F39050L32. Klipper có tên MGB18 này với điện trở 100 kΩ tại 25°C, beta 4100. Chưa xác nhận nhãn người bán có cùng đường cong. Tên/đường cong không giải thích được số đo nhảy hàng chục độ trong vài giây.
- Drift khác: Git heater_bed.max_temp 120°C; live 150°C. Chưa có bằng chứng về giới hạn phần cứng 150°C, nên không sao chép giá trị cao hơn vào Git.

### Nguyên nhân
- Pickup T0 thất bại do dock Y trong Git cũ hơn chỉnh sửa đã được người vận hành thử trên máy. KTC đặt chốt recovery theo đúng thiết kế sau khi không xác nhận được tool.
- Macro RECOVER_TOOL cũ chọn tool kỳ vọng trước INITIALIZE_TOOLCHANGER. Nếu lúc đó active=None nhưng cảm biến nhận lại T0 sau khởi tạo, macro kỳ vọng -1 và tự từ chối lần phục hồi hợp lệ.
- QGL cũ tự xóa latch khi shuttle rỗng dù QGL chỉ đo gantry, không xác minh ngàm/tool.
- Bàn nhiệt: đã xác nhận tín hiệu đo NTC không ổn định. Chưa tách được điểm lỗi cụ thể giữa cảm biến, dây/crimp/đầu nối PB0, điểm gắn hoặc nhiễu điện. Không có bằng chứng để tăng check_gain_time, max_error, smooth_time hay đổi PID/SSR.

### Thay đổi trong repository
- config/toolchanger/tools/T0.cfg: params_park_y 1.8 → 1.3 mm, bằng giá trị live đã hoạt động.
- config/toolchanger/tools/T2.cfg: params_park_y 2.1 → 1.6 mm, bằng giá trị live; chưa có coupon riêng xác nhận T2.
- config/Printer-Setup/tool-crash.cfg: RECOVER_TOOL/CONFIRM_TOOL_RECOVERY khởi tạo KTC trước, rồi helper mới đọc active/detected và xác thực; một lệnh attended đủ cho T0 gắn hoặc shuttle rỗng. Không có lệnh XYZ.
- config/Printer-Setup/print-macros.cfg: QGL khởi tạo lại KTC và kiểm tra active/detected trước khi probe; bỏ tự xóa recovery latch qua QGL. PRINT_START chỉ yêu cầu nhiệt purge khi T0 có nhựa; nhánh T0 trống dùng MODE=DEEP PURGE=0 trước QGL (TOUCH trước QGL bị macro vệ sinh từ chối).
- AGENTS.md trong Git và AGENTS.md tại workspace: thay bộ quy tắc cũ bằng trạng thái/nguồn bằng chứng hiện hành; các file .agents cũ là lịch sử.
- README.md/README.vi.md: cập nhật dock, Orca start G-code và ghi rõ chênh lệch giới hạn bàn live/Git.
- KNOWN_ISSUES.md mới trong Git: ghi trạng thái sự cố đang mở, thay cho kết luận quá hạn trong bộ .agents lịch sử.
- extras/tests/Test-ProductionCfg.ps1: cập nhật các hợp đồng đúng với dock đã đo và phục hồi sau khi khởi tạo.

### Sao lưu
- extras/backups/pre-tool-recovery-and-rules-20261027-194340/ giữ nguyên bản trước sửa của các CFG liên quan và bộ quy tắc cũ.
- extras/backups/live-before-recovery-deploy-20261027-1958/ là bản tải trực tiếp từ Moonraker của hai macro và hardware.cfg; hai macro live khớp SHA256 với bản trước sửa trong repository. Bản hardware live được giữ để không làm mất chênh lệch max_temp 150°C.

### Kiểm tra
- Test-ProductionCfg.ps1: 78 bài, đạt; 13 skip gồm kiểm tra lịch sử và các bài phụ thuộc Bash/POSIX PTY. Jinja CFG được compile trong bộ kiểm tra. Không sửa file .py.
- 19:49 máy vẫn đang in ZAssembly_ABS_43m39s.gcode, T0 active/detected, bed target/actual khoảng 100°C. Chưa triển khai CFG hoặc restart vì job còn chạy.
- Chưa có kiểm tra phần cứng sau khi chỉnh repo; pickup T0 live đã hoạt động theo xác nhận người vận hành.
- Commit a85df9f đã push lên origin/main; lúc in khoảng phút 37, chỉ có Git thay đổi, máy chưa reload cấu hình.
- 20:14, job ZAssembly_ABS_43m39s.gcode báo complete; print_stats complete, _PRINT_STATE idle, pause false, idle_timeout Ready, toolchanger ready, dryer/benchmark tắt. Upload chọn lọc print-macros.cfg và tool-crash.cfg qua Moonraker; tải lại so SHA256 khớp Git. hardware.cfg giữ nguyên hash và max_temp live 150°C.
- Restart Klipper khi idle: webhooks ready, hai helper macro mới có trong configfile. Chạy RECOVER_TOOL một lần với shuttle rỗng: toolchanger ready, active/detected đều -1, latch required=0, homed_axes vẫn rỗng; không có chuyển động XYZ. Chưa thử pickup tool hoặc QGL sau triển khai.

### Việc còn lại
- Khi bàn nguội và ngắt nguồn AC: kiểm tra đầu NTC, đường dây tới PB0, crimp/connector, cách ly dây nhiệt/SSR; đo điện trở khoảng 100 kΩ ở 25°C và độ liên tục khi lay nhẹ dây. Thay cảm biến/dây nếu số đo gián đoạn; sau đó mới đánh giá cần đổi sensor_type/PID.
- Các macro đã triển khai riêng; không dùng trình cập nhật toàn bộ cấu hình cho đến khi đối chiếu drift max_temp 120/150°C. Cần xác nhận T0/T2 pickup có giám sát và chu trình QGL, cùng xu hướng nhiệt bàn ổn định. Không đánh dấu lỗi bàn đã khắc phục khi chưa kiểm tra phần cứng.

---

## 3. Rà luồng in và bỏ lệnh phục hồi tool thủ công

### Bằng chứng và quyết định
- Đối chiếu mã nguồn cekim `tool_crash.py` với bản cài trên máy: module phát hiện lỗi qua chân tool và gọi `crash_gcode`, không có giao thức `RECOVER_TOOL`. Bản cài trên máy đã có bản vá `_sync_expected()` trong callback cạnh cảm biến, chỉ xét trạng thái tool đang hoạt động. Không sửa file Python.
- `No tool detected` sau pickup do KTC không xác nhận được T0 ở dock đã xê dịch; người vận hành đã chỉnh dock và T0 hoạt động. Lệnh `RECOVER_TOOL`/`CONFIRM_TOOL_RECOVERY` là lớp riêng trong CFG, tạo thêm bước và có thể từ chối khi tool ban đầu chưa xác định.
- Đọc `PRINT_START`, QGL, CLEAN_NOZZLE, PRIME_LINES, PAUSE/RESUME, CANCEL_PRINT, PRINT_END và G-code Orca của bản in đang chạy. Các lượt kiểm tra của PRIME_LINES và cleaner vẫn cần vì chúng là macro gọi độc lập; vệ sinh sâu trước QGL và lau ngắn trước Touch có mục đích khác nhau; tắt heater lần hai sau dropoff giữ các tool không bị KTC standby làm nóng lại.

### Sửa đổi
- `config/Printer-Setup/tool-crash.cfg`: xóa các lệnh phục hồi/xác nhận thủ công. Chỉ giữ `_TOOL_RECOVERY.required` như chốt crash nội bộ cho pause/hủy không di chuyển; sự kiện lúc idle không giữ chốt.
- `config/Printer-Setup/print-macros.cfg`: `RESUME` khởi tạo KTC, xác thực tool gốc/cảm biến filament/nhiệt trước khi tự xóa chốt; nếu không biết tool gốc thì chỉ cho hủy. `CANCEL_PRINT` và `PRINT_END` không park khi chốt bật rồi tự xóa chốt khi kết thúc. `PRINT_START` dựng một danh sách nhiệt của các tool in để dùng xuyên suốt, gộp nhánh ngâm nhiệt, đợi nhiệt bàn theo số đo hiện tại bằng `TEMPERATURE_WAIT MINIMUM=BED_TEMP-1`, bỏ LED và lệnh xóa mesh/tắt bàn lặp không cần thiết. Dùng một helper kiểm tra trạng thái KTC cho cả trước G28 và QGL.
- `config/toolchanger/toolchanger-config.cfg`: hook đổi tool thành công chỉ xóa chốt nội bộ, không lưu biến tool thừa.
- `config/Printer-Setup/fans-leds.cfg`, `AGENTS.md`, `KNOWN_ISSUES.md`, `extras/tests/Test-ProductionCfg.ps1`: chỉnh comment/quy tắc và hợp đồng kiểm tra theo luồng mới.

### Sao lưu và kiểm tra
- Bản gốc trước khi sửa: [pre-print-flow-simplification-20261027-2023](file:///D:/Desktop/All-Config-Voron-main/Voron%205%20Tool/extras/backups/pre-print-flow-simplification-20261027-2023/).
- `Test-ProductionCfg.ps1`: 80 bài đạt, 13 bài bỏ qua do môi trường Windows hoặc kiểm tra lịch sử; Jinja CFG được biên dịch và phát lại các luồng cancel/end. `git diff --check` đạt. Không sửa file `.py`.
- Khi đang rà máy live tại `192.168.1.43`, `ZAssembly_ABS_48m6s.gcode` vẫn in, T0 active/detected, Klipper ready. Các CFG của mục này chưa triển khai hoặc reload trên máy trong lúc in.
- Commit `722e576` đã push lên `origin/main`. Sau khi job báo `complete` và máy idle `Ready`, upload chọn lọc bốn CFG đã sửa qua Moonraker. Hash SHA256 tải lại của cả bốn file khớp repository trước và sau `restart`; không upload `hardware.cfg`.
- Klipper sau reload báo `ready`; `configfile` không còn `RECOVER_TOOL`/`CONFIRM_TOOL_RECOVERY`, có bed wait và luồng RESUME mới, `tool_crash.crash_gcode` vẫn gọi `_TOOL_CRASH_SAFE_PAUSE`, `heater_bed.max_temp` live vẫn 150°C. `INITIALIZE_TOOLCHANGER` khi standby đọc shuttle rỗng: active = detected = -1, trạng thái ready, tọa độ toolhead giữ nguyên. Đọc lại Python live xác nhận bản vá `_sync_expected()` vẫn có; không ghi Python.
- Chạy hai helper không chuyển động `_REQUIRE_MOTION_PREPARATION` và `_REQUIRE_TOOL_STATE` khi standby/shuttle rỗng: Moonraker trả `ok`, Klipper vẫn ready, tọa độ không đổi. Chưa chạy G28/QGL/pickup vì đó là chuyển động vật lý cần quan sát tại máy.

### Việc còn lại
- Các CFG đã triển khai; vẫn cần thử pickup/QGL và một lượt in dưới giám sát để xác nhận chuyển động thật. Không dùng deploy toàn bộ vì heater_bed.max_temp trong Git 120°C khác live 150°C.
- Lỗi bàn nhiệt gián đoạn vẫn cần kiểm tra dây/cảm biến PB0 và linh kiện thực tế; phần refactor không thay verify_heater, PID hoặc sensor_type.
