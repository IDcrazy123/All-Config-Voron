# QGL sau đổi tool và chạy Z — 30/10/2026

**Hoàn tất hai lượt PETG 70°C, cả hai hội tụ. Phần ABS 100/105°C phải dừng trước phép đo vì tín hiệu nhiệt bàn nhảy bất thường. Sau đó reset một lần theo yêu cầu mới của người dùng; máy Ready với toàn bộ heater tắt, chưa tiếp tục thử nhiệt.**

## Điều kiện và quy trình

Người dùng yêu cầu trước mỗi QGL phải đổi T0/T2 vài lần và nâng/hạ Z để mô phỏng máy đã di chuyển nhiều. Đã kiểm tra máy standby, không pause/recovery/drying, T0 active/detected khớp, không chuyển động chờ; bàn sạch/không vướng theo xác nhận người dùng. Đọc AGENTS.md và cấu hình live trước thử.

- Giữ nguyên cấu hình production: Cartographer scan samples=200, coil calibration bị bỏ (không bù nhiệt), model scan mới và Touch threshold=1504; QGL tolerance=0,0075 mm, retries=10. Không sửa CFG/Python hoặc chạy SAVE_CONFIG.
- Dự kiến hai lượt mỗi mức PETG 70°C, ABS 100°C, ABS 105°C, theo thứ tự tăng nhiệt. Đây là mô phỏng riêng giai đoạn trước QGL, không đùn nhựa, Touch hoặc mesh, không phải bản in thật.
- T0 và T2 giữ 150°C, quạt bàn 50%. Trước **mỗi lượt**, bàn phải liên tục trong target ±1°C và hai nozzle trong 148–152°C đủ 60 giây với PETG hoặc 90 giây với ABS.
- Home một lần lúc chuẩn bị. Đo PROBE ba lần tại X174 Y168, sau đó đo bốn góc production (20,0), (20,280), (330,280), (330,0), không chỉnh gantry trong phép đo nền.
- Mỗi lượt chạy **ba vòng T0→T2→T0**, tổng sáu lần đổi tool qua đường dock native. Sau mỗi lần xác nhận toolchanger ready và active/detected đúng tool. Dock Z=343 mm, đỉnh đường pickup=346 mm, giới hạn Z=347 mm; không tự sửa đường gắp.
- Về tâm rồi chạy **ba chu kỳ Z20→Z200→Z20 ở 25 mm/s**. Tiếp tục PROBE ba lần tại cùng tâm và gọi QUAD_GANTRY_LEVEL production ngay. Không G28 Z hoặc Touch giữa đo trước và đo sau chuyển động; macro QGL chỉ home Z ở cuối sau khi hội tụ.
- Bộ giám sát ngoài Klipper lấy telemetry khoảng 2 giây/lần và dừng toàn bộ bài thử khi có lỗi tool/probe hoặc tín hiệu nhiệt bàn nhảy quá 8°C trong dưới 3,5 giây. Đây là điều kiện dừng của bài thử, không sửa ngưỡng heater trong Klipper.

## Kết quả đã hoàn tất

| Điều kiện | Hoàn tất (UTC+07) | ΔZ tâm sau−trước (mm) | Range QGL đầu→cuối (mm) | Retry cuối | Nhiệt bàn lúc QGL (°C) |
|---|---|---:|---|---:|---|
| PETG 70°C, lượt 1 | 18:41:12 | −0.038139 | 0.106030 → 0.002764 | 3/10 | 70.02–70.08 |
| PETG 70°C, lượt 2 | 18:46:20 | −0.173363 | 0.034246 → 0.005048 | 1/10 | 69.94–70.05 |

Tổng thực hiện **12 lần đổi tool, sáu chu kỳ Z**, không có lỗi xác thực pickup trong những lần này. Hai QGL đều đạt range ≤0,0075 mm, không nới tolerance hoặc tăng retries. Chưa thực hiện các lượt ABS có chuyển động của bài thử mới; không gộp với kết quả ABS của bài thử nhiệt trước đó.

| Phép đo phụ | PETG lượt 1 | PETG lượt 2 |
|---|---:|---:|
| Range ba PROBE tâm trước chuyển động (mm) | 0.023649 | 0.010838 |
| Range ba PROBE tâm sau chuyển động (mm) | 0.027926 | 0.022941 |
| Trung bình dịch Z của bốn góc (mm) | −0.0039705 | −0.1257743 |
| Max−min của bốn độ dịch góc (mm) | 0.051549 | 0.019850 |

Độ dịch góc được tính từ lượt khảo sát nền đến bốn điểm QGL đầu tiên, trước điều chỉnh gantry. Range max−min của độ dịch đã loại phần dịch chung bằng phép trừ, nhưng vẫn chứa drift đầu dò theo thời gian đo; không đồng nhất với độ nghiêng cơ khí thuần.

## Vì sao dừng phần ABS

Lúc chuyển target từ 70 lên 100°C, máy đang đứng tại X174 Y168 Z20 với T0; chưa bắt đầu đo nền hoặc chuỗi đổi tool của lượt ABS đầu. Bộ giám sát phát hiện lúc **18:47:40 theo đồng hồ máy điều khiển**: số đo bàn **76,59→89,22°C trong 2,259 giây**, gửi `/printer/emergency_stop` rồi dừng. Log Klipper ở độ phân giải khoảng một giây cho thấy các bước nhảy rõ hơn:

| Klipper monotonic (s) | Nhiệt bàn (°C) | Target (°C) | PWM |
|---:|---:|---:|---:|
| 7900.5 | 85.6 | 100 | 1.000 |
| 7901.5 | 65.5 | 100 | 1.000 |
| 7902.5 | 86.4 | 100 | 0.663 |
| 7932.5 | 68.9 | 100 | 1.000 |
| 7933.5 | 101.0 | 100 | 0.000 |

