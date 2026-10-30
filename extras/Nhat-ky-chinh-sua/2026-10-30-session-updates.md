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

## 6. Thử nghiệm QGL ở điều kiện ABS và PETG

- Người dùng xác nhận bàn sạch/không vướng và yêu cầu thử nhiệt. Đợi QGL thủ công đang chạy kết thúc; kiểm tra standby, không pause/recovery/drying, không chuyển động chờ rồi mới home/lấy T0. Mô phỏng riêng giai đoạn QGL trước in: T0=150°C, quạt bàn 50%, không chạy chu trình đùn/vệ sinh/Touch/mesh.
- Giữ samples=200, không bù nhiệt coil, retries=10 và tolerance=0,0075 mm. Không sửa CFG hoặc Python trong thử nghiệm.
- ABS 100°C sau soak ban đầu 90 giây: **3/3 đạt**, range cuối **0,007445 / 0,007069 / 0,005980 mm**, retry **8 / 6 / 3**. ABS 105°C sau soak ban đầu 90 giây: **3/3 đạt**, **0,004011 / 0,006525 / 0,005040 mm**, retry **6 / 4 / 3**.
- PETG target 70°C theo profile trong repo, soak ban đầu 60 giây: ba lượt đạt **0,001506 / 0,005967 / 0,004392 mm**, retry **2 / 3 / 1**. Lượt đầu thực tế còn **71,89–74,83°C**, vì nhiệt tăng lại sau khi chạm dải; giữ riêng là kết quả chuyển tiếp, không gọi là thử 70°C ổn định.
- Bổ sung một lượt PETG kiểm chứng sau khi bàn liên tục nằm trong 69–71°C và nozzle trong 148–152°C đủ **60,9 giây**: đạt **0,007201 mm**, retry **3**; bàn **69,80–69,92°C** trong lúc QGL. Tổng **10/10 lệnh QGL** hội tụ; một số lượt rất sát ngưỡng và cần nhiều retry, chưa chứng minh đã hết lỗi cảm biến hoặc khởi động lạnh ổn định.
- Trong pha nguội 105→70°C, ghi đoạn nhiệt bàn giảm về khoảng 75°C rồi tăng gần 80°C, kèm xung PWM ngắn. Chưa tách được đáp ứng nhiệt/PID khỏi bất thường NTC. Không sửa/nới PID, verify_heater hoặc smoothing. Khuyến nghị đợi nhiệt ổn định liên tục trước khi tính soak, thay vì chỉ đợi chạm dải một lần.
- Sau kiểm chứng cuối: tắt mọi heater và quạt bàn; xác nhận Ready/standby, không pause, QGL applied=true, T0 active/detected khớp ở X174 Y168 Z10. Toàn bộ configfile.settings trước/sau giống nhau. Không khởi động bản in khác.
- Báo cáo và dữ liệu bền vững: `extras/docs/qgl-thermal-trial-2026-10-30.md`, CSV tóm tắt và JSON các bước retry cùng tên. Telemetry mỗi khoảng 2 giây và G-code thô ở thư mục TEMP `voron-qgl-thermal-trial-20261030`.

## 7. QGL sau đổi T0/T2 và nâng/hạ Z; dừng vì tín hiệu nhiệt bàn

