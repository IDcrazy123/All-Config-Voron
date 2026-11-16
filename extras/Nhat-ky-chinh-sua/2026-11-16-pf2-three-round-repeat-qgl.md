# Ba lượt đo Z tương đối PF2 và QGL xen giữa — 2026-11-16

## Điều kiện và cách đo

- Người vận hành yêu cầu đo lại T0–T4 ba lượt, lấy trung bình, và chạy QGL sau mỗi lượt T0–T4 để kiểm tra độ hội tụ. Người vận hành trực tiếp quan sát, xác nhận dock và giá PF2 tại X81 Y-7, đầu phun sạch. Bàn không gia nhiệt theo yêu cầu.
- Production trước đo: Klipper/KTC `ready`, print `standby`, XYZ homed, T0 active/detected, `[axiscope]` X81/Y-7, `zswitch_z_pos=3`, `lift_z=1`, năm tool đăng ký. Không sửa cấu hình production hoặc offset.
- Mỗi tool được đo một lần trong mỗi lượt, mỗi phép đo gồm năm mẫu PF2 ở đầu phun khoảng 150 °C. Sau chọn tool, kiểm tra active/detected, đưa về X81 Y-7 với G-code Z8 để giữ khoảng hở, xác nhận PF2 `open` rồi mới gọi `PROBE_ZSWITCH SAMPLES=5`. Mỗi độ lệch Z tính so với T0 **cùng lượt**, vì QGL và home Z làm thay đổi mốc tọa độ tuyệt đối.
- Trước lượt chính, ba lần T0 3,1903/3,1944/3,1952 mm được đo khi đầu phun chưa vệ sinh lại. Người vận hành yêu cầu tạm dừng và gia nhiệt cả năm tool lên 150 °C để vệ sinh; các số này không đưa vào trung bình. Sau khi xác nhận vệ sinh xong mới bắt đầu bảng dưới.
- Lượt 3, phép đo T1 đầu tiên bị loại: năm mẫu 2,958–3,022 mm, trải 0,064 mm, mẫu đầu cao nhất rồi giảm. T1 được đưa ra giữa bàn ở Z15; người vận hành vệ sinh và xác nhận ngàm chắc. Đo lại T1 có năm mẫu 2,8345–2,8425 mm, trải 0,008 mm. Dữ liệu bị loại lưu riêng.

## Z tương đối so với T0 (mm)

| Tool | Lượt 1 | Lượt 2 | Lượt 3 | Trung bình 3 lượt | Biên độ giữa lượt |
| --- | ---: | ---: | ---: | ---: | ---: |
| T0 | 0 | 0 | 0 | 0 | 0 |
| T1 | -0,3648 | -0,3753 | -0,4182 | **-0,3861** | 0,0534 |
| T2 | -0,4347 | -0,4100 | -0,4162 | **-0,4203** | 0,0247 |
| T3 | -0,4015 | -0,3840 | -0,3798 | **-0,3884** | 0,0217 |
| T4 | -0,2261 | -0,1898 | -0,1752 | **-0,1970** | 0,0509 |

T0 kích hoạt tuyệt đối lần lượt ở Z3,2024 / 3,2697 / 3,2571 mm. Dữ liệu gốc gồm 15 hàng tại `extras/diagnostics/2026-11-16-pf2-three-rounds/measurements.csv`; phép T1 bị loại ở `rejected-measurements.csv`.

## QGL sau từng lượt

- Theo yêu cầu mới, người vận hành xác nhận giá PF2 không chạm đường QGL. Đã đối chiếu: bốn điểm nozzle QGL là X20/330, Y10/280; home Z giữa bàn; giá PF2 tại X81 Y-7. Cả ba QGL chạy với XYZ đã home, T0 active/detected, người vận hành quan sát, giá PF2 vẫn gắn, bàn target 0. Điều này chỉ xác minh đường đi cụ thể trong ba lượt này; quy tắc mặc định vẫn là tháo giá trước G28/QGL/Touch/mesh/in.
- Macro production chạy lượt thô nếu QGL chưa `applied`, sau đó lượt tinh với tolerance 0,0075 mm và tối đa 10 retry; cuối macro G28 Z.

| QGL sau lượt | Nhiệt bàn khoảng (°C) | Range tinh đầu (mm) | Range cuối (mm) | Retry tinh | Kết quả |
| --- | ---: | ---: | ---: | ---: | --- |
| 1 | 27,7 | 0,070117 | 0,004698 | 7 | Đạt |
| 2 | 28,1 | 0,019403 | 0,006180 | 2 | Đạt |
| 3 | 28,5 | 0,013147 | 0,005309 | 1 | Đạt |

Range tinh ban đầu và số retry giảm qua ba lượt; cả ba range cuối đều dưới 0,0075 mm. Kết quả chỉ ở bàn gần nhiệt phòng, chưa đánh giá QGL tại nhiệt độ bàn in. Console của từng lần ở `qgl-round1.txt` đến `qgl-round3.txt`; bảng tóm tắt ở `qgl.csv` cùng thư mục diagnostics.

## Trạng thái sau thử và việc còn lại

- Klipper/KTC `ready`, `print_stats=standby`, XYZ homed, QGL `applied=true`, T0 active/detected, toolhead X169,1 Y164,9 Z10, toàn bộ heater target 0, không pause. Crash detection đã bật lại.
- Giá PF2 vẫn gắn theo lời người vận hành; phải tháo trước các chuyển động chuẩn bị in hoặc in. Các Z offset production vẫn là giá trị cũ; số đo PF2 chỉ là sơ bộ. T1 và T4 có biên độ giữa lượt trên 0,05 mm; cần kiểm tra đầu phun/ngàm và first-layer trước khi lưu Z cuối.
