# 2026-11-22 — Đo lại LDC1612 sau QGL nóng không hội tụ

## Trạng thái live trước phép thử

- Người vận hành dừng bản in và xác nhận đứng cạnh máy để quan sát. Moonraker/Klipper `ready`, `print_stats=standby`; sau `INITIALIZE_TOOLCHANGER`, T0 active/detected. Không dùng bản CFG tồn dư ở workspace cha.
- Cấu hình live khác Git: QGL tinh đang dùng `METHOD=scan HORIZONTAL_MOVE_Z=2`, `retry_tolerance=0.01`, `retries=20`, `max_adjust=20`; Git dùng phương pháp mặc định, Z10, 0.0075, 10, 10. Live `tap_z_offset=-0.1`, Git `+0.1`. Không ghi đè các thay đổi live này trong lượt thử.
- Live và Git trước thử đều có `reg_drive_current=17`, bảng Z 101 điểm, `calibration_temp=46.683760`; thermal compensation đang tắt. Bản sao trước thử nằm tại `extras/backups/pre-ldc1612-full-recal-20261122/`.

## Thử dòng kích theo Klipper

- Sau `INITIALIZE_TOOLCHANGER`, `G28` thành công. Đặt sensor giữa bàn X174 Y168 Z20, chạy `LDC_CALIBRATE_DRIVE_CURRENT CHIP=ldc1612_eddy_coil` hai lần. Ở bàn khoảng 90°C/tắt heater/cuộn 64°C và bàn 100°C/vòi 150°C/cuộn 64°C, cả hai lần đều trả `reg_drive_current: 19`.
- Đã `SAVE_CONFIG` 19; Klipper restart `ready`, không warning cấu hình. Git `config/printer.cfg` đồng bộ riêng giá trị dòng kích này. Bảng Z cũ vẫn là kết quả đo với dòng 17, do đó chưa được xác nhận với dòng 19.

## Đo đứng yên với dòng 19

Tại X174 Y168 Z2, bàn/vòi quanh 100/150°C, không ra lệnh trục trong các cửa sổ 12 giây; mỗi cửa sổ khoảng 4.824 mẫu từ `ldc1612/dump_ldc1612`:

| Trạng thái bàn | Cuộn gần cửa sổ | Z trung bình theo bảng cũ | Std Z sau bỏ xu hướng | Xu hướng Z |
| --- | ---: | ---: | ---: | ---: |
| PID 100°C | khoảng 66–67°C | 2.801 mm | 0.00864 mm | −0.00954 mm/s |
| Tắt, bàn bắt đầu nguội | khoảng 67–68°C | 2.796 mm | 0.01618 mm | −0.00546 mm/s |
| PID 100°C bật lại | khoảng 68–69°C | 2.850 mm | 0.01209 mm | −0.00514 mm/s |
| PID 100°C sau khoảng 7 phút | khoảng 75°C | 3.105 mm | 0.00732 mm | −0.00697 mm/s |

- Cờ `Amplitude Low/High` tăng gần một lần trên mỗi mẫu. Tại cùng tọa độ máy Z2, bảng cũ trả Z2.8–3.1; đây không phải tọa độ thực của đầu phun vì đã đổi dòng và cuộn còn tăng nhiệt. Không dùng các số này để sửa Z cơ khí.
- Đối chứng bật/tắt/bật lần này **không tái lập kết quả giảm nhiễu khi tắt bàn** của phép thử trước với dòng 17. Trạng thái nhiệt thay đổi trong mỗi cửa sổ, nên chưa kết luận SSR là nguồn nhiễu điện. Xu hướng theo thời gian và độ phân tán đứng yên đều lớn so với tolerance QGL 0.01 mm, đủ giải thích vòng tinh đổi dấu/tăng dải khi dò bốn góc lần lượt.
- Một luồng thô khác có 11.988 mẫu/30 giây ở dòng 19, bàn/vòi 100/150°C, cuộn tăng khoảng 69,31→70,07°C, lưu tại `extras/diagnostics/2026-11-22-qgl/ldc-warming-drive19.csv`. Tại điểm cố định, Z theo bảng cũ có khoảng 5–95% là 2,825–2,946 mm; 11.988/11.988 mẫu bị tăng bộ đếm lỗi biên độ. Phân tích FFT đơn giản sau bỏ đường thẳng cho thấy khoảng 97,9% năng lượng biến thiên tần số nằm dưới 0,5 Hz; dải quanh 10 Hz chỉ khoảng 0,023% và 50–150 Hz khoảng 0,7%. Điều này ủng hộ biến thiên chậm là thành phần chính của sai số QGL; chưa chứng minh nguồn điện cụ thể.
- Sau đo đã nâng lên Z20, tắt bàn và vòi; `print_stats=standby`. Chưa chạy lại QGL hoặc tap với bảng Z cũ. Bước tiếp theo là hiệu chuẩn Z mới bằng paper test khi trạng thái nhiệt được chọn và ổn định, sau đó so scan/default QGL. Không dùng `SAVE_CONFIG` cho bảng Z/tap cũ như thể chúng đã được xác minh.