- Theo yêu cầu mới, trước **mỗi QGL** chạy ba vòng T0→T2→T0, xác nhận active/detected sau từng lần, rồi ba chu kỳ Z20→Z200→Z20 ở 25 mm/s. Đo PROBE ba lần ở tâm và bốn góc trước chuyển động; đo lại tâm rồi QGL ngay, không home Z/Touch giữa các phép đo trước/sau. Dự kiến hai lượt PETG 70°C, hai lượt ABS 100°C và hai lượt ABS 105°C; soak ổn định liên tục 60/90 giây trước từng lượt. T0/T2=150°C, quạt bàn 50%.
- Hoàn tất PETG **2/2 đạt**: lúc 18:41:12 range QGL 0,106030→0,002764 mm, retry 3; lúc 18:46:20 0,034246→0,005048 mm, retry 1. Nhiệt bàn trong QGL lần lượt 70,02–70,08°C và 69,94–70,05°C. Tổng **12 lần đổi tool không lỗi xác thực**, sáu chu kỳ Z. Giữ samples=200, tolerance=0,0075 mm và retries=10.
- ΔZ đo ở tâm sau−trước là **−0,038139 / −0,173363 mm**; range ba PROBE liên tiếp trước/sau khoảng **0,010838–0,027926 mm**. Dịch chung bốn góc **−0,0039705 / −0,1257743 mm**, max−min bốn độ dịch **0,051549 / 0,019850 mm**. Không kết luận mất bước/trượt belt từ phép đo chứa cả drift đầu dò và nhiệt. Probe gắn trên shuttle nên chưa đo được độ lặp Z nozzle T0/T2.
- Khi tăng target bàn 70→100°C, chưa bắt đầu đo nền/đổi tool ABS, bộ giám sát phát hiện **76,59→89,22°C trong 2,259 giây**, chủ động gửi emergency_stop lúc **18:47:40 theo đồng hồ client**. Log Klipper còn ghi **85,6→65,5→86,4°C trong hai giây** và **68,9→101,0°C trong một giây**. Đường đo NTC bàn tiếp tục lỗi; không coi đây là biến thiên nhiệt thật hoặc lỗi QGL/coil Cartographer.
- Máy **shutdown do webhooks request** từ bộ thử nghiệm. API xác nhận power=0 ở bàn và cả năm extruder; target vẫn giữ 100/150°C. TURN_OFF_HEATERS/BED_FAN_OFF bị từ chối sau shutdown, quạt còn hiển thị 0,5; không tuyên bố dọn dẹp bằng G-code đã thành công hoặc đo xác nhận SSR vật lý. T0 vẫn detected, toolchanger trở về uninitialized sau shutdown. Không restart, không tự gắp lại, không cấp nhiệt/chạy thử tiếp.
- Phần ABS 100/105°C của bài chuyển động **chưa thực hiện**. Cần ngắt điện lưới/chờ nguội, kiểm tra NTC bàn, dây/crimp/giắc PB0 và nhiễu/đường dây AC, đo điện trở khi uốn nhẹ dây để khoanh vùng trước khi thử nhiệt lại. Không sửa/nới PID, verify_heater hoặc smoothing.
- Đối chiếu toàn bộ configfile.settings trước/sau khớp; hash probe config vẫn `69ca73536dccbc1e0567351fbb8af0a10f903f253659878c0e8cfd7a6f5a7977`. Không sửa bất kỳ CFG, model, offsets hay runtime Python. Cập nhật KNOWN_ISSUES theo lỗi tái diễn và giới hạn của phép đo.
- Báo cáo: `extras/docs/qgl-motion-trial-2026-10-30.md`; CSV/JSON kết quả và CSV log nhiệt bàn cùng tiền tố. Dữ liệu thô tại TEMP `voron-qgl-motion-trial-20261030`. Mốc giờ báo cáo là client UTC+07; dữ liệu lỗi nhiệt dùng Klipper monotonic để tránh trộn hai đồng hồ.

## 8. Reset theo yêu cầu sau khi dừng thử nhiệt

- Người dùng yêu cầu reset để thử hoàn chỉnh trước, sửa NTC sau. Đã thực hiện phần reset: kiểm tra standby, không pause/recovery/drying, không chuyển động chờ, T0 detected, heater power=0; đọc delayed_gcode startup chỉ có LED, không tự bật heater hoặc di chuyển. Gửi **một FIRMWARE_RESTART**.
- Xác nhận **18:52:17 UTC+07** Klipper **Ready**, target=0/power=0 ở bàn và cả năm extruder, T0 detected; homed_axes rỗng sau reset là dự kiến. Toàn bộ configfile.settings vẫn khớp trước thử; samples=200/model/coil compensation/retries không đổi.
- Không home/di chuyển/cấp nhiệt sau reset. Chưa tiếp tục phần ABS 100/105°C: phản hồi NTC đã sai rõ ràng, có thể khiến điều khiển bàn 1000 W cấp sai công suất; reset không sửa đường đo. Cần xử lý đường NTC trước khi tiếp tục thử nhiệt. Snapshot sau shutdown được giữ làm bằng chứng và bổ sung snapshot sau reset vào JSON báo cáo.

## 9. Đối chiếu log và theo dõi nhiệt trong bản in hiện tại

