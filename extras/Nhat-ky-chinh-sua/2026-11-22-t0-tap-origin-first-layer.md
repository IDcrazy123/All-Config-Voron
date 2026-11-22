# 2026-11-22 — T0 lớp đầu và hiệu chỉnh gốc Z sau tap

## Bằng chứng từ bản in live

- Người vận hành báo bản in lớp đầu đẹp khi nâng T0 thêm 0,10 mm. File `Khoi lap phuong_ABS_3m31s.gcode` hoàn tất; sau in Klipper `ready`, T0 ở dock, heater target 0. Console ghi các lệnh `SET_GCODE_OFFSET Z_ADJUST` trong bản in với tổng đại số +0,10 mm; offset tạm được `PRINT_END` xóa, không tự lưu cho bản tiếp theo.
- `PRINT_START` làm sạch T0, giữ bàn 105°C, QGL hội tụ dải 0,005320 mm; lau T0 rồi thực hiện 5 lần native tap tại T0 150°C. Kết quả tap tại X174/Y168 ước tính tiếp xúc Z=+0,059759 mm. Ngay sau đó console báo `Unknown command:"_LDC1612"`. Tên `_LDC1612_APPLY_TAP_Z` bị bộ tách lệnh Klipper cắt ở nhóm chữ/số; phần `_APPLY_TAP_Z` không thuộc tên lệnh đã phân tích. Vì vậy `SET_KINEMATIC_POSITION` trong helper chưa chạy.
- Sau tap, máy quét adaptive 17×18 trong vùng X130..218/Y124..212 ở Z2, hoàn tất mesh; sau đó bật lại bàn 105°C, gia nhiệt T0 từ 150°C đến 260°C, prime rồi in. Trong lúc mesh, bàn hạ tới khoảng 98,5°C. `PRINT_START` không bù Z bổ sung sau khi tăng nhiệt vòi. Việc thiếu hiệu chỉnh tap là nguyên nhân chắc chắn của sai khác gốc Z; phần ảnh hưởng do giãn nở khi tăng 150→260°C chưa được đo tách riêng.
- Live `printer.cfg` có mô hình Z của đầu mới đã lưu lại ở `calibration_temp=46,683760°C` và `tap_threshold=25318,090`, khác Git trước lượt sửa. Đã sao lưu cả live/Git trước khi đồng bộ; không ghi đè dữ liệu hiệu chuẩn live bằng đường cong nguội cũ.

## Sửa đổi

- Đổi helper và nơi gọi sang `_LDC_APPLY_TAP_Z`, tên toàn chữ/underscore nên bộ phân tích Klipper nhận đủ lệnh. Giữ phép tính `SET_KINEMATIC_POSITION Z=current_z-contact_z`, cần thực hiện sau khi `PROBE METHOD=tap` hoàn tất để đọc kết quả mới.
- Đồng bộ `config/printer.cfg` với mô hình Z và threshold đã được người vận hành lưu trên máy. Không cộng cố định +0,10 mm vào T0 hoặc `PRINT_START`: lượt thử 0,10 mm diễn ra khi helper hiệu chỉnh tap chưa hoạt động. Sau khi sửa, mức cần bù còn lại phải đo lại bằng first layer có người quan sát tại nhiệt in thực tế.
- Backup: `extras/backups/pre-tap-origin-fix-20261122/`.
- Khi dry-run triển khai, installer phát hiện live `printer.cfg` đã thay đổi tiếp: người vận hành lưu T2 `gcode_z_offset` từ -0,4203 thành -0,6203 mm. Đã lấy lại bản live, sao lưu `printer.live-after-commit.cfg` và đồng bộ giá trị mới vào Git trước khi triển khai; không dùng cờ thay thế hiệu chuẩn để ghi đè.

## Triển khai và xác minh

- Sau khi đồng bộ T2, installer dry-run chỉ thấy thay đổi dự kiến ở `calibration-probe.cfg` và timestamp của `printer.cfg`. Đã deploy lúc máy idle; backup production tại `/home/voron/printer_data/config_backups/config-install-20261122-112835-pYlfNN`. `RESTART` hoàn tất, Klipper `ready`, không warning; registry G-code có `_LDC_APPLY_TAP_Z` và không có helper tên cũ. T2 vẫn là -0,6203 mm, threshold LDC vẫn 25318,090.
- G28 có người vận hành quan sát đã thành công sau restart để đo QGL/LDC; chưa chạy hot tap hoặc bản in đầu mới sau bản sửa. Lượt tap tiếp theo phải hiện `LDC1612 tap corrected Z by ... mm` và không còn `Unknown command`. Sau đó thử lớp đầu để xác định có cần bù Z do chênh nhiệt vòi hay không.
- Rà soát QGL và phép đo LDC khi máy đứng yên: xem `extras/diagnostics/2026-11-22-qgl/REPORT.vi.md`. Không chỉnh tolerance QGL hoặc offset T0 dựa trên dữ liệu chưa tách được ảnh hưởng nhiệt.
