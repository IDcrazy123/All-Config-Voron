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

## 4. Audit toàn bộ G-code cũ và các rủi ro còn lại

### Phạm vi và phần đã loại trừ

- Đọc toàn bộ file cũ khoảng 335 MB/13,57 triệu dòng, 403 lần đổi lớp từ `Z=0.24` đến `Z=80.64`.
- Không có `NaN`/`Inf`, Z đi lùi, tọa độ vượt khổ máy, lệnh nhiệt bị thiếu, chuyển đổi `M82/M83` sai hoặc bước nhảy E thật bất thường.
- 1.167 lần đổi tool đều unload tổng đúng 5 mm; mỗi lần chọn tool đều có `M109`. Pressure Advance đúng theo T0/T1/T2/T3 là 0.072/0.060/0.066/0.076.
- Lưu lượng lệnh bình thường không vượt `max_extrude_cross_section=0.64 mm²`; lỗi extrusion khi exclude vẫn là state-transform của Klipper, không phải G-code gốc đòi phun quá mức.
- File lớn không làm Klippy nghẽn: không có bằng chứng buffer starvation hay tải host gây job abort.

### Phát hiện chắc chắn

1. `retract_restart_extra=+0.2 mm` ảnh hưởng toàn bộ job, không chỉ tám Arm ở lớp 3. Có 163.495 lần restart thường dùng `E0.7` sau retract 0,5 mm và 1.164 lần phục hồi đổi tool dùng `E5.2` sau unload 5 mm. Tổng dư lý thuyết là 32.931,8 mm filament, khoảng 79,2 cm³ hoặc xấp xỉ 99 g PETG. Footer của Orca không cộng phần restart-extra này nên ước lượng vật liệu cũ che giấu lượng dư. Không được tái dùng G-code cũ.
2. Wipe tower đang là Type 2 nhưng `tool_change_on_wipe_tower=0`. Replay XY cho thấy 0/1.167 lần đổi tool thật xảy ra tại tháp; tất cả được gọi khi đầu in còn ở trên hoặc gần chi tiết, rồi mới đi tới tower. `t_command_restore_axis: Z` không phục hồi XY. Đây là rủi ro rỉ nhựa/va chạm độc lập với lỗi restart-extra.
3. `M220 S100` xuất hiện 1.168 lần tại các block wipe/toolchange và không có restore. Mọi Speed Factor giảm trong Mainsail bị trả về 100% ở lần đổi đầu kế tiếp; không được dùng slider live làm biện pháp giảm tốc cho bài multi-tool này.
4. Z-hop gần như không hoạt động vì `retract_lift_enforce=Top Only`: chỉ khoảng 198/156.827 chu kỳ retract-to-print có nâng Z đủ 0,15 mm; 6.194/6.222 lần chuyển object không nâng. Tại `sd_pos` của watchdog Arm5, G-code đang ở chuỗi travel 350 mm/s cùng Z ngay sau retract, nên tương quan với cơ chế nozzle quệt phần đã cong là rất mạnh, dù cảm biến không xác định vật bị chạm.
5. Orca phát `SQUARE_CORNER_VELOCITY=9` khi in và `12` khi travel, mỗi mức 218.662 lần; G-code không dùng SCV 5 đặt trong `printer.cfg`. Travel đạt 350 mm/s, acceleration 7.000. Không vượt giới hạn slicer, nhưng tạo chuyển động gắt hơn baseline máy và tăng hậu quả khi đi qua island nhỏ.
6. `filament_max_volumetric_speed=20 mm³/s` được dùng thật ở sparse/internal solid infill. Khoảng 8,1% thể tích extrusion được lệnh từ 18 mm³/s trở lên và khoảng 3,5% ở vùng 20 mm³/s. Giá trị 20 chưa có log hiệu chuẩn từng spool/hotend; nhật ký cũ từng giữ trần tạm 15 mm³/s. Đây là nguy cơ thiếu đùn/độ bám lớp về sau, không phải nguyên nhân blob T1 lớp 3.
7. Lớp đầu dùng perimeter 30 mm/s nhưng bottom surface/infill 105 mm/s; `slow_down_layers=0`, nên không có ramp tốc độ các lớp đầu. Đây là rủi ro độ bám nền cho job 44 giờ nhiều vật, chưa thấy bằng chứng nó gây ba Arm bị loại.
8. Chamber khoảng 49,5–49,7°C khi T1 in lớp lỗi, khoảng 53°C quanh watchdog; `PRINT_START` bật bed-fan 50% nhưng G-code không điều khiển exhaust thật. Nhiệt buồng cao có thể làm PETG island/overhang nguội chậm. Metadata exhaust không chứng minh quạt xả vật lý đang chạy.
9. Tại lớp T1 kế tiếp có 176 cặp đổi PWM quạt 90%↔10% trong khoảng 102 giây. Với `fan_min_speed=10%` và không có phản hồi RPM, cần kiểm tra blower có tự khởi động/duy trì ở `M106 S25`; không suy đoán một duty tối thiểu khi chưa đo.
10. Prime tower dùng khoảng 58.945 mm³, xấp xỉ 74 g PETG, cho 1.167 lần đổi tool. Đây là chi phí dự kiến của job; chỉ giảm purge/prime sau coupon nhiều tool, không giảm mù.

