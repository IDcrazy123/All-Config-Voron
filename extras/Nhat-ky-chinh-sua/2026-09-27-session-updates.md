# Nhật ký chỉnh sửa 2026-09-27

## 1. Đồng bộ profile OrcaSlicer active

### Mục tiêu

Đồng bộ đầy đủ các preset người dùng đã sửa ngày 2026-09-26 từ AppData vào repository trước khi phân tích bản in mới nhất.

### Nguồn

- Profile ID: `838ce884-12ee-416b-9e1b-1c7503cf6b5f`
- Thư mục: `C:\Users\batca\AppData\Roaming\OrcaSlicer\user\838ce884-12ee-416b-9e1b-1c7503cf6b5f`

### Kết quả

- Đồng bộ 19 JSON active; 9 đích repository/alias thay đổi.
- Bổ sung preset mới `Orca Config/PETG Bambu Basic White.json`.
- Giữ nguyên các thay đổi mới của người vận hành, gồm retraction, Spiral Lift, `z_hop=0.15`, prime tower và filament.
- Backup trước đồng bộ: `extras/backups/pre-orcaslicer-profile-sync-20260927-123646/`.
- Tất cả JSON nguồn/đích đều parse được bằng `ConvertFrom-Json`.

## 2. Điều tra bản in RoboOctopus bị lỗi

### Dữ liệu

- Job: `RoboOctopus_4Color_PETG_1d20h9m.gcode`, OrcaSlicer 2.4.2.
- Log tải từ máy: `extras/logs/klippy-20260927-122410-latest-print.log` và `extras/logs/moonraker-20260927-122410-latest-print.log`.
- G-code phân tích: file gốc 334,864,509 byte tải qua Moonraker.
- Ảnh thực tế: phần nhô màu xanh/trắng của cả Arm1–Arm8 bị blob/cong từ lớp 3.

### Nguyên nhân hình học đã xác nhận

1. Profile machine active có `retract_restart_extra=+0.2 mm` cho cả năm tool. Tại mỗi micro-island T1 của lớp 3, G-code retract tổng `-0.50 mm` rồi deretract `+0.70 mm`, vì vậy cố ý bơm dư `+0.20 mm` filament trước khi in. Island đầu chỉ cần khoảng `0.07132 mm` filament cho toàn bộ đường in; phần prime dư lớn gấp khoảng 2.8 lần và có thể tích khoảng `0.481 mm³`.
2. Chi tiết xanh T1 bắt đầu ở lớp vật lý 3, `Z=0.64`. Toàn block Arm1–Arm8 có 74 lệnh `M106 S0` vì `close_fan_the_first_x_layers=3`; Orca chỉ cho quạt hoạt động từ lớp 4. Sang `Z=0.84`, T1 mới xen kẽ `M106 S229` (90% overhang) và `M106 S25` (xấp xỉ 10%).
3. Các micro-island được gắn loại `Outer wall` và chạy tới 86–120 mm/s. `small_perimeter_speed=50%` không có tác dụng vì `small_perimeter_threshold=0` tắt hoàn toàn tính năng này.
4. `fan_speedup_overhangs=1` nhưng `fan_speedup_time=0`, vì vậy việc đưa quạt lên 90% không được phát sớm; các burst ngắn có thể kết thúc trước khi blower đạt tốc độ.

Chuỗi trên giải thích trực tiếp việc lỗi xuất hiện đồng loạt 8/8 Arm tại đúng lớp bắt đầu của hình học tách đảo. `retract_restart_extra=+0.2` tạo blob; quạt bị khóa, tốc độ cao và small-perimeter bị vô hiệu làm blob còn nóng, cong lên và tăng nguy cơ nozzle va vào chi tiết.

### Ba lần loại object và lỗi kết thúc job

- Watchdog chỉ ghi một crash của T1 khi đang in Arm5 tại `Z=2.84` (`klippy.log` dòng 231069). Va chạm với phần in đã cong là cơ chế phù hợp nhất, nhưng log không đo trực tiếp lực va chạm.
- Sau resume 11:49:11, người vận hành loại Arm5, Arm8 và Arm6 (`klippy.log` dòng 232064, 232102 và 235894). Arm8/Arm6 không có fault firmware độc lập; ba lần exclude là thao tác loại các vật đã quan sát thấy hỏng.
- Khoảng 11:54:58, Klipper dừng bằng `Move exceeds maximum extrusion (1.590mm^2 vs 0.640mm^2)` tại `sd_pos=29595007` (`klippy.log` dòng 241364).
- Vị trí đó là lệnh travel không có `E`, `G1 X255.74 Y211.517 F21000`, ngay khi rời Arm6 đã exclude để sang Arm3.

Mô phỏng 1:1 thuật toán `exclude_object.py` trên G-code thật tái hiện đúng lỗi: travel dài `55.1980166 mm` bị transform tạo `ΔE=+36.4941600 mm`, cho tiết diện `1.5902517 mm²`. Nguyên nhân là `extrusion_offsets` được tách theo extruder nhưng `max_position_extruded` và `max_position_excluded` của Klipper commit `60fc7aa67` lại dùng chung. Hai cực đại T3 (`8467.53118` và `8482.64796`) bị trộn với E hiện tại của T0, tạo `extruder_adj=-36.49416` rồi biến travel thành lệnh đùn giả.

