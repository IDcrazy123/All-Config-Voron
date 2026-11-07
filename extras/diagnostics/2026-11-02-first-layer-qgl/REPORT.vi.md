# Chẩn đoán lớp đầu và QGL — 02/11/2026

## Kết luận hiện tại

**Cập nhật từ người vận hành ngày 02/11/2026:** đã tìm ra nguyên nhân là thay nhầm một part đệm. Đây là nguyên nhân cơ khí được người vận hành xác định, thay thế bảng nghi ngờ ban đầu bên dưới. Chưa có thông tin chính xác vị trí/mã part, cơ chế gây lệch hoặc kết quả QGL/first layer sau khi thay đúng; không tự suy là pulley trượt, GE5C bó hay motor mất bước. Các phân tích và tỷ lệ bên dưới được giữ làm lịch sử điều tra, không còn là kết luận nguyên nhân hiện hành. Các bất thường coil/NTC đã quan sát vẫn là vấn đề riêng chưa được xác nhận xử lý.

### Nhận định trước khi người vận hành xác định part đệm

Giả thuyết dẫn đầu là hệ Z không giữ được hình học/mốc cao sau hành trình lên dock và xuống bàn, đặc biệt nhánh Z2, sau khi thay/lắp lại các chi tiết Z và GE5C. Tốc độ Z hiện hành 80 mm/s, gia tốc 1.000 mm/s² và khoảng hở cấu hình nhỏ ở đỉnh dock là các yếu tố cần kiểm chứng cùng cơ khí. Chưa đo độc lập nên chưa xác nhận mất bước, pulley trượt hay GE5C bị bó.

Đồng thời có hai bất thường đo lường đã được ghi nhận trực tiếp: nhiệt coil Cartographer âm và tín hiệu nhiệt bàn nhảy phi vật lý. Touch cũng có mẫu ngoại lai lớn. Có thể có nhiều nguyên nhân cùng tồn tại; không được suy số QGL thành độ lệch cơ khí thật hoặc quy mọi lỗi cho một cảm biến.

Chỉ đọc trong lượt này: đọc AGENTS.md, cấu hình repository, hồ sơ ngày 30/10 và 01/11; GET Moonraker, tải log/G-code/cấu hình; SSH đọc mã đang cài; xem cửa sổ OrcaSlicer và các profile trên máy tính. Không phát G-code, chuyển động, gia nhiệt, restart, SAVE_CONFIG hoặc sửa production/profile Orca. Các lệnh vận hành trong console là hoạt động có sẵn của người vận hành/client khác.

## 1. Bằng chứng live và QGL

Snapshot đầu: Klipper Ready; bản `Khoi lap phuong_ABS_1m14s.gcode` complete; T0 active/detected khớp; homed xyz; homing_origin Z=0; bàn target 80°C, số đo 79,96°C. Không xem homing_origin=0 sau PRINT_END là bằng chứng offset lúc đang in bằng 0.

Các thời điểm dưới đây lấy từ console Moonraker, giờ Việt Nam. Log có lệch thời gian trong một số phiên khởi động: không dùng một offset wall-time/monotonic duy nhất để gán giờ cho toàn bộ file. Đối chiếu console bằng chính retry/range/tolerance; nhiệt độ lấy raw Stats trong đoạn tương ứng. Độ chính xác thời điểm log khoảng một vài giây.

