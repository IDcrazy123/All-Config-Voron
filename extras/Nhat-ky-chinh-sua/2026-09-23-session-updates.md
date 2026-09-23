# Nhật ký — 2026-09-23

## 1. Khôi phục Z về trước thay đổi lúc 20:15 thứ Ba

### Yêu cầu và đối chiếu

- Người vận hành yêu cầu đổi về Z offset trước thay đổi lúc 20:15 thứ Ba. Đã xác định chính xác commit `7763e82`, thời gian `2026-09-22T20:15:07+07:00`, là lần áp dụng riêng Z từ lượt SexBolt 18:37.
- Bản trước thay đổi nằm tại `extras/backups/pre-sexbolt-z-1837-20260922-200957/live/printer.cfg`, trùng bản repository cùng thư mục; giữ nguyên các bản sao lưu lịch sử.
- Snapshot máy ngày 23/09 khoảng 20:55: Klipper ready, print_stats cancelled, idle Ready, mọi heater target 0 và không có SAVE_CONFIG pending. Offset trước hoàn tác vẫn là bộ sau commit `7763e82`.

| Tool | Z trước hoàn tác | Z đã khôi phục |
| --- | ---: | ---: |
| T1 | +0.242 | +0.2465 |
| T2 | -0.284 | -0.2715 |
| T3 | -0.232 | -0.2465 |
| T4 | +0.086 | +0.1079 |

### Sao lưu và xác nhận

- [Sao lưu hiện trạng trước hoàn tác](<D:/Desktop/All-Config-Voron-main/Voron 5 Tool/extras/backups/pre-restore-z-before-20260922-2015-20260923-205455/>): bản repository và live trùng SHA256 `d29aa55da363ae1e09711053b16f2788339a8ab322193b1480526acf84dd247a`.
- Sao lưu độc lập trên máy: `/home/voron/printer_data/config_backups/restore-z-before-20260922-2015-20260923-205455/original/printer.cfg`, cùng SHA256.
- Theo quy trình rollback của dự án, đã gửi bảng thay đổi cụ thể và yêu cầu xác nhận khôi phục/restart. Ở bước chuẩn bị chưa sửa CFG hoặc gửi G-code; bản sao lưu đã được commit/push trong `d061da1`.
- Người vận hành đã trả lời: **"Xác nhận khôi phục và restart"**. Chỉ sửa bốn giá trị Z, giữ nguyên X/Y và mọi cấu hình khác; không triển khai toàn bộ snapshot cấu hình cũ.

### File đã sửa đổi và triển khai

- `config/printer.cfg`: hoàn tác riêng `gcode_z_offset` của T1–T4 theo bảng trên. T0 vẫn là `(0, 0, 0)`.
- `README.md`, `README.vi.md`: cập nhật bảng offset active, nguồn hoàn tác và tình trạng chưa in thử trong lần này.
- Chỉ tải `printer.cfg` đã kiểm tra vào staging trên máy, xác minh hash của candidate, live và backup trước khi sao chép vào `/home/voron/printer_data/config/printer.cfg`. Không chạy installer/update script, không sửa calibration-probe hoặc readonly configs.
- Kiểm tra lại ngay trước triển khai: máy ready, không in/paused, heater targets bằng 0, không có SAVE_CONFIG pending.
- Gửi duy nhất `FIRMWARE_RESTART`, được Moonraker chấp nhận lúc **21:02:07 +07:00 ngày 2026-09-23**. Không gửi lệnh home, đổi tool, gia nhiệt, hiệu chuẩn hoặc chuyển động.

### Kiểm tra và kết quả

- Cú pháp main CFG và SAVE_CONFIG được phân tích thành công; giá trị XYZ của T1–T4 khớp mục tiêu.
- So sánh toàn file với bản trước hoàn tác xác nhận chỉ bốn dòng Z thay đổi, không đổi bất kỳ byte nào khác.
- SHA256 của repository và live sau hoàn tác: `8d6b2958bab328e8afeace4b0d6aa11fb2f05854ceef9f738e9f083d978878b9`, trùng cả hai bản sao lưu trước thay đổi 20:15.
- Kiểm tra độc lập xác nhận diff chỉ có bốn Z, README khớp và `git diff --check` đạt.
- Sau restart: Klipper `ready`, print_stats `standby`, idle `Ready`, SAVE_CONFIG pending `false`. Cả cấu hình đã nạp và runtime tool objects đều xác nhận T1 `0.2465`, T2 `-0.2715`, T3 `-0.2465`, T4 `0.1079`; X/Y giữ nguyên.

### Vấn đề còn lại

- Chưa in thử hoặc kiểm tra first layer trong tác vụ hoàn tác này.
- Sau restart, trục chưa home và toolchanger `uninitialized` là trạng thái khởi động. Cần tháo đế SexBolt khỏi giữa bàn nếu còn lắp trước khi người vận hành home/in lại.
