# 2026-11-25 — Input shaper T0 và đánh giá gợn sóng khi quét bàn

## Nguồn và trạng thái live

- Hai đồ thị ShakeTune trên máy: `Generated-Data/ShakeTune/input_shaper/inputshaper_20261125_161249_axis_X.png` và `_axis_Y.png`. Phép đo dùng ADXL345 trên T0, lúc T0 gắn trên shuttle.
- Trước sửa, Git và `configfile` live cùng có MZV X 43,6 Hz / damping 0,124; MZV Y 33,4 Hz / damping 0,080. `print_stats=standby`, KTC `ready`, T0 active/detected, XYZ homed, QGL applied, Klipper `ready`. Bàn đang giữ target 100°C, vì vậy không triển khai hoặc restart trong lượt này.
- Backup hai file CFG trước thay đổi tại `extras/backups/pre-t0-shaper-20261125/` (bản Git HEAD trước khi sửa).

## Thay đổi và lý do

| Trục | Cũ | Mới | ShakeTune 25/11 |
|---|---|---|---|
| X | MZV 43,6 Hz; damping 0,124 | MZV 51,8 Hz; damping 0,145 | Đỉnh 49,2 Hz; MZV 51,8 Hz, rung 3,3%, smoothing 0,075, max accel 8000 |
| Y | MZV 33,4 Hz; damping 0,080 | MZV 35,0 Hz; damping 0,067 | Đỉnh 33,8 Hz; MZV 35,0 Hz, rung 1,2%, smoothing 0,167, max accel 3590 |

- Sửa `config/Printer-Setup/input-shaper.cfg` và ví dụ đang comment trong `config/toolchanger/tools/T0.cfg`. Hook KTC chỉ dùng override khi tần số per-tool dương; các dòng T0 vẫn comment, nên profile toàn cục mới sẽ áp dụng cho mọi tool. Phép đo này trực tiếp xác minh T0, chưa đo lại T1–T4.
- Giữ MZV theo khuyến nghị hiệu năng của hai đồ thị. Max accel 3590 mm/s² ở Y là giới hạn gợi ý từ mức smoothing cho shaper mới, không phải lỗi cú pháp hay giới hạn firmware. `max_accel` máy đang 7000; chưa thay vì cần phân biệt gia tốc in và travel và kiểm tra mẫu in.

## Đánh giá gợn sóng mesh

- [Cuộc trao đổi được cung cấp](https://chatgpt.com/share/6b06a83d-46c0-83ec-8f82-ea7297b94bb8) mô tả năm lượt quét **đều thực hiện ngày 25/11/2026**, khi heater bàn tắt: rapid 150/Z2 range 0,099 mm; rapid 50/Z2 0,117; scan 150/Z2 0,214; rapid 150/Z1 0,136; rapid 50/Z2 sau xoay PEI 90° 0,131. Sóng vẫn được quan sát ở cả năm điều kiện. Vì vậy chưa có cơ sở quy riêng cho rapid scan, tốc độ 150, độ cao Z2 hoặc tấm PEI xoay. Range toàn bàn không đo riêng biên độ gợn; khác biệt giữa các lượt trong cùng ngày vẫn có thể bị ảnh hưởng bởi trôi nhiệt/theo thời gian, nhất là `scan` 55×55 kéo dài.
- Mesh `default` đang có trong Moonraker là ma trận raw 55×55, min −0,043669 tại X242,00 Y236,66; max +0,087493, range 0,131162 mm. Min và range khớp ảnh số 5 trong cuộc trao đổi (X242 Y236,7; −0,044; range 0,131), nên profile live này chính là hoặc rất có thể là lượt xoay PEI cuối. Bàn hiện đang giữ 100°C, khác trạng thái heater-off lúc quét; dữ liệu lưu là kết quả quét cũ, không phải phép đo mới lúc đang gia nhiệt. Chỉ có một profile `default` live; thiếu bốn ma trận raw còn lại để định lượng độ tương quan/chu kỳ sọc. `mesh_pps: 0,0`, nên ma trận raw không phải nội suy bicubic.
- Từ ma trận raw của lượt số 5, lấy trung bình theo X ở từng hàng Y rồi trừ xu hướng đa thức bậc 2–5: đỉnh chu kỳ đều rơi vào khoảng 35,6 mm theo Y (biên độ thành phần bậc 3 khoảng 0,0066 mm). Đây là dấu hiệu định lượng của dải theo Y, chưa nhận diện được bộ phận gây ra nó; độ phân giải tần số của 55 hàng còn thô.
- Sự lặp lại hình sọc theo hệ tọa độ máy làm tăng nghi vấn về cơ khí XY/giá coil hoặc đế nam châm cố định, nhưng chưa phân biệt được chúng. Kết luận trong cuộc trao đổi rằng ray Y hay đế nam châm là nguyên nhân chính vẫn là giả thuyết. Tắt heater giảm nhiễu PWM bàn lúc đo nhưng không loại trừ trôi nhiệt coil hay nguồn nhiễu khác.
- Không đổi `bed_mesh`, `descend_z`, LDC1612, QGL hoặc `max_accel` từ năm ảnh. Chẩn đoán tiếp có giá trị nhất: lưu `probed_matrix` của từng lượt ở cùng nhiệt độ/soak và QGL, so sánh hình sọc theo tọa độ; đo một tuyến bằng native Tap sau khi xác nhận nozzle/T0 sạch và điều kiện tap an toàn. `scan` 55×55 mất nhiều thời gian, nên không chạy lặp tự động.

## Xác minh và việc còn lại

- `git diff --check` đạt; hai đồ thị và effective config live đã đối chiếu. Chưa reload, chưa chạy cơ khí, chưa in mẫu xác minh ghosting/lớp đầu; sửa shaper không tự giải quyết mesh.
- Khi máy hết gia nhiệt và rảnh, đối chiếu lại live/SAVE_CONFIG trước khi triển khai đúng hai file CFG và restart. Sau đó xác minh `configfile.settings.input_shaper` và in mẫu T0; nếu T1–T4 có chất lượng xấu đi thì cần profile riêng từng tool thay vì suy rộng phép đo T0.
