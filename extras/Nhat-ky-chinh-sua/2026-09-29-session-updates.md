# Nhật ký — 2026-09-29

## 1. Điều tra shutdown bản in RoboOctopus mới nhất

### Triệu chứng

- Job Moonraker `000301`, file `RoboOctopus_4Color_PETG_2d5h7m.gcode`, bắt đầu lúc **2026-09-28 06:32:11.575 +07:00** và dừng lúc **2026-09-29 07:51:05.748 +07:00** với trạng thái `klippy_shutdown`.
- Job đã in `90,213.118 s` (khoảng 25 giờ 03 phút 33 giây) và dùng `72,768.655 mm` filament trước khi dừng. Metadata G-code ghi OrcaSlicer 2.4.2, 404 lớp và 1.167 lần đổi filament/tool.
- Job `000300` ngay trước đó dùng cùng file cũng được Moonraker ghi `klippy_shutdown`, nhưng log lưu ngày 28/09 xác nhận đây là `Shutdown due to webhooks request` trong giai đoạn khởi động, không phải một lần tái diễn độc lập của lỗi EBB1.

### Phân tích nhật ký

- Log tải đọc-only từ máy:
  - [klippy-20260929-latest-print-failure.log](<D:/Desktop/All-Config-Voron-main/Voron 5 Tool/extras/logs/klippy-20260929-latest-print-failure.log>) — SHA-256 `54925CB1D710F98965E0642FF132F47A2DFC0B5B7D9FB2213754E29444B98EA1`.
  - [moonraker-20260929-latest-print-failure.log](<D:/Desktop/All-Config-Voron-main/Voron 5 Tool/extras/logs/moonraker-20260929-latest-print-failure.log>) — SHA-256 `E16749F1D6ABF59E02C596B8076BFD4A0ECDA53E437A7AF2BEF514B24AA15774`.
- Klippy chuyển sang shutdown ở dòng 526634. Nguồn lỗi đầu tiên và duy nhất là `MCU 'EBB1' shutdown: Timer too close` ở dòng 526863/527078; packet nhận từ EBB1 ở dòng 527239 chứa `static_string_id=Timer too close`.
- Main MCU, EBB0, EBB2, EBB3, EBB4 và Cartographer sau đó đều ghi `Command request`; đây là shutdown lan truyền sau khi EBB1 đã báo lỗi, không phải sáu lỗi độc lập.
- EBB1 có ba đợt lỗi truyền thông rõ rệt trong cùng job. Một đợt tăng `rx_error` từ 89 lên 453 trong khoảng một giây và `bytes_retransmit` từ 0 lên 370. Sau đó bộ đếm đạt `rx_error=680`, `bytes_retransmit=972`; ngay trước shutdown tăng `rx_error=680 → 929`, `bytes_retransmit=972 → 1,199`, và dump sau shutdown ghi `rx_error=1,146`, `bytes_retransmit=1,739`. Các MCU CAN khác không có retransmit tương ứng.
- Host không có dấu hiệu quá tải tại thời điểm lỗi: Klippy `sysload≈0.51`, còn khoảng 3,063 MB RAM, `buffer_time≈1.16 s`, `print_stall=3` không tăng. Moonraker ghi CPU khoảng 0.9–2.35%, nhiệt CPU `50.634 °C` và không có cờ throttling.
- Không có `bytes_invalid`, `No buffer space available`, lỗi đĩa hoặc cảnh báo undervoltage trong cửa sổ sự cố. Sau lần khởi động lại, `can0` đang `ERROR-ACTIVE`, bitrate `1,000,000`, `txqueuelen=128`; kernel `6.12.96`, phù hợp mức tối thiểu mới trong hướng dẫn CAN của Klipper.
- Cấu hình đang chạy xác nhận EBB1 là BTT EBB36 V1.2 của T1, UUID `6475b5b9e028`, điều khiển `extruder1`, heater và quạt T1.
- Topology và vị trí jumper termination thật không được ghi trong repository, nên không thể xác nhận thiếu/thừa termination bằng phần mềm. USB `1d50:606f`, product `stm32h723xx`, là Manta chạy Klipper USB-to-CAN bridge qua `gs_usb`; không có lỗi/drop ở link counters sau reboot.

### Đối chiếu G-code

- Tại shutdown, T1 đang active ở `220 °C`; Z hiện hành là `13.04 mm`, tương ứng lớp vật lý 65/404 (chỉ số lớp 64 nếu đếm từ 0).
- `sd_pos=195502693` trỏ tới vị trí parser/queue gần lệnh `G1 X67.278 Y197.942 F21000`, là travel 350 mm/s không có `E`. Do Klipper vẫn có khoảng 1,16 giây dữ liệu đã đệm, đây là mốc con trỏ file gần sự cố chứ không được coi là chính lệnh gây lỗi.
- Các burst CAN trước đó cũng xảy ra khi T1 hoạt động ở vùng X khoảng 59–72 mm, Y khoảng 198–278 mm. Tương quan này củng cố khả năng cáp/connector/strain-relief của nhánh T1 bị ảnh hưởng theo vị trí uốn/rung; nó chưa xác định được chính xác conductor hoặc đầu nối nào nếu chưa kiểm tra phần cứng.
- File mới đã tắt `exclude_object=0` và `gcode_label_objects=0`; lỗi state E của `exclude_object` đã biết không tham gia vào shutdown này. `tool_change_on_wipe_tower=0` vẫn là rủi ro G-code riêng nhưng không tạo `Timer too close` lần này.

