# Nhật ký — 2026-09-22

## 1. Đánh giá ba lượt SexBolt so với offset production

### Triệu chứng và nguồn dữ liệu

- Người vận hành cung cấp ba log có `CHECK_OFFSETS` lúc 15:55, 16:13 và 16:23. Các nhãn thời gian bên dưới chỉ thời điểm kiểm tra kết quả, không phải tất cả đều là thời điểm kết thúc phép đo.
- Log 15:55: [dữ liệu gốc](<C:/Users/batca/.codex/attachments/717bd7eb-59ab-4426-a61a-44b9e042c5f8/Văn bản đã dán.txt>).
- Log 16:13: [dữ liệu gốc](<C:/Users/batca/.codex/attachments/da7949bb-2014-4996-8b21-47e935bc6c88/Văn bản đã dán.txt>).
- Log 16:23: [dữ liệu gốc](<C:/Users/batca/.codex/attachments/d89e107e-4d94-482b-b605-7b38c78a4768/Văn bản đã dán.txt>).
- Cả ba macro báo hoàn tất; tuy nhiên lượt cuối có thay đổi Z đồng loạt và bất thường tiếp xúc tại T0.

### Đối chiếu trực tiếp trên máy

- Snapshot đọc qua Moonraker lúc 16:26:24: Klipper `ready`, máy `standby/Ready`, toolchanger `ready`, T0 active/detected, target bàn và cả năm hotend bằng 0.
- `save_config_pending=true`; offset runtime T1-T4 đúng bằng lượt 16:23. Chưa SAVE_CONFIG không có nghĩa bộ production cũ vẫn đang được sử dụng trong runtime.
- File `printer.cfg` trên máy và `configfile.settings` vẫn giữ nguyên bộ production bên dưới, trùng repository.
- Cấu hình đang nạp: `spread: 3.5`, `lower_z: 0.3`, `lift_z: 1.0`, `samples: 5`, `samples_result: median`, `samples_tolerance: 0.15`, `samples_tolerance_retries: 2`, `sample_retract_dist: 2.0`.

### Bảng kết quả

Tất cả bộ ba là X/Y/Z, đơn vị mm. Production XY đến từ Axiscope; production Z đã tinh chỉnh bằng bản in Oxplow/first-layer. Chênh lệch với production không phải phép đo repeatability cùng phương pháp.

| Tool | Production đã lưu | 15:55 | 16:13 | 16:23 / runtime lúc kiểm tra |
| --- | --- | --- | --- | --- |
| T1 | `-0.139/-0.341/+0.2465` | `-0.187500/-0.196875/+0.102000` | `-0.159375/-0.203125/+0.076000` | `-0.259375/-0.153125/-0.184000` |
| T2 | `+1.095/-0.090/-0.2715` | `+1.093750/+0.068750/-0.314000` | `+1.059375/+0.043750/-0.314000` | `+1.015625/+0.106250/-0.576000` |
| T3 | `+0.003/+0.369/-0.2465` | `-0.046875/+0.387500/-0.238000` | `-0.015625/+0.343750/-0.238000` | `-0.125000/+0.409375/-0.506000` |
| T4 | `+0.213/-0.007/+0.1079` | `+0.162500/-0.121875/+0.092000` | `+0.193750/-0.112500/+0.094000` | `+0.100000/-0.065625/-0.168000` |

### Hai lượt đầu

- Không có retry trong hai log đầu. Chênh tối đa giữa hai lượt: X `0.034375`, Y `0.043750`, Z `0.026` mm. Z T2/T3 không đổi, T4 đổi `0.002`, T1 đổi `0.026` mm.
- Range lớn nhất của một nhóm fine-probe được chấp nhận: lượt 15:55 là `0.10625` mm ở cạnh X dương của T4; lượt 16:13 là `0.04375` mm ở cạnh Y âm của T0.
- Bề rộng tiếp xúc hiệu dụng theo X đổi từ khoảng `3.83-4.06` sang `3.41-3.49` mm giữa hai lượt trên toàn bộ tool. Đây là khoảng cách hai median cạnh dò, không phải đường kính vật lý quả bi. Điều kiện tiếp xúc có thể đã thay đổi; hai bộ midpoint tương đối gần nhau chưa chứng minh độ chính xác tuyệt đối.

Trung bình hai lượt đầu trừ production, chỉ dùng để so sánh, không đề xuất áp dụng:

| Tool | Delta X | Delta Y | Delta Z |
| --- | ---: | ---: | ---: |
| T1 | -0.0344375 | +0.1410000 | -0.1575 |
| T2 | -0.0184375 | +0.1462500 | -0.0425 |
| T3 | -0.0342500 | -0.0033750 | +0.0085 |
| T4 | -0.0348750 | -0.1101875 | -0.0149 |

### Bất thường ở lượt 16:23

- Delta Z so với lượt 16:13: T1 `-0.260`, T2 `-0.262`, T3 `-0.268`, T4 `-0.262` mm. Dịch chung trung bình `-0.263` mm; phần dư chỉ `+0.003/+0.001/-0.005/+0.001` mm. Quan hệ Z giữa T1-T4 chỉ đổi tối đa `0.008` mm, trong khi cả nhóm đổi lớn so với T0.
- T0 fine-probe cạnh Y âm đầu tiên có hai điểm `-7.315625 -> -6.796875`, range `0.51875` mm, phải retry. Sau retry, median Y âm là `-6.465625`; median Y dương là `-4.771875`.
- Bề rộng tiếp xúc hiệu dụng Y của T0 co từ `3.41875` xuống `1.69375` mm (giảm khoảng 50.5%). T1-T4 vẫn có bề rộng Y khoảng `3.44-3.62` mm.
- T0 cạnh Y dương trôi tuần tự `-4.696875 -> -4.746875 -> -4.771875 -> -4.784375 -> -4.803125`. Range `0.10625` mm vẫn nhỏ hơn tolerance 0.15 nên macro có thể báo hoàn tất mặc dù điều kiện tiếp xúc đã đổi.
- Bề rộng X T1-T4 trong lượt cuối tăng lên khoảng `3.91-4.09` mm, trong khi T0 vẫn khoảng `3.44` mm; đây là dấu hiệu bổ sung của thay đổi điều kiện tiếp xúc trong chu trình.

### Nguyên nhân và giới hạn kết luận

- Đã xác nhận: lượt cuối không lặp lại được tham chiếu đo của lượt trước; riêng chuỗi tiếp xúc T0 có biến động lớn. Không nên gộp trung bình cả ba lượt hoặc chọn lượt cuối chỉ vì macro báo hoàn tất.
- Nghi vấn: trạng thái lắp T0, bề mặt nozzle/sock/nhựa dư, hoặc SexBolt dịch/đổi trạng thái tiếp xúc giữa lúc đo T0 và T1-T4. Chưa xác nhận chi tiết phần cứng nào từ log; đã hỏi người vận hành về thao tác giữa các lượt.
- Không dùng riêng chênh tọa độ sensor Z tuyệt đối giữa các lượt để suy ra chiều cao bi thay đổi: mỗi lượt có G28 và hệ tọa độ Z có thể khác.
- Code đã đối chiếu trong phiên trước tính offset bằng `location - sensor_location`, không cộng dồn offset runtime cũ.

### Hướng xử lý và kết quả

- Chỉ đọc dữ liệu máy in, phân tích và ghi nhật ký; không gửi G-code, restart, sửa cấu hình hoặc SAVE_CONFIG trong phiên này.
- Giữ bộ production đã lưu làm mốc. Lượt 16:23 đang active trong runtime và lệch Z so với production lần lượt `-0.4305/-0.3045/-0.2595/-0.2759` mm; chưa nên dùng bộ này để in.
- Khi kết thúc thử nghiệm, người vận hành có thể FIRMWARE_RESTART lúc máy rảnh để bỏ offset pending và nạp lại bộ đã lưu; sau restart cần home theo quy trình trước chuyển động.
- Kiểm tra tiếp xúc T0 và độ hồi của SexBolt; sau khi điều kiện cơ khí ổn định, đo lại T0 ở đầu/cuối chu trình để kiểm chứng tham chiếu. Không tăng tolerance để che bước nhảy, không bù tay +0.263 vào bộ lỗi.
- Chỉ hai lượt đầu có mức lặp tương đối khả quan. Chưa đủ dữ liệu để thay offset production, nhất là Y T1/T2/T4 và Z T1 vốn đã được tinh chỉnh theo bản in.

## 2. Chuyển SexBolt vào tâm bàn và khôi phục spread/lower_z mặc định

### Mục tiêu và xác nhận của người vận hành