### Thứ tự thay đổi đề xuất

1. **Bắt buộc trước job dài:** reslice bằng profile đã sửa restart/cooling/small-perimeter; đặt `tool_change_on_wipe_tower=1`; tạm đặt `gcode_label_objects=0` cho multi-tool để không thể kích hoạt bug exclude-object hiện tại. Sau slice, kiểm tra mọi `Tn` nằm tại tower và không còn marker object.
2. **Plate chẩn đoán 1–2 Arm:** `Z-hop enforcement=All Surfaces`, Spiral Lift 0,20 mm; travel 250 mm/s, travel acceleration 5.000 mm/s²; đưa jerk/SCV print và travel về 5 mm/s để khớp `printer.cfg`. Chỉ tăng hop lên 0,30 mm nếu vẫn có bằng chứng quệt; không áp toàn bộ profile trước khi đo thời gian và chuyển động Z phát sinh.
3. **Độ bám lớp đầu:** thử initial-layer infill khoảng 50 mm/s và `slow_down_layers=3`; giữ nguyên brim gap 0,2 mm nếu không có dấu hiệu bong nền.
4. **Vật liệu:** tạm dùng 15 mm³/s cho lượt xác minh độ tin cậy, rồi chạy Temperature Tower và Max Volumetric Speed cho đúng từng spool/tool; lưu kết quả bền vững trừ biên 10–15%. Với Bambu PETG Basic, preset hệ thống Orca hiện dùng MVS 13 và dải nozzle 230–270°C, trong khi profile job là 20 và 220/225°C; cần tower trước khi xác nhận nhiệt production.
5. **Cooling:** chạy thử PETG với bed-fan tắt hoặc enclosure thông thoáng và theo dõi chamber thấp hơn; đây là thử nghiệm riêng, chưa sửa macro chung. Đo khả năng khởi động của từng blower ở 10%; chỉ sau đó mới nâng `fan_min_speed`/kickstart nếu cần.
6. **Vận hành:** không dựa vào Speed Factor live vì `M220 S100`; không bật tùy chọn Orca mới “Wait for Temperature on Wipe Tower” khi KTC `pickup_gcode` đã có `M109`, trừ khi thiết kế lại và kiểm thử chuỗi nhiệt. Chưa sửa purge volume hay firmware motion dựa trên G-code cũ.

### Trạng thái

- Phiên audit này chỉ thay tài liệu; chưa sửa thêm profile Orca, cấu hình Klipper hoặc máy in.
- Các thay đổi trên cần được áp theo từng nhóm và reslice/preview lại, ưu tiên coupon ngắn trước job đầy đủ.

### Tham chiếu upstream bổ sung

- Orca Type 2 wipe tower: https://github.com/OrcaSlicer/OrcaSlicer/wiki/printer_multimaterial_wipe_tower
- Orca initial-layer speed: https://github.com/orcaslicer/orcaslicer/wiki/speed_settings_initial_layer_speed
- Orca Z-hop: https://github.com/OrcaSlicer/OrcaSlicer/wiki/printer_extruder_z_hop
- Orca calibration: https://github.com/OrcaSlicer/OrcaSlicer/wiki/Calibration/2b70123e50cc43b7f6003339030c76eb2a8067c6
- Orca MVS: https://github.com/OrcaSlicer/OrcaSlicer/wiki/material_volumetric_speed_limitation
- Orca `M220 S100` issue: https://github.com/OrcaSlicer/OrcaSlicer/issues/7021
- Klipper G-code state: https://www.klipper3d.org/G-Codes.html