## Đối chứng nhanh khi nhiệt cuộn gần ổn định

- Theo lựa chọn của người vận hành, ưu tiên bàn/vòi 100/150°C. Giữ sensor tại X174 Y168 Z2 đến khi cuộn quanh 74,6°C. Đo liên tục 30 giây, đổi target bàn bật→tắt→bật→tắt→bật mỗi 6 giây. Cuộn giữ 74,63–74,69°C ở các mốc chuyển pha; bàn từ khoảng 99,98 xuống 99,50°C. Dữ liệu thô tại `extras/diagnostics/2026-11-22-qgl/ldc-pwm-phase-drive19.csv`.
- Std Z sau bỏ đường thẳng theo năm pha, cắt 0,5 giây ở mỗi đầu: bật 0,00264, tắt 0,00478, bật 0,00270, tắt 0,00204, bật 0,00644 mm. Không có thay đổi nhất quán theo PWM; chỉ riêng tắt SSR không giải thích hay chữa được trôi QGL. Tín hiệu vẫn dịch đáng kể theo thời gian ở điểm đứng yên dù nhiệt cuộn gần ổn định. Chưa tách được chuyển động cơ học của bàn/gantry khỏi drift của bo/cuộn.

## Hiệu chuẩn bảng Z nóng mới

- Người vận hành xác nhận vòi và bàn sạch, dùng giấy để chọn mốc có thể đẩy/kéo; bước thấp hơn chỉ rút được giấy. Khi bắt đầu manual probe ở Z2, trợ lý gửi một `TESTZ Z=-1` và log ghi hai bước xuống Z1 rồi Z0 vì người vận hành cũng đang dùng `TESTZ` trên giao diện. Trợ lý dừng gửi lệnh ngay khi thấy Z0. Sau đó người vận hành tự tinh chỉnh và `ACCEPT` ở Z khoảng 0,250 mm; không có lệnh chuyển động từ trợ lý trong giai đoạn tinh chỉnh này.
- `PROBE_EDDY_CURRENT_CALIBRATE CHIP=ldc1612_eddy_coil` hoàn tất 101 điểm. Klipper báo `noise 0.000897mm`, `MAD_Hz=69.271` trên 4.039 query, dải tần 335006.221 Hz; nhiệt hiệu chuẩn ghi `73.565570°C`. Đã `SAVE_CONFIG`, bảng Z và nhiệt mới được đồng bộ riêng vào Git, không ghi đè live T2 offset, tap offset hay QGL macro đang khác Git.
- Host `SAVE_CONFIG` ghi file lúc 17:47:02 rồi restart. Sau restart, EBB0 ở trạng thái shutdown nên Klipper báo `Can not update MCU 'EBB0' config`; log trước restart không có dòng lỗi EBB0, CAN counters cuối vẫn 0. Heater đã tắt, không có chuyển động. Một `FIRMWARE_RESTART` đưa Klipper về `ready`, không warning; XYZ chưa home. Nguyên nhân EBB0 giữ trạng thái shutdown chưa được chứng minh và cần theo dõi.
- Sau nạp bảng mới, đã gia nhiệt lại 100/150°C, `INITIALIZE_TOOLCHANGER`, `G28` thành công. Lúc G28 cuộn khoảng 69°C, thấp hơn mốc 73,6°C. Tại X174 Y168 Z2, luồng 12 giây lúc cuộn khoảng 69°C vẫn trôi −0,00569 mm/s, std sau bỏ đường thẳng 0,00864 mm; lỗi biên độ 4.437/4.824 mẫu. Chờ cuộn trở lại khoảng nhiệt hiệu chuẩn để kiểm tra QGL cùng điều kiện.

## Kiểm tra sau hiệu chuẩn và điểm chặn hiện tại

