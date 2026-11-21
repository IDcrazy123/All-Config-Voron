# 2026-11-22 — Quét theo vùng in, chờ xác nhận cảm biến mới

## Bằng chứng

- Moonraker 192.168.1.43:7125 báo `print_stats=standby`, `toolchanger=uninitialized`, XYZ chưa home, QGL chưa áp dụng, bàn không gia nhiệt, Klipper `ready`, không có config warning.
- Live và Git vẫn nạp `[probe_eddy_current ldc1612_eddy_coil]` với `sensor_type: ldc1612`, X0/Y35, I²C3 PA8/PC9 100 kHz, nhiệt cuộn PC5. SAVE_CONFIG đang chứa drive current 17, mô hình Z quét, tap threshold 24888,543 và mesh của đầu dò trước. Các giá trị này chưa được xác nhận cho đầu dò mới.
- `print-macros.cfg` live trùng Git HEAD trước sửa. `printer.cfg` live khác Git duy nhất ở mesh `default`: live đã lưu 55×55, Git còn mesh 15×15. Script triển khai sẽ chặn ghi đè SAVE_CONFIG nếu chưa xử lý chênh lệch này.
- Orca G-code đã kiểm tra có `EXCLUDE_OBJECT_DEFINE` trước `PRINT_START`; `[exclude_object]` đang nạp. Klipper upstream chỉ khai báo `sensor_type: ldc1612`; chưa tìm được hỗ trợ `ldc1618`. Cần xác nhận mã trên IC/bo và dây/offset trước khi sửa khai báo cảm biến hoặc hiệu chuẩn có chuyển động.

## Sửa trong Git

- `config/Printer-Setup/print-macros.cfg`: `PRINT_START` yêu cầu định nghĩa vật thể trước khi khởi động, chuyển mesh từ `ADAPTIVE=0` sang `ADAPTIVE=1`, giữ rapid scan 25×25 tối đa, 180 mm/s và margin 10 mm trong `[bed_mesh]`. Profile mỗi bản in là `print_adaptive`. Mesh tay ở Console giữ thiết lập riêng.
- Backup trước sửa: `extras/backups/pre-adaptive-mesh-20261122/`.

## Xác minh và việc còn chờ

- Đã parse Jinja của `PRINT_START` thành công. Chưa triển khai production, chưa reload, chưa home/QGL/tap/mesh hoặc in bằng đầu dò mới.
- Chờ người vận hành xác nhận mã chip/bo, kết nối I²C và nhiệt, tâm cuộn và khoảng cách cuộn với vòi. Sau đó bỏ hiệu chuẩn cũ, nạp cấu hình đúng phần cứng và làm tuần tự: dòng kích, mô hình Z, offset XY, QGL, tap guess/refine/verify, drift nhiệt, mesh adaptive và first layer có người quan sát.