Đây là biến thiên tín hiệu đo không hợp lý đối với nhiệt độ toàn bàn. Lỗi đường đo nhiệt bàn đã ghi nhận từ trước vẫn tái diễn; chưa xác định phần hỏng cụ thể là NTC, dây/giắc/crimp, nhiễu hay đầu vào PB0. Không có phép đo nhiệt độc lập trong bài thử và không coi số đo này là nhiệt thật của bàn.

Shutdown ghi `Shutdown due to webhooks request` vì **bộ điều khiển thử nghiệm chủ động emergency stop**; không phải Klipper tự phát lỗi ADC hoặc QGL thất bại. Lệnh dọn dẹp TURN_OFF_HEATERS/BED_FAN_OFF sau đó bị từ chối vì Klipper đã shutdown. API sau shutdown xác nhận power=0 của bàn và cả năm extruder; target vẫn có thể giữ giá trị cũ 100/150°C và trạng thái quạt hiển thị 0,5. Không tuyên bố đã chạy thành công lệnh tắt heater/quạt hoặc đã xác minh SSR thực tế bằng đo điện. Toolchanger trở về uninitialized do shutdown, detection vẫn là T0; không tự di chuyển/gắp lại hoặc firmware restart.

## Nhận định và việc cần làm

1. **PETG có khả năng QGL hội tụ sau chuỗi chuyển động đã thử**, nhưng hai lần đạt không đủ chứng minh toàn bộ hệ Z ổn định lâu dài hoặc lớp đầu chính xác. Dịch Z tại tâm tới khoảng 0,173 mm là đáng kể dù QGL cuối đạt; QGL chủ yếu chỉnh chênh lệch giữa các góc, không chứng minh Z tuyệt đối không trôi.
2. Ba PROBE liên tiếp đã có range khoảng 0,011–0,028 mm. ΔZ sau chuyển động chứa cả nhiệt, đầu dò, cơ khí và thời gian đo; chưa thể gọi đó là mất bước, trượt belt hoặc riêng lỗi Cartographer. Samples=200 không loại được drift chậm. Không có đối chứng không chuyển động cùng khoảng thời gian hay đồng hồ so độc lập trong bài này.
3. Cartographer gắn trên shuttle. Chuỗi đổi tool kiểm chứng pickup và tác động lên phép đo shuttle; **không đo trực tiếp độ lặp Z đầu nozzle T0/T2**. Muốn tách lỗi cơ khí khỏi drift đầu dò cần đồng hồ so/tham chiếu độc lập ở cùng điểm, cùng nhiệt, đồng thời quan sát gá Cartographer và ngàm tool.
4. Ưu tiên kiểm tra đường NTC bàn trước khi thử ABS tiếp. Ngắt điện lưới, chờ nguội, kiểm tra gá NTC, dây, crimp, giắc PB0 và đường đi gần dây AC/SSR. Đo điện trở tại đầu controller khi uốn nhẹ dây/giắc để tìm chập chờn; nếu bất thường, đo gần cảm biến để khoanh vùng và sửa/thay phần hỏng. Chỉ chạy lại chu trình nhiệt có giám sát sau khi tín hiệu ổn định. Không nới verify_heater, đổi PID hoặc smoothing để che lỗi.
5. Sau khi đường nhiệt được sửa và xác nhận ổn định, mới hoàn tất hai lượt ABS 100°C và hai lượt 105°C, soak 90 giây trước từng lượt, giữ nguyên chuỗi chuyển động này. Bài thử hiện tại **dừng có nguyên nhân**, không tự lặp restart hoặc cấp nhiệt lại.

## Reset theo yêu cầu tiếp theo

Người dùng yêu cầu reset và hoàn tất thử nghiệm trước, sửa NTC sau. Đã thực hiện phần reset an toàn: đọc lại trạng thái standby, không pause/recovery/drying, không chuyển động chờ, T0 detected, heater power=0; kiểm tra delayed_gcode startup không tự cấp nhiệt/chuyển động. Gửi **một FIRMWARE_RESTART**. Lúc **18:52:17 UTC+07** xác nhận Klipper Ready, target=0 và power=0 ở bàn/cả năm extruder, homed_axes rỗng (dự kiến sau reset), T0 detected và toàn bộ configfile.settings vẫn khớp trước thử. Không home, di chuyển hoặc cấp nhiệt sau reset.

Phần thử nhiệt chưa tiếp tục vì tín hiệu phản hồi NTC đã sai rõ ràng, có thể khiến bộ điều khiển cấp sai công suất bàn 1000 W. Reset không sửa được đường đo. Trạng thái shutdown trong dữ liệu là snapshot ngay sau dừng thử; trạng thái cuối sau yêu cầu mới là Ready/heater tắt, lưu bổ sung trong JSON.

## Cấu hình và dữ liệu

Toàn bộ `configfile.settings` trước/sau giống nhau. Hash probe config live vẫn là `69ca73536dccbc1e0567351fbb8af0a10f903f253659878c0e8cfd7a6f5a7977`. Không sửa config/model, coil compensation, retries, offsets, heater limit hoặc runtime Python.

- [CSV kết quả](qgl-motion-trial-2026-10-30.csv).
- [JSON: probe, retry, sự kiện và snapshot sau shutdown](qgl-motion-trial-2026-10-30-results.json).
- [CSV log nhiệt bàn khi chuyển lên ABS](qgl-motion-trial-2026-10-30-bed-fault.csv), dùng Klipper monotonic để không trộn đồng hồ printer và client.
- Telemetry đầy đủ, phản hồi G-code và log thô giữ tại `%TEMP%/voron-qgl-motion-trial-20261030` của phiên làm việc.