## 5. Xác minh cách chỉnh Z-hop trong OrcaSlicer 2.4.2

- Profile active hiện đặt cả năm tool: `On surfaces=Top Only`, `Z-hop type=Spiral Lift`, `Z-hop height=0.15 mm`, `Traveling angle=15°`, `Only lift Z above/below=0/0` và `retraction_minimum_travel=2 mm`.
- Đối chiếu source OrcaSlicer tag v2.4.2 xác nhận `Top Only` chỉ cho lift khi extrusion role cuối là Top Solid Infill hoặc Ironing; nó không có nghĩa là mọi travel phía trên object. `All Surfaces` mới cho phép lift sau mọi retract/toolchange đủ điều kiện.
- Z-hop vẫn phụ thuộc vào retraction: travel ngắn hơn ngưỡng hoặc travel bị bỏ retract sẽ không hop. `Auto Lift` không quyết định có hop hay không; nó chỉ chọn Spiral khi đường đầu travel cắt vùng overhang, ngược lại chọn Slope. Toolchange/layer change dùng Auto bị ép về Spiral.
- Thiết lập coupon đề xuất: đổi `On surfaces` thành `All Surfaces` cho năm tool, tăng height lên 0,20 mm, giữ Spiral/15°/0/0 để thay đổi tối thiểu. Nếu vẫn quệt ngay tại điểm rời island, dùng `Normal Lift` để hoàn tất nâng Z trước chuyển động XY.
- Không áp thẳng cho plate đầy đủ: G-code cũ có hơn 156 nghìn chu kỳ retract-to-print nên All Surfaces có thể tạo số hop rất lớn. Cần reslice 1–2 Arm và xác nhận sau retract có Z tăng khoảng 0,20 mm, sau đó hạ lại trước extrusion; Spiral có thể hiện bằng G2/G3 hoặc move XYZ, không nhất thiết là một dòng `G1 Z` riêng.
- Đường dẫn UI: Advanced → Edit Printer preset → `Extruder 1`…`Extruder 5` → nhóm `Z-Hop`.
- Tài liệu: https://github.com/OrcaSlicer/OrcaSlicer/wiki/printer_extruder_z_hop
- Phiên này chỉ xác minh và đề xuất; chưa thay đổi profile active.

## 6. Xác minh Speed Factor trong Mainsail bị trả về 100%

### Triệu chứng

- Khi giảm Speed Factor trong Mainsail, mức giảm chỉ giữ được đến lần đổi tool kế tiếp; sau đó giao diện và chuyển động trở lại 100%.
- G-code cũ và bản reslice mới đều chứa 1.168 lệnh chính xác `M220 S100`: 1.167 lệnh trong các lần đổi tool thật và một lệnh ở final unload.
- Không có `M220 B`, `M220 R`, `SAVE_GCODE_STATE` hoặc cơ chế tương đương để khôi phục mức Speed Factor trước đó.

### Nguyên nhân gốc đã xác nhận

- Đây không phải lỗi của Mainsail, KTC hoặc lần mất nguồn. Mainsail chỉ gửi `M220 S<phần-trăm>`; Klipper gán trực tiếp giá trị này vào `speed_factor`.
- OrcaSlicer 2.4.2 Type 2 wipe tower gọi backup, đặt `M220 S100`, rồi gọi restore. Tuy nhiên, trong `WipeTower2.cpp`, backup/restore chỉ phát `M220 B/R` cho Marlin; nhánh Klipper không phát gì. Vì vậy lệnh `M220 S100` ghi đè mức người vận hành chọn và giá trị cũ bị mất.
- Orca issue #7021 mô tả đúng lỗi này; issue đã đóng vì stale/not planned và source hiện tại vẫn còn logic tương tự. Không có setting Orca 2.4.2 để tắt riêng lệnh reset này.
- KTC lưu G-code state sau khi `M220 S100` đã chạy, nên state của KTC cũng chỉ ghi nhớ 100% và không thể phục hồi mức cũ.

