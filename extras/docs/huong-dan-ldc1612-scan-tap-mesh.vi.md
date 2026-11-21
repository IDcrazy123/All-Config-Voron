# Hiệu chuẩn LDC1612 trong Klipper trên Voron 5 Tool

Dùng Console của Mainsail và chạy từng khối theo thứ tự. Hướng dẫn này dành cho T0, bàn ABS 100°C, vòi đo 150°C và cảm biến LDC1612 trên shuttle. Vị trí giữa bàn là X174 Y168. Lưới đối chiếu trong hướng dẫn là 15×15 ở Z2. Nút Calibrate trong Mainsail chạy quét liên tục 55×55 theo cấu hình máy, và `PRINT_START` chạy 25×25 trên cùng vùng đo.

| Bước | Tác dụng | Kết quả lưu |
| --- | --- | --- |
| Scan | Dùng thử giấy và lấy mẫu tần số theo độ cao | Đường cong `calibrate` |
| Tap | Tìm ngưỡng để Klipper nhận biết lúc vòi chạm bàn | `tap_threshold` |
| Bed mesh | Lấy mốc Z bằng tap rồi đo độ cao tương đối khắp bàn | Mesh đang dùng, hoặc profile nếu chọn lưu |

Trước khi chạy, lau sạch vòi T0 và mặt bàn, lấy mẫu in ra, tháo gá PF2, kiểm tra T0 gắn chắc và quan sát tại máy. Nếu vòi tiếp tục ép xuống bàn, bấm Emergency Stop trong Mainsail hoặc gửi `M112`. Dừng chuỗi nếu bất kỳ lệnh nào báo lỗi.

## 1. Chuẩn bị và cân giàn