| Thời điểm console | Điều kiện | Range đầu → cuối (mm) | Retry cuối | Bù Z2 ở lượt đầu (mm) | Số đo bàn trong đoạn QGL |
|---|---|---|---|---|---|
| 18:32:08 | QGL thô khi chuẩn bị bản T4 | 0,903825; lượt tolerance=1 | 0 | +0,735942 | ~105,4°C ở thời điểm chốt lượt |
| 18:32:17 | QGL tinh tiếp ngay sau đó | 0,298761 → 0,004466 | 7/10 | +0,258206 | 103,7–106,7°C |
| 18:39:56 | QGL thô khi chuẩn bị bản T4 tiếp theo | 0,874345; lượt tolerance=1 | 0 | +0,711927 | ~104,6–104,7°C |
| 18:40:05 | QGL tinh tiếp theo | 0,241297 → 0,002025 | 8/10 | +0,202483 | 104,7–105,1°C |
| 18:45:01 | Sau PRINT_END/dock T4; shuttle rỗng | 0,981970 → 0,006561 | 7/10 | +0,804013 | 88,1–93,6°C, bàn đang nguội |
| 18:49:35 | Lấy T0 từ shuttle rỗng, rồi bốn vòng T0→T4→T0 | 2,026687 → 0,006181 | 7/10 | +1,709277 | 52,9–76,2°C; đang đổi nhiệt và có tín hiệu lỗi |
| 18:54:44 | Năm vòng T0→T4→T0, kết thúc T0 | 1,179902 → 0,006416 | 5/10 | +1,026219 | 79,9–80,1°C |

Không gọi lượt 18:45 là phép đo T0 trước/sau một vòng T4: lúc đó shuttle rỗng. Không dùng lượt 18:49 để tách riêng ảnh hưởng đổi tool vì nhiệt bàn đang thay đổi và tín hiệu hỏng. Lượt 18:54 có số đo bàn ổn định hơn, nhưng coil vẫn thay đổi và không có đối chứng không chuyển động/đồng hồ so.

Trong các lượt lớn này, điểm 2 là điểm thấp nhất trong biểu diễn gantry-relative và Z2 luôn nhận lệnh bù dương lớn nhất. Theo sơ đồ QGL, Z2 là góc sau phải; cần xác nhận wiring/corner thật trên máy trước khi quy linh kiện. Đây là khoanh vùng kiểm tra, không phải phép đo motor đã thực sự đi đúng số mm được lệnh.

Ví dụ vòng 18:45 giảm dần 0,981970 → 0,370438 → 0,197989 → 0,107829 → 0,053522 → 0,028977 → 0,018687 → 0,006561 mm. Quá trình có đáp ứng nhưng sửa chưa hết mỗi lượt. Có thể do hình học QGL, độ đàn hồi/bó khớp, truyền động hoặc phép đo; không phải dấu hiệu duy nhất của sai thứ tự motor. QGL đạt cuối không bảo đảm giữ được độ phẳng qua lần lên dock tiếp theo.

## 2. Vì sao T0 đơn đẹp nhưng nhiều màu bắt đầu T0 lại xấu

PRINT_START đang nạp thực hiện home, chọn/làm sạch T0, QGL, Touch bằng T0, mesh, sau đó PRIME_LINES. PRIME_LINES prime tool không bắt đầu trước và để tool bắt đầu ở cuối:

- Chỉ T0: sau Touch/mesh, T0 tiếp tục prime và in, không cần gắp tool khác ở giai đoạn này.
- T0 + T3, bắt đầu T0: sau Touch/mesh có T0→T3→T0 rồi mới vào vật thể.
- Chỉ T3 hoặc chỉ T4: vẫn Touch bằng T0, sau đó đổi sang T3/T4 để prime và in.

Cả ba biểu hiện người vận hành mô tả đều phù hợp với sự thay đổi xảy ra sau Touch/mesh: hành trình Z tới dock, độ ngồi tool, tải dây hoặc gá probe. Offset T3 sai đơn thuần giải thích T3 đơn nhưng không giải thích đủ T0 xấu ngay nét đầu sau gắp lại và QGL đổi lớn.

Luồng nhiều màu là tác nhân làm lộ lỗi có thể có; chưa chứng minh macro tính Z sai. KTC đang cài đặt transform theo tool được chọn, không thấy bằng chứng cộng dồn offset T3 sang T0. PRINT_START cũng reset SET_GCODE_OFFSET trước chuẩn bị.

