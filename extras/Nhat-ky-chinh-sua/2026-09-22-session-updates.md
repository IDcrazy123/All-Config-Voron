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
