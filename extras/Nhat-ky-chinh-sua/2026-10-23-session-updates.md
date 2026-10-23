# Nhật ký — 2026-10-23

## 1. Điều chỉnh vị trí đỗ (park) trục Z sau khi kết thúc in trong PRINT_END

### Mục tiêu
Khắc phục hiện tượng shuttle/gantry sau khi hoàn tất lệnh in (`PRINT_END`) bị giữ nguyên ở cao độ đỉnh máy ($Z \approx 331\text{ mm}$ do dock StealthChanger ở $Z=343$), khiến đầu in kết thúc ở vị trí quá cao ngay cả khi in các bản in có chiều cao thấp.

### File đã sửa đổi
- `config/Printer-Setup/print-macros.cfg` — Sửa macro `_PRINT_FINISH_PARK`: di chuyển shuttle rỗng về vị trí đỗ phía sau bàn in ($X = 174, Y = 316$) trước ở độ cao an toàn, sau đó hạ trục $Z$ xuống `target_z = max(Z_bản_in + 10, 50 mm)`.

### Sao lưu
- [print-macros.cfg (Backup)](file:///d:/Desktop/All-Config-Voron-main/Voron%205%20Tool/extras/backups/pre-park-z-lower-on-print-end-20261023-200502/print-macros.cfg)

### Chi tiết thay đổi
- Trong macro `_PRINT_FINISH_PARK`:
  - Trước:
    ```jinja2
    {% set target_z = [[params.MIN_Z|float, th.position.z|float]|max, th.axis_maximum.z|float]|min %}
    # No tool transform, mesh or live offset is active here. Never descend
    # from the dock just to reach the requested minimum clearance.
    SET_GCODE_OFFSET X=0 Y=0 Z=0
    G90
    G0 Z{target_z} F3000
    G0 X{th.axis_maximum.x // 2} Y{th.axis_maximum.y - 20} F9000
    ```
    (Do `th.position.z` sau khi drop tool tại dock $Z=343$ là khoảng $331\text{ mm}$, phép toán `max(MIN_Z, th.position.z)` luôn giữ gantry ở $331\text{ mm}$, không bao giờ hạ xuống `MIN_Z`).
  - Sau:
    ```jinja2
    {% set target_z = [[params.MIN_Z|default(50.0)|float, 0.0]|max, th.axis_maximum.z|float]|min %}
    # No tool transform, mesh or live offset is active here.
    # Move empty shuttle to rear park position at clearance height first, then lower Z to target_z (z_safe).
    SET_GCODE_OFFSET X=0 Y=0 Z=0
    G90
    G0 X{th.axis_maximum.x // 2} Y{th.axis_maximum.y - 20} F9000
    G0 Z{target_z} F3000
    ```

### Lý do
- Đảm bảo tính an toàn cơ học tuyệt đối: Khi vừa cất tool xong ở dock phía trước ($Y \approx 20, Z \approx 331$), shuttle di chuyển $XY$ về mép sau bàn in ($X = 174, Y = 316$) ở cao độ đỉnh máy $Z \approx 331\text{ mm}$ nên hoàn toàn không có nguy cơ va chạm vào bất kỳ vật in nào trên bàn.
- Sau khi đã ở tọa độ đỗ phía sau, việc hạ trục $Z$ xuống `target_z` (tương ứng với `z_safe = max(Z_bản_in + 10, 50 mm)`) giúp gantry hạ xuống tầm quan sát hợp lý, gần bản in hơn, không bị treo lơ lửng trên đỉnh máy, đồng thời vẫn bảo đảm khoảng hở an toàn cách bề mặt bản in tối thiểu $10\text{ mm}$ (hoặc sàn $50\text{ mm}$ với bản in mỏng).

### Kiểm tra
- Chạy bộ kiểm thử tự động `Test-ProductionCfg.ps1`: đạt 78/78 tests (13 skip môi trường POSIX PTY/Bash), toàn bộ replay logic boundary và macro compiling đều hoàn hảo.
- Khởi động lại Klipper: (Người dùng thực hiện trên máy in thực tế)
- Thử in: (Người dùng thực hiện trên máy in thực tế)

### Kết quả
Macro `PRINT_END` và `_PRINT_FINISH_PARK` đã được cập nhật chính xác theo đúng lựa chọn đã thống nhất với người vận hành.

### Vấn đề còn lại
Không có.
