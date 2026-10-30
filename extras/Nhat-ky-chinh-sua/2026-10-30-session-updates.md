# Nhật ký — 2026-10-30

## 1. Đối chiếu nhiệt coil, model scan và khả năng hội tụ QGL

- Đọc trực tiếp log Klipper/Moonraker hôm qua, sáng nay và trạng thái live máy `192.168.1.43`. Mẫu nhiệt âm đầu tiên xác định khoảng **20:11:35 ngày 29/10**, sau khi hiệu chỉnh đồng hồ khởi động bằng monotonic trong cùng phiên. Mẫu dương cuối trước khoảng mất dữ liệu là 10:14:15,3, +33,7°C. Không xác định được thời điểm hỏng vật lý trong khoảng không có dữ liệu.
- Plugin lúc xuất hiện nhiệt âm là **1.9.0**; Moonraker ghi nâng lên **1.10.1 lúc 09:32:54 ngày 30/10**. Không có cơ sở quy thời điểm bắt đầu lỗi cho cập nhật 1.10.1.
- Đã đọc Python đang cài qua SSH. Khi còn hệ số coil calibration, nhiệt mẫu đi qua bù tần số trước khi tính khoảng cách cho QGL. Nhiệt ngoài dải chỉ được cảnh báo, không bị loại khỏi phép tính.
- Thu khoảng 4 giây dữ liệu tĩnh bằng `CARTOGRAPHER_STREAM` vào `/tmp`, không di chuyển trục. Phát lại với model/bù nhiệt cũ: cửa sổ 20 mẫu dao động khoảng 16,9 µm; cố định nhiệt chỉ trong đối chứng ngoại tuyến còn khoảng 1,3 µm. Cửa sổ 200 mẫu với bù cũ còn khoảng 3,7 µm. Đây là kiểm tra số học trên dữ liệu tĩnh, chưa chứng minh hiệu quả QGL sau chuyển động hoặc với model mới.

## 2. Thay đổi người vận hành đã thực hiện trên máy

- Bỏ hệ số `[cartographer coil] calibration`; xác nhận cả file trên đĩa và `configfile.settings` live không còn calibration. Không có cảnh báo lỗi khối SAVE_CONFIG.
- Chạy `CARTOGRAPHER_SCAN_CALIBRATE` lúc 16:45:25, lưu model lúc 16:46:36 và `SAVE_CONFIG` lúc 16:47:02. Live model scan mới có `reference_temperature=-8.53`, `software_version=1.10.1`; bộ coefficients/domain khác Git.
- Hiệu chuẩn Touch đạt threshold **1504**, speed **2**, verification 10 mẫu có range **0,006000 mm**; lưu bằng `SAVE_CONFIG` lúc 17:04:01.
- Người vận hành tăng `[quad_gantry_level] retries` từ **5** lên **10** trên máy. Đây là số vòng QGL thử lại; `cartographer scan samples` live vẫn **20**. Không sửa đè các thay đổi live này từ Git.
- Sau hiệu chuẩn scan, QGL có lượt đạt **0,005785 mm lúc 16:50:07** và **0,005141 mm lúc 16:53:15**. Lượt thủ công sau SAVE_CONFIG lúc 17:04 có bed target=0, bàn đang nguội, abort ở retry 6 vì range tăng 0,008532 → 0,015332 → 0,024449 mm.
- Trong PRINT_START của `[a]_belt_tensioner_x2+1mm_ABS_26m52s.gcode`, bàn giữ target **105°C**; QGL đạt **0,005290 mm ở retry 7/10 lúc 17:09:34**. Touch hoàn tất lúc 17:10:07; mesh hoàn tất và job chuyển sang pha `printing` bằng T2 khoảng 17:10:46. Active/detected T2 khớp, không pause. Không tuyên bố chất lượng lớp đầu đạt chỉ từ trạng thái này.

## 3. Chuẩn bị 200 mẫu mỗi điểm, chờ in xong để cài

- Theo yêu cầu người dùng, thêm `[cartographer scan] samples: 200` vào `config/Printer-Setup/calibration-probe.cfg`; giá trị trước đó là mặc định **20**. Giữ nguyên phần còn lại, không sửa Python, QGL tolerance, retries, model hoặc heater.
- Backup trước sửa: `extras/backups/pre-cartographer-samples-20261030-171001/`, gồm probe config Git/live, printer.cfg live, print-macros.cfg live và README. Probe config Git và live khớp sau chuẩn hóa newline trước sửa.
- ConfigParser đọc được section mới, samples=200, không trùng section; `git diff --check` đạt. Chưa triển khai/restart vì job hiện tại đã qua QGL và đang in.
- Người dùng yêu cầu rõ **cài sau khi in xong**. Đã tạo heartbeat `c-i-cartographer-200-m-u-sau-khi-in-xong`, kiểm tra mỗi 5 phút, giữ yên khi job chưa kết thúc; khi job complete và máy thực sự idle sẽ backup lại, chỉ sửa probe config live, RESTART một lần rồi xác nhận samples=200 và giữ nguyên model scan/touch mới, trạng thái không bù nhiệt. Không tự home, QGL hoặc chạy lại bản in sau khi cài.
- Chưa xác minh trên máy với 200 mẫu. Cần cập nhật mục này sau triển khai; việc bật Klipper ready không chứng minh QGL đã hội tụ. Không triển khai nguyên config vì model/retries live và giới hạn bàn nhiệt còn khác Git.
