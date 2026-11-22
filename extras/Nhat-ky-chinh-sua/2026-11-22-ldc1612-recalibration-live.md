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