Khi mô phỏng các giá trị last/max theo từng extruder, cùng travel có `extruder_adj=0`, `ΔE≈0` và không còn lỗi. Không được tăng `max_extrude_cross_section`: làm vậy chỉ bỏ van an toàn và cho máy thật sự đẩy khoảng 36.5 mm filament trên một travel.

### Mất nguồn

- Job đã bị Klipper dừng khoảng 11:55:01.
- Klippy khởi động lại khoảng 11:57:26 và Moonraker `Unsafe Shutdown Count` tăng `301 → 302`.
- Lần rút nguồn xảy ra sau lỗi gần hai phút, nên không gây blob lớp 3, crash T1 hay ba thao tác exclude. Nó chỉ tạo một lần shutdown không an toàn và làm đứt phần đuôi log cũ.

## 3. Sửa profile để xác minh lần in kế tiếp

### Thay đổi

- `Orca Config/Voron Stealthchanger.json`
  - `retract_restart_extra`: `0.2 → 0` cho cả năm tool.
  - `fan_speedup_overhangs=1` và `fan_speedup_time=0.5 s`.
- `Orca Config/PETG Kabber Blue.json`
  - Override `close_fan_the_first_x_layers=2`, cho T1 dùng cooling từ lớp 3.
- `Orca Config/0.20mm Multicolor PetG.json`
  - `small_perimeter_threshold=5 mm`.
  - `small_perimeter_speed=30 mm/s`.
- Cập nhật hai alias phân tích trong `extras/Orcasilcer setting/`.
- Chép ba preset đã sửa trở lại đúng profile AppData active. Cửa sổ OrcaSlicer Store đã mở từ trước khi chép, vì vậy cần đóng/mở lại Orca sau khi lưu công việc đang mở để nạp chắc chắn các giá trị mới từ đĩa.

### Sao lưu

- Trước sửa mục tiêu: `extras/backups/pre-robooctopus-orca-fix-20260927-124213/` (có cả bản repo và AppData).
- Trước cập nhật alias: `extras/backups/pre-orcaslicer-profile-sync-20260927-124749/`.

### Kiểm tra

- Ba JSON sửa đều parse thành công.
- SHA-256 của các preset repo và bản active trong AppData vẫn khớp sau khi sửa, kể cả khi tiến trình Orca GUI đang mở.
- Reslice cô lập thành công project gốc `RoboOctopus_4Color.3mf` bằng OrcaSlicer portable 2.4.2; exit code `0`, G-code đầu ra `317,282,288` byte. Bản CLI chỉ thêm metadata `type`/compatibility vào các bản sao tạm vì JSON do GUI lưu không có các trường bắt buộc riêng của CLI; không sửa project 3MF hay profile production vì việc này.
- Footer G-code mới xác nhận `retract_restart_extra=0,0,0,0,0`, `close_fan_the_first_x_layers=3,2,3,3,3`, `fan_speedup_time=0.5`, `small_perimeter_speed=30` và `small_perimeter_threshold=5`.
- Tại layer 3 của cả Arm1–Arm8, 88 lần deretraction (10–12 lần mỗi Arm) đều đổi từ `E0.7` thành đúng `E0.5`, loại 17.6 mm filament prime dư, tương đương khoảng 42.333 mm³ nhựa. T1 không còn chuỗi 74 lệnh `M106 S0`; cooling mới dùng `M106 S25` (10%) và `M106 S229` (90% overhang).
- Các vòng được Orca phân loại small perimeter chạy `F1800`, tương đương 30 mm/s. Setting này không bắt mọi segment cực ngắn: một số đoạn vẫn theo outer-wall speed 109–120 mm/s, nên đây là lớp bảo vệ phụ; không hạ outer-wall speed toàn cục khi hai sửa trực tiếp đã loại prime dư và bật cooling đúng lớp.
- Replay `exclude_object` trên G-code mới, với Arm5/Arm8/Arm6 được loại tại các mốc logic tương ứng job cũ, vẫn tái hiện bug ở travel Arm6 → Arm3 không có `E`: transform tạo `+26.40971 mm` extrusion ảo và `1.1508167 mm² > 0.640 mm²`. Ba biến thể thời điểm loại trong cùng cửa sổ cho cùng kết quả; state E theo từng extruder vẫn cho `extruder_adj=0` và `ΔE=0`. Vì vậy sửa profile Orca giải quyết lỗi hình học nhưng không sửa bug Klipper độc lập.
- Chưa có lượt in vật lý sau sửa; trạng thái hiện tại là **reslice đã xác minh, chờ đóng/mở lại Orca và in mẫu ngắn**.
- Trước khi Klipper được backport/test cơ chế state E theo từng extruder, không dùng `EXCLUDE_OBJECT` trong job multi-tool. Không copy nguyên file từ fork khác và không tăng giới hạn extrusion.

### Tham chiếu upstream

- Orca cooling: https://github.com/OrcaSlicer/OrcaSlicer/wiki/material_cooling
- Orca small perimeters: https://github.com/OrcaSlicer/OrcaSlicer/wiki/speed_settings_other_layers_speed
- Orca retraction: https://github.com/OrcaSlicer/OrcaSlicer/wiki/printer_extruder_retraction
- Klipper exclude object guide: https://github.com/Klipper3d/klipper/blob/master/docs/Exclude_Object.md
- Klipper source tại commit đang chạy: https://github.com/Klipper3d/klipper/blob/60fc7aa67/klippy/extras/exclude_object.py
