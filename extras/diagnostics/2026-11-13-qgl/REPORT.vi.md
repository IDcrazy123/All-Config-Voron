# Đánh giá QGL sau thay NTC bàn và hiệu chuẩn lại — 13/11/2026

## Nguồn và trạng thái

Đọc log Klipper 11/11, 12/11 và log hiện tại 13/11 qua Moonraker, đọc trực tiếp mã Python đang cài trên `192.168.1.43` qua SSH, so file CFG live với repository và đọc trạng thái Moonraker trước/sau bản `Cube_ABS_2m5s.gcode`. Không gửi lệnh chuyển động, gia nhiệt, reload hoặc triển khai. Bản in kết thúc ở `state=complete`; sau đó `quad_gantry_level.applied=true`, bàn target/power bằng 0 và toolchanger `ready` với shuttle rỗng. Trạng thái hoàn thành bản in không tự xác nhận chất lượng lớp đầu.

## Cảm biến bàn: đối chứng log

- Trước thay cảm biến, log cũ đã ghi các cú nhảy phi vật lý khi dùng bàn: 27/10 khoảng 104→71,7°C ở target 105°C; 30/10 85,6→65,5→86,4°C khi tăng target lên 100°C; 07/11 109,0→44,3→106,2°C trong khoảng hai giây ở target 100°C. Đây là lỗi đường đo nhiệt, không thể do khối lượng bàn nguội/nóng thật nhanh như vậy. Người vận hành đã xác nhận cảm biến cũ có dấu hiệu hỏng khi sử dụng và đã thay nó.
- Khẳng định tuyệt đối rằng lúc không dùng thì không có lỗi **không khớp hoàn toàn với log**: 28/10, target và PWM bằng 0 hơn 15 phút, số đọc vẫn 49,7→4,4→49,8°C trong hai giây. Cảm biến khi đó vẫn ở trên máy và có thể còn ấm, nhưng sự cố không chỉ xuất hiện khi SSR đang cấp nhiệt. Log không phân biệt chắc chắn lõi NTC với dây/đầu nối/PB0; kết quả kiểm tra linh kiện của người vận hành là bằng chứng bổ sung.
- Sau thay, lượt gia nhiệt giám sát 11/11 có 389 mẫu 1 Hz, 24,5→100,4°C, không bước nào từ 2°C. Bộ phân tích log 11/11 và 13/11 cũng không thấy bước >=2°C trong các cặp Stats liên tiếp có target bàn >0 (đã loại ranh giới restart). Đây là bằng chứng đường đọc ổn hơn trong các khoảng đã quan sát, chưa là phép xác nhận dài hạn hoặc đo nhiệt tuyệt đối.

## QGL hội tụ sau các hiệu chuẩn mới

Ngày 11/11, log xác nhận `PID_CALIBRATE` bàn đã lưu `Kp/Ki/Kd=64.710/2.713/385.835` lúc 17:09:11. Scan model hiện hành được `SAVE_CONFIG` lúc 20:28:42, nhiệt tham chiếu coil `-21.41°C`; Touch được lưu lại với threshold 792 lúc 20:46:36. Bảng sau chỉ lấy các lượt QGL **tinh** với tolerance 0,0075 mm sau khi model cuối cùng và Touch này đã lưu, tại target bàn 105°C. `retry` là số Klipper in ở vòng cuối, không gồm lượt thô tolerance 1 mm.

| Nguồn log, dòng đầu | Range tinh đầu → cuối (mm) | Retry cuối | Kết quả |
|---|---:|---:|---|
| 11/11, 85855 | 0,119413 → 0,043574 | 4 | Hủy vì range tăng |
| 11/11, 86356 | 0,075756 → 0,005728 | 7 | Đạt |
| 11/11, 103531 | 0,119835 → 0,002801 | 3 | Đạt |
| 11/11, 104053 | 0,093904 → 0,033513 | 3 | Hủy vì range tăng |
| 11/11, 104446 | 0,078877 → 0,005539 | 6 | Đạt |
| 13/11, 6437 | 0,095679 → 0,353690 | 5 | Hủy vì range tăng |
| 13/11, 8353; bản in hoàn tất | 0,025144 → **0,003413** | 2 | Đạt |

Tổng ở điều kiện nóng trên là **4/7 đạt, 3/7 thất bại**. Những lượt đạt cần 2–7 retry, nên QGL vẫn chưa hội tụ tin cậy dù NTC và PID đã thay/hiệu chuẩn lại. Lượt lạnh ngày 13/11 (bàn 22°C, target 0) đạt 0,007061 mm ở retry 1, nhưng không cùng điều kiện nhiệt. Log 12/11 không có lượt QGL. Các lượt trong bảng không phải thí nghiệm A/B kiểm soát: trạng thái gantry, lịch sử đổi tool và thời gian chờ khác nhau.