- Người dùng yêu cầu xác minh lỗi nhiệt khi đang in, khoanh vùng NTC/SSR/nhiễu và khả năng dùng tụ 104. Đọc lại AGENTS.md, live/config, lịch sử Moonraker, console, G-code và log mới; máy đang in `ZAssembly_ABS_1h13m.gcode`. Tác vụ chỉ đọc, không pause/cancel/restart, đổi nhiệt/quạt, đổi tool hoặc sửa CFG/Python.
- Tách PRINT_START khỏi in thực tế: bản mới vào G-code chi tiết khoảng 19:22:10. Target 105→100°C lúc 19:24:52 khớp G-code M140 S100, không phải tự nó là nhiễu. Belt trước đó cũng đổi target 105→100°C lúc 17:13:01. Lỗi T2 pause được tách khỏi pha in/chạy tiếp.
- Khởi động belt 17:08:43–45 có 100,7→79,8→116,4°C trong khoảng hai giây, target 105°C. Khi đã in, có nấc nhỏ **99,8→101,5°C lúc 17:20:51**; bản mới có **99,2→101,1°C lúc 19:28:29** và **100,3→102,4°C lúc 19:28:54**, target 100°C. Không thấy bước ≥3°C giữa mẫu liền nhau trong các đoạn đang in đã kiểm tra; không gọi là hết lỗi.
- Theo dõi thụ động **19:45:07–19:55:07 theo client UTC+07**: 600 GET API, không lỗi đọc; printing/T0 suốt cửa sổ, XYZ thay đổi. API bàn **99,91–100,12°C**, target 100°C; PWM bàn **22,1–32,4%**, nozzle **0–60,3%**, quạt chi tiết **9,8–80%**, quạt bàn 50%. Đối chiếu **599 Stats thô** đúng boot và cửa sổ monotonic: bàn **99,9–100,1°C**, bước lớn nhất **0,1°C**; khoảng mẫu tối đa 1,1 giây. Không tái hiện lỗi lớn trong 10 phút này.
- Đọc heaters.py đang cài: Stats dùng last_temp, API dùng smoothed_temp; live smooth_time=3 giây. Không dùng riêng biểu đồ làm mượt để loại trừ xung. Khi lọc theo monotonic phải kèm boot/epoch vì cùng số monotonic có thể lặp sau reboot; dữ liệu xuất đã kiểm tra đúng boot, không trộn phiên sáng/chiều.
- Bàn nhảy 79,8→116,4°C nhưng buồng PB1 vẫn 46,2°C; bàn 68,9→101°C nhưng buồng 43,8→43,7°C. Ưu tiên nhánh NTC bàn/dây/giắc/TH0-PB0 hoặc nhiễu riêng nhánh này; chưa phân biệt linh kiện. PWM là lệnh điều khiển, không đo dòng SSR và không đủ xác định chiều nhân quả. Người dùng xác nhận giữ mạch, dây bàn và SSR khi nâng StealthChanger; không giả định đã đi lại dây/thay SSR.
- Đọc trực quan pinout người dùng gửi và trang 4 schematic BTT: TH0/PB0 là cảm biến bàn live, THB/PB1 là buồng. TH0 đã có R55=4,7 kΩ, R56/R57 mỗi con 2,37 kΩ, C34=0,1 µF (104) phía ADC. Thêm tụ tại giắc có thể thêm lọc nhanh nhưng chưa là sửa lỗi; không sửa tiếp xúc/NTC hỏng hoặc lỗi chậm. Không hàn/thêm tụ hay đổi smoothing; không dùng tụ 104 thường cho phía AC/SSR.
- Phép phân biệt còn thiếu: sau in và ngắt điện/chờ nguội, kiểm tra điện trở/dây/giắc; đối chứng NTC tốt hoặc điện trở chuẩn dây ngắn tại TH0 với **heater vô hiệu**, rồi đánh giá nhánh ADC/nguồn-GND nếu vẫn lỗi. Không thử điện trở giả rồi chạy heater; không thử phần cứng trong bản in này.
- Live đầu tác vụ hiện **samples=20**, khác snapshot triển khai 200; model scan/Touch và không bù nhiệt giữ nguyên. Repo probe file vẫn 200, không tự đồng bộ. QGL 19:18 abort 0,075379→0,076728→0,092545 mm trong khi bàn 104,7–105,3°C; QGL sau đạt 0,006676 mm retry 2 lúc 19:21:08, bàn 104,9–105°C. Cả hai bỏ heat soak. Chưa thể quy lần abort này trực tiếp cho NTC hoặc dùng làm đối chứng 20/200.
- Báo cáo/dữ liệu: `extras/docs/bed-temperature-review-2026-10-30.md`, CSV log, CSV 600 mẫu theo dõi, JSON thống kê và Stats thô. Cập nhật KNOWN_ISSUES; dữ liệu thô tại TEMP `voron-bed-log-review-20261030-1924`.
- Cuối tác vụ xác nhận job **completed lúc 20:28:28**. Đọc bổ sung toàn bộ pha in gia nhiệt **19:22:11–20:28:10**, **3.956 Stats** cách nhau tối đa 1,1 giây: không có bước ≥3°C, lớn nhất 2,1°C. Chỉ ba nấc ≥0,8°C tập trung **19:27:58 / 19:28:29 / 19:28:54**, lần lượt 0,9/1,9/2,1°C. Target bàn được PRINT_END đưa về 0 lúc 20:28:11; snapshot cuối Ready, job complete, target/PWM bàn 0. Đã bổ sung CSV/JSON/báo cáo với cả bản in, không chỉ cửa sổ 10 phút. Settings đầu/cuối tác vụ khớp; không có can thiệp job.