### Phương án sửa đề xuất

Không override `M220` toàn cục và không xóa mù mọi `M220 S100`, vì các lệnh reset ở `PRINT_END`/cancel/final unload là có chủ đích. Không dùng full `SAVE_GCODE_STATE` chỉ cho việc này vì nó còn lưu/khôi phục modes, vị trí cơ sở/G92, offsets, feed, M221 và trạng thái E.

Dùng hai macro chỉ lưu riêng Speed Factor:

```ini
[gcode_macro ORCA_WIPE_SPEED_BEGIN]
variable_saved_percent: 100.0
gcode:
  {% set pct = printer.gcode_move.speed_factor|float * 100.0 %}
  SET_GCODE_VARIABLE MACRO=ORCA_WIPE_SPEED_BEGIN VARIABLE=saved_percent VALUE={pct}
  M220 S100

[gcode_macro ORCA_WIPE_SPEED_END]
gcode:
  {% set pct = printer["gcode_macro ORCA_WIPE_SPEED_BEGIN"].saved_percent|float %}
  M220 S{pct}
```

Postprocessor Orca phải là state machine và fail-closed:

1. Chỉ bọc một `CP TOOLCHANGE` khi block đó có đủ cặp `; WIPE_TOWER_START` / `; WIPE_TOWER_END`; thay đúng dòng `M220 S100` sau `WIPE_TOWER_START` bằng `ORCA_WIPE_SPEED_BEGIN`.
2. Với block đã thay, chèn `ORCA_WIPE_SPEED_END` ngay trước marker `; CP TOOLCHANGE END`.
3. Từ chối xuất file nếu block lồng nhau, marker không đóng, block wipe thiếu hoặc thừa reset, hay số wipe-start/wipe-end/BEGIN/END không bằng nhau.
4. Không sửa block final unload không có marker wipe, reset cuối job hoặc các macro `PRINT_END`/cancel. Với file này, kết quả đúng phải là 1.167 BEGIN + 1.167 END và còn đúng một `M220 S100` ở final unload.

Với Speed Factor 50%, kết quả mong đợi là object chạy 50%, toolchange/wipe tower tạm chạy 100%, rồi object tự trở lại 50%. Nếu chỉ xóa reset trong tower thì slider cũng được giữ, nhưng docking/unload/wipe sẽ chịu cả mức tăng trên 100%; phương án này không được khuyến nghị cho máy nhiều tool.

### Xác minh bắt buộc trước production

- Test lạnh: đặt `M220 S50`, gọi BEGIN và xác nhận 100%, gọi END và xác nhận trở lại 50%.
- Xác nhận không đổi XYZ, E, tool transform, G90/G91, M82/M83 hoặc M221.
- Post-process coupon hai tool; kiểm tra số BEGIN bằng số END, bằng số cặp wipe tower được bọc, và chỉ còn reset có chủ đích ngoài các block đó.
- In coupon ở 50–70%; quan sát tower/toolchange lên 100% rồi object trở lại giá trị đã chọn.
- Không chỉnh slider trong lúc đang ở giữa BEGIN/END, vì END có chủ đích phục hồi giá trị đã lưu trước block.
- Xác nhận cancel và `PRINT_END` vẫn trả Speed Factor về 100%.

### Trạng thái

- Phiên này chỉ xác minh nguyên nhân và thiết kế cách sửa; chưa thay đổi cấu hình Klipper, profile Orca hoặc G-code production.
- Cần tạo backup, cài macro, thêm postprocessor, replay lạnh và in coupon trước khi dùng cho job dài.

### Tham chiếu

- OrcaSlicer 2.4.2 `WipeTower2.cpp`: https://github.com/OrcaSlicer/OrcaSlicer/blob/v2.4.2/src/libslic3r/GCode/WipeTower2.cpp
- OrcaSlicer issue #7021: https://github.com/OrcaSlicer/OrcaSlicer/issues/7021
- Klipper G-Codes (`M220`, `SAVE_GCODE_STATE`): https://www.klipper3d.org/G-Codes.html
- Klipper status `gcode_move.speed_factor`: https://www.klipper3d.org/Status_Reference.html
