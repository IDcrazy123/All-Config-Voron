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

## 3. A/B góc nhìn MF-500 tại vị trí quan sát toàn bàn

### Phép thử

- Sau khi người vận hành đưa camera về vị trí quan sát toàn bàn, snapshot raw `1280x720` cho thấy bàn 350×350 mm gần như nằm trọn khung và cân ngang. Cạnh bàn sau chiếm khoảng 648 px; cạnh trước còn khoảng 10–25 px trong snapshot đầu tiên và có thêm lề khi toolhead di chuyển ra sau.
- Trước phép thử, Moonraker xác nhận máy `standby`. Không sửa `crowsnest.conf`: chỉ dừng riêng Crowsnest tạm thời, chạy camera-streamer snapshot-only trên loopback port 8090 ở `1280x960 MJPEG @ 30 FPS`, lấy một frame rồi dừng tiến trình thử và khởi động lại Crowsnest.
- Đăng ký đặc trưng giữa hai ảnh A/B tìm được 482 inlier. Ảnh 960p là ảnh 720p phóng `1.333×`, với miền ngang tương ứng chỉ còn khoảng `x=160..1119` của ảnh 720p; miền dọc vẫn tương ứng `y=0..719`.

### Kết quả

- Mode `1280x960` không bổ sung cảnh phía trên/dưới. Nó giữ nguyên FOV dọc, cắt khoảng 160 px ở mỗi bên của ảnh 720p và làm mất tổng cộng khoảng 25% FOV ngang.
- Vì vậy `1280x720` vẫn là mode có góc nhìn hữu dụng lớn nhất đã đo trên camera này. Tăng độ phân giải hoặc chuyển 4:3 không tạo được góc rộng hơn; không có control zoom-out/crop trên V4L2.
- Với mô hình hình chữ nhật của người vận hành: chuyển từ trung điểm cạnh trên sang trung điểm cạnh dưới là phép đối xứng 180°. Nếu giữ cùng độ cao, khoảng lùi và hướng chĩa vào tâm, lens hiện tại vẫn phù hợp như vị trí đang dùng.
- Chuyển sang góc trái phía dưới không tương đương đối xứng: đường chéo và chênh lệch khoảng cách tới bốn góc làm yêu cầu FOV dọc/chéo lớn hơn. Khung hiện tại chỉ có lề hữu hạn, còn mode 4:3 lại cắt ngang; vì vậy không nên coi lens hiện tại là bảo đảm phủ toàn bàn ở góc nếu vị trí mới thấp hơn hoặc gần hơn. Cần đặt thử ở đúng gá, hoặc tăng độ cao/khoảng lùi; nếu vẫn cắt thì phải dùng lens tiêu cự ngắn hơn/camera wide-angle.

### Trạng thái hoàn nguyên

- Crowsnest đã trở về capture `1280x720`; snapshot hoạt động, `dropped=0` và bộ đếm frame tiếp tục tăng.
- Klipper không restart, không có chuyển động máy và trạng thái in sau phép thử vẫn là `standby`.

## 4. Nghiên cứu cải tiến vệ sinh T0 trước Cartographer Touch

### Phạm vi và số đo mới

- Chỉ audit cấu hình, tài liệu và nguồn Bambu; chưa sửa cấu hình máy, chưa gửi G-code và chưa điều khiển máy.
- Vùng silicone do người vận hành đo lại: `X=277..312`, `Y=0..-10`; nozzle bắt đầu/chạm trong vùng `Z=1.0..0.5`.
- Điểm purge mới yêu cầu: `X315 Y1 Z6`.
- Biên chuyển động production: `X=0..348`, `Y=-10..336`. Đường làm việc đề xuất inset 1 mm là `X=278..311`, `Y=-1..-9`, nên còn 1 mm so với cả mép silicone và hard limit Y=-10.

### Audit macro hiện tại

- `PRINT_START` gọi `CLEAN_NOZZLE TEMP=150 WIPES=5` hai lần, nhưng cả hai lần đều `PURGE=0`; purge/prime thật chỉ diễn ra sau Cartographer Touch và mesh.
- Circular scrub hiện tại chạy ở `Z1.2`, cao hơn vùng tiếp xúc mới nên có khả năng không chạm silicone.
- Flick hiện hạ tới `Z0.7` rồi chạy `X307..320` tại `Y-8`; đoạn `X312..320` nằm ngoài vùng silicone đã xác nhận.
- Các cung hiện tại có extrema `X277..312`, `Y-9.5..-6.5`; chỉ còn 0.5 mm so với hard limit Y=-10. Lịch sử đã từng ghi lỗi out-of-range `Y=-10.041`, nên phương án mới ưu tiên G1 có extrema chứng minh được.
- Purge hiện tại diễn ra ở `X320 Y-8 Z>=15`, không khớp điểm purge mới.