## 3. Đường Z và cụm thay mới

- Cấu hình đang nạp và repository đều có `max_z_velocity=80`, `max_z_accel=1000`.
- Bốn Z: rotation_distance=32, gear_ratio=80:16, full_steps_per_rotation=200, run_current~0,8 A, SpreadCycle. Chưa đếm răng pulley thực tế nên không kết luận đúng tỷ số chỉ từ CFG. Với tỷ số cấu hình, Z80 tương ứng khoảng 750 rpm motor; đây là số suy ra từ lệnh, không phải tốc độ đo được.
- KTC fast_speed=15000 mm/min, tức yêu cầu 250 mm/s cho các đoạn nhanh; chuyển động có thành phần Z còn chịu giới hạn động học Z. Đây là giới hạn/yêu cầu, không khẳng định mọi đoạn đều đạt 80 mm/s.
- Park Z=343, đường gắp/thả có đỉnh Z346, position_max=347. Khoảng chênh cấu hình chỉ 1 mm, không chứng minh khoảng hở vật lý. Sau thay chi tiết, cần đo có cạ, chạm, kéo dây hoặc bó ở vùng đỉnh hay không. Babystep và thay đổi mốc Z cũng cần tính khi kiểm tra đường dock.
- Profile tham chiếu chính thức Voron M8P dùng Z15/350 và ghi có thể tăng tốc với driver 24 V. Đây là tham chiếu cho phép thử giảm tải, không phải chứng minh máy này không thể chạy 80.

Những thứ cần kiểm tra tại Z2 trước, rồi đối chiếu ba góc còn lại: vít hãm pulley vào mặt phẳng trục; pulley 16T/80T và trục; dây đai dài/ngắn, tension và kẹp đai; idler, spacer, vòng đệm và cạ flange; liên kết gantry với rail; GE5C có bó hoặc rơ, chiều dài vít/spacer và preload; biến dạng/nứt/lỏng chi tiết in; dây/ống căng ở Z cao. Cùng hãng/cùng ABS không thay thế việc kiểm tra độ lắp chi tiết màu mới. Sự kiện tháo/lắp là bằng chứng cần điều tra, màu nhựa tự nó chưa phải nguyên nhân được xác nhận.

## 4. Cartographer và nhiệt bàn

Snapshot đọc chi tiết: coil khoảng −19,62°C, min/max phiên −21,38/−10,69°C; MCU probe ~65,37°C. Scan model reference_temperature=−18,26; software 1.10.1; không có hệ số bù nhiệt coil đang active. Scan samples=20. Hiệu chuẩn lại model không sửa đường đo nhiệt âm.

Tài liệu Cartographer nêu nhiệt coil âm thường liên quan hư hại linh kiện trên coil và không nhất thiết làm Touch mất chức năng. Vì vậy cần kiểm tra board/dây/điện trở, nhưng không được suy coil âm tự động chứng minh toàn bộ Touch sai hoặc thay board chắc chắn chữa mọi lỗi.

Touch khi chuẩn bị bản T4 gần nhất có chuỗi −0,6290; −0,1750; −0,6090; −0,6090; −0,6090 mm. Range toàn chuỗi 0,454 mm; ba mẫu cuối trùng nên được chấp nhận. Đây là bằng chứng mẫu không ổn định, dù kết quả cuối lặp tốt. Giá trị `adjusted z by +0,609` là sửa mốc home scan trước đó, không phải nozzle lún bàn 0,609 mm. Threshold=1379, z_offset=−0,05, speed=2. Mốc này không được tự chỉnh theo số adjusted z by.

Raw Stats phiên gần nhất tiếp tục có tín hiệu nhiệt bàn phi vật lý:

- 18:47:46–18:47:48: 84,1→38,8→25,8→86,8°C.
- 18:49:08–18:49:09: 73,5→58,0→78,9°C.
- 18:50:55: 53,7→76,9°C trong khoảng một giây.