### Nguyên nhân gốc

- **Đã xác nhận ở mức firmware:** EBB1 nhận/lập lịch một timer quá muộn và tự shutdown bằng `Timer too close`.
- **Đã xác nhận ở mức truyền thông:** ngay trước lỗi có burst lỗi nhận CAN và retransmit tập trung bất thường tại EBB1, làm dữ liệu thời gian thực tới EBB1 bị trễ.
- **Khả năng vật lý cao nhất:** tiếp xúc chập chờn hoặc toàn vẹn tín hiệu/nguồn tại nhánh T1 — CAN-H/CAN-L, 24 V/GND, crimp/connector, đoạn dây chịu uốn, strain relief, termination/topology, hoặc transceiver/board EBB1. Log chưa thể phân biệt duy nhất một linh kiện trong nhóm này.
- Host overload, thiếu RAM, quá nhiệt/throttling, lỗi cú pháp G-code, `exclude_object`, cooling, Z-hop và một lần mất nguồn toàn máy không phù hợp với chuỗi bằng chứng. Mất nguồn toàn máy thường làm nhiều MCU mất liên lạc cùng lúc; ở đây EBB1 gửi được packet shutdown cụ thể rồi host mới yêu cầu các MCU còn lại dừng.
- Moonraker/host tiếp tục hoạt động sau 07:51; power-cycle/unsafe shutdown `303 → 304` xảy ra hơn 1 giờ 33 phút sau khi print đã bị Klipper dừng. Vì vậy việc rút nguồn là sự kiện hậu sự cố, không phải nguyên nhân của shutdown lúc 07:51.

### Hướng khắc phục đã thực hiện

- Chỉ đọc lịch sử Moonraker, tải và phân tích log/G-code, đọc cấu hình và kiểm tra trạng thái hệ thống qua SSH/API. Không gửi G-code, không home, không đổi tool, không gia nhiệt và không sửa cấu hình máy.
- Máy hiện `ready/standby`; sau reboot, bộ đếm CAN của tất cả MCU đang về 0. Đây chỉ xác nhận máy kết nối lại, không chứng minh lỗi chập chờn đã được sửa.
- Không tăng `txqueuelen`: giá trị hiện tại là 128 và log không có lỗi đầy hàng đợi. Tăng mù có thể làm tăng độ trễ. Không cập nhật Klipper/MCU trong phiên chẩn đoán này vì không có commit mới nào được xác nhận sửa burst CAN vật lý này.
- Host đang ở Klipper `v0.13.0-740-g60fc7aa67`; EBB1/EBB0 dùng firmware `v0.13.0-628-g373f200ca`, các node khác cũng có build không đồng nhất. Có thể chuẩn hóa firmware sau khi phần cứng ổn định, nhưng build EBB1 hiện tại không phải bằng chứng nguyên nhân: EBB0 dùng cùng build mà không retransmit. 37 commit host còn thiếu so với upstream tại thời điểm kiểm tra không có thay đổi CAN/scheduler liên quan tới lỗi này.

### Phòng ngừa và thứ tự kiểm tra

1. Tắt nguồn hoàn toàn; kiểm tra/pull-test nhẹ CAN-H, CAN-L, 24 V và GND của T1 ở cả hai đầu, crimp, connector và strain relief, đặc biệt đoạn dây thay đổi độ cong khi carriage ở X khoảng 59–72 mm.
2. Khi toàn bộ bus đã mất nguồn, đo CAN-H ↔ CAN-L theo topology thật; bus có đúng hai termination 120 Ω thường đo xấp xỉ 60 Ω. Khoảng 120 Ω thường là thiếu một terminator, khoảng 40 Ω thường là ba terminator; không kết luận theo jumper nếu chưa truy được hai đầu vật lý của bus. Chỉ đặt termination ở hai đầu trunk, không bật trên mọi EBB.
3. Kiểm tra sụt áp 24 V tại EBB1 dưới tải T1 và dấu hiệu nóng/lỏng/oxy hóa; nếu dây và connector đạt, hoán đổi có kiểm soát cáp hoặc board để tách lỗi transceiver EBB1 khỏi harness.
4. Sau khi xử lý phần cứng, chạy coupon T1 ngắn ở vùng chuyển động liên quan và theo dõi `canbus_stats EBB1`. Dừng thử nếu `rx_error`, `tx_error` hoặc retransmit tăng; chưa chạy lại job 53 giờ chỉ vì máy đã `ready`.
5. Có thể tạm giảm travel 350 → 250 mm/s và acceleration 7.000 → 5.000 mm/s cho coupon để giảm kích thích cơ khí, nhưng đây chỉ là biện pháp giảm rủi ro, không sửa nguyên nhân CAN.