### Đối chiếu Bambu chính thức và video

- Machine start G-code chính thức của A1/A1 mini/P1S/X1 cho thấy mẫu chung: purge ở nhiệt vật liệu hoặc nhiệt flush, retract ngắn, bật quạt và shake/wipe để tách sợi, làm sạch cơ khí nhiều track/hướng, hạ và chờ khoảng 140 C, rồi mới ABL/Z contact.
- A1/A1 mini còn kết hợp touch-off nhiều điểm, brush/silicone và hard-rub trên exposed steel; P1S/X1 dùng nhiều đường hard-rub và cung tròn trên vùng thép. Những lệnh firmware riêng như `G380`, `G29.2`, `M1002`, `M622/M623`, soft-endstop và Z âm không được chuyển sang Klipper.
- A2L mới dùng enhanced-brush dạng G1 nhiều hướng; đây là phần phù hợp nhất để quy đổi sang pad silicone của máy.
- Video X1C thực tế của bên thứ ba xác nhận thứ tự purge ở chute, bed nâng, wipe/rub ở mép sau rồi mới leveling. Video A1 mini ngắn xác nhận nozzle chạy ngang, áp sát dãy silicone; video không được dùng để suy ra nhiệt độ hoặc tốc độ.
- Cartographer chính thức yêu cầu nozzle sạch và nhiệt Touch không vượt quá 150 C; cấu hình production đang dùng 150 C nên phương án giữ nhiệt chuẩn này và thêm wait giới hạn trên chính xác trước Touch.

### Phương án đề xuất chờ duyệt

1. Chia thành hai pha: lần đầu trước soak là purge có điều kiện tại `X315 Y1 Z6` rồi deep-clean; lần cuối ngay trước `CARTOGRAPHER_TOUCH_HOME` là short-clean không purge ở 150 C rồi Touch ngay.
2. Chỉ auto-purge khi slicer truyền `T0_TEMP>0`; dùng chính nhiệt T0 và purge nhỏ khoảng 8 mm. Nếu T0 không dùng trong job thì không đoán vật liệu/nhiệt purge, chỉ soften-and-wipe ở 150 C.
3. Sau purge: retract bảo thủ 0.8 mm, bật quạt, đặt 150 C, bắt đầu lấy cục ở tối đa 170 C và hoàn tất lượt cuối sau khi nozzle đã xuống không quá 150 C.
4. Thay G2/G3 bằng đường G1 enhanced-brush scale theo pad: anchor `X311 Y-5`, rồi lần lượt `Y-1 -> X294.5 -> Y-9 -> X278 -> Y-1 -> X294.5 -> Y-9 -> X311 -> Y-5`. Extrema tiếp xúc luôn là `X278..311`, `Y-9..-1`.
5. Commissioning bắt đầu ở `Z1.0`; chỉ hạ theo bước 0.1 mm tới `Z0.9/Z0.8` khi test có giám sát cho thấy tiếp xúc chưa đều; không cho phép thấp hơn `Z0.5`. Luôn nâng Z thẳng đứng khỏi pad trước khi đi ra ngoài.
6. Thêm validation/hard-abort cho active T0/KTC-ready, XYZ homed, QGL applied ở lượt pre-Touch, `WIPE_Z`, số pass, chiều dài và nhiệt purge. Nếu kiểm `can_extrude` sau M109 thì dùng helper macro riêng vì Jinja của macro ngoài được render trước khi motion thực thi.
7. Không mô phỏng hard-rub thép/Z âm của Bambu khi máy chưa có bề mặt hy sinh và phép đo Z riêng. Silicone-only có thể cải thiện mạnh nhưng không bảo đảm bóc được nhựa cháy/cục lớn như hệ Bambu nhiều bề mặt.

### Trạng thái

- Chưa tạo backup vì chưa sửa file cấu hình.
- Chờ người vận hành duyệt phương án và giá trị commissioning trước khi backup, triển khai, kiểm tra cú pháp, dry-run có giám sát và commit phần cấu hình.

## 5. Triển khai purge và vệ sinh T0 hai giai đoạn trước Cartographer Touch

### Quyết định sau khi duyệt

