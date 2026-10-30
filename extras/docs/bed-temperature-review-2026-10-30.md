# Đối chiếu nhiệt bàn lúc khởi động và đang in — 30/10/2026

**Có biến thiên bất thường trong lúc in, nhưng những đoạn đã kiểm tra không có bước nhảy hàng chục độ như lúc gia nhiệt/thử nghiệm. Một cửa sổ theo dõi thụ động đủ 10 phút sau đó ổn định. Bằng chứng thu hẹp tới nhánh đo nhiệt bàn; chưa phân biệt được NTC/dây/giắc, mạch TH0/PB0 hay nhiễu tác động riêng lên nhánh này.**

## Nguồn và phương pháp

Đọc AGENTS.md hiện hành, trạng thái live, lịch sử job Moonraker, console, G-code và log Klipper mới nhất. Máy đang in `ZAssembly_ABS_1h13m.gcode`; toàn bộ tác vụ chỉ đọc, không đổi heater/quạt/cấu hình, không pause/cancel/restart hay thử đổi tool trong bản in.

- Ghép thời gian Stats qua cặp epoch/monotonic của từng `Start printer`; không trộn monotonic giữa các lần reboot. Thời gian log dưới đây theo printer UTC+07, chính xác khoảng một giây; đồng hồ client chạy trước khoảng 4–5 giây.
- Tách chuẩn bị, in, pause và chạy tiếp. Job start của Moonraker bao gồm PRINT_START, không đồng nghĩa đã bắt đầu đùn/in chi tiết. Bản in mới chuyển qua crash detection/prime và vào G-code chi tiết khoảng 19:22:10.
- Theo dõi riêng từ **19:45:07 đến 19:55:07 theo client UTC+07**: 600 lần GET API, không lỗi kết nối. Ghép thêm 599 dòng Stats chưa làm mượt trong đúng cửa sổ monotonic và cùng lần boot. Khoảng cách giữa Stats tối đa 1,1 giây; API tối đa 1,26 giây.
- Đọc `heaters.py` đang cài: `stats()` ghi `last_temp`, còn `get_status()`/API ghi `smoothed_temp`. Live `smooth_time=3.0`; PID nhận nhiệt từ callback trước phần làm mượt hiển thị. Vì vậy không dùng riêng biểu đồ giao diện để loại trừ xung ngắn.

## Những gì thực sự xảy ra

| Giai đoạn | Quan sát nhiệt bàn | Target/PWM và nhận xét |
|---|---|---|
| Bắt đầu bản in belt, 17:08:43–17:08:45 | 100,7→79,8→116,4°C, mỗi bước khoảng 1 giây | Target giữ 105°C; PWM 100%→100%→0%. Không phải lệnh đổi target |
| Belt đã in, 17:11–17:25 | Không có bước ≥3°C/giây; lớn nhất 99,8→101,5°C lúc 17:20:51 | Target đổi 105→100°C lúc 17:13:01; phần giảm dần sau đó là đáp ứng với target mới |
| Belt pause, 17:25:17–17:29:12 | 99,9–100,1°C | Target 100°C |
| Belt chạy tiếp, 17:29:14–17:38:00 | 99,8–100,2°C, bước lớn nhất 0,1°C | Target 100°C; loại phần PRINT_END tắt heater khỏi thống kê |
| Thử gia nhiệt, 18:47:32–18:47:33 | 68,9→101,0°C trong khoảng 1 giây | Target giữ 100°C, PWM 100%→0%; sau đó bộ thử đã emergency stop như báo cáo trước |
| Bản ZAssembly đang in, 19:28:28–19:28:29 | 99,2→101,1°C trong khoảng 1 giây | Target giữ 100°C, PWM 89,8%→0% |
| Bản ZAssembly đang in, 19:28:53–19:28:54 | 100,3→102,4°C trong khoảng 1 giây | Target giữ 100°C, PWM 35,2%→0% |