### Vấn đề còn lại

- Cần kiểm tra trực tiếp harness/termination/nguồn EBB1 để xác định linh kiện vật lý cuối cùng. Không thể xác nhận một crimp, dây hay transceiver cụ thể chỉ từ log.
- Sau sửa phần cứng cần lưu counters trước/sau coupon. Một lượt idle với counters bằng 0 không đủ điều kiện đóng sự cố.

## 2. Kiểm tra góc nhìn camera MF-500

### Trạng thái trực tiếp

- Kiểm tra read-only trên máy xác nhận chỉ có một camera UVC Sunplus `1bcf:0c18`, product `MF500 camera`, nối tại `/dev/video0`.
- Crowsnest đang chạy `camera-streamer` ở `1280x720`, MJPEG, 30 FPS. Endpoint trạng thái xác nhận capture, snapshot, stream và H.264 đều ở 1280×720; tại thời điểm kiểm tra không có frame bị drop.
- Moonraker/Mainsail có hai entry `VoronBed` và `Axiscope`, nhưng cả hai đều trỏ tới cùng `/webcam`; đây không phải hai camera vật lý độc lập.
- Snapshot raw `/webcam/?action=snapshot` đúng 1280×720. Khung raw không bị Mainsail crop, nhưng camera đang bị roll/nghiêng và chĩa lên: phần lớn ảnh là trần/tường/phản sáng, còn vùng máy in chỉ chiếm dải bên phải. Giới hạn quan sát hữu dụng hiện tại chủ yếu do hướng gá, không phải do phần mềm cắt mất khung.

### Khả năng FOV và giới hạn phần mềm

- V4L2 không expose control zoom, pan, tilt, focus hoặc ROI/crop có thể sử dụng. Crop bounds/default đều là toàn bộ 1280×720. Không có setting Crowsnest/Mainsail nào tạo thêm cảnh nằm ngoài góc quang học của lens.
- MF-500 quảng bá các mode MJPEG 30 FPS gồm `1280x720`, `1280x960`, `1920x1080` và `2560x1440`. Tăng từ 720p lên 1080p/1440p cùng tỷ lệ 16:9 chỉ tăng số pixel, không bảo đảm tăng góc nhìn; hai mode cao này trước đây đã gây màn hình đen qua WebRTC.
- `1280x960` 4:3 là phép thử cấu hình duy nhất có khả năng lấy thêm phần trên/dưới nếu firmware đang crop sensor ở 16:9. Mức tăng lý thuyết tối đa là 33% số pixel theo chiều dọc, nhưng phải A/B snapshot từ cùng vị trí vì firmware có thể chỉ scale/crop theo cách khác. FOV ngang không tăng.
- Tài liệu MF-500 lưu trong repository ghi sensor 1/3-inch và lens được chọn theo góc/tiêu cự nhu cầu. Không có tiêu cự hoặc FOV của lens đang lắp trong USB descriptor hay cấu hình, nên chưa thể xác nhận chính xác 90°, 100° hoặc 120° từ model camera.
- Calibration cũ khoảng `0.023 mm/px` ở khoảng cách gần cho ước lượng HFOV thực tế cỡ 40–60° tùy khoảng cách quang học thật; đây là lens normal/moderate chứ không có bằng chứng là ultra-wide 90–120°. Ảnh Mainsail lịch sử `extras/pictures/Screenshot 2026-06-12 213902.png` cho thấy khi đặt đúng vị trí xa, lens hiện tại nhìn được gần trọn bàn 350×350 mm.

### Kết luận và đề xuất

1. Ưu tiên chỉnh lại gá: xoay camera về ngang, chĩa tâm vào bàn in và nếu cần đưa camera lùi/cao hơn. Đây là cách an toàn và có khả năng tăng vùng quan sát hữu dụng nhiều nhất mà không đổi phần mềm.
2. Nếu sau khi chỉnh gá vẫn thiếu chiều dọc, sao lưu `crowsnest.conf`, thử A/B `1280x960` và đổi aspect ratio Mainsail sang 4:3; đo coverage, FPS và độ ổn định rồi mới quyết định giữ hay hoàn tác.
3. Muốn tăng FOV quang học thật sự, cần lens tiêu cự ngắn hơn phù hợp sensor 1/3-inch hoặc camera wide-angle khác. Phải xác minh ren lens/image circle trước khi mua; lens quá rộng có thể gây méo barrel/fisheye, mờ rìa và giảm độ chính xác nhận dạng nozzle.
4. Bất kỳ thay đổi vị trí, lens hoặc resolution nào cũng làm mất hiệu lực calibration camera-origin/MPP của workflow thị giác trước đây; cần calibrate lại nếu dùng workflow đó.

Không sửa cấu hình, không restart dịch vụ và không điều khiển chuyển động máy trong phiên kiểm tra này.
