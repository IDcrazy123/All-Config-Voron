# Nhật ký — 2026-09-08

## 1. Tích hợp TKC f68dc99, đo Cartographer T0–T4 và điều tra riêng T3

### Mục tiêu

Đọc dự án/quy tắc, dọn TKC cũ trên 192.168.1.43, cài mới, thử T0 trước rồi
T0–T4, so sánh offset và đối chiếu logic/tài liệu. Người vận hành bổ sung yêu cầu
thử riêng T3, phản ánh nâng Z35 và xác nhận bộ offset lưu đo ở hotend 150 °C / bed 70 °C.

### File đã sửa đổi

- `config/printer.cfg` — bật một include TKC, cập nhật tình trạng commissioning.
- `config/moonraker.conf` — thêm update_manager user service TKC.
- `config/tool_calibrator/tool_calibrator.cfg` — master upstream với điểm Touch 174/168,
  home random radius 0, mode nozzle, macro tiện ích mặc định SAVE_CONFIG=0.
- `config/tool_calibrator/tool_offsets.cfg` — seed XY production, không thêm Z đo mới.
- `config/Printer-Setup/calibration-probe.cfg` — status hiển thị backend TKC đúng thực tế.
- `config/scripts/install.sh` — preflight TKC, bảo vệ offsets/backups/manifest qua rsync.
- README, config README, hướng dẫn TKC và báo cáo cùng bằng chứng ở
  `extras/experiments/tkc-f68dc99-20260908/`.
- `.agents/KNOWN_ISSUES.md` tại workspace được đính chính nhận định Touch/Scan cũ;
  nội dung đính chính cũng có trong báo cáo được Git quản lý.

### Sao lưu

- [Backup](<D:/Desktop/All-Config-Voron-main/Voron 5 Tool/extras/backups/pre-tkc-install-20260908-200037/README.md>)
- Remote: `/home/voron/printer_data/config_backups/pre-tkc-install-20260908-200037/`.
- Có bản PC/live, Git bundle source cũ, archive config TKC cũ và các default mới trước sửa.
  Source/config cũ chuyển khỏi vị trí hoạt động, không xóa mất backup lịch sử.

### Chi tiết thực hiện

- Kiểm kê thấy service/extras cũ đã gỡ, nhưng source 5e55137 và config còn sót.
- Dọn vị trí hoạt động, clone main f68dc99, chạy upstream installer --user-service.
- Nạp thật bằng Klipper; service active/enabled, Update Manager pristine, health OK.
- Đo T0 ba lượt lạnh trước khi mở rộng; mọi phép thử không lưu offset mới.
- Lượt T0–T4 dừng tại T3; xác nhận detected T3 nhưng logical uninitialized, G28 phục hồi,
  sau đó đo riêng T0→T4 và trả T0.
- T3 native lạnh riêng có hai lượt cùng median -0.165414 mm, vẫn có outlier.
- Thử riêng native T3 nóng sau khi người dùng nêu điều kiện 150/70; telemetry được lưu.
  Ba median -0.206/-0.210/-0.222 mm, mean -0.212667, range giữa lượt 0.016 mm.
  Cả ba đạt bộ chọn mẫu; không lưu Z. So với T3 lưu -0.1896, mean chênh -0.023067 mm.
  Cửa sổ ổn nhiệt 5 phút liên tục không đạt; bed target70 đọc tới75.41 rồi giảm.
  Không quy chênh cho riêng giãn nở nhiệt; không đổi PID/tolerance hoặc mở rộng
  thêm chuỗi nóng toàn bộ khi còn dao động. Trả T0, tắt heater, restart và G28 cuối.

### Kết quả lạnh và phân tích

T1 +0.266; T2 -0.326; T3 không đạt; T4 +0.196 mm. Bộ đang dùng tương ứng
+0.236, -0.316, -0.1896, +0.120 mm. **Không cùng nhiệt độ: không dùng chênh lạnh/nóng
để kết luận bộ lưu sai.** T2 raw spread 0.166 mm dù nhóm chọn đạt 0.002 mm;
T3 raw spread 0.682 mm, không đạt 3 mẫu/0.010 mm trong cửa sổ 5 sau 10 chạm.

Cartographer Touch thật đo tiếp xúc nozzle, khác Scan không tiếp xúc; vị trí gắn
shuttle không tự loại khả năng đo nozzle tương đối. TKC còn cache Z-only làm mất XY
lần kế tiếp (đã tái hiện offline) và recovery báo sai thành công (đã thấy trên máy).
Nâng Z35 nằm ở ranh giới đổi tool/thoát lỗi, không xuất hiện giữa các native probe
liên tiếp cùng T3. Không thay clearance toàn cục hoặc nới tolerance để ép pass.

### Kiểm tra

- Upstream unittest: 140/140 đạt trên host env TKC; source không patch.
- Cấu hình được Klipper nạp; các macro status thực thi thành công.
- Bash syntax đạt; test rsync trong thư mục tạm xác nhận giữ dữ liệu TKC.
- Sau thử lạnh, toàn bộ XYZ runtime và SAVE_CONFIG giữ nguyên; ready/homed/T0/heaters off.
- Sau thử nóng, kiểm tra lại toàn bộ XYZ/SAVE_CONFIG, ready/homed/T0/heaters off;
  bằng chứng cuối `evidence/verification-after-hot.json`.
- Báo cáo chi tiết và trạng thái sau thử nóng được cập nhật ở
  [REPORT.vi.md](../experiments/tkc-f68dc99-20260908/REPORT.vi.md).

### Vấn đề còn lại

Chưa đủ bằng chứng chấp nhận Z production. Cần xử lý cache/recovery, theo dõi outlier
T2/T3 và dao động nhiệt bed khi giữ 70 °C. Không thay PID hoặc phần cứng từ suy đoán.