- Tại X174 Y168 Z2 sau G28 mới, cuộn ổn định quanh 70,7°C, bàn/vòi 100/150°C. Luồng 12 giây vẫn trôi `-0.005127 mm/s`, std sau bỏ xu hướng `0.002602 mm`, dải 5–95% `1.980837–2.033431 mm` (rộng 0,052594 mm); 4.752/4.824 mẫu có cờ biên độ. Điều này cho thấy mô hình Z mới cho nhiễu ngắn tại từng điểm nhỏ nhưng **không loại bỏ được biến thiên chậm giữa các điểm QGL**. Nhiệt cuộn lúc vận hành này thấp hơn nhiệt hiệu chuẩn khoảng 2,9°C vì sau `SAVE_CONFIG` máy đã G28 lại và hình học Z ở cùng tọa độ lệnh thay đổi.
- Gửi một lượt `QUAD_GANTRY_LEVEL` live lúc 100°C/150°C, T0 active/detected, XYZ homed, cuộn khoảng 70,7°C. Main MCU shutdown `Missed scheduling of next digital out event` khoảng 10,6 giây sau lệnh, trước khi log có bất kỳ dòng `Gantry-relative probe points` hoặc `Retries`. Lượt này **không có kết quả hội tụ** và không thể dùng để so scan với default. Stats trước lỗi: bàn 100,0°C/PWM khoảng 0,259; cuộn 70,3°C; CAN rx/tx errors và retransmits đều 0; `mcu_awake` tăng từ 0,002 lên 0,892 khi QGL/đọc LDC hoạt động; bulk sensor `possible_overflows=0`. Chưa xác định output OID hay linh kiện gây trễ lịch cụ thể. Không tự reset rồi lặp QGL nóng khi lỗi này còn mở.
- Ngay sau shutdown, heater outputs bằng 0 nhưng target status còn 100/150°C, QGL false. Vị trí báo X330 Y280 Z-5 trong trạng thái shutdown không được coi là vị trí cơ khí chắc chắn. Trợ lý không gửi thêm lệnh chuyển động/gia nhiệt/reset để lặp QGL.
- Kiểm tra live sau đó khoảng 18:03: Klipper đã trở lại `ready` từ thao tác ngoài lượt lệnh của trợ lý; heater target 0, `print_stats=standby`, XYZ chưa home, QGL chưa applied, T0 được nhận diện nhưng toolchanger `uninitialized`. Việc reset thành công không chứng minh lỗi digital output đã hết; không tự lặp hot QGL.
- Người vận hành không có đồng hồ so hay cảm biến khoảng cách độc lập. Vì vậy các phép đo đứng yên hiện tại không thể tách chắc chắn chuyển động vật lý bàn/gantry khỏi drift điện/nhiệt của cảm biến. Trước khi quy hỏng bo/cuộn hoặc một Z stepper, cần phép đo độc lập hoặc kiểm tra phần cứng có kiểm soát sau khi xử lý lỗi MCU.

## Tài liệu