Sau khi job hoàn tất **20:28:28**, đã kiểm tra toàn bộ pha in có gia nhiệt **19:22:11–20:28:10**, gồm **3.956 mẫu Stats**, khoảng mẫu tối đa 1,1 giây. Không có bước ≥3°C giữa hai mẫu liền nhau; bước lớn nhất **2,1°C**. Chỉ có ba nấc ≥0,8°C: **0,9°C lúc 19:27:58; 1,9°C lúc 19:28:29; 2,1°C lúc 19:28:54**. Các nấc này tập trung vào đầu pha in; không gọi là hết lỗi. Target đổi **105→100°C lúc 19:24:52**; file G-code có `PRINT_START ... BED_TEMP=105` ở dòng 357 và `M140 S100` ở dòng 3476, nên hạ nhiệt từ khoảng 105 về 100°C không phải tự nó là lỗi cảm biến. PRINT_END tắt target bàn lúc **20:28:11**, được loại khỏi thống kê pha in; snapshot cuối xác nhận job complete, Klipper Ready, target/PWM bàn 0, không có can thiệp từ tác vụ này.

## Kết quả kiểm nghiệm thụ động 10 phút

| Đại lượng | Kết quả |
|---|---|
| Trạng thái và chuyển động | Printing suốt 600 mẫu, T0 suốt cửa sổ; vị trí XYZ đổi ở 599 cặp mẫu |
| Nhiệt bàn API đã làm mượt | **99,91–100,12°C**, trung bình 100,003°C, độ lệch chuẩn 0,032°C |
| Nhiệt bàn Stats chưa làm mượt | **99,9–100,1°C**, bước lớn nhất **0,1°C**; 599 mẫu |
| Target bàn | 100°C suốt cửa sổ |
| PWM bàn được ra lệnh | 22,1–32,4% |
| T0 / PWM T0 | 248,8–251,9°C / 0–60,3% |
| Quạt chi tiết T0 / quạt bàn | 9,8–80% / 50% |

Không tái hiện bước nhảy lớn trong cửa sổ này, dù có chuyển động, nozzle đóng/ngắt công suất và tốc độ quạt thay đổi. Điều này loại cách diễn giải đơn giản rằng cứ có PWM nozzle/quạt hoặc cứ in là nhiệt bàn sẽ nhảy; **không loại lỗi chập chờn, nhiễu theo điều kiện tải khác hoặc xung ngắn hơn tần suất ghi**. Không có đổi tool trong cửa sổ này và không có phép chủ động bật/tắt từng tải để xác định nhân quả.

## Khoanh vùng nguyên nhân

- Nhiệt bàn thật không thể đi theo chuỗi tăng/giảm hàng chục độ trong một giây của log. Đường đo/phản hồi có bất thường; không có nhiệt kế độc lập để xác định giá trị nào là nhiệt thật tại từng thời điểm.
- Live bàn dùng **PB0/TH0**, cảm biến buồng dùng **PB1/THB** trên cùng Manta. Khi bàn **79,8→116,4°C**, buồng vẫn **46,2→46,2°C**; khi bàn **68,9→101,0°C**, buồng **43,8→43,7°C**. Ngay hai nấc trong lúc in, buồng cũng chỉ đổi 0–0,1°C. Vì vậy ưu tiên nhánh riêng NTC bàn/dây/giắc/TH0 hoặc nhiễu ghép riêng vào nó; chưa có bằng chứng nhiễu toàn bộ ADC/nguồn chung cùng lúc.
- Một giả thuyết phù hợp là điện trở tiếp xúc/đường NTC tăng chập chờn làm số đo thấp, PID cấp nhiều nhiệt rồi tín hiệu hồi. Nhiễu cũng có thể tạo phản hồi tương tự. Đây chưa phải xác nhận NTC element hỏng.
- PWM ghi trong log là **lệnh công suất**, không phải đo dòng AC/đầu ra SSR. Nhiệt nhảy lên rồi PWM về 0 có thể là PID phản ứng với số đo sai; không dùng nó làm bằng chứng SSR tạo nhiễu hoặc SSR bị dính.
- Người dùng xác nhận nâng StealthChanger vẫn giữ mạch, dây bàn và SSR, không đi lại hay thay SSR. Điều này loại giả định thay SSR/đi lại dây gây lỗi. Tải/bo toolhead mới vẫn có thể thay môi trường điện, nhưng 10 phút ổn định với nozzle/quạt hoạt động chưa chứng minh nguồn nhiễu từ chúng. Không suy từ thời điểm nâng cấp ra linh kiện hỏng.

## Tụ 104 và đúng cổng trên pinout

