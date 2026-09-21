# Nhật ký — 2026-09-21

## 1. Rà soát code, đồng bộ tài liệu và dọn dữ liệu cũ

### Mục tiêu
Đối chiếu code production với README/comment, cập nhật profile OrcaSlicer từ AppData, chặn đường hiệu chuẩn KTC cũ không còn backend, phân loại tài liệu retired và dọn bản sao trùng mà không làm mất bằng chứng độc nhất.

### File đã sửa đổi
- `config/printer.cfg` — thay comment include thử nghiệm cũ bằng mô tả Axiscope Klipper extra.
- `config/Printer-Setup/calibration-probe.cfg` — chuẩn hóa comment tiếng Anh; giữ nguyên toàn bộ giá trị production X80/Y-5/Z8.
- `config/Printer-Setup/fans-leds.cfg` — bỏ tuyên bố sai rằng trạng thái LED calibration được gọi bởi `CALIBRATE_ALL_OFFSETS`.
- `config/toolchanger/toolchanger-config.cfg` — sửa ownership backend và override `CALIBRATE_MOVE_OVER_PROBE`/`CALIBRATE_ALL_OFFSETS` bằng lỗi rõ ràng.
- `config/toolchanger/tools/T0.cfg`, `T2.cfg`, `T3.cfg` — sửa comment offset theo Axiscope + `SAVE_CONFIG`.
- `config/scripts/install.sh` — không còn tuyên bố đã xác thực Axiscope khi script không thực hiện preflight đó.
- `README.md`, `README.vi.md`, `config/README.md`, `config/README.vi.md` — viết lại theo code Axiscope/Cartographer/KTC hiện tại, pinout và offset live.
- `Orca Config/*.json` — đồng bộ 18 profile active; cập nhật machine `z_hop` 0.6 → 0.4 và process PETG 2.4.0.2.
- `Orca Config/Sync-OrcaProfiles.ps1` — đổi alias phân tích từ preset PETG Multimaterial đã cũ sang `0.20mm Multicolor PetG.json` active.
- `Orca Config/README.md`, `README.vi.md` — cập nhật inventory và thay đổi vừa đồng bộ.
- `extras/docs/` — cập nhật index/guide active, chuyển tài liệu kTAMV/TKC sang `history/`, thêm `legacy-calibration-troubleshooting.md`.
- `.agents/PROJECT.md`, `DIRECTORY.md`, `KNOWN_ISSUES.md`, `TODO.md` — cập nhật baseline AI ngoài Git repo theo Axiscope và trạng thái công việc.

### Sao lưu
- `D:/Desktop/All-Config-Voron-main/Voron 5 Tool/extras/backups/pre-code-docs-orca-audit-20260920-160649/`
- `D:/Desktop/All-Config-Voron-main/Voron 5 Tool/extras/backups/pre-orcaslicer-profile-sync-20260920-160720/`
- `D:/Desktop/All-Config-Voron-main/Voron 5 Tool/extras/backups/pre-orcaslicer-profile-sync-20260921-192813/`

### Chi tiết thay đổi
- Xác nhận `readonly-configs/calibrate-offsets.cfg` vẫn chứa macro `tools_calibrate`; comment “disabled” trước đây không chặn code. Override user-owned hiện báo lỗi và hướng người vận hành sang Axiscope cổng 3000.
- Orca đã ghi thêm `prime_tower_brim_width: 10` vào process PETG trong lúc phiên đang chạy; lượt đồng bộ cuối đã lấy đúng byte mới nhất từ AppData.
- Không đổi PID, dòng motor, giới hạn chuyển động, heater, tọa độ dock hoặc offset production.
- Xóa sáu JSON chỉ còn trong repository sau khi xác nhận profile active không kế thừa chúng; bản gốc nằm trong backup và Git history.
- Xóa mười ZIP snapshot, tổng 43.928.538 byte (41,89 MiB), sau khi so sánh SHA-256 từng entry và xác nhận trùng hoàn toàn với thư mục giải nén được giữ lại.
- Giữ `config-20260903-080600.zip` vì có sáu file ShakeTune không có trong thư mục giải nén; giữ các ZIP độc lập và toàn bộ `extras/backups/`.
- Tổng hợp dấu hiệu lỗi cũ từ ToolVision, kTAMV, TKC/KCC, SexBolt, Cartographer và TMC vào một bảng tra cứu ngắn.

### Đối chiếu máy thật
- Trước triển khai, Moonraker xác nhận máy `standby`, idle timeout `Ready`, không có tool được gắn; Klipper, Moonraker và Axiscope đều active.
- Trạng thái dirty cũ của `~/All-Config-Voron` được giữ an toàn trong `stash@{0}: pre-production-sync-20260921-201008`, sau đó checkout được fast-forward tới `f327f4b`.
- Chạy `config/scripts/install.sh`; backup live được tạo tại `/home/voron/printer_data/config_backups/config-install-20260921-201100` trước khi đồng bộ payload.
- Restart Klipper và Moonraker qua Moonraker API. Sau restart, Klipper báo `Printer is ready`, máy vẫn `standby`; Klipper, Moonraker và Axiscope đều active.
- Dry-run `rsync` theo đúng exclude của installer không phát hiện sai khác giữa checkout và payload live. Axiscope được nạp, kTAMV không còn trong object/file active, sáu symlink KTC readonly hợp lệ và offset T1-T4 được giữ nguyên.
- Log từ thời điểm restart không có lỗi parse cấu hình hoặc Klipper shutdown; các lỗi 503/WebSocket chỉ xuất hiện trong cửa sổ dịch vụ đang restart.