Các giờ ở phiên cuối tương ứng offset boot ổn định và được đối chiếu với console QGL. Không dùng các số này làm nhiệt thật mặt bàn. Lỗi NTC/dây/giắc/đầu vào PB0 hoặc nhiễu cục bộ vẫn chưa được xác định linh kiện; target ổn định không đồng nghĩa nhiệt mặt bàn đã ổn định. Cần xử lý/xác minh đường đo này trước thử nóng ABS thêm. Không nới verify_heater, smoothing hoặc PID để che tín hiệu.

## 5. OrcaSlicer và G-code

Đã xem trực tiếp phiên `*Không tiêu đề - OrcaSlicer`: Voron Stealthchanger, nozzle 0.4; process 0.20mm Standard @Voron có chỉnh trong project; ba miếng một lớp đang dùng filament slot 5 ABS Tpoimns Purple/T4. GUI hiện có slot T3 mang tên PETG Luminous; không suy profile GUI mới thành profile của file đã in trước đó.

Đọc file được tải trực tiếp từ máy in:

- T0 đơn `Voron_linear_rail_cap_base_ABS_24m41s.gcode`: TOOL=0, chỉ T0_TEMP, lớp đầu 0,20, z_offset=0.
- T0/T3 `Voron_linear_rail_cap_base_ABS_12m44s.gcode` và `Belt-Clam_ABS_30m49s.gcode`: TOOL=0, T0_TEMP và T3_TEMP, lớp đầu 0,20, z_offset=0.
- T3 đơn `Khoi lap phuong_ABS_52s.gcode`: TOOL=3, chỉ T3_TEMP; lớp đầu 0,20, z_offset=0.
- T4 đơn `Khoi lap phuong_ABS_45s.gcode` và `...1m14s.gcode`: TOOL=4, chỉ T4_TEMP; lớp đầu 0,20, z_offset=0.
- Các file vừa nêu đều nozzle initial=260°C cho tool ABS dùng in, bed initial=105°C. Flow T0=0,96; profile tím=0,97. Không có lệnh SET_GCODE_OFFSET hoặc G92 Z trong phần G-code chạy của tám file đã tải.
- File hình trụ T0 trước đó dùng lớp đầu 0,25, offset=0. Khác biệt 0,25→0,20 có thể làm giảm dung sai với lỗi Z sẵn có, nhưng T0 đơn 0,20 và nhiều màu 0,20 vẫn có cùng phân nhánh quy trình nên chưa phải giải thích chính.

Các G-code có thể bị ghi đè khi upload cùng tên. File `GE5C mod_ABS_2h10m.gcode` hiện trên máy ghi T0/T3, trong khi người vận hành nhớ những lần T0/T2 trước vẫn tốt; không suy từ file hiện tại để phủ nhận lịch sử T0/T2 hay gán chắc tool cho bản in cũ.

Offset live T0=0; T1=+0,1665; T2=−0,3515; T3=−0,3865; T4=+0,0279 mm. Offset riêng T3/T4 có thể cần đo lại sau khi hệ Z ổn định; không thể từ dấu/giá trị này một mình biết nozzle nào quá thấp.

Trong bản T4 18:37, console có 18 lệnh +0,05 và tám lệnh −0,05, tổng can thiệp +0,50 mm; một số lệnh bắt đầu trước khi vào vật thể. Đây là thao tác thử của người vận hành, không phải phép đo offset đúng hay bằng chứng first layer đã đạt. Bản T4 trước đó có ba lệnh +0,05. Chưa có xác nhận ảnh/chất lượng cuối của T4.

## 6. Ước lượng phần trăm

**Bảng lịch sử trước khi tìm ra part đệm lắp nhầm; không dùng làm đánh giá nguyên nhân hiện hành.**