Đã kiểm tra trực quan [pinout BTT](https://github.com/bigtreetech/Manta-M8P/blob/master/V2.0/Hardware/BIGTREETECH%20MANTA%20M8P%20V2.0%20PinOut.png) và trang 4 [sơ đồ hãng](https://github.com/bigtreetech/Manta-M8P/blob/master/V2.0/Hardware/BIGTREETECH%20MANTA%20M8P%20V2.0-SCH.pdf):

- Theo chiều ảnh, cụm thermistor từ trên xuống là TH3, TH2, TH1, **TH0**, THB. TH0 là cặp áp chót, giữa TH1 và THB; chân trên là tín hiệu PB0, chân dưới GND. PB1/THB hiện đang đo buồng, không phải bàn trên máy này.
- TH0 có pull-up R55=4,7 kΩ, R56/R57 mỗi con 2,37 kΩ và **C34=0,1 µF về GND phía ADC**. Giá trị 0,1 µF chính là tụ mã 104. C34 nằm sau điện trở nối tiếp, không mắc trực tiếp tại chân giắc cảm biến.
- Thêm 100 nF giữa SIG/GND ngay giắc TH0 sẽ thêm một tầng lọc; không thể hứa loại lỗi đã thấy. Nó có thể giảm nhiễu nhanh nhưng không sửa giắc hở, tiếp xúc điện trở thay đổi, NTC hỏng hoặc lỗi đầu vào. Không tự hàn tụ hoặc tăng smooth_time trong tác vụ này.
- Nếu thử tụ sau khi khoanh vùng, chỉ làm ở nhánh tín hiệu thấp áp, ngắt điện trước khi thao tác; **không mắc tụ 104 thông thường vào phía AC/SSR**. Không thay điện trở kéo lên, jumper PT1000, PID hay ngưỡng bảo vệ để ép số đo ổn định.

## Phép kiểm tra còn thiếu để kết luận linh kiện

Sau khi in xong và ngắt điện/chờ nguội: đo điện trở toàn đường NTC tại đầu controller khi lay nhẹ dây/giắc, kiểm tra crimp và gá cảm biến. Đối chứng bằng NTC tốt với dây ngắn ngay TH0, **heater giữ tắt**, rồi quan sát khi các tải thấp áp hoạt động. Nếu chỉ bộ dây/cảm biến cũ lỗi thì khoanh vùng nhánh đó; nếu nguồn đo chuẩn ngay cổng vẫn nhảy thì xét TH0/ADC/nguồn-GND và đo điện thực tế. Điện trở giả cảm biến chỉ dùng khi heater bị vô hiệu, không dùng để chạy gia nhiệt. Phân biệt nhiễu SSR cần phép đo/đối chứng có kiểm soát; log và thử thêm tụ đơn lẻ không đủ kết luận.

## QGL và cấu hình hiện hành

Lượt QGL khoảng 19:18 abort với range **0,075379→0,076728→0,092545 mm**, trong khi bàn **104,7–105,3°C**, không có bước nhiệt lớn. Lượt tiếp theo đạt **0,006676 mm ở retry 2** lúc 19:21:08; bàn **104,9–105,0°C**. Console ghi bỏ heat soak cả hai lần (bed rise 5,0°C / 0,9°C). Không thể quy trực tiếp lần QGL abort mới cho bước nhảy NTC; drift đầu dò/cơ khí và thời gian ổn định còn cần phân biệt.

Snapshot live đầu tác vụ cho thấy **scan samples=20**, khác lần triển khai trước samples=200; so settings với snapshot trước chỉ khác số mẫu. Model scan/Touch và trạng thái không bù nhiệt vẫn giữ. Repository probe config còn 200; không tự đồng bộ hoặc triển khai trong lúc in. Toàn bộ tác vụ này không sửa CFG/Python.

Dữ liệu: [CSV log theo giai đoạn](bed-temperature-review-2026-10-30-log.csv), [600 mẫu theo dõi API](bed-temperature-review-2026-10-30-monitor.csv), [JSON thống kê và 599 mẫu Stats thô trong cửa sổ theo dõi](bed-temperature-review-2026-10-30-results.json). Log và dữ liệu đầy đủ tại TEMP `voron-bed-log-review-20261030-1924` của phiên làm việc.