### Kiểm tra
- Orca JSON: đạt `ConvertFrom-Json`; byte source AppData được chép nguyên vẹn.
- KTC readonly: không có file nào bị sửa.
- So sánh ZIP/thư mục: 10/10 ZIP đã xóa trùng SHA-256 từng file.
- PowerShell parse: đạt; ba shell script đạt `bash -n` trên host Linux qua stdin, không ghi file lên máy.
- Include Klipper: mọi target tồn tại; guard macro cũ và toàn bộ offset/tọa độ production đạt assertion.
- Link Markdown hiện hành: đạt; không còn đường dẫn kTAMV active hoặc địa chỉ host trong tài liệu mới.
- `git diff --check`: đạt; chỉ có cảnh báo chuyển line ending theo `.gitattributes`, không có whitespace error.

### Kết quả
Code, comment và tài liệu hiện hành thống nhất trên Axiscope + Cartographer + KTC-Easy; profile Orca active đã đồng bộ; dữ liệu trùng giảm 41,89 MiB; kiến thức lỗi lịch sử được giữ trong tài liệu tra cứu và bằng chứng bất biến.

### Vấn đề còn lại
- `toolchanger.status` là `uninitialized` ngay sau service restart, phù hợp trạng thái chưa home/chưa khởi tạo; không chạy macro chuyển động trong phiên triển khai. Xác nhận lại detection/tool state theo quy trình vận hành trước lần in kế tiếp.
- Giữ stash trước triển khai trên máy để có thể đối chiếu hoặc phục hồi thủ công; không tự động apply/drop vì chứa thay đổi live cũ của người vận hành.

## 2. Chuẩn bị thử nghiệm SexBolt tools_calibrate

### Dữ liệu đo và nguyên nhân sửa
- Người vận hành đã lắp SexBolt và đưa nozzle T0 tới tâm quả bóng tại `X80 Y-5.5 Z12`.
- Macro cũ báo lỗi có chủ đích vì Axiscope đang chiếm PF2 và `[tools_calibrate]` bị tắt; hai Klipper extra này không thể được cấu hình đồng thời.
- `spread: 7` không phù hợp giới hạn Y: lượt dò `y+` sẽ bắt đầu tại Y-12.5 trong khi `position_min` là Y-10.

### Thay đổi
- Thay `[axiscope]` bằng `[tools_calibrate]` trên `^PF2`; giữ Cartographer làm probe home Z/mesh.
- Đặt tâm SexBolt `X80 Y-5.5`, Z tiếp cận an toàn 18 và ghi Z12 là chiều cao tiếp xúc quan sát được.
- Dùng `spread: 3.5`; điểm bắt đầu Y thấp nhất là -9.0, còn 1 mm biên so với giới hạn máy.
- Thêm `SEXBOLT_QUERY`, guard home/toolchanger cho các macro di chuyển và giữ `CALIBRATE_NOZZLE_PROBE_OFFSET` bị khóa.
- Cập nhật README và hướng dẫn vận hành để yêu cầu kiểm tra công tắc `open`/`TRIGGERED` trước lần dò đầu tiên.

### Sao lưu và kiểm tra trước triển khai
- Backup: `extras/backups/pre-sexbolt-trial-20260921-203854/`.
- `git diff --check`: đạt; chỉ có cảnh báo line ending theo môi trường Windows.
- Dry parse bằng bản sao config trong `/tmp` trên máy in đã qua bước đọc config/Jinja và chỉ dừng ở giai đoạn debug MCU do không cung cấp dictionary cho mọi MCU; không có lỗi config hoặc template.
- Chưa chạy chuyển động SexBolt hoặc ghi offset trong bước chuẩn bị này.

### Triển khai máy thật
- Commit cấu hình `66928cd` được fast-forward lên checkout máy và cài bằng `config/scripts/install.sh` khi máy `standby/Ready`, T0 được phát hiện đúng.
- Backup live trước cài đặt: `/home/voron/printer_data/config_backups/config-install-20260921-204735`.
- Sau restart, Klipper và Moonraker active; Klipper báo `Printer is ready`, object `tools_calibrate` có mặt và object `axiscope` không còn được nạp.
- `SEXBOLT_QUERY` không chuyển động trả `Calibration Probe: open` khi công tắc đang nhả; `CALIBRATION_STATUS` báo đúng X80/Y-5.5, tiếp xúc gần Z12 và tiếp cận Z18.
- Không chạy `CALIBRATE_MOVE_OVER_PROBE`, `TOOL_LOCATE_SENSOR` hoặc chu trình đo offset. Cần người vận hành nhấn tay SexBolt và xác nhận `SEXBOLT_QUERY` trả `TRIGGERED` trước mọi chuyển động dò.

## 3. Chuyển cảm biến nhựa T2 sang EBB2 PB8

- Đối chiếu toàn bộ namespace `EBB2`: PB8 chưa được dùng; PB8 trong `hardware.cfg` thuộc MCU chính nên không xung đột.
- Đổi `filament_sensor_T2.switch_pin` từ `^EBB2:PB9` sang `^EBB2:PB8`; giữ nguyên pull-up, debounce và runout macro.
- Sửa comment offset T2 đã lỗi thời để không còn ghi Axiscope là backend active.
- Backup: `extras/backups/pre-t2-filament-pb8-20260921-205006/`.
- Deploy commit `33f5557` khi máy `standby/Ready`; backup live: `/home/voron/printer_data/config_backups/config-install-20260921-205053`.
- Sau restart, Klipper/Moonraker active và không có lỗi pin/config; `filament_sensor_T2` được enable trên PB8 và hiện báo `filament_detected: true`.
