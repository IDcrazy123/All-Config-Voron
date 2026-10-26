# Backup: pre-park-z-floor-streamline-20261026-152700

## Mục đích
Sao lưu trước khi cập nhật sàn độ cao Z sau khi kết thúc in từ 50mm xuống 20mm (`Z = max(print_z + 10, 20.0)`), giúp gantry đỗ ở vị trí cách đỉnh bản in 10mm (tối thiểu 20mm để an toàn nếu chi tiết quá mỏng), tránh treo quá cao gây lâu khi G28 lần sau và tránh sát giới hạn trần Z.

## File sao lưu
- `print-macros.cfg`