- Chuyển mục tiêu đo từ `X80 Y-5.5` tới tâm bàn theo quy ước hiện tại `X174 Y168` cho đế giữ mới.
- Người vận hành xác nhận đế chưa lắp và `Z55` là độ cao an toàn. Chưa xác nhận tâm bi thực tế hoặc Z nozzle T0 chạm bi của đế mới.
- Theo yêu cầu bổ sung, đưa `spread` và `lower_z` về mặc định. Đọc trực tiếp `/home/voron/klipper/klippy/extras/tools_calibrate.py`: `spread` mặc định `5.0`, `lower_z` mặc định `0.5`.

### File đã sửa đổi và sao lưu

- `config/Printer-Setup/calibration-probe.cfg`: thông số dò, báo cáo trạng thái động, đường tiếp cận và chốt chặn chiều cao.
- `config/toolchanger/toolchanger-config.cfg`: tọa độ mục tiêu và biến chiều cao của đế mới.
- README EN/VI ở gốc và `config/`, cùng hướng dẫn StealthChanger EN/VI: đồng bộ thông số và quy trình đế tháo rời.
- [Sao lưu repository và live trước thay đổi](<D:/Desktop/All-Config-Voron-main/Voron 5 Tool/extras/backups/pre-sexbolt-bed-center-20260922-175811/>). Các bản live giữ nguyên override cũ `lower_z: 0.3`, `variable_z: 12.0`; bản repository trước sửa là `1.0` và `18.0`.
- Bản sao lưu độc lập trên máy: `/home/voron/printer_data/config_backups/sexbolt-bed-center-20260922-175811/original/`, gồm hai file cấu hình và `printer.cfg` nguyên trạng. Đối chiếu SHA256 trước triển khai; không ghi đè bản sao lưu có sẵn.

### Chi tiết và bảo vệ đường chạy

- `_CALIBRATION_SWITCH`: `x: 174`, `y: 168`, `z: 55`; `probe_z: -1`, `contact_z: -1` là dấu hiệu chưa đo, không phải tọa độ được phép dò.
- `spread: 3.5 -> 5.0`; `lower_z: 0.3 live / 1.0 repository -> 0.5`. Các điểm bắt đầu danh nghĩa `X169/179`, `Y163/173` không còn vướng giới hạn mép trước như vị trí cũ.
- `CALIBRATE_MOVE_OVER_PROBE` mặc định nâng tới `max(Z hiện tại, 55)` trước XY, tới tâm rồi dừng ở Z55, không dò. Chỉ nhánh `PROBE=1` mới xuống độ cao bắt đầu dò đã đo.
- `CALIBRATE_ALL_OFFSETS` chặn trước chọn tool, gia nhiệt và chuyển động nếu chưa có `0 <= contact_z < probe_z <= 55`; vẫn giữ kiểm tra home/toolchanger. Không dùng lại Z12 của đế cũ.
- Review đường đổi tool phát hiện backend chỉ nâng `contact Z + final_lift_z (6)` sau đo; KTC dropoff sau đó nâng thêm 1 mm rồi đi ngang tới Y120, chưa đảm bảo thoát đế ở Z55.
- Thêm `_CALIBRATE_SAFE_TRANSIT` nâng thẳng tại XY hiện tại, đánh giá Z runtime mỗi lần gọi, trước mọi `SELECT_TOOL` trong chu trình (6 lần khi đo 5 tool). Đã đối chiếu đường RESTORE trong source KTC đang cài.
- Không sửa file KTC readonly, homing, mesh, PID hoặc offset production. Phải tháo đế trước `G28`, QGL, Cartographer Touch, mesh và in vì đường chạy đi qua vùng tâm bàn.

### Kiểm tra và triển khai

