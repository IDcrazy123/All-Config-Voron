# Nhật ký — 2026-09-23

## 1. Chuẩn bị khôi phục Z về trước thay đổi lúc 20:15 thứ Ba

### Yêu cầu và đối chiếu

- Người vận hành yêu cầu đổi về Z offset trước thay đổi lúc20:15 thứBa. Đã xác định chính xác commit `7763e82`, thời gian `2026-09-22T20:15:07+07:00`, là lần áp dụng riêng Z từ lượt SexBolt18:37.
- Bản trước thay đổi nằm tại `extras/backups/pre-sexbolt-z-1837-20260922-200957/live/printer.cfg`, trùng bản repository cùng thư mục; giữ nguyên các bản sao lưu lịch sử.
- Snapshot máy ngày23/09 khoảng20:55: Klipper ready, print_stats cancelled, idle Ready, mọi heater target0 và không có SAVE_CONFIG pending. Offset đã lưu hiện tại vẫn là bộ sau commit7763e82.

| Tool | Z hiện tại | Z cần khôi phục |
| --- | ---: | ---: |
| T1 | +0.242 | +0.2465 |
| T2 | -0.284 | -0.2715 |
| T3 | -0.232 | -0.2465 |
| T4 | +0.086 | +0.1079 |

### Sao lưu và trạng thái chờ xác nhận

- [Sao lưu hiện trạng trước hoàn tác](<D:/Desktop/All-Config-Voron-main/Voron 5 Tool/extras/backups/pre-restore-z-before-20260922-2015-20260923-205455/>): bản repository và live trùng SHA256 `d29aa55da363ae1e09711053b16f2788339a8ab322193b1480526acf84dd247a`.
- Sao lưu độc lập trên máy: `/home/voron/printer_data/config_backups/restore-z-before-20260922-2015-20260923-205455/original/printer.cfg`, cùng SHA256.
- Theo quy trình rollback của dự án, đã gửi bảng thay đổi cụ thể và yêu cầu xác nhận khôi phục/restart. Dự kiến chỉ sửa bốn giá trị Z, giữ nguyên X/Y và mọi cấu hình khác; không khôi phục toàn bộ cấu hình bằng snapshot cũ.
- Chưa sửa CFG, chưa gửi G-code, restart hoặc di chuyển. Chờ câu trả lời xác nhận trước khi áp dụng.