Đây là phân bổ nghi ngờ nguyên nhân chính để ưu tiên kiểm tra, không phải xác suất thống kê hay tỷ lệ hỏng đo được. Mỗi cột cộng 100%; các lỗi có thể đồng thời tồn tại. Tách hai triệu chứng vì một nguyên nhân không nhất thiết giải thích được cả hai.

| Nhóm nguyên nhân | Lớp đầu sát bàn | QGL đổi lớn/hội tụ lâu | Căn cứ/giới hạn |
|---|---:|---:|---|
| Cơ khí/truyền động Z sau lắp lại, gồm mất bước khi chạy Z nhanh hoặc cạ ở vùng dock; ưu tiên Z2 | 60% | 60% | Liên quan chuỗi đổi tool, cùng nhánh Z2 bù lớn; chưa có đồng hồ so hoặc dấu trượt |
| Ngàm tool/nozzle/gá Cartographer thay đổi khi gắp và dưới tải dây | 15% | 3% | Giải thích mốc sau Touch thay đổi; riêng nozzle không giải thích trực tiếp QGL shuttle |
| Cartographer Scan/Touch thiếu ổn định, drift nhiệt hoặc tín hiệu | 15% | 20% | Coil âm, bù nhiệt bỏ, mẫu Touch ngoại lai 0,454 mm; chưa đo đối chứng độc lập |
| Offset tương đối T3/T4 đã cũ | 5% | 0% | Phù hợp tool đơn, không đủ giải thích T0 sau gắp lại hoặc QGL |
| Đường NTC bàn và ổn định nhiệt gantry/bed | 3% | 5% | Lỗi tín hiệu xác nhận; QGL vẫn lệch lớn ở lượt đọc bàn 80°C ổn định |
| Hình học QGL/gantry_corners chưa đúng vị trí đai thật | 1% | 12% | Có thể gây bù thiếu, nhiều retry; không tự gây lệch trở lại sau hành trình Z |
| Slicer/flow/chất liệu in đang dùng | 1% | 0% | Z=0,20/offset=0 đúng trong các file mới; không giải thích QGL offline khỏi bản in |

Trong nhóm cơ khí dẫn đầu, chưa có căn cứ phân chia một tỷ lệ đáng tin cậy giữa pulley, dây đai, GE5C và mất bước motor. Không coi 60% là xác nhận Z2 hỏng.

## 7. Hình học QGL cần kiểm tra riêng

Live gantry_corners=(-10,−10), (350,350); points theo thứ tự Z/Z1/Z2/Z3 là (20,0), (20,280), (330,280), (330,0). Offset Cartographer Y=35. Theo Klipper, gantry_corners là vị trí hai góc tác động của hệ Z, không phải kích thước bàn hoặc giới hạn XY. Cấu hình mẫu Voron 350 dùng (−60,−10), (410,420), nhưng máy có mod nên phải đo vị trí đai thật theo hệ tọa độ đang dùng và cách plugin xử lý offset trước khi sửa.

Nếu đang dùng góc quá gần nhau so với vị trí đai thật, QGL có thể ngoại suy lệnh bù chưa đủ nên phải lặp. Điều này đáng điều tra cho vấn đề hội tụ lâu; chưa chứng minh nó là nguồn lệch phát sinh sau đổi tool. Không tự thay bằng số stock hoặc tăng retries/tolerance để che tình trạng.

## 8. Phép kiểm tra tách nguyên nhân, chưa thực hiện

