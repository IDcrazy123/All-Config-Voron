# Nhật ký — 2026-09-07

## 1. Gỡ sạch, cài lại TKC a6bb715 và thử Z bằng Cartographer

### Triệu chứng

- Bản TKC trước đó làm Klippy shutdown khi Moonraker đọc status trong lúc calibration do `NameError: time is not defined`.
- Người vận hành yêu cầu gỡ hoàn toàn, cài bản mới nhất đã sửa, đo thử Z bằng Cartographer và xác định lỗi còn lại.
- Camera đã được dời khỏi vị trí đo; toàn bộ đầu phun được người vận hành xác nhận sạch.

### Phân tích nhật ký

- Bằng chứng chính: `extras/experiments/tkc-a6bb715-reinstall-cartographer-z-20260907/`
- Báo cáo tổng hợp: `extras/experiments/tkc-a6bb715-reinstall-cartographer-z-20260907/REPORT.md`
- T2 không đạt ba mẫu trong cửa sổ 0,010 mm sau mười lần chạm; biên độ mẫu 1,054 mm.
- T3 lỗi tương tự; biên độ mẫu 0,710 mm.
- T0 chạm khoảng X174/Y168; T1-T4 chạm khoảng X174/Y163, không cùng một điểm.
- Status polling không còn làm Klippy crash, nhưng `elapsed_sec` âm rất lớn do trộn Unix wall clock với Klipper monotonic clock.
- Sau lỗi probe và cả lỗi chặn `ERR_Z_003`, tool thật vẫn được cảm biến nhận đúng nhưng trạng thái logic toolchanger thành `uninitialized`.
- Sau checkpoint đầu tiên, G-code store ghi nhận thêm lệnh rời `T2` rồi `cartographer_touch_probe`; probe T2 tiếp tục lỗi repeatability trong khi TKC ở `IDLE` và các hook TKC đã tắt. Nguồn phát hai lệnh này không được xác định.

### Nguyên nhân gốc

- Lỗi chênh điểm 5 mm là lỗi lookup của TKC: code tìm `bed_mesh.zero_ref_pos` và `bed_mesh.bmc.zero_ref_pos`, trong khi Klipper máy này lưu giá trị tại `bed_mesh.bmc.probe_mgr.zero_ref_pos`. TKC rơi xuống tâm hành trình X174/Y163; Cartographer touch-home tự dùng cấu hình X174/Y168.
- Lỗi T2/T3 phát sinh trong bộ kiểm tra độ lặp của Cartographer trước khi TKC tính offset. Đầu phun bẩn đã được loại trừ theo xác nhận của người vận hành; nguyên nhân cơ khí/cảm biến cụ thể chưa được xác định.
- Cartographer gắn cố định trên shuttle không trực tiếp đo chiều dài từng nozzle. Bản mới đã chặn đúng trường hợp này theo mặc định; phép thử chỉ chạy được nhờ override thí nghiệm.
- Lỗi trạng thái toolchanger thuộc đường cleanup của TKC: lỗi được ghi nhận và station được rời, nhưng tool logic không được đồng bộ lại với tool vật lý được phát hiện.

### Hướng khắc phục đã thực hiện

- Sao lưu cấu hình, service, manifest, hash và source Git bundle trước thao tác.
- Chạy uninstaller mới với `--config-subdir Printer-Setup --purge-repo`; kiểm tra và di chuyển phần config/archive còn giữ lại vào backup để tạo checkpoint sạch.
- Clone đúng upstream `main` tại `a6bb71564a982b867fb7c1a310a6b4eef764cfd6` và chạy đúng hướng dẫn `./scripts/install.sh --user-service --config-subdir Printer-Setup`.
- Khôi phục các file riêng của máy trong `Printer-Setup` từ backup.
- Tạm bật hai hook Cartographer để đo có giám sát; mọi lệnh dùng `SAVE_CONFIG=0`, `CLEAN_NOZZLE=0`.
- Chạy riêng T0→T3 và T0→T4 sau khi lượt T0-T4 bị dừng tại T2.
- Khôi phục `touch_home_gcode` và `touch_probe_gcode` về `_TKC_Z_DISABLED`, firmware restart và `G28` bình thường.
- Sau chuỗi lệnh rời phát sinh cuối phiên, chạy `G28` để khởi tạo T2 rồi `T0` để trả máy về tool tham chiếu.
- Không sửa code TKC và không ghi bất kỳ offset thử nghiệm nào.