- Parse riêng hai file cấu hình và biên dịch 12 template bằng Jinja `2.11.3` của môi trường Klipper trên máy: đạt, không gửi lệnh chuyển động.
- Render offline: đúng mặc định 5.0/0.5; giữ độ cao hiện tại nếu cao hơn 55; chặn chưa home/chưa khởi tạo toolchanger/chưa đo chiều cao/chiều cao sai; 5 lần tiếp cận dò và nâng an toàn trước cả 6 lần chọn tool đều đạt.
- `git diff --check`: đạt. Chỉ triển khai hai file CFG, không chạy trình cài đặt đồng bộ rộng.
- Kiểm tra ngay trước restart: Klipper ready, không in/paused, idle Ready, target bàn và cả 5 hotend bằng 0. Đã thông báo restart bỏ bộ offset thử nghiệm chưa lưu.
- `FIRMWARE_RESTART` thành công; Klipper trở lại `ready`, nạp đúng `spread: 5.0`, `lower_z: 0.5`, `X174 Y168 Z55`, hai chiều cao chưa đo bằng `-1`.
- `save_config_pending=false`; offset runtime T1-T4 trở lại đúng bộ production ở mục 1. Không chạy `SAVE_CONFIG`.
- SHA256 hai file live trùng repository: calibration `da3142150b0354c74cae31bb9f4ccc0651affc909d36e290f87764099e19cf8c`, toolchanger `b47ab00367c24f89fd02d978563e16e3e1a4256d880261a521b0fe2ceb019d6f`.
- `printer.cfg` giữ nguyên SHA256 `8d6b2958bab328e8afeace4b0d6aa11fb2f05854ceef9f738e9f083d978878b9` trước/sau triển khai.

### Kết quả và việc còn lại

- Đã đồng bộ cấu hình, chưa chạy home, gia nhiệt, đổi tool, phép đo hoặc thử in. Sau restart máy chưa home và toolchanger `uninitialized` là trạng thái chờ khởi tạo, không phải lỗi nạp cấu hình.
- Home với mặt bàn không có đế; đưa đầu in lên độ cao an toàn và ra khỏi đường lắp, rồi mới lắp đế. Căn tâm bi theo nozzle T0 tại X174/Y168, kiểm tra công tắc bằng `SEXBOLT_QUERY`, xác định Z tiếp xúc và Z bắt đầu dò trước khi mở khóa đo tự động.
- Các thay đổi Printables/Oxplow có sẵn và file `AGENTS.md` chưa theo dõi không thuộc tác vụ, được giữ nguyên và không stage.

## 3. Chẩn đoán chốt chặn chiều cao SexBolt lúc 18:16

### Triệu chứng và đối chiếu chỉ đọc