1. Kiểm tra cơ khí Z2/GE5C/đai/pulley và khoảng hở đỉnh dock; đồng thời kiểm tra nozzle/ngàm T0 và gá Cartographer. Trước thao tác điện cần ngắt điện phù hợp; gantry cần được đỡ trước khi nới hệ truyền động.
2. Dùng đồng hồ so hoặc tham chiếu vật lý độc lập ở cùng XY/Z, đo chiều cao bốn góc và khe nozzle. Đo trước/sau một khoảng chờ cùng thời lượng, chưa chuyển động, để có mẫu đối chứng drift.
3. So sánh hành trình Z thấp/cao không đổi tool với một vòng T0→T4→T0, cùng nhiệt, cùng điểm trở về và cùng tốc độ đã xác minh an toàn. Không home/QGL/Touch lại giữa hai lần đo vì sẽ che mất sai lệch cần tìm. Không tự đi Z346 khi chưa xác minh khoảng hở mới.
4. Để thử giảm tải, có thể dùng giới hạn Z15 mm/s, gia tốc 150–350 mm/s² dưới giám sát, ghi rõ đây là điều kiện thử và chưa chứng minh tốc độ production. Không cần thử lại ở 80 nếu cơ khí đã có dấu cạ/trượt. Trong lượt này không áp dụng các giá trị thử.
5. Nếu đồng hồ so cũng lệch: khoanh vùng truyền động/bó/trượt/mất bước. Nếu vật lý giữ nguyên nhưng Cartographer báo đổi: ưu tiên probe/gá/Scan/thermal. Nếu gantry/probe giữ nhưng nozzle riêng thay đổi: ưu tiên ngàm/hotend/offset tool.
6. Sau khi đường NTC bàn được sửa và chu kỳ nhiệt đã kiểm chứng, xác minh Touch T0 lặp được khe hở vật lý rồi mới cân offset T3/T4 bằng mẫu first layer cùng XY. Tiếp tục để T1/T2 ngoài bài thử theo tình trạng bảo trì người dùng nêu.

## 9. Drift cấu hình và giới hạn thu thập

- Live scan samples=20 do section override đang comment; repository=200.
- Live QGL retries=10, góc thứ hai (350,350); repository=5, (353,350).
- Scan/Touch model live đã thay sau ngày 01/11; không overwrite bằng SAVE_CONFIG cũ trong Git.
- Live bed max_temp=150, repository=120. Không tự đồng bộ cao hơn.
- T0–T4 CFG, toolchanger-config và prime-lines live bằng repository ở thời điểm thu thập.
- Những lần đọc SSH và Moonraker cuối lượt bị timeout sau khi đã thu thập dữ liệu; không xác minh được trạng thái máy sau thời điểm mất kết nối và không suy là printer shutdown.

Dữ liệu gốc và dẫn xuất nằm cùng thư mục: `state.json`, `detail-state.json`, `console.json`, `history.json`, `klippy.log`, các file CFG/G-code; `qgl-events.json`, `qgl-summary-console-anchored.json`, `touch-samples.json`, `raw-temperatures.json`, `evidence-excerpts.log`. Chưa có đo cơ khí độc lập, ảnh first layer hoặc kết quả thử giảm tốc.

## Nguồn kỹ thuật chính thức

- [Klipper: quad_gantry_level](https://www.klipper3d.org/Config_Reference.html#quad_gantry_level): hình học và thứ tự góc.
- [Voron M8P V2 reference](https://raw.githubusercontent.com/VoronDesign/Voron-2/Voron2.4/firmware/klipper_configurations/M8P/Voron2_M8P-v2.0_config.cfg): tham chiếu tốc độ Z và gantry_corners 350.
- [Voron gantry squaring](https://docs.vorondesign.com/build/mechanical/v2_gantry_squaring.html): liên hệ cơ khí gantry, khớp và first layer.
- [Cartographer FAQ](https://docs.cartographer3d.com/cartographer-probe/faq): coil âm và giới hạn suy luận đối với Touch. Các phần lệnh cũ trên FAQ không được áp dụng thay mã 1.10.1 đang cài.
- [Cartographer coil compensation](https://docs.cartographer3d.com/cartographer-probe/features/coil-temperature-offset-calibration): mục đích bù drift Scan; không thực hiện hiệu chuẩn trong lượt này.
