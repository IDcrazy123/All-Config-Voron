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

## 4. Kiểm tra T2 báo hết nhựa sai khi vẫn còn sợi

- Người dùng xác nhận còn nhựa tại lúc T2 báo runout. Log hiện tại ghi sự kiện cảm biến lúc **17:25:15**, handler xác nhận/pause lúc **17:25:17**. Sự kiện thứ hai lúc **17:29:01** tự hồi và được lọc lúc **17:29:03**. Không thấy sự kiện runout thật trong log ngày 29/10 được kiểm tra; không tính các dòng cấu hình dump là sự kiện.
- Lúc **17:29:03**, console có `SET_FILAMENT_SENSOR SENSOR=filament_sensor_T2 ENABLE=0`. Đối chiếu API: T2 đang `filament_detected=true`, `enabled=false`; job đã tiếp tục in, không pause. Không tự bật lại cảm biến hoặc sửa job đang chạy.
- Live T2 dùng `switch_pin: ^EBB2:PB8`, `event_delay: 0.5`, `pause_delay: 0.5`; runout gọi delayed_gcode sau 0,5 giây rồi kiểm tra trạng thái một lần. Giữ nguyên pin/polarity vì chưa có phép kiểm tra vật lý chứng minh cần đổi.
- Đọc trực tiếp Python Klipper đang cài: `filament_switch_sensor.py` cập nhật trạng thái ngay, `event_delay` chỉ hạn chế sự kiện; nhánh insert_gcode chỉ chạy khi idle_timeout không ở Printing. Vì vậy hook insert hủy delayed_gcode không bảo đảm hoạt động trong lúc in. Không kết luận tín hiệu đã mất liên tục 2 giây chỉ từ hai mốc log.
- `buttons.py` có `DebounceButton` và tham số `debounce_delay` mặc định 0. Phương án nhắm riêng T2 là thêm **debounce_delay: 0.5**, yêu cầu input ổn định trước khi báo sang runout helper, vẫn giữ delayed confirmation và kiểm tra tool active. Chưa sửa CFG hay triển khai phương án này trong tác vụ kiểm tra.
- Replay độc lập đúng class đang cài với reactor giả lập: xung ngắn và chuỗi chập chờn bị bỏ, mất nhựa liên tục vẫn phát sự kiện; 3 trường hợp đạt. Không sửa runtime Python và không điều khiển máy để thử cơ khí.
- Còn cần kiểm tra cơ cấu tác động của sợi vào cảm biến, lực PTFE, gá, giắc và dây SIG/GND khi máy idle. Log chưa phân biệt được lỗi cơ cấu với lỗi dây/điện. Bộ lọc phần mềm không sửa được input sai kéo dài. Tắt sensor chỉ là trạng thái phiên; RESTART thường bật lại mặc định.

## 5. Cài samples=200 sau khi bản in hoàn tất

- Heartbeat khoảng **17:38** xác nhận đúng file `[a]_belt_tensioner_x2+1mm_ABS_26m52s.gcode` chuyển sang `complete`, idle_timeout=Ready, `_PRINT_STATE=idle`, không pause/recovery/drying, toolchanger ready và active/detected đều rỗng; không còn chuyển động chờ. Không hủy hoặc can thiệp lúc job đang chạy.
- Đọc lại toàn bộ hướng dẫn hiện hành, config live và file trên đĩa. Backup mới tại `extras/backups/pre-live-cartographer-samples-20261030-174004/`, có probe config, printer.cfg, print-macros.cfg, T2.cfg và snapshot trạng thái trước/sau. Backup trên máy: `/home/voron/printer_data/config_backups/pre-cartographer-samples-20261030-174004/`.
- Chỉ thêm `[cartographer scan] samples: 200` vào file live `Printer-Setup/calibration-probe.cfg`; trước đó dùng mặc định **20**. Diff đúng bốn dòng đã review, ConfigParser đọc được và nội dung chuẩn hóa khớp bản đã commit. Recheck idle/hash trước ghi atomic và trước reload. Không chạy install.sh hoặc triển khai nguyên config.
- Một lần chuẩn bị script bị lỗi cú pháp trước khi thực thi nên chưa ghi file/chưa gửi RESTART; đã sửa và compile script trước lần thực thi thành công. Chỉ gửi **một RESTART** lên máy.
- Xác minh lúc **17:41:18**: Klipper **ready**, `configfile.settings['cartographer scan'].samples=200`, không cảnh báo config. So toàn bộ settings trước/sau chỉ khác samples 20→200. Model scan mới, Touch threshold=1504, trạng thái không bù nhiệt coil, QGL retries=10 và mọi setting còn lại giữ nguyên.
- SHA256 probe config sau triển khai: `69ca73536dccbc1e0567351fbb8af0a10f903f253659878c0e8cfd7a6f5a7977`; hash `printer.cfg`, `print-macros.cfg` và `T2.cfg` không đổi. Không sửa runtime Python.
- Không chạy G28/QGL/Touch hoặc khởi động bản in khác sau reload; chưa xác minh cơ khí với 200 mẫu. Trạng thái homed_axes rỗng sau RESTART là dự kiến. T2 tự bật lại mặc định (`enabled=true`, `filament_detected=true`); không áp dụng phương án debounce T2 trong lần cài này.
- Đã hoàn tất yêu cầu cài sau khi in xong; xóa heartbeat một lần để không tiếp tục polling/reload.