- Người vận hành dừng hướng nghiên cứu vị trí camera/timelapse và duyệt triển khai cải tiến vệ sinh nozzle theo số đo thực tế.
- Giá trị purge đề xuất ban đầu trong mục 4 đã được đánh giá lại sau khi phát hiện `PRINT_END` retract tổng cộng `10 mm` (`E-2` rồi `E-8`). `15 mm` gross chỉ còn khoảng `5 mm` nhựa thực, tương đương `12.03 mm³`, nên không đủ tin cậy để tạo cục purge rõ ràng.
- Macro start chính thức của Bambu A1/A1 mini/P1S/X1 dùng chuỗi explicit `E50 + E50 + E5`, rồi retract ngắn `E-0.5`. Tổng này phục vụ cả workflow load/switch/flush của Bambu nên không sao chép nguyên `105 mm`; cấu hình này chọn `40 mm` gross ở `F200`, tối đa khoảng `96.21 mm³` nếu T0 không có retract trước đó, hoặc khoảng `72.16 mm³` nhựa ra thực nếu phải bù đủ retract `10 mm`.
- Nguồn chính thức được đối chiếu: [Bambu P1S start profile](https://github.com/bambulab/BambuStudio/blob/7e048cf7b5622277503d9ec3ea1e4d1c83b95475/resources/profiles/BBL/machine/Bambu%20Lab%20P1S%200.4%20nozzle%20template%20machine_start_gcode.json), [Bambu X1C start profile](https://github.com/bambulab/BambuStudio/blob/7e048cf7b5622277503d9ec3ea1e4d1c83b95475/resources/profiles/BBL/machine/Bambu%20Lab%20X1%20Carbon%200.4%20nozzle%20template%20machine_start_gcode.json), [Bambu A1 start profile](https://github.com/bambulab/BambuStudio/blob/ceba5cc20ab34ed70a9b0458b590276b5b50726f/resources/profiles/BBL/machine/Bambu%20Lab%20A1%200.4%20nozzle%20template%20machine_start_gcode.json). Không tìm được video startup/wipe chính thức từ kênh Bambu có thể xác minh; video blob lớn chỉ được coi là quan sát thứ cấp, còn định lượng lấy từ profile chính thức.

### Sao lưu

- Tạo `extras/backups/pre-improve-nozzle-clean-20260929-195313/` trước khi sửa từng file cấu hình.
- Bản sao gồm `nozzle-clean.cfg`, `print-macros.cfg`, `tool-temp-bench.cfg` và `README.md` mô tả phạm vi/rollback.

### Thay đổi cấu hình

- `config/Printer-Setup/nozzle-clean.cfg`:
  - Chỉ cho phép T0 đã được cảm biến xác nhận, KTC `ready`, XYZ đã home, `_PRINT_STATE` là `idle/starting`, offset X/Y/Z bằng 0 và mesh đã clear.
  - Thêm `MODE=DEEP` và `MODE=TOUCH`; `TOUCH` cấm purge và yêu cầu QGL đã áp dụng.
  - Purge tại `X315 Y1 Z6`, mặc định `40 mm` ở `F200`, sau đó retract `0.8 mm` ở `F300`; purge chỉ chạy ở `170..280 °C` và helper runtime kiểm `can_extrude` sau khi đã chờ nhiệt.
  - Thay circular scrub bằng đường G1 nhiều track/hai hướng. Mọi tiếp xúc nằm trong `X278..311`, `Y-9..-1`; mặc định `CLEAN_Z=1.0`, hard-limit tham số `0.5..1.0`.
  - Mọi XY ra/vào trạm chạy ở `Z>=15`; hạ qua approach `Z3`, nâng thẳng khỏi silicone rồi mới rời vùng.
  - Lượt deep đầu lấy cục khi nozzle đã xuống `<=170 °C`; lượt cuối và toàn bộ mode Touch chờ đúng cửa sổ `148..150 °C`, sau đó xác nhận upper bound `<=150 °C` trước Cartographer.
  - Thêm guard riêng cho các helper nội bộ, kể cả tọa độ purge với sai số `0.2 mm`, để gọi nhầm từ console không thể extrude/chạy đường lau tùy ý.
- `config/Printer-Setup/print-macros.cfg`:
  - Sau khi chọn T0, chạy deep clean; chỉ auto-purge khi slicer truyền `T0_TEMP>0`, dùng đúng nhiệt vật liệu và `PURGE=40`.
  - Ngay sau QGL và trước `CARTOGRAPHER_TOUCH_HOME`, chạy `MODE=TOUCH`, `CLEAN_Z=1.0`, một lượt, không purge.
  - Bỏ các `M109` deadband cũ; macro mới dùng `TEMPERATURE_WAIT ... MAXIMUM=150` rõ ràng.
- `config/Printer-Setup/tool-temp-bench.cfg`: đồng bộ điểm park cao từ bucket cũ sang `X315 Y1`, vẫn giữ `Z>=15` và không hạ tới purge/pad.
- Cập nhật tài liệu Việt/Anh về tọa độ, hai mode, lượng purge, guard và yêu cầu commissioning có giám sát.

### Kiểm tra tĩnh

- `git diff --check`: đạt, không có whitespace error.
- `RawConfigParser`: parse thành công và không trùng section cho `nozzle-clean.cfg`, `print-macros.cfg`, `tool-temp-bench.cfg`.
- Jinja parser với delimiter tương thích Klipper: parse thành công toàn bộ template trong hai file macro chính.
- Render mô phỏng cả `DEEP`, `TOUCH` và helper: xác nhận mesh đã clear có dạng `[[]]` được chấp nhận, mesh thật bị chặn, helper purge chỉ chạy gần `X315 Y1 Z6`, purge chờ đủ nhiệt yêu cầu, và lượt cuối có cửa sổ `148..150 °C`.
- Mô phỏng toàn bộ lệnh G1 của cả hai hướng lau: extrema tiếp xúc đúng `X278..311`, `Y-9..-1`, `Z1.0`; không có XY ngoài pad khi Z thấp.
- Rà soát độc lập về Klipper/Jinja và chuyển động đã phát hiện rồi sửa hai lỗi trước commit: trạng thái `BED_MESH_CLEAR` là `[[]]` thay vì `[]`, và biên purge 170 °C phải chờ ít nhất đúng 170 °C trước khi kiểm `can_extrude`.

### Trạng thái và giới hạn

- Chưa gửi G-code, chưa restart Klipper và chưa điều khiển máy trong phiên triển khai repository.
- Cấu hình vượt qua kiểm tra tĩnh, nhưng chưa được commissioning vật lý. Lượt đầu phải có người giám sát để xác nhận cục purge `40 mm` rơi/gãy gọn trong bucket tại `X315 Y1 Z6`, nozzle tiếp xúc vừa đủ ở `Z1.0`, và không kéo sợi sang silicone. Chỉ hạ Z theo bước `0.1 mm` khi quan sát cho thấy chưa chạm đều; không thấp hơn `Z0.5`.

## 6. Triển khai live và audit cập nhật tại 192.168.1.43

### Trạng thái an toàn trước khi cập nhật

- Moonraker/Klipper báo `ready`; máy `standby`, virtual SD không active, không pause và không có file đang in.
- XYZ chưa home; mọi target của bed và năm extruder đều bằng `0 °C`. Tool sensor nhận T0, nhưng không gửi G-code, không home, không đổi tool, không di chuyển và không gia nhiệt trong toàn bộ phiên.
- Repo live `/home/voron/All-Config-Voron` sạch ở `41283d875c73`; sáu symlink KTC-Easy trong `toolchanger/readonly-configs` hợp lệ; bản vá active-tool validation trong `tool_crash.py` đã có sẵn; filesystem còn khoảng 12 GB.

### Triển khai All-Config-Voron

- Gọi Moonraker Update Manager đưa repo live `41283d875c73 → 9dd6aac53bf8`, sau đó xác nhận repo sạch và trùng `origin/main`.
- Phát hiện `install_script: config/scripts/install.sh` không phải post-update hook: Moonraker chỉ parse script để tìm package (`No packages found in script`) rồi restart Klipper; ba file macro live vẫn giữ hash cũ và không có backup mới. Vì vậy chạy trực tiếp `bash /home/voron/All-Config-Voron/config/scripts/install.sh` khi máy vẫn idle.
- Installer tạo backup đầy đủ `/home/voron/printer_data/config_backups/config-install-20260929-203558`, xác nhận KTC readonly links, giữ Axiscope ngoài phạm vi và chép cấu hình mới. Sau `RESTART`, Klipper trở lại `ready`.
- Đối chiếu source/live xác nhận macro mới đã có purge `X315 Y1 Z6`, `PURGE=40`, hai mode `DEEP/TOUCH` và vùng lau đã giới hạn. `nozzle-clean.cfg` và `tool-temp-bench.cfg` trùng SHA-256 local/live; `print-macros.cfg` trùng Git blob và `diff` bằng 0 (working tree Windows dùng line ending khác nên SHA-256 thô khác).

### Xung đột cấu hình live và khắc phục

- Lần rsync đầu làm lộ hai hiệu chỉnh thực tế chỉ tồn tại trên máy: `spread 7.0 / lower_z 0.7` bị repo đưa về `5.0 / 0.5`; `contact_z 50 / probe_z 55` bị đưa về `-1 / -1`. Klipper vẫn parse được nhưng không được phép chạy calibration ở giá trị `-1`.
- Tạo thêm bản lưu live `/home/voron/printer_data/config_backups/pre-calibration-restore-20260929-203724/`, sau đó khôi phục đúng hai file từ backup `203558`. Restart lần hai thành công; giá trị effective hiện là `spread=7.0`, `lower_z=0.7`, `variable_z=55`, `variable_contact_z=50`, `variable_probe_z=55`.
- Để lần triển khai sau không lặp regression, đồng bộ các giá trị người vận hành đã xác nhận vào repository:
  - `config/Printer-Setup/calibration-probe.cfg`
  - `config/toolchanger/toolchanger-config.cfg`

### Sao lưu repository

- [calibration-probe.cfg](<D:/Desktop/All-Config-Voron-main/Voron 5 Tool/extras/backups/pre-persist-live-calibration-20260929-203905/calibration-probe.cfg>)
- [toolchanger-config.cfg](<D:/Desktop/All-Config-Voron-main/Voron 5 Tool/extras/backups/pre-persist-live-calibration-20260929-203905/toolchanger-config.cfg>)
- [README backup](<D:/Desktop/All-Config-Voron-main/Voron 5 Tool/extras/backups/pre-persist-live-calibration-20260929-203905/README.md>)

### Audit và quyết định cập nhật thành phần

- **Đã cập nhật:** Mainsail `v2.18.2 → v2.19.0`. Đây là frontend stable; endpoint web trả HTTP 200 sau cập nhật và máy in vẫn `ready/standby`.
- **Đã cập nhật Moonraker:** `985c1d0 → 9e676eb` (`v0.11.0-3`); symlink timelapse untracked được giữ, API và Klipper vẫn ready. Máy không có section `[timelapse]`, nên endpoint render 404 là trạng thái chưa bật sẵn, không phải regression.
- **Đã cập nhật Klipper host:** `60fc7aa → 7bc4d094` (`v0.13.0-777`); không flash MCU. Không có path upstream trùng 12 plugin untracked; toàn bộ symlink và `tool_crash.py` được giữ. Đã tạo bundle rollback trước update.
- **Đã cập nhật KlipperScreen:** `fbe7451c → 3f08a9f7` (`v0.4.7-191`); service active, websocket và printer state khởi tạo lại bình thường.
- **Đã cập nhật Sonar:** `0d1d7c8 → 74494cc3` (`v0.2.0-2`). Không có `sonar.conf`; mặc định `enable=False`, nên service thoát `0/SUCCESS` và ở `inactive/dead` như thiết kế.
- **Đã cập nhật toàn bộ 48 thao tác package hệ thống:** 42 upgrade + 6 package mới, 0 remove. `dpkg --audit` sạch và mô phỏng `full-upgrade` còn `0 upgraded`; reboot và kiểm tra hậu khởi động được ghi trong nhật ký 2026-09-30.
- Crowsnest, timelapse, Cartographer stable `1.9.0`, ShakeTune, KTC-Easy, Axiscope và mainsail-config đều đang latest theo Update Manager.

### Rủi ro còn lại và kiểm tra sau cập nhật

- Klipper `ready`, service Klipper/Moonraker/KlipperScreen/Crowsnest active; sáu KTC symlink còn hợp lệ; lần khởi động mới không có config error, traceback, shutdown hay `Timer too close`.
- Máy vẫn `standby`, XYZ chưa home, toàn bộ heater target `0`, virtual SD inactive và T0 được sensor nhận. Toolchanger `uninitialized` là trạng thái bình thường sau restart khi chưa home/initialize.
- Cartographer plugin `1.9.0` có upstream issue [#510](https://github.com/Cartographer3D/cartographer3d-plugin/issues/510) về Touch sample âm bị clamp ở movement floor; máy này có `position_min: -5`. Guard liên quan mới chỉ ở beta `1.10.x`, nên không tự chuyển beta. Lần `PRINT_START`/Touch Home đầu tiên sau thay đổi phải có người giám sát và sẵn E-stop.
- Macro clean/purge mới chưa được commissioning cơ khí. Lượt purge/wipe đầu tiên vẫn phải quan sát bucket, khả năng tách cục nhựa và tiếp xúc silicone ở `Z1.0`; không tự động hạ thấp hơn nếu chưa đánh giá trực tiếp.
- Với cấu trúc hiện tại, nút Update của `All-Config-Voron` chỉ pull repo; sau đó vẫn phải chạy installer backup-first thủ công. Không coi Git HEAD mới là bằng chứng rằng config live đã được triển khai.
