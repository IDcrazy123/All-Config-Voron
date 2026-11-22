# Hiệu chuẩn LDC1612 trong Klipper trên Voron 5 Tool

Dùng Console của Mainsail và chạy từng khối theo thứ tự. Hướng dẫn này dành cho T0, bàn ABS 100°C, vòi đo 150°C và cảm biến LDC1612 trên shuttle. Vị trí giữa bàn là X174 Y168. Lưới đối chiếu trong hướng dẫn là 15×15 ở Z2. Nút Calibrate trong Mainsail chạy quét liên tục 55×55 theo cấu hình máy; `PRINT_START` dùng adaptive mesh, quét vùng vật thể cộng lề 10 mm và tự thu nhỏ số điểm từ mật độ lưới 55×55 của cấu hình máy. Nếu vùng in không chứa điểm X174 Y168, Klipper có thể đo thêm một điểm mốc Z ở giữa bàn.

**Sau khi thay bo/cuộn LDC1612:** drive current, mô hình chiều cao, ngưỡng tap và mesh của đầu dò cũ không phải kết quả hiệu chuẩn của đầu dò mới. Không chạy `G28 Z`, QGL, tap, mesh hoặc `PRINT_START` dựa trên các giá trị cũ. Xác nhận dây, offset và khoảng hở thật trước; dùng [quy trình hiệu chuẩn lần đầu của Klipper](https://www.klipper3d.org/Eddy_Probe.html#performing-initial-calibration-when-homing-with-probe) nếu đã xóa mô hình cũ. Các khối có `G28` bên dưới chỉ áp dụng sau khi mô hình Z của cảm biến mới đã được lưu và xác minh.

| Bước | Tác dụng | Kết quả lưu |
| --- | --- | --- |
| Scan | Dùng thử giấy và lấy mẫu tần số theo độ cao | Đường cong `calibrate` |
| Tap | Tìm ngưỡng để Klipper nhận biết lúc vòi chạm bàn | `tap_threshold` |
| Bed mesh | Lấy mốc Z bằng tap rồi đo độ cao tương đối khắp bàn | Mesh đang dùng, hoặc profile nếu chọn lưu |

Trước khi chạy, lau sạch vòi T0 và mặt bàn, lấy mẫu in ra, tháo gá PF2, kiểm tra T0 gắn chắc và quan sát tại máy. Nếu vòi tiếp tục ép xuống bàn, bấm Emergency Stop trong Mainsail hoặc gửi `M112`. Dừng chuỗi nếu bất kỳ lệnh nào báo lỗi.

## 1. Chuẩn bị và cân giàn

Sau mỗi `SAVE_CONFIG`, chờ Klipper trở lại `ready` rồi chạy lại khối này trước bước có chuyển động. Chỉ home Z bằng LDC1612 sau khi đã có mô hình Z của cảm biến **đang gắn trên máy**. Nếu chưa có mô hình đó, dùng quy trình hiệu chuẩn lần đầu của Klipper. Các tọa độ Z dưới đây chỉ dùng sau khi đã home. [Hiệu chuẩn lần đầu khi home bằng eddy probe](https://www.klipper3d.org/Eddy_Probe.html#performing-initial-calibration-when-homing-with-probe)

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

`reg_drive_current=17` của đầu dò cũ đã được lưu trên máy. Với đầu dò mới, đưa cuộn vào giữa bàn, cách mặt bàn khoảng 20 mm, chạy `LDC_CALIBRATE_DRIVE_CURRENT CHIP=ldc1612_eddy_coil`, rồi `SAVE_CONFIG`. Dùng số do Klipper đo ở đúng khoảng hở thực tế. [Hiệu chuẩn dòng kích và chiều cao](https://www.klipper3d.org/Eddy_Probe.html#calibrating-drive-current)

Ở giữa bàn sau bước 1, chạy:

```gcode
PROBE_EDDY_CURRENT_CALIBRATE CHIP=ldc1612_eddy_coil
```

Khi Mainsail hiện điều khiển thử giấy, đặt tờ giấy dưới vòi và hạ từng nấc. Gần giấy, dùng `TESTZ Z=-0.1`, rồi `TESTZ Z=-0.025` nếu cần tinh chỉnh. Dùng `TESTZ Z=+0.025` để nhấc nhẹ lên. Khi giấy vừa rà và vẫn kéo qua được, gửi `ACCEPT` rồi rút giấy ra. Nếu cần hủy thử giấy, gửi `ABORT`. [Thử giấy trong Klipper](https://www.klipper3d.org/Bed_Level.html#the-paper-test)

Chờ Klipper tự lấy mẫu xong và console báo dữ liệu hiệu chuẩn, sau đó lưu:

```gcode
SAVE_CONFIG
```

`SAVE_CONFIG` ghi `printer.cfg` và khởi động lại Klipper. Giữ cùng loại tấm in và vị trí gá khi dùng kết quả scan. Với cảm biến mới, tiếp tục bước bù nhiệt bên dưới trước khi đánh giá mesh nóng. [Hiệu chuẩn trôi nhiệt](https://www.klipper3d.org/Eddy_Probe.html#thermal-drift-calibration)

## 3. Bù trôi nhiệt từ nguội đến bàn 100°C / vòi T0 150°C

Cấu hình `[temperature_probe ldc1612_eddy_coil]` có `calibration_position: 174,168,1`, `extruder_heating_z: 50`, `calibration_extruder_temp: 150`, `calibration_bed_temp: 100` và `max_validation_temp: 100`. Lệnh dưới đây tự đưa vòi T0 lên Z50 để gia nhiệt 150°C, tới giữa bàn ở Z1 để thử giấy lần đầu, rồi bắt đầu gia nhiệt bàn 100°C sau mẫu đầu tiên. Bắt đầu khi bàn/cuộn/vòi nguội, T0 đã gắn và được phát hiện, XYZ đã home, vòi và bàn sạch. Mô hình Z của cảm biến mới phải được `SAVE_CONFIG` trước. Không chạy `PRINT_START` trong lúc hiệu chuẩn.

```gcode
TEMPERATURE_PROBE_CALIBRATE PROBE=ldc1612_eddy_coil TARGET=58 STEP=2
```

Ở mỗi lần Klipper yêu cầu manual probe, dùng giấy và `TESTZ` từng nấc nhỏ rồi `ACCEPT` khi vừa rà. Klipper tự lấy mẫu tần số, đợi cuộn tăng thêm khoảng 2°C và mở lượt thử giấy kế tiếp. TARGET=58°C là mốc khởi đầu dựa trên nhiệt cuộn cũ khoảng 58,51°C khi bàn 100°C/vòi 150°C; kiểm tra nhiệt cuộn thực của cảm biến mới. Nếu nhiệt ổn định thấp hơn 58°C nhưng đã có ít nhất ba mẫu, dùng `TEMPERATURE_PROBE_COMPLETE` để kết thúc với dải thực tế; nếu thao tác sai dùng `ABORT` và đo lại từ nguội. Khi hoàn tất, `SAVE_CONFIG`, rồi kiểm tra `drift_calibration` xuất hiện và `temperature_probe ... compensation_enabled=true`. [Quy trình Klipper](https://www.klipper3d.org/Eddy_Probe.html#thermal-drift-calibration)

## 4. Hiệu chuẩn tap

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

## 5. Lấy mốc Z bằng tap và quét mesh

Sau khi Klipper khởi động lại, chạy lại bước 1. Lau vòi lần cuối và đợi bàn trở lại gần 100°C nếu đã nguội. Lấy mốc Z bằng lệnh có sẵn của máy `LDC_TAP_HOME`. Lệnh này chạy `PROBE METHOD=tap` với 5 mẫu, áp dụng kết quả làm mốc Z và nhấc vòi lên. Lệnh `PROBE METHOD=tap` chạy riêng chỉ trả số đo, nên dùng `LDC_TAP_HOME` khi chuẩn bị mesh theo mốc vòi. Nếu tap báo lỗi, dừng trước khi quét. Home Z sau tap sẽ thay mốc vừa lấy.

Klipper native trên máy dùng `tap_z_offset` trong `[probe_eddy_current ldc1612_eddy_coil]`. Tên `tap_adjust_z` thuộc plugin `eddy-ng` lưu trong `extras/LDC1612/` và không được Klipper native nạp. Khi nâng Z lúc in bằng babystep dương, offset native giảm cùng độ lớn; lệnh chính thức để lưu kết quả là `Z_OFFSET_APPLY_PROBE METHOD=tap` rồi `SAVE_CONFIG`. `tap_z_offset` thay đổi số Z mà lần tap sau trả về. Macro `LDC_TAP_HOME` vẫn cần áp dụng số đo đó vào mốc tọa độ Z; nếu chỉ bỏ bước áp dụng, offset sẽ không ảnh hưởng vị trí in. [Tham chiếu cấu hình Klipper](https://www.klipper3d.org/Config_Reference.html#probe_eddy_current), [lệnh lưu offset tap](https://www.klipper3d.org/G-Codes.html#probe_eddy_current).

```gcode
M140 S0
G4 P1000
LDC_TAP_HOME
BED_MESH_CALIBRATE METHOD=scan HORIZONTAL_MOVE_Z=2 PROBE_COUNT=15,15 PROFILE=ldc1612_abs100_t0
M400
BED_MESH_OUTPUT
```

Kiểm tra bản đồ trong mục Heightmap của Mainsail. Nếu muốn giữ mesh vừa đo để so sánh hoặc nạp lại, chạy `SAVE_CONFIG` để ghi profile `ldc1612_abs100_t0` đã đặt trong lệnh quét. Khi hiệu chuẩn xong và chưa in, chạy `TURN_OFF_HEATERS`. [Klipper Bed Mesh và profile](https://www.klipper3d.org/Bed_Mesh.html#bed-mesh-gcodes)

Để dùng đúng kiểu quét của bản in, G-code phải khai báo vật thể bằng `EXCLUDE_OBJECT_DEFINE` **trước** `PRINT_START`. Bốn preset process Orca trong repository đã bật `exclude_object` và `gcode_label_objects`; file G-code cũ phải được slice lại nếu chưa có khai báo này. Khi in, Klipper tự thu nhỏ vùng quét và số điểm theo vùng vật thể cộng lề 10 mm, lấy lưới 55×55 trong `[bed_mesh]` làm mật độ tham chiếu. Một lệnh gửi riêng từ Console không có khai báo vật thể sẽ không có vùng adaptive. `PRINT_START` bật và đợi bàn trở lại nhiệt độ yêu cầu trước prime. [Klipper adaptive mesh](https://www.klipper3d.org/Bed_Mesh.html#adaptive-meshes)

```gcode
BED_MESH_CALIBRATE ADAPTIVE=1
```

Macro `BED_MESH_CALIBRATE` tự thêm `METHOD=rapid_scan`; các giá trị Z2, 150 mm/s và lưới tham chiếu 55×55 lấy từ `[bed_mesh]`. Khi bấm Calibrate trong Mainsail hoặc gửi `BED_MESH_CALIBRATE` sau QGL mà không có khai báo vật thể, máy dùng toàn vùng 55×55. Có thể truyền `PROBE_COUNT=25,25` cho lượt kiểm tra ngắn hơn. `METHOD=scan` tường minh vẫn sử dụng được để đo đối chiếu tại chỗ. Hai lượt `rapid_scan` 55×55 trước đây đã gây shutdown MCU, nên chỉ chạy bản in đầu có người quan sát sau khi xử lý lỗi lịch digital output.