### Sao lưu

- [Local backup](file:///D:/Desktop/All-Config-Voron-main/Voron%205%20Tool/extras/backups/pre-tkc-a6bb715-z-20260907-160309/)
- Remote backup: `/home/voron/printer_data/config_backups/tkc-a6bb715-z-20260907-160309/`

### Kết quả

- Uninstall đạt checkpoint sạch trước khi cài lại; script vẫn giữ lại một số dữ liệu người dùng và cần bước dọn thủ công nếu yêu cầu là gỡ tuyệt đối.
- Install theo hướng dẫn thành công. Service active/enabled, port 8090 hoạt động, update manager sạch và không chậm commit; kTAMV port 8086 không xung đột.
- Upstream tests: 112/112 đạt.
- T1 cho kết quả thí nghiệm `+0,140 mm`; T4 `+0,097 mm`; T2 và T3 không đạt repeatability. Không kết quả nào được áp dụng.
- Cuối phiên: Klipper ready, XYZ homed, toolchanger ready, active/detected T0, vị trí khoảng X30,2/Y120/Z10, toàn bộ heater target 0.
- Hash cuối của `printer.cfg`, `tool-calibrator.cfg`, `tool_offsets.cfg` lần lượt là `959dfa72...ede4`, `158d91d7...073`, `99527383...9a49`; khớp cấu hình trước thử nghiệm.

### Phòng ngừa

- Không dùng Cartographer gắn shuttle để lưu Z offset từng nozzle.
- TKC phải bảo đảm reference và secondary đo cùng tọa độ, log requested/actual XY và dừng khi lệch điểm.
- Thêm cleanup đồng bộ tool logic với tool vật lý, sửa clock status và thêm chế độ tiếp tục đo tool kế tiếp sau lỗi.
- Không tăng tolerance để ép qua các mẫu có biên độ 0,7-1,05 mm.

### Vấn đề còn lại

- Điều tra repeatability riêng của T2/T3 tại cùng một điểm đo bằng quy trình phù hợp.
- Chờ upstream sửa lookup zero-reference, recovery toolchanger và elapsed clock trước khi thử lại TKC Z.

---

## 2. Gỡ bỏ hoàn toàn Tool-Klipper-Calibration (TKC) và đồng bộ trạng thái thực tế về PC & GitHub

### Mục tiêu
Đồng bộ trạng thái thực tế từ máy in Voron 2.4 (sau khi người vận hành đã gỡ bỏ hoàn toàn bộ công cụ Tool-Klipper-Calibration bằng lệnh `./scripts/uninstall.sh --purge-all`) về kho cấu hình PC và cập nhật lên GitHub.

### Triệu chứng & Bối cảnh
- Sau các thử nghiệm đo Z bằng Cartographer, Tool-Klipper-Calibration (TKC) vẫn chưa đáp ứng yêu cầu độ lặp và kiến trúc shuttle probe không đo trực tiếp nozzle offset.
- Người vận hành đã thực hiện gỡ bỏ triệt để TKC trên máy in qua terminal:
  - Chạy `./scripts/uninstall.sh --purge-all`
  - Gỡ bỏ hoàn toàn dịch vụ người dùng `tool_calibrator.service`
  - Xóa mã nguồn `~/Tool-Klipper-Calibration` và môi trường ảo `~/tkc-env`
  - Dọn dẹp các file cấu hình và bản backup liên quan trong `printer_data/config`
- Cần đồng bộ cấu hình sạch này về máy tính cá nhân để tránh lệch pha (configuration drift) và đẩy lên kho lưu trữ GitHub theo đúng quy chuẩn dự án.

### File đã sửa đổi
- `config/printer.cfg` — Loại bỏ các dòng include module TKC (`tool_calibrator_macros.cfg`, `safe_staging_macros.cfg`, `tool-calibrator.cfg`, `tool_offsets.cfg`), giữ lại dòng chú thích `# [include tool_calibrator/tool_calibrator.cfg]`.
- `config/moonraker.conf` — Loại bỏ block `[update_manager tool_calibrator]`.
- `config/Printer-Setup/tool-calibrator.cfg` — Xóa khỏi cấu hình vận hành (đã lưu trữ an toàn trong backup).
- `config/Printer-Setup/tool_offsets.cfg` — Xóa khỏi cấu hình vận hành (các offset thực tế T1–T4 vẫn được quản lý đầy đủ trong block `#*# <SAVE_CONFIG>` của `printer.cfg`).

### Sao lưu
- [pre-sync-purge-tkc-20260907-211000](file:///d:/Desktop/All-Config-Voron-main/Voron%205%20Tool/extras/backups/pre-sync-purge-tkc-20260907-211000/)
- [pre-tkc-30abb5-z-20260907-174008](file:///d:/Desktop/All-Config-Voron-main/Voron%205%20Tool/extras/backups/pre-tkc-30abb5-z-20260907-174008/)

### Chi tiết thay đổi
- Gỡ bỏ 4 dòng include TKC trong `printer.cfg`:
  ```ini
  -[include Printer-Setup/tool_calibrator/tool_calibrator_macros.cfg]
  -[include Printer-Setup/tool_calibrator/safe_staging_macros.cfg]
  -[include Printer-Setup/tool-calibrator.cfg]
  -[include Printer-Setup/tool_offsets.cfg]
  +# [include tool_calibrator/tool_calibrator.cfg]
  ```
- Gỡ bỏ section Moonraker update manager trong `moonraker.conf`:
  ```ini
  -[update_manager tool_calibrator]
  -type: git_repo
  -path: ~/Tool-Klipper-Calibration
  -...
  ```
- Xóa 2 file cấu hình dư thừa của TKC trong `Printer-Setup/`.
- Xác nhận block `#*# <SAVE_CONFIG>` trong `printer.cfg` khớp 100% với dữ liệu vận hành trên máy in thực tế.

### Kiểm tra
- Trạng thái máy in thực tế: Klipper `ready`, Moonraker `ready`.
- Kiểm tra dịch vụ: `systemctl --user is-active tool_calibrator.service` trả về `inactive` (unit file không tồn tại).
- Kiểm tra toàn vẹn (Verification): So sánh MD5/hash tất cả file trong `config/` (gồm `crowsnest.conf`, `KlipperScreen.conf`, `mainsail.cfg`, `moonraker.conf`, `printer.cfg`, toàn bộ `Printer-Setup/`, `toolchanger/`, `scripts/`) giữa PC và máy in thật: Đạt 100% (ALL MATCHED: True).
- Kiểm tra Git: Cấu hình sạch sẽ, không còn file rác.

### Kết quả
- Toàn bộ hệ thống cấu hình trên PC đã đồng bộ tuyệt đối với máy in thực tế.
- Trạng thái máy in hoạt động ổn định ở chế độ sản xuất chuẩn, không còn bất kỳ thành phần nào của TKC.
- Git repository đã được cập nhật và push thành công lên GitHub `origin/main`.

### Vấn đề còn lại
- Hiệu chuẩn Z offset giữa các tool tiếp tục sử dụng phương pháp đo tiếp xúc qua công tắc vi mô Z-offset trên chân `PF2` (tại tọa độ X:68, Y:-10, Z:7) hoặc Axiscope, không dùng probe Cartographer gắn cố định trên shuttle.