- Người vận hành báo `Center SexBolt contact_z/probe_z are unconfirmed` khi chạy `CALIBRATE_ALL_OFFSETS`, sau home/QGL; đồng thời cho biết đã tự đổi `spread: 7`, `lower_z: 1`.
- Đọc [klippy.log trực tiếp trên máy](http://192.168.1.43/server/files/logs/klippy.log), hai file cấu hình live và Moonraker: đúng `spread: 7.0`, `lower_z: 1.0` đã được nạp. Không ghi đè thay đổi của người vận hành.
- `_CALIBRATION_SWITCH` runtime là X174/Y168/Z55, `contact_z: -1`; `probe_z` không tồn tại vì dòng `variable_probe_z` đã bị comment trong file live.
- QGL trong log hoàn tất với range `0.002989 < 0.007500`; lỗi được phát ra tại bước render guard chiều cao của macro, trước bất kỳ lệnh đo nào, không phải lỗi tolerance QGL hoặc do spread/lower_z.

### Nguyên nhân và hướng xử lý

- Z55 chỉ là độ cao di chuyển được xác nhận; chưa có Z tiếp xúc bi và Z bắt đầu dò của đế mới. `contact_z: -1` chủ động khóa chu trình. Comment `probe_z` không bỏ được khóa; sau khi sửa contact_z còn có thể gây lỗi biến thiếu.
- Cần xác nhận Z nozzle T0 chạm đỉnh bi thực tế, khôi phục biến `probe_z` và đặt độ cao bắt đầu dò đã kiểm chứng sao cho `0 <= contact_z < probe_z <= 55`. Không tự gán Z55 làm chiều cao tiếp xúc hoặc dùng lại Z12 của đế cũ.
- Snapshot: Klipper ready, XYZ đã home, Z55, nhưng toolchanger `uninitialized`/active tool -1. Source `toolchanger.py::_handle_command_error` xóa active tool và đưa trạng thái về uninitialized khi có command error; cần khởi tạo/xác nhận lại tool sau khi xử lý guard, không nhầm đây là bằng chứng tool rơi.
- Phiên này chỉ đọc máy in và ghi nhật ký; không sửa cấu hình, restart, khởi tạo toolchanger hoặc gửi chuyển động. Chờ số đo chiều cao đế mới từ người vận hành.

## 4. Tiếp nhận chiều cao bi mới khoảng Z50

- Người vận hành báo nozzle chạm bi khoảng Z50; đây là số quan sát gần đúng, chưa phải kết quả probe tự động.
- Snapshot và source live được kiểm tra chỉ đọc: máy vẫn XYZ homed ở Z55, toolchanger uninitialized, `spread: 7`, `lower_z: 1`, `contact_z: -1`, `probe_z` bị comment.
- Đề xuất `contact_z: -1 -> 50.0` (tham chiếu quan sát) và khôi phục `probe_z: 55.0`, giữ transit Z55 đã được người vận hành xác nhận. Không chọn một độ cao tiếp cận mới thấp hơn Z55 khi chưa kiểm chứng khoảng hở.
- Source `locate_sensor` tự dò Z thực tế trước khi dò XY; `contact_z` của macro không được dùng làm kết quả đo hoặc offset. `run_probe` hiện có giới hạn mặc định 100 mm rồi chặn theo giới hạn trục, không phải 4 mm dù cấu hình đọc được `max_travel: 4`. Vì vậy khoảng 5 mm từ Z55 tới Z50 không bị giới hạn 4 mm; đồng thời Z50 không phải chốt dừng nếu công tắc không kích hoạt.
- Cần kiểm tra công tắc nhả/nhấn và căn tâm bi, giữ lần đo đầu có người giám sát. `lower_z: 1` là độ hạ so với Z tiếp xúc vừa đo khi dò cạnh, không phải độ cao bắt đầu dò Z.
- Chờ xác nhận áp dụng cặp chiều cao trên; chưa sửa cấu hình hoặc gửi bất kỳ lệnh G-code nào trong lượt này.

## 5. Đánh giá ba lượt SexBolt giữa bàn 18:37 / 19:12 / 19:40

### Phạm vi và nguồn dữ liệu

- Người vận hành yêu cầu so sánh kết quả đo với giá trị gốc của máy; không yêu cầu áp dụng offset.
- [Log 18:37](<C:/Users/batca/.codex/attachments/49ed18ba-e83f-4755-99f3-192aa6d956d3/Văn bản đã dán.txt>), [log 19:12](<C:/Users/batca/.codex/attachments/985be6d9-1a77-4f2e-9c69-a73470f6ada8/Văn bản đã dán.txt>), [log 19:40](<C:/Users/batca/.codex/attachments/52fe5bce-82ea-4437-8e6c-6857743fd38f/Văn bản đã dán.txt>). Nhãn thời gian là lúc CHECK_OFFSETS; từng chu trình kết thúc khoảng 18:36, 19:12, 19:39.
- Dùng kết quả offset 6 chữ số trong từng log, không dùng bản CHECK_OFFSETS làm tròn 4 chữ số để tính thống kê. Các dòng console đảo thứ tự thời gian; đã đọc lại theo trình tự thực khi phân tích retry.
- Đối chiếu trực tiếp lúc 19:55:36: `printer.cfg` và `configfile.settings` vẫn giữ nguyên bộ production ở mục 1. SHA256 `printer.cfg` không đổi: `8d6b2958bab328e8afeace4b0d6aa11fb2f05854ceef9f738e9f083d978878b9`.
- Live đã có `contact_z: 50`, `probe_z: 55`, transit Z55, XY174/168; `spread: 7`, `lower_z: 0.7`. Đây là các chỉnh sửa trên máy sau phiên trước, không phải thay đổi do phiên đánh giá này thực hiện.
- Snapshot có `idle_timeout: Printing`, hotend T3 target150; pending T1/T2 đã khác lượt19:40 trong khi T3/T4 còn trùng. Có dấu hiệu một lượt mới đang tiến hành: không trộn snapshot runtime này vào ba kết quả hoàn tất được cung cấp, không restart hay can thiệp.

### Bảng giá trị gốc và ba lượt

Các bộ ba bên dưới là X / Y / Z, đơn vị mm. T0 luôn là mốc tương đối `(0,0,0)`, không có nghĩa tham chiếu T0 không thể bị sai hoặc dịch chuyển.

| Tool | Production đã lưu | 18:37 | 19:12 | 19:40 |
| --- | --- | --- | --- | --- |
| T1 | `-0.139/-0.341/+0.2465` | `-0.156250/-0.318750/+0.242000` | `-0.150000/-0.328125/+0.212000` | `-0.168750/-0.306250/+0.220000` |
| T2 | `+1.095/-0.090/-0.2715` | `+1.084375/+0.056250/-0.284000` | `+1.087500/+0.059375/-0.304000` | `+1.065625/+0.043750/-0.286000` |
| T3 | `+0.003/+0.369/-0.2465` | `-0.012500/+0.453125/-0.232000` | `+0.006250/+0.087500/-0.254000` | `-0.009375/+0.409375/-0.230000` |
| T4 | `+0.213/-0.007/+0.1079` | `+0.196875/+0.006250/+0.086000` | `+0.159375/-0.518750/+0.056000` | `+0.171875/-0.021875/+0.076000` |

Chênh lệch lượt 19:40 trừ production (không phải giá trị đề xuất cộng thêm):

| Tool | Delta X | Delta Y | Delta Z |
| --- | ---: | ---: | ---: |
| T1 | -0.029750 | +0.034750 | -0.026500 |
| T2 | -0.029375 | +0.133750 | -0.014500 |
| T3 | -0.012375 | +0.040375 | +0.016500 |
| T4 | -0.041125 | -0.014875 | -0.031900 |

### Chất lượng từng lượt và dấu hiệu bất thường

- **18:37:** đủ150 contact, không retry; mỗi tool có5 điểm coarse và25 điểm fine. Range nhóm Z lớn nhất0.006 mm; nhóm XY lớn nhất0.0875 mm tại T3 cạnh Y thấp. Bề rộng tiếp xúc hiệu dụng X của5tool khoảng6.8625–6.96875, Y6.60625–6.6875 mm, không thấy T0 bị co hẹp riêng như lượt16:23. Đây là lượt ít dấu hiệu bất thường nhất trong ba log, chưa phải bằng chứng chính xác tuyệt đối.
- **19:12:** có1 retry,155 contact. T3 cạnh Y cao theo thứ tự thời gian: `171.825 -> 171.8125 -> 171.750 -> 171.7125 -> 171.08125`, range0.74375 mm. Sau retry, median nhóm mới171.14375 với range0.100 mm; macro chấp nhận nhóm mới nhưng điểm tiếp xúc đã thay đổi lớn so với đầu nhóm.
- Y T3 của19:12 giảm0.365625 mm so18:37; Y T4 đo sau đó giảm0.525 mm. T1/T2 Y chỉ đổi-0.009375/+0.003125 mm. Đây không phải dịch Y đồng đều của cả lượt, mà tập trung từ quá trình đo T3 trở đi. Dữ liệu gợi ý đế/bi hoặc điều kiện tiếp xúc thay đổi giữa chu trình; chưa xác nhận bộ phận cơ khí nào. Không lấy Y T3/T4 của lượt này làm ứng viên production.
- **19:40:** có1 retry,152 contact. Ngay fine X thấp của T0, hai điểm `170.434375 -> 171.915625` cách nhau1.48125 mm, sau đó retry. Nhóm được nhận sau retry có range0.05 mm, nhưng bước nhảy trước đó không thể bị bỏ qua chỉ vì chu trình báo complete.
- T0 lượt19:40 coarse midpoint X173.38125 khác final midpoint X174.828125 tới1.446875 mm. Fine Z và Y vẫn được đo tại X173.38125; source chỉ tính midpoint X mới sau khi hoàn tất bốn cạnh, không đo lại Z/Y tại X174.828125 trong lượt đó. Vì vậy tham chiếu T0 của lượt cuối chưa sạch dù offset cuối khá gần baseline.
- T0 lượt19:40 có bề rộng Y hiệu dụng4.94375 mm, trong khi T1–T4 khoảng5.74375–5.79375 mm. Có thể liên quan đo một lát cắt lệch tâm hoặc điều kiện tiếp xúc thay đổi; không khẳng định đã đo đúng đường kính vật lý quả bi.

### Độ biến thiên giữa các lượt

Range max-min, không gọi đây là repeatability thuần túy vì điều kiện cấu hình đã thay đổi:

| Tool | Range X | Range Y | Range Z |
| --- | ---: | ---: | ---: |
| T1 | 0.018750 | 0.021875 | 0.030000 |
| T2 | 0.021875 | 0.015625 | 0.020000 |
| T3 | 0.018750 | 0.365625 | 0.024000 |
| T4 | 0.037500 | 0.525000 | 0.030000 |

- So riêng18:37 và19:40: chênh tối đa X0.025, Y0.04375, Z0.022 mm. Đây là đối chiếu hai lượt, không đủ để loại mọi ảnh hưởng của bất thường T0 trong lượt cuối.
- Log18:37/19:12 có Z dò cạnh thấp hơn Z fine tương ứng1.0 mm; log19:40 là0.7 mm, khớp cấu hình live. Bề rộng tiếp xúc giảm khi đổi độ hạ là thay đổi hình học đo dự kiến, không tự chứng minh đế đã dịch.
- Y T2 lặp trong khoảng+0.04375 đến+0.059375, trong khi production là-0.090: chênh có cùng chiều+0.13375 đến+0.149375 mm. Đây là khác biệt cần kiểm chứng bằng mẫu căn XY T0/T2, không kết luận bộ cũ sai chỉ từ độ lặp của SexBolt.
- Z ba lượt mới biến thiên tối đa0.030 mm, không có bước dịch chung khoảng0.263 mm như lượt16:23; mức độ bất thường Z đã nhỏ hơn trong dữ liệu này. Tuy nhiên sai lệch0.02–0.03 mm vẫn có thể ảnh hưởng first layer. Production Z vốn đã tinh chỉnh bằng bản in, khác với phép đo tiếp xúc tương đối.

### Kết luận và việc tiếp theo

- X/Z nhìn chung gần bộ production hơn các lượt bất thường trước đó, nhưng chuỗi mới vẫn chưa đủ cơ sở thay toàn bộ offset đã lưu. Không trung bình cả ba lượt: lượt19:12 có lỗi Y rõ, lượt19:40 có vấn đề tham chiếu T0 và khác lower_z.
- Giữ cố định cấu hình và cách lắp đế trong các lượt kiểm tra tiếp theo; kiểm tra độ giữ đế/bi, dây kéo và tiếp xúc nozzle, đồng thời quan sát T0 đầu/cuối để phát hiện tham chiếu dịch. Không tăng tolerance để che các bước nhảy.
- Cần các lượt đầy đủ liên tiếp không retry/bước nhảy, rồi xác minh bằng mẫu in XY (ưu tiên T2 Y) và first-layer Z trước khi thay production. Kết quả complete hoặc năm mẫu cuối khít không bảo đảm toàn bộ chu trình đáng tin.
- Chỉ đọc máy in, phân tích và ghi nhật ký; không sửa CFG, gửi G-code, restart, SAVE_CONFIG hoặc áp dụng offset. Offset runtime/pending đang khác production; chưa SAVE_CONFIG không có nghĩa máy đang dùng bộ production cũ.

## 6. Đối chiếu riêng bộ 18:37 với bản đã lưu

- Theo yêu cầu tiếp theo, kiểm tra lại `configfile.settings` qua Moonraker lúc 20:03:53: offset đã lưu T1–T4 vẫn là bộ production trong bảng mục5; `save_config_pending=false` tại snapshot này.
- Chênh lệch dưới đây bằng **kết quả18:37 trừ giá trị đã lưu**, đơn vị mm, không phải giá trị tự động áp thêm:

| Tool | Delta X | Delta Y | Delta Z |
| --- | ---: | ---: | ---: |
| T1 | -0.017250 | +0.022250 | -0.004500 |
| T2 | -0.010625 | +0.146250 | -0.012500 |
| T3 | -0.015500 | +0.084125 | +0.014500 |
| T4 | -0.016125 | +0.013250 | -0.021900 |

- X của cả bốn tool rất gần bản đã lưu, chênh tuyệt đối0.010625–0.017250 mm. Z chênh tối đa0.0219 mm tại T4; riêng T1 chỉ0.0045 mm. Khác biệt nổi bật là Y T2(+0.14625 mm), tiếp theo Y T3(+0.084125 mm).
- Lượt18:37 không retry và có chất lượng nội bộ tốt hơn hai lượt sau, nhưng không đủ để xác nhận thay bộ production. Giữ Z đã tinh chỉnh bằng bản in, ưu tiên kiểm chứng XY T0/T2 và T0/T3 bằng mẫu in cùng các lượt đo lặp cùng cấu hình.
- Chỉ đọc dữ liệu máy và ghi nhật ký; không sửa cấu hình, áp dụng offset hoặc gửi G-code.
