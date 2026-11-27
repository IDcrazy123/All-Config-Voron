# Nạp Z offset PF2 sơ bộ, T3 tạm — 2026-11-27

## Yêu cầu và nguồn số liệu

Người vận hành yêu cầu cập nhật Z offset mọi tool và dùng giá trị trung bình tạm cho T3, thay cho quyết định trước đó chưa lưu số PF2. Đã đọc lại `AGENTS.md`, nhật ký đo `2026-11-27-all-tool-pf2-z-after-dock-alignment.md`, `configfile` và trạng thái live trước khi sửa. Máy `ready`, `standby`, T0 active/detected, XYZ homed, heater target 0, không có `SAVE_CONFIG` chờ.

Tính đến 0,0001 mm:

| Tool | Cách chọn từ phép đo PF2 | Z mới |
| --- | --- | ---: |
| T0 | Tool tham chiếu, giữ nguyên | 0 |
| T1 | Trung bình ba giá trị giữa A/B/C; loại hai đầu D/E | -0,3913 |
| T2 | Trung bình A/B/C/E; loại D=-0,325336 vì bốn lượt còn lại tụ gần -0,29 | -0,2902 |
| T3 | **Tạm**: trung bình ba chu kỳ gắp T3 mới nhất -0,3428/-0,3516/-0,3088 | -0,3344 |
| T4 | Trung bình ba giá trị giữa B/C/E; loại hai đầu A/D | -0,1943 |

T1/T4 vẫn có độ trải lớn, nên đây là offset PF2 sơ bộ theo yêu cầu, không phải kết quả lớp đầu. T3 có dải 0,0428 mm ngay trong ba chu kỳ gắp mới nhất, từng lệch 0,0772 mm sau tái gắp, và người vận hành xác nhận rít khi lắp tay. Giá trị T3 **chỉ là số tạm trong cấu hình; chưa xác minh cơ khí để in**.

## File và giá trị cũ/mới

| Tool | Live cũ | Git cũ | Live/Git mới |
| --- | ---: | ---: | ---: |
| T1 | -0,3861 | -0,3861 | -0,3913 |
| T2 | -0,2703 | -0,6203 | -0,2902 |
| T3 | -0,3884 | -0,3884 | -0,3344 |
| T4 | -0,1970 | -0,1970 | -0,1943 |

Chỉ sửa bốn dòng `gcode_z_offset` trong khối `SAVE_CONFIG` của `config/printer.cfg` ở Git và file `printer.cfg` live. Bản live có nhiều giá trị/model khác Git, nên đã tạo ứng viên từ **file live** và đối chiếu diff chỉ bốn dòng, không triển khai nguyên file Git lên máy. Backup Git và live ở `extras/backups/pre-pf2-z-offsets-20261127/`; trên máy có `/home/voron/printer_data/config/printer-20261127-pre-pf2-z-offsets.cfg`.

Ứng viên live được xác minh SHA-256, áp dụng nguyên tử khi máy idle, rồi gọi `RESTART`. Sau restart Klipper `ready`, `configfile.warnings=[]`, `save_config_pending=false`, bốn giá trị trong config và runtime cùng khớp bảng trên. Đã `INITIALIZE_TOOLCHANGER`: T0 active/detected, máy `standby`, heater target 0. XYZ chưa home và QGL chưa applied sau restart; chưa chạy G28, QGL, gắp/thả hay in thử với offset mới.

## Việc cần xác minh

- Xử lý hiện tượng T3 rít khi gắn vào shuttle, rồi đo lại qua nhiều chu kỳ gắp trước khi dùng T3 để in.
- Kiểm tra lớp đầu từng tool để tinh chỉnh offset cuối; PF2 chỉ cung cấp Z tương đối sơ bộ. T1/T4 đặc biệt cần đối chứng vì các lượt PF2 dao động.
- Trước triển khai Git lần sau, tiếp tục so live `printer.cfg`/QGL/model LDC với Git; các khác biệt ngoài bốn Z offset không được ghi đè theo lượt này.
