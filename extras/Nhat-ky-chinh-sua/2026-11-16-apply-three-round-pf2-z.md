# Áp dụng trung bình ba lượt PF2 làm Z offset tạm — 2026-11-16

## Yêu cầu và bằng chứng

- Sau ba lượt đo PF2 T0–T4 ở 150 °C với QGL xen giữa, người vận hành yêu cầu cập nhật các giá trị mới đo. Nguồn số liệu: `extras/Nhat-ky-chinh-sua/2026-11-16-pf2-three-round-repeat-qgl.md` và `extras/diagnostics/2026-11-16-pf2-three-rounds/measurements.csv`.
- Trước sửa, production và repository `config/printer.cfg` trùng nội dung. Klipper/KTC `ready`, print `standby`, T0 active/detected, XYZ đã home, mọi heater target 0, không pause/dryer, `configfile.warnings=[]`.
- PF2 chỉ đo Z tương đối sơ bộ. Theo yêu cầu mới, trung bình ba lượt được nạp làm **offset production tạm**; chưa có xác nhận first-layer. T1 và T4 dao động giữa lượt khoảng 0,05 mm, nên cần đặc biệt kiểm tra trước khi dùng cho bản in thực tế.

## Thay đổi

| Tool | Z cũ (mm) | Z mới từ trung bình 3 lượt (mm) |
| --- | ---: | ---: |
| T0 | 0 | 0 (giữ mốc) |
| T1 | +0,1665 | -0,3861 |
| T2 | -0,3515 | -0,4203 |
| T3 | -0,4865 | -0,3884 |
| T4 | +0,0279 | -0,1970 |

- Chỉ sửa bốn dòng `gcode_z_offset` trong khối `SAVE_CONFIG` của `config/printer.cfg`; giữ nguyên XY, dock, PID, Cartographer và mọi section khác.
- Sao lưu `printer.cfg` của repository và production trước sửa tại `extras/backups/pre-three-round-pf2-z-offsets-20261116-165316/`.
- Tải file lên Moonraker, đọc lại thấy khớp repository, rồi chạy `RESTART` khi máy idle. Klipper `ready`, không config warning, offset live T0–T4 đúng 0 / -0,3861 / -0,4203 / -0,3884 / -0,1970. `INITIALIZE_TOOLCHANGER` không di chuyển, đưa KTC về `ready`, active/detected T0. Mọi heater target vẫn 0.

## Giới hạn và bước tiếp theo

- `RESTART` xóa trạng thái home; hiện XYZ **chưa home**. Vị trí số Klipper sau restart không phải tọa độ cơ khí đã xác minh. Không chạy G28 khi giá PF2 còn gắn.
- Offset mới là điểm bắt đầu cho first-layer từng tool, chưa được xác nhận là Z cuối. Phải tháo giá PF2, home/QGL theo điều kiện in, rồi quan sát first-layer và hiệu chỉnh từng tool trước khi in bình thường.
