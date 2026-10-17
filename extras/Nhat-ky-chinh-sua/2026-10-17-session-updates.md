# Nhật ký — 2026-10-17

## 1. Triển khai bộ CFG hardening lên máy in

### Mục tiêu

Triển khai bộ sửa đổi đã kiểm tra theo yêu cầu trực tiếp của người dùng; ưu tiên
cấu hình, giữ nguyên các file Python và thông số hiệu chuẩn đang chạy.

### File đã sửa đổi

- `config/scripts/install.sh` — chặn triển khai khi macro phase khác `idle`.
- `extras/tests/Test-ProductionCfg.ps1` — thêm kiểm tra chặn phase `calibrating`
  và phase không biết trước khi tạo backup hoặc gọi rsync.
- `extras/docs/cfg-hardening-2026-10-16.md` — bổ sung trạng thái đã triển khai.
- Thêm báo cáo `extras/docs/cfg-deployment-2026-10-17.md` và bằng chứng kiểm tra
  trong `extras/audits/2026-10-17-deployment/`.
- Trên máy in: chép bảy CFG trong `Printer-Setup/` và `toolchanger/`, cùng
  `scripts/install.sh`; danh sách chính xác có trong báo cáo và manifest.

### Sao lưu

- [Bản sao lưu local và manifest](</D:/Desktop/All-Config-Voron-main/Voron 5 Tool/extras/backups/pre-printer-deploy-hardening-20261017-160508/README.md>).
- Backup riêng trên máy in:
  `/home/voron/printer_data/config_backups/pre-cfg-hardening-deploy-20261017-160614-7hw1x39d/`.
- Chín bản gốc live được xác minh SHA-256 trước khi ghi file; backup trên máy in
  được kiểm tra lại sau restart. Không ghi đè backup cũ.

### Chi tiết thay đổi

- Điều kiện installer: danh sách `starting/printing/paused/drying` → mọi phase
  khác `idle`; trường hợp macro tùy chọn không tồn tại vẫn mặc định `idle`.
- Bộ CFG từ commit `4e55588` được triển khai cùng bản vá guard trên. Chức năng
  chi tiết được ghi trong báo cáo hardening ngày 16/10.
- Máy được xác nhận không có job/pause, phase idle, dryer/bench tắt và sáu heater
  target bằng 0 trước khi ghi. So sánh hash lại ngay trước triển khai.
- Chép tám file nguyên tử từng file, giữ quyền, kiểm tra hash cả bộ rồi gọi đúng
  một lần `RESTART`; không cần rollback.

### Lý do

Đưa các sửa đổi CFG đã rà soát vào máy thực tế, đồng thời khép lỗ hổng kiểm tra
phase hiệu chuẩn trong installer để tránh cập nhật giữa một thao tác đang chạy.

### Kiểm tra

- Native Jinja2 2.11.3: biên dịch 139 template; kiểm tra năm cặp rename bằng
  implementation đang cài, các interface KTC/Axiscope và crash patch hiện có.
- Production runner: 69 bài, 63 đạt, 6 bỏ qua có lý do, không failure/error.
  Hai invariant cũ đã thay thế và bốn Linux PTY không chạy trên Windows.
- Cú pháp Bash đạt. Không sửa file `.py` hiện có.
- Klipper restart thành công, trạng thái `ready`; warning Klipper/Moonraker rỗng.
- Sau restart: tám hash triển khai đúng, 26 file khác và chín module Python
  giữ nguyên, sáu symlink giữ nguyên; 103 section phần cứng/hiệu chuẩn bảo toàn.
- Đủ 14 helper/base command; standby, không pause, phase idle, recovery clear,
  sáu heater target bằng 0. Không chạy chuyển động, gia nhiệt, hiệu chuẩn hoặc in.

### Kết quả

Triển khai thành công và xác minh cấu hình đã được Klipper nạp. Toàn bộ bằng chứng
công khai, backup và nhật ký được đưa vào cùng commit; capture tạm `.local.json`
được gitignore và không đưa lên Git.

### Vấn đề còn lại

Sau restart trục chưa homing và toolchanger chưa khởi tạo, cảm biến nhận T0;
đây là trạng thái bình thường. Cần homing và thử in ngắn có người giám sát,
kiểm tra end/cancel/pause/load/resume, vị trí đỗ shuttle cao và shaping thực tế.
Chưa xác nhận độ hở đường chạy bằng phần cứng. Hiệu chuẩn PF2 và vấn đề cảm biến
T1 vẫn là việc riêng chưa xử lý trong lần triển khai này.

## 2. Rà soát bổ sung, sửa các lỗ hổng CFG và triển khai khi máy rảnh

### Mục tiêu

Theo yêu cầu người dùng, kiểm tra lỗi còn sót và hoàn thiện các phần có thể sửa
chắc chắn qua CFG, ưu tiên không can thiệp Python hay thông số phần cứng.

### File đã sửa đổi

- Chín CFG trong `config/Printer-Setup/`: `print-macros`, `fans-leds`,
  `filament-dryer`, `nozzle-clean`, `prime-lines`, `tool-temp-bench`,
  `test-speed`, `calibration-probe`, `tool-crash`.
