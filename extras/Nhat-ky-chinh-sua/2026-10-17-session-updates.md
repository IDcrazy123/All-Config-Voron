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
