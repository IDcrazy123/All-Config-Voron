# Nhật ký — 2026-09-25

## 1. Lưu mức chỉnh Z -0,08 mm từ màn hình BTT cho T1–T4

### Mục tiêu và xác nhận

- Người vận hành báo mức chỉnh trên BTT 5 inch: T3, T2, T1, T4 đều `-0,08 mm`.
- Đã đọc các quy tắc bắt buộc trong `.agents/`, quy tắc repository, README, hướng dẫn cấu hình/vận hành, triển khai và các hướng dẫn Z/Oxplow liên quan. Đối chiếu thêm lịch sử khôi phục ngày 23/09 và trạng thái máy thật.
- Đã đưa bảng giá trị cụ thể để phân biệt delta với số Z tuyệt đối hiển thị. Người vận hành xác nhận đây là mức **hạ thêm -0,08 mm cho từng tool**, chưa lưu vào cấu hình; đồng ý cập nhật và restart khi máy rảnh.

| Tool | Z trước thay đổi (mm) | Delta (mm) | Z mới (mm) |
| --- | ---: | ---: | ---: |
| T0 | 0 | 0 | 0 |
| T1 | +0.2465 | -0.0800 | +0.1665 |
| T2 | -0.2715 | -0.0800 | -0.3515 |
| T3 | -0.2465 | -0.0800 | -0.3265 |
| T4 | +0.1079 | -0.0800 | +0.0279 |

### Bằng chứng trước thay đổi

- Khoảng 19:33:42 +07:00: Klipper `ready`, bản in `First_Layer_Patch-0.25mm_PETG_1m53s.gcode` đã `complete`, idle `Ready`, cả sáu heater target bằng 0, không có SAVE_CONFIG pending.
- Cả saved settings và runtime tool offsets vẫn là bộ khôi phục ngày 23/09. Không có active tool; `gcode_move.homing_origin` là `[0, 0, 0, 0]` sau khi kết thúc in.
- Moonraker G-code store của lần thử T4 gần nhất có bốn lệnh `SET_GCODE_OFFSET Z_ADJUST=... MOVE=1`: `-0.05`, `-0.05`, `+0.01`, `+0.01`, tổng `-0.08 mm`. Đây là dữ liệu lệnh đã chạy bởi người vận hành; assistant không gửi lại các lệnh chuyển động này. Các mức T1–T3 lấy từ báo cáo và xác nhận của người vận hành, không suy ra từ lượt T4.
- Không dùng `SAVE_CONFIG` hoặc macro lưu probe từ màn hình để tránh ghi nhầm sang Cartographer hoặc áp dụng lại chỉnh tạm.

### Đối chiếu mã màn hình và quy ước dấu

- Kiểm tra độc lập mã đang cài: `/home/voron/KlipperScreen/panels/fine_tune.py:112-115,140-156` gửi `SET_GCODE_OFFSET Z_ADJUST=-<step> MOVE=1` khi bấm Z−.
- `/home/voron/klipper/klippy/extras/gcode_move.py:208-226` cộng Z_ADJUST vào homing position; `/home/voron/klipper/klippy/extras/toolchanger.py:738-748` áp tool Z theo `requested Z + tool.gcode_z_offset`. Vì vậy delta `-0.08` phải cộng số học vào giá trị đã lưu, không đảo dấu.
- KlipperScreen `fine_tune.py:124-132` và `job_status.py:621-623` hiển thị `gcode_move.homing_origin[2]`, không phải tool Z. Sau restart hiển thị 0 là bình thường.
- `job_status.py:446-453` dùng `Z_OFFSET_APPLY_PROBE` rồi `SAVE_CONFIG` cho thao tác lưu probe; không dùng nút đó để lưu bốn offset riêng. Usermod `save_babies` không active trên máy.

### Sao lưu

- [Bản sao lưu local và live](<D:/Desktop/All-Config-Voron-main/Voron 5 Tool/extras/backups/pre-btt-z-minus-008-20260925-193458/>), tạo trước khi chỉnh `printer.cfg`.
- SHA256 trước thay đổi của cả hai bản: `8d6b2958bab328e8afeace4b0d6aa11fb2f05854ceef9f738e9f083d978878b9`.
- Sao lưu độc lập trên máy: `/home/voron/printer_data/config_backups/btt-z-minus-008-20260925-193458/original/printer.cfg`, cùng SHA256.

### File đã sửa và kiểm tra

- `config/printer.cfg`: chỉ sửa bốn dòng `gcode_z_offset` T1–T4. Giữ nguyên X/Y, T0, Cartographer, PID, mesh và mọi byte khác.
- `README.md`, `README.vi.md`: cập nhật bảng offset và ghi rõ mức `-0.08 mm` đã được tính đúng một lần, không babystep lặp lại sau khi nạp.
- Kiểm tra bằng Decimal: mỗi delta đúng `-0.0800 mm`. Parser strict đọc được main CFG và SAVE_CONFIG; XYZ khớp bảng mục tiêu; so sánh byte xác nhận chỉ bốn dòng được sửa. `git diff --check` đạt.
- SHA256 candidate: `31e2c0acd4755a30327cb59704f82512764b85b206de86564df2ad0aa5d04bfb`.

### Triển khai và kết quả

- Đã tải candidate vào staging riêng. Kiểm tra lại ngay trước triển khai: máy ready, không in/paused, heater targets bằng 0, không có cấu hình chờ lưu và global Z bằng 0.
- Xác minh hash của live, backup và staging, rồi chỉ sao chép candidate `printer.cfg` vào live. Không chạy installer hoặc thay các file cấu hình khác.
- `FIRMWARE_RESTART` được Moonraker chấp nhận lúc **19:37:55 +07:00 ngày 2026-09-25**.
- Sau restart: Klipper `ready`, print_stats `standby`, SAVE_CONFIG pending `false`; saved settings và runtime T0–T4 đều khớp toàn bộ XYZ đã xác nhận. Global origin vẫn `[0, 0, 0, 0]`; SHA256 live khớp candidate.
- Trục chưa home và toolchanger `uninitialized` sau restart; không gửi home, motion, toolchange hoặc heater G-code. Chỉ gửi lệnh restart đã được chấp thuận.
- README và nhật ký được đưa vào scoped commit cùng cấu hình/backup; đồng bộ GitHub và fast-forward checkout sạch trên máy, không gọi deployment script toàn bộ. Giữ nguyên các thay đổi Printables không liên quan.

### Lưu ý và vấn đề còn lại

- Hai tài liệu trong `extras/docs/` có quy ước dấu trái nhau: quick guide `Oxplow-Z-Offset-Guide.md` ghi trừ delta, comprehensive guide ghi cộng. Không lấy công thức mâu thuẫn này làm nguồn duy nhất để điều khiển máy; lần này dùng delta người vận hành xác nhận và đối chiếu mã đang chạy. Không sửa các file Printables đang có thay đổi không liên quan.
- Cần in lại first layer để kiểm chứng bộ đã lưu. Không áp thêm cùng mức `-0.08 mm` sau restart.
- Nếu đế SexBolt còn trên bàn, tháo ra trước khi home/in. Tác vụ không bao gồm chạy calibration, home, đổi tool hoặc in tự động.