- [Klipper Eddy Probe](https://www.klipper3d.org/Eddy_Probe.html): thứ tự dòng kích → bảng Z → tap; phương pháp mặc định được khuyên dùng cho QGL; hiệu chuẩn và dò nên ở trạng thái nhiệt nhất quán.

## Kiểm tra PF2 và đối chứng trôi sau đó

- Lệnh người vận hành gửi `CALIBRATE_ALL_Z_OFFSETS` bị `Error evaluating ... CALIBRATE_COARSE_Z_OFFSETS` với yêu cầu `CONFIRM=1`. Live CFG cho thấy `CALIBRATE_ALL_Z_OFFSETS` là alias của macro PF2 và guard này chủ ý yêu cầu thử công tắc trước khi di chuyển; không có bằng chứng lỗi do đổi LDC1612. `QUERY_ENDSTOPS` khi nhấn PF2 trả `Axiscope:TRIGGERED`, khi nhả trả `Axiscope:open`.
- Ban đầu live XYZ đã home, QGL applied, T0 được nhận diện nhưng toolchanger `uninitialized`. `INITIALIZE_TOOLCHANGER` đưa T0 active/detected, không làm máy di chuyển. `CALIBRATE_MOVE_OVER_PROBE` tới X81 Y−7 Z15, `MOVE_TO_ZSWITCH` tới Z4. Năm lần chạm T0 lúc vòi khoảng 50°C ở Z1,934039–1,946039 mm, trung bình 1,941239 mm.
- Chạy `CALIBRATE_ALL_Z_OFFSETS CONFIRM=1` với người vận hành quan sát. T0 nóng 150°C chạm Z1,970–1,992 mm, trung bình 1,9848. T1 chạm Z1,622–1,648 mm, offset tương đối −0,3440. T2 chạm Z1,700–1,720 mm, offset −0,2720. Live T2 đang −0,2703; chênh 0,0017 mm quá nhỏ cho một chỉnh sửa sơ bộ, nên không sửa offset. Người vận hành ưu tiên T0 và T2.
- Khi gắp T3, log ghi `No tool detected` và `Expected tool tool T3 but active is None`. Người vận hành quan sát T3 vẫn nằm trong dock và nói vị trí hơi sai; không sửa tọa độ dock khi chưa đo. Chuỗi dừng trước T4. Đã `TURN_OFF_HEATERS` (mọi target 0), phục hồi `_PRINT_STATE=idle`, bật lại `START_CRASH_DETECTION`, xác nhận shuttle rỗng rồi `INITIALIZE_TOOLCHANGER` và gắp T0 thành công. Không coi lượt batch là hiệu chuẩn đầy đủ năm đầu.
- QGL thành công gần nhất sau bảng LDC mới đạt 0,008977 mm ở lần chỉnh thứ ba, nhưng log lúc đó cho thấy bàn nguội 67,4→66,8°C, target/PWM 0 và vòi khoảng 51°C, target 0. Nó chưa xác minh hội tụ ở điều kiện ưu tiên 100/150°C.
- Tại tâm X174 Y168 Z2, heater đều tắt, dùng cùng stream `ldc1612/dump_ldc1612` 12 giây, 4.824 mẫu mỗi lượt. Lượt đầu khi cuộn vừa tiếp cận bàn: trôi −0,005630 mm/s, std sau bỏ xu hướng 0,003190 mm, dải 5–95% 0,063099 mm. Lượt sau khi cuộn tăng 46,267→46,358°C: trôi −0,004766 mm/s, std 0,001649 mm, dải 0,048470 mm. Lượt thứ ba khi cuộn gần ổn nhiệt 46,495→46,519°C: trôi −0,005385 mm/s, std 0,004635 mm, dải 0,060654 mm; bàn giảm 52,74→52,59°C. Như vậy tốc độ trôi không biến mất khi heater tắt và nhiệt cuộn gần như đứng yên. Điều kiện lúc đo khác nhiệt hiệu chuẩn 73,566°C; giá trị Z tuyệt đối của stream không phải số đo nozzle chính xác.
- Người vận hành xác nhận giá PF2 bắt vào **khung cố định**. Dùng PF2 làm mốc cơ khí độc lập cho gantry so với khung, không đo trực tiếp mặt bàn. T0 nguội chạm năm lần: trung bình Z1,9160; sau khoảng 52 giây Z1,9316; thêm khoảng 52 giây Z1,9340, năm mẫu cuối đều 1,9340. Sau khi công tắc ổn định, thay đổi +0,0024 mm/52 giây nhỏ hơn nhiều biến thiên LDC ~0,005 mm/s. Điều này loại trừ gantry Z tự trôi đủ lớn làm nguyên nhân duy nhất. PF2 không tách được dịch chuyển riêng của bàn khỏi drift điện/nhiệt của đầu LDC; chưa quy hỏng bo/cuộn. Không có đồng hồ so hoặc máy đo sóng; chỉ có đồng hồ vạn năng.
- Đối chứng thêm với giấy ở tâm bàn khi bàn/vòi khoảng 47/43°C và heater tắt: người vận hành tự chỉnh từ Z0,3 qua Z−0,3 rồi trả về Z−0,2, xác nhận giấy có thể đẩy/kéo ở Z−0,2 và rít khi xuống thêm. Giữ nguyên Z−0,2 trong cửa sổ 12 giây, người vận hành nhận thấy lực kéo gần như không đổi. LDC trả model Z=`−99,9` vì tần số vượt đầu dải bảng Z (khoảng 11,85 MHz so với 11,799 MHz ở đầu dải), nên **không** dùng model Z ở vị trí này; tần số thô vẫn có xu hướng +303,3 Hz/s trong 4.824 mẫu, 12,06 giây. Dữ liệu thô: `extras/diagnostics/2026-11-22-qgl/ldc-paper-drag-20261122.csv`. Giấy là kiểm tra cảm giác, chưa đủ phân biệt dịch chuyển bàn mức vài chục µm với trôi cảm biến. Sau đó nâng T0 lên Z20.
- Cuối lượt Klipper `ready`, `print_stats=standby`, `_PRINT_STATE=idle`, XYZ homed, QGL applied, T0 active/detected, X174 Y168 Z20, mọi heater target 0, không warning cấu hình. Giá PF2 vẫn lắp theo xác nhận của người vận hành; họ xác nhận fixture không cản G28/QGL trên máy này. Không thay CFG production trong lượt kiểm tra. T3/T4 chờ chỉnh dock/hiệu chuẩn sau. Lỗi main MCU `Missed scheduling of next digital out event` khi QGL nóng vẫn chưa có nguyên nhân OID/pin xác định; không coi QGL lúc nguội là phép xác nhận lỗi đã hết.
