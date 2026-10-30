# Kiểm tra QGL theo nhiệt độ — 30/10/2026

Người dùng xác nhận bàn sạch, không vướng và cho phép thử ABS/PETG. Đối chiếu trạng thái live máy 192.168.1.43 trước thử; đợi các lệnh QGL thủ công trước đó kết thúc rồi mới bắt đầu. Đây là mô phỏng giai đoạn QGL trước in, không chạy toàn bộ PRINT_START, vệ sinh/đùn nhựa, Touch hoặc mesh trong bài thử này.

## Điều kiện và cách đo

- Giữ nguyên cấu hình live: Cartographer scan samples=200, không có coil calibration (không bù nhiệt), QGL retries=10, retry_tolerance=0,0075 mm. Model scan và Touch mới của người vận hành giữ nguyên.
- Home theo macro đang chạy, lấy T0 sau home và xác nhận active/detected khớp. Nozzle T0 giữ 150°C; quạt bàn 50%; nghỉ giữa các lượt ở X174 Y168 Z10. Dùng macro QUAD_GANTRY_LEVEL production, có home Z ở cuối khi thành công.
- ABS: bàn 100°C, chờ vào 99–101°C rồi gọi _PRINT_START_HEAT_SOAK SOAK=90 AUTO_SOAK=0 MATERIAL=ABS; đo lặp ba lần. Sau đó đổi target lên 105°C, chờ vào 104–106°C, soak 90 giây rồi đo lặp ba lần. Soak ban đầu áp dụng cho từng mức nhiệt; lượt lặp sau không reset máy về lạnh.
- PETG: target 70°C theo các profile PETG có hot_plate_temp=70 trong repo; chờ bàn nguội từ ABS. Soak 60 giây theo thời gian PETG production rồi đo ba lần. Do nhiệt bật lên lại sau lần đầu chạm dải, lượt PETG đầu còn 71,89–74,83°C; không coi đó là một lượt ở 70°C ổn định.
- Thêm một lượt PETG đối chứng sau khi bàn nằm liên tục trong 69–71°C và nozzle trong 148–152°C đủ 60,9 giây. Lượt này giữ bàn 69,80–69,92°C trong lúc QGL.
- Lấy telemetry khoảng mỗi 2 giây, lưu phản hồi probe/retry từng lượt. Nhiệt ghi dưới đây là số đo cảm biến, không có nhiệt kế độc lập xác minh. Mốc giờ trong bảng do bộ điều khiển thử nghiệm ghi, UTC+07.

## Kết quả

| Vật liệu/target | Lượt | Hoàn tất | Retry | Range cuối (mm) | Nhiệt bàn min–max (°C) | Kết quả |
|---|---:|---|---:|---:|---|---|
| ABS/100 | 1 | 17:51:56 | 8 | 0.007445 | 100.01–100.12 | Đạt |
| ABS/100 | 2 | 17:53:32 | 6 | 0.007069 | 99.56–100.35 | Đạt |
| ABS/100 | 3 | 17:54:33 | 3 | 0.005980 | 100.01–100.34 | Đạt |
| ABS/105 | 1 | 17:58:03 | 6 | 0.004011 | 105.00–106.10 | Đạt |
| ABS/105 | 2 | 17:59:16 | 4 | 0.006525 | 104.84–105.04 | Đạt |
| ABS/105 | 3 | 18:00:18 | 3 | 0.005040 | 103.87–105.08 | Đạt |
| PETG/70 (chuyển tiếp) | 1 | 18:13:21 | 2 | 0.001506 | 71.89–74.83 | Đạt |
| PETG/70 | 2 | 18:14:23 | 3 | 0.005967 | 70.16–71.47 | Đạt |
| PETG/70 | 3 | 18:15:00 | 1 | 0.004392 | 69.93–70.06 | Đạt |
| PETG/70 (đối chứng ổn nhiệt) | 4 | 18:19:14 | 3 | 0.007201 | 69.80–69.92 | Đạt |

Tổng cộng 10/10 lượt đạt tiêu chí range ≤0,0075 mm; trong đó một lượt PETG diễn ra khi bàn còn chuyển tiếp nhiệt. Không có lỗi probe/tool, không phải nới tolerance hoặc sửa CFG/Python để hoàn tất bài thử.

## Nhận định và giới hạn

- Trong điều kiện giữ nhiệt/soak có kiểm soát, ABS 100°C và 105°C đều đạt 3/3 lượt. Số retry giảm theo thời gian nóng: 100°C là 8→6→3; 105°C là 6→4→3. Kết quả phù hợp ảnh hưởng của thời gian ổn định nhiệt, nhưng không phân biệt hoàn toàn drift đầu dò, khung/bàn và cơ khí Z.
- Đây là khả năng hội tụ trong bài thử, chưa phải bằng chứng hết lỗi cảm biến hoặc mọi lần khởi động lạnh đều ổn định. Lượt ABS 100°C đầu chỉ thấp hơn tolerance 0,000055 mm; lượt PETG kiểm chứng cũng khá sát ngưỡng.
- Samples=200 giảm nhiễu ngắn hạn nhưng không thay thế sửa đường nhiệt coil. Nhiệt coil vẫn sai và không được dùng để bù; drift vật lý của đầu dò vẫn có thể tồn tại.
- Trước bài thử, hai lượt 200 mẫu khi bàn còn tăng nhiệt có một lượt abort ở 0,016713 mm và một lượt đạt 0,006337 mm tại retry 7. Không dùng một lần đạt riêng lẻ để kết luận ổn định.
- Trong pha hạ từ 105 xuống 70°C có đoạn số đo giảm về khoảng 75°C rồi tăng gần 80°C, kèm xung PWM ngắn. Soak PETG theo kiểu chỉ đợi chạm dải rồi G4 đã bắt đầu khi nhiệt chưa ổn định; vì vậy đã thêm phép kiểm tra ổn định liên tục. Dữ liệu này chưa tách được đáp ứng nhiệt/PID khỏi bất thường đường NTC; vấn đề NTC cũ chưa được tuyên bố đã sửa.
- Để lặp lại điều kiện ABS của thử nghiệm, dùng SOAK=90 rõ ràng trong PRINT_START. AUTO_SOAK hiện có thể rút xuống 18 giây hoặc bỏ qua khi bàn đã nóng; trường hợp đó khác bài thử này. PETG nên đợi nhiệt ổn định thực sự rồi mới tính soak 60 giây.
- Các lượt là đo lặp trên cùng máy đã nóng, PETG chạy sau ABS; chưa kiểm chứng khởi động lạnh, chất lượng lớp đầu hoặc bản in PETG thật.

## Kết thúc

Sau lượt đối chứng cuối, xác nhận Ready/standby, không pause, QGL applied=true, T0 active/detected khớp ở X174 Y168 Z10. Target của bàn và cả năm extruder đều bằng 0, quạt bàn bằng 0. Toàn bộ configfile.settings trước/sau khớp; không thay model, samples, retries, tolerance, PID, heater limit hay Python runtime.

Dữ liệu: [CSV tóm tắt](qgl-thermal-trial-2026-10-30.csv), [các bước retry](qgl-thermal-trial-2026-10-30-results.json). Telemetry và phản hồi G-code thô được giữ tại thư mục TEMP voron-qgl-thermal-trial-20261030 của phiên làm việc.