- `extras/tests/Test-ProductionCfg.ps1`: thêm kiểm tra hồi quy và cập nhật mô
  phỏng comment có dấu chấm phẩy nằm trong chuỗi.
- Bốn README cấu hình/chỉ mục: cập nhật trạng thái đã triển khai.
- Báo cáo mới `extras/docs/cfg-followup-2026-10-17.md` và bằng chứng audit.
- `.agents/KNOWN_ISSUES.md` của workspace: bổ sung trạng thái hiện tại, giữ các
  mục lịch sử. File ngoài Git repo; patch thay đổi được lưu trong audit.

### Sao lưu

- [Backup repository trước sửa](</D:/Desktop/All-Config-Voron-main/Voron 5 Tool/extras/backups/pre-cfg-followup-20261017-161410/README.md>).
- [Backup bản live trước triển khai](</D:/Desktop/All-Config-Voron-main/Voron 5 Tool/extras/backups/pre-printer-cfg-followup-20261017-162039/README.md>).
- [Backup sổ lỗi workspace](</D:/Desktop/All-Config-Voron-main/Voron 5 Tool/extras/backups/pre-workspace-issue-register-20261017-162614/README.md>).
- Backup riêng trên máy in:
  `/home/voron/printer_data/config_backups/pre-cfg-followup-20261017-162128-66m1xrah/`.
  Mười bản gốc (chín CFG và printer.cfg tham chiếu) được kiểm tra hash trước ghi
  và sau restart. Không ghi đè backup đã tồn tại.

### Chi tiết thay đổi

- EXCLUDE_OBJECT: `RESET is defined` → điều kiện chuỗi RESET thực sự không rỗng,
  khớp native; không cho `RESET= NAME=...` vượt chốt multi-tool.
- CANCEL_PRINT/PRINT_END: thêm `_STOP_AUXILIARY_HEAT_TASKS` ngay sau tắt heater;
  hủy callback dryer/benchmark để không bật nhiệt lại sau shutdown.
- Dryer: `UNSELECT_TOOL` → `UNSELECT_TOOL RESTORE_AXIS=`; nâng tương đối có chặn
  trần Z và helper park đọc trạng thái mới sau dock. Giữ X175/Y310, tối thiểu
  Z200, không hạ shuttle từ độ cao dock chỉ để về Z200.
- Thêm kiểm tra cờ recovery vào các macro thủ công và helper cleaner gọi sau
  chờ nhiệt. Prime từ chối nhiệt dưới min_extrude_temp và thao tác cạnh tranh.
- PAUSE tự quản lý: lần đầu giữ hành vi Mainsail; gọi lặp không sửa nhiệt/tool
  lưu và không park lại; recovery/error dùng handler không di chuyển XYZ.
- Tách thay đổi trạng thái vận hành khỏi năm wrapper LED; `_PRINT_PAUSED` và
  luồng start/resume/dryer sở hữu các chuyển trạng thái.
- G32/QGL và di chuyển tới công tắc kiểm tra thêm trạng thái in/thao tác khác.

### Lý do

Các lỗi đã được tái hiện bằng template/replay. Đặc biệt, bản CANCEL_PRINT cũ
không xóa is_drying, nên callback sau cancel có thể phát lại `M140 S70`. Thao tác
đổi LED hoàn tất cũng có thể làm phase đang in thành idle. Chi tiết nằm trong
báo cáo và `reproduced-before.json`.

### Kiểm tra

- Đọc log live Klipper/Moonraker; scan ban đầu không thấy dòng traceback,
  shutdown hoặc error khớp mẫu. Không coi đây là chứng nhận phần cứng.
- Toàn bộ runner: 78 bài, 72 đạt, 6 bỏ qua có lý do, không failure/error.
- Native Jinja2 2.11.3: 142 template compile, 10 cặp rename và 12 tình huống
  render giả lập đạt; không phát G-code trong kiểm tra native này.
- Kiểm tra Bash/whitespace đạt. Cả 33 Python trong repo giữ nguyên hash.
- Chín file đã triển khai đúng hash; 25 file khác, sáu symlink và 10 runtime
  Python giữ nguyên. 104 section không phải G-code macro giữ nguyên toàn bộ.
- Một lần RESTART thành công, Klipper ready, cảnh báo Klipper/Moonraker rỗng.
  Standby, phase idle, không pause/job, dryer/benchmark dừng, sáu heater target 0.
- Không chạy chuyển động, gia nhiệt, homing, hiệu chuẩn hoặc in thử.

### Kết quả

Các lỗi CFG xác định được đã sửa và nạp thành công lên máy. Không sửa PID,
offset, wiring, giới hạn chuyển động, tọa độ dock, readonly KTC/Mainsail hoặc
profile JSON Orca. Báo cáo phân biệt rõ giới hạn kiểm thử và việc còn mở.

### Vấn đề còn lại

Cảm biến T1 vẫn chờ xác minh sau thay; native exclusion multi-extruder chưa vá
Python; timer vẫn đếm callback; prime area/đường chạy chi tiết cao, PF2 và nhiệt
cần kiểm tra có giám sát/dữ liệu đo. Sau restart cần homing trước khi in. Cần
thử mẫu ngắn để xác nhận end/cancel/pause/load/resume và vị trí đỗ thực tế.
