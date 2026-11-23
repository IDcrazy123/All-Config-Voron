# 2026-11-23 — Cứu bản in Boxturtle sau khi T2 in khô

## Bằng chứng trước can thiệp

- Bản đang pause: `Boxturtle_ABS_5h40m.gcode`, Klipper `ready`, `print_stats=paused`, `pause_resume.is_paused=true`, `virtual_sdcard.file_position=22547710/22706252` (99,3018%). XYZ còn home, QGL applied, T2 active/detected, filament sensor T2 báo có nhựa; bàn/T2 target 100/250°C.
- Console báo runout T2 và pause lần đầu. `klippy.log` ghi `Filament Sensor filament_sensor_T2: runout event detected` rồi `Exiting SD card print (position 22243619)`; lần resume kế tiếp bắt đầu chính byte đó. Lần pause sau ở byte 22547710. Người vận hành xác nhận toàn bộ đoạn giữa hai mốc đã **in khô**, không có lớp nhựa mới phía trên, và T2 đã được nạp lại đến khi đùn đều, vòi sạch.
- Metadata G-code: 165 lớp, cao tối đa 33,04 mm. Byte 22243619 nằm trong lớp Z32,24 mm; lệnh tiếp theo là `G1 X129.446 Y277.759 E2.71008`, điểm cuối của lệnh ngay trước đó là X218.554 Y277.759. Byte pause sau nằm trong lớp cuối. Tua từ đúng byte đầu tránh lặp phần đã in trước runout.

## Thao tác cứu

1. Kiểm tra lại trạng thái pause, file position, T2 active/detected, filament sensor, homing và QGL trước khi di chuyển.
2. Khi vẫn pause, nâng lên G-code Z37, di chuyển ở cao độ này tới X218.554 Y277.759, hạ từng bước qua Z32,44 xuống Z32,24 với `M400` và người vận hành quan sát.
3. Đặt `G90`, `M83`, rồi `SAVE_GCODE_STATE NAME=PAUSE_STATE` tại đúng điểm bắt đầu; dùng `M26 S22243619` để đặt lại con trỏ SD. Xác nhận live còn pause, file position đúng 22243619, T2 còn được nhận diện và cảm biến có nhựa.
4. Gửi `RESUME`. Klipper trả `print_stats=printing`; người vận hành xác nhận đường nhựa đầu tiên bám đều. Theo dõi tiến độ qua mốc pause cũ 22547710 và tới hết file.

## Kết quả và giới hạn

- Kết thúc `print_stats=complete`, `virtual_sdcard.file_position=22706252/22706252` (100%), không có runout/pause mới trong đoạn in lại. T2 được thả về dock, heater target bàn và T2 đều 0; Klipper vẫn `ready`.
- Người vận hành kiểm tra trực quan sau khi in xong và xác nhận vùng in bù **liền, bám đều**, không thấy khe/hụt nhựa. Độ bền liên kết bên trong vẫn chưa được thử sau khi nguội. Sensor runout đánh dấu điểm pause của G-code; nó không tự chứng minh vị trí bắt đầu thiếu nhựa vật lý trong mọi trường hợp. Lần này người vận hành xác nhận đoạn giữa hai pause đều in khô.
- Không sửa CFG production hay thay thông số máy trong thao tác cứu. Chỉ đặt lại pause state và vị trí đọc của file đang pause.