Trong lượt thất bại ngày 13/11, range tinh lần lượt là `0,095679 → 0,024908 → 0,024000 → 0,013422 → 0,249438 → 0,353690 mm`. Các số Stats tại vòng đo giữ bàn khoảng **105,1–105,2°C**, trong khi nhiệt coil Cartographer hiển thị khoảng **−31,4 đến −29,1°C**. Điểm Scan ở X330 Y10 đọc 1,726881 rồi 1,516505 mm ở hai vòng liên tiếp; sau bù motor, vòng sau cho X330 Y280 = 1,515384 và X330 Y10 = 1,869075 mm. Các giá trị giữa vòng có bù Z nên không thể coi chênh lệch trực tiếp là hành trình gantry, nhưng các điểm phải dao động quá lớn so với ngưỡng 0,0075 mm. Lượt bản in kế tiếp ở cùng target bàn bắt đầu 0,025144 và đạt 0,003413 mm ở retry 2; tại các vòng này số bàn in ra đều 105,2°C. Điều đó tái hiện tính lúc được lúc không dù số bàn ổn định.

## Đường dữ liệu trong Python đang chạy

- `/home/voron/klippy/klippy/extras/cartographer.py` chỉ import `cartographer.extra`; mã thật ở `klippy-env/lib/python3.11/site-packages/cartographer/` phiên bản 1.10.1. `mcu/mcu.py` lấy `data["temp"]` từ **MCU Cartographer** và gắn vào `Sample.temperature`; không đọc `heater_bed`.
- `probe/scan_mode.py:128-145` thu các mẫu sau khi dừng chuyển động, bỏ 5 mẫu đầu, mặc định lấy 20 mẫu, đổi tần số coil sang khoảng cách rồi lấy median. `probe/scan_model.py:78-96` có thể bù theo `Sample.temperature`, nhưng `core.py:128-140` chỉ tạo `CoilTemperatureCompensationModel` khi có `config.coil.calibration`. Cấu hình đang nạp không có hệ số coil; nhánh `NoTemperatureCompensationModel` trả tần số nguyên vẹn. Giá trị coil âm vẫn được log và lưu làm nhiệt tham chiếu model, nhưng **không chạy phép bù nhiệt coil** trong QGL hiện tại. `heater_bed` không phải biến đầu vào của phép đổi tần số.
- `quad_gantry_level.py:45-112` dùng bốn số `bed_z`, ngoại suy vị trí bốn motor và ra lệnh bù. `z_tilt.py:102-125` chỉ kiểm tra max−min bốn điểm; nếu range tăng qua hai vòng thì hủy và thêm thông báo `Possibly Z motor numbering is wrong`. Thông báo là quy tắc đếm range, không phải phép xác thực đấu dây motor. Các lượt khác cùng mapping đạt, nhưng chưa đo hành trình motor độc lập.

**Kết luận:** không có đường mã Python đưa nhiệt NTC bàn trực tiếp vào phép đo QGL. NTC cũ có lỗi đường đọc thật; thay NTC đã cải thiện tín hiệu bàn trong mẫu quan sát nhưng không giải thích được các lần QGL nóng vẫn thất bại khi bàn báo ổn định. Nguồn bất ổn gần nhất trong log là số đo Scan/đáp ứng sau bù Z ở các điểm phải. Chưa thể xác định duy nhất gá/coil Cartographer, drift nhiệt vật lý, mặt bàn, cáp hoặc cơ khí Z bằng log phần mềm. Không sửa tolerance, retries, mapping motor hay hệ số bù để che lỗi. Phép phân biệt tiếp theo: đo đồng hồ so tại các góc, cùng nhiệt 105°C và cùng T0, trước/sau vòng QGL hoặc vòng T0→T3→T0; đồng thời thu Scan ngắn tại từng điểm. So đồng hồ so với Scan để tách chuyển động thật khỏi drift đầu dò. Cần người vận hành giám sát phép thử nóng/chuyển động đó.

## Đồng bộ cấu hình

- `config/printer.cfg`: đồng bộ PID bàn và Scan model cuối cùng từ file live; giữ nguyên Touch 792, mesh, offset tool và các phần khác.
- `config/Printer-Setup/hardware.cfg`: ghi nhận live dùng `smooth_time=1.0 s` và `pwm_cycle_time=0.1 s` mặc định bằng cách comment hai override 3.0/0.2; `PA5`, `PB0`, sensor_type và max_temp 120°C giữ nguyên.
- `config/Printer-Setup/calibration-probe.cfg`: phản ánh section axis twist đang tắt và không có hệ số lưu. QGL macro và hình học không đổi.
- Sao lưu ba CFG cũ ở `extras/backups/pre-qgl-live-sync-20261113-085432/`. Đây chỉ là đồng bộ Git theo trạng thái đã nạp; không reload hoặc deploy lên máy.

Chi tiết từng lượt và trạng thái Stats kèm theo ở `qgl-runs.csv`, `summary.json`; `analyze.py` tái lập bản tóm tắt từ các log Klipper. Log gốc nằm trên máy tại Moonraker root `logs` và bản đọc tạm trên máy phân tích, không đưa file log hàng chục MB vào Git.