Sau mỗi `SAVE_CONFIG`, chờ Klipper trở lại `ready` rồi chạy lại khối này trước bước có chuyển động. Cấu hình hiện tại đã có scan model nên có thể home Z bằng LDC1612. Nếu đã xóa model và `G28` báo cảm biến chưa hiệu chuẩn, dừng và dùng quy trình hiệu chuẩn lần đầu của Klipper. Các tọa độ Z dưới đây chỉ dùng sau khi đã home. [Hiệu chuẩn lần đầu khi home bằng eddy probe](https://www.klipper3d.org/Eddy_Probe.html#performing-initial-calibration-when-homing-with-probe)

```gcode
INITIALIZE_TOOLCHANGER
BED_MESH_CLEAR
SET_GCODE_OFFSET X=0 Y=0 Z=0
G28
G90
G0 Z10 F3000
T0
M140 S100
M104 T0 S150
TEMPERATURE_WAIT SENSOR=heater_bed MINIMUM=99
TEMPERATURE_WAIT SENSOR=extruder MINIMUM=148 MAXIMUM=150
```

Khi bàn và nhiệt cuộn ổn định, chạy khối QGL:

```gcode
QUAD_GANTRY_LEVEL
G90
G0 Z10 F3000
G0 X174 Y168 F6000
```

QGL chạy khi bàn giữ target 100°C. Khi chưa cân giàn, vòng thô dò từng góc từ Z10 để xác lập khoảng hở. Vòng tinh dùng `METHOD=scan` ở Z2 để lấy mẫu tại bốn góc ở độ cao cố định. Lượt tinh phải báo dải bốn góc trong ngưỡng 0,0075 mm. Nếu MCU báo `Missed scheduling of next digital out event`, giữ log và dừng quy trình tại đó.

## 2. Hiệu chuẩn scan bằng giấy

`reg_drive_current=17` đã được đo và lưu trên máy. Nếu thay cuộn hoặc cần đo lại dòng kích, đưa cuộn vào giữa bàn, cách mặt bàn khoảng 20 mm, chạy `LDC_CALIBRATE_DRIVE_CURRENT CHIP=ldc1612_eddy_coil`, rồi `SAVE_CONFIG` và làm lại bước 1. Dùng số do Klipper đo với phần cứng thực tế. [Hiệu chuẩn dòng kích và chiều cao](https://www.klipper3d.org/Eddy_Probe.html#calibrating-drive-current)

Ở giữa bàn sau bước 1, chạy:

```gcode
PROBE_EDDY_CURRENT_CALIBRATE CHIP=ldc1612_eddy_coil
```

Khi Mainsail hiện điều khiển thử giấy, đặt tờ giấy dưới vòi và hạ từng nấc. Gần giấy, dùng `TESTZ Z=-0.1`, rồi `TESTZ Z=-0.025` nếu cần tinh chỉnh. Dùng `TESTZ Z=+0.025` để nhấc nhẹ lên. Khi giấy vừa rà và vẫn kéo qua được, gửi `ACCEPT` rồi rút giấy ra. Nếu cần hủy thử giấy, gửi `ABORT`. [Thử giấy trong Klipper](https://www.klipper3d.org/Bed_Level.html#the-paper-test)

Chờ Klipper tự lấy mẫu xong và console báo dữ liệu hiệu chuẩn, sau đó lưu:

```gcode
SAVE_CONFIG
```

`SAVE_CONFIG` ghi `printer.cfg` và khởi động lại Klipper. Giữ cùng loại tấm in, vị trí gá và điều kiện nhiệt khi dùng kết quả scan. Nếu cần bù trôi nhiệt cho nhiều mức nhiệt, đó là quy trình riêng bắt đầu khi máy nguội với `TEMPERATURE_PROBE_CALIBRATE`. [Hiệu chuẩn trôi nhiệt](https://www.klipper3d.org/Eddy_Probe.html#thermal-drift-calibration)

## 3. Hiệu chuẩn tap

Sau khi chạy lại bước 1, đảm bảo đã rút giấy, vòi và bàn sạch. Ở X174 Y168, chạy `G0 Z7 F1200` và xác minh khoảng hở thật khoảng 3–10 mm. Với máy này, `LIFT_SPEED=10` đã giúp tránh lỗi `insufficient lift` gặp ở tốc độ mặc định. Chạy từng lệnh dưới đây riêng lẻ và xem vòi chạm nhẹ, nhấc lên ngay trước khi gửi lệnh kế tiếp. Đưa vòi về Z7 nếu khoảng hở giữa hai lượt ra ngoài 3–10 mm.

```gcode
M140 S0
G4 P1000
```

Hai lệnh trên tạm ngắt điện bàn đã được làm nóng để đo tap, giống cách chuẩn bị của `PRINT_START`. QGL ở bước 1 dùng PID bàn bình thường.

```gcode
PROBE_EDDY_CURRENT_TAP_CALIBRATE TAP=guess LIFT_SPEED=10
PROBE_EDDY_CURRENT_TAP_CALIBRATE TAP=refine LIFT_SPEED=10
PROBE_EDDY_CURRENT_TAP_CALIBRATE TAP=verify LIFT_SPEED=10
```

`verify` thực hiện 5 lần chạm. So sánh Z cao nhất và thấp nhất, đồng thời quan sát cả 5 lần có chạm nhẹ và nhấc ngay. Dung sai tap của `PRINT_START` trên máy là 0,040 mm cho 5 mẫu. Nếu kết quả vượt mức đó hoặc có lần chạm bất thường, kiểm tra sạch vòi, gá T0 và độ lặp trước khi lưu. Khi `verify` báo giá trị `tap_threshold` và kết quả ổn định, chạy `SAVE_CONFIG`. [Hiệu chuẩn tap native](https://www.klipper3d.org/Eddy_Probe.html#tap-calibration)

## 4. Lấy mốc Z bằng tap và quét mesh

Sau khi Klipper khởi động lại, chạy lại bước 1. Lau vòi lần cuối và đợi bàn trở lại gần 100°C nếu đã nguội. Lấy mốc Z bằng lệnh có sẵn của máy `LDC_TAP_HOME`. Lệnh này chạy `PROBE METHOD=tap` với 5 mẫu, áp dụng kết quả làm mốc Z và nhấc vòi lên. Lệnh `PROBE METHOD=tap` chạy riêng chỉ trả số đo, nên dùng `LDC_TAP_HOME` khi chuẩn bị mesh theo mốc vòi. Nếu tap báo lỗi, dừng trước khi quét. Home Z sau tap sẽ thay mốc vừa lấy.

```gcode
M140 S0
G4 P1000
LDC_TAP_HOME
BED_MESH_CALIBRATE METHOD=scan HORIZONTAL_MOVE_Z=2 PROBE_COUNT=15,15 PROFILE=ldc1612_abs100_t0
M400
BED_MESH_OUTPUT
```

Kiểm tra bản đồ trong mục Heightmap của Mainsail. Nếu muốn giữ mesh vừa đo để so sánh hoặc nạp lại, chạy `SAVE_CONFIG` để ghi profile `ldc1612_abs100_t0` đã đặt trong lệnh quét. Khi hiệu chuẩn xong và chưa in, chạy `TURN_OFF_HEATERS`. [Klipper Bed Mesh và profile](https://www.klipper3d.org/Bed_Mesh.html#bed-mesh-gcodes)

Để dùng đúng kiểu quét của bản in, thay lệnh `BED_MESH_CALIBRATE` trong khối trên bằng lệnh dưới đây. Klipper đo 625 điểm trong lúc đầu in di chuyển trên các đường quét liên tục. `PRINT_START` tự làm bước này, rồi bật và đợi bàn trở lại nhiệt độ yêu cầu trước prime. [Klipper rapid scan](https://www.klipper3d.org/Bed_Mesh.html#rapid-continuous-scanning)

```gcode
BED_MESH_CALIBRATE METHOD=rapid_scan ADAPTIVE=0 HORIZONTAL_MOVE_Z=2 PROBE_COUNT=25,25 SCAN_SPEED=180 PROFILE=ldc1612_rapid
```

Khi bấm Calibrate trong Mainsail hoặc gửi `BED_MESH_CALIBRATE` sau QGL, máy mặc định quét liên tục 55×55 ở Z2, 150 mm/s. Có thể truyền `PROBE_COUNT=25,25` cho lượt kiểm tra ngắn hơn. `METHOD=scan` tường minh vẫn sử dụng được để đo đối chiếu tại chỗ. Hai lượt `rapid_scan` 55×55 trước đây đã gây shutdown MCU, nên quan sát lần chạy đầu với cấu hình hiện tại.
