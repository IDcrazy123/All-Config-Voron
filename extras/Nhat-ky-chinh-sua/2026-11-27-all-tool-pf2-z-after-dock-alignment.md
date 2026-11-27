# Đo Z tương đối T0–T4 sau khi căn lại dock — 2026-11-27

## Nguồn và điều kiện

- Đọc `Voron 5 Tool/AGENTS.md`, trạng thái và `configfile` live qua Moonraker `192.168.1.43:7125` trước chuyển động. Lúc đầu Klipper `ready`, `print_stats=standby`, toolchanger chưa khởi tạo, XYZ chưa home, heater target 0.
- Người vận hành xác nhận gá PF2 luôn lắp và đường G28/QGL không va chạm gá; người vận hành đứng cạnh máy quan sát. Đây là xác nhận cơ khí mới hơn ghi chú cũ yêu cầu tháo gá.
- `INITIALIZE_TOOLCHANGER` xác nhận shuttle rỗng. `QUERY_ENDSTOPS` cho PF2 nhả `open`, nhấn `TRIGGERED`, thả lại `open`. G28 hoàn tất. Đo bằng `CALIBRATE_ALL_Z_OFFSETS CONFIRM=1`, 5 mẫu/tool, vòi 150°C, bàn không gia nhiệt. Macro chỉ đo sơ bộ, không lưu `gcode_z_offset`.
- Trước lượt C, người vận hành vệ sinh các đầu phun, tháo rồi gắn lại T0. G28 hoàn tất. QGL đầu không hội tụ: range 0,050464 → 0,017521 → 0,024010 → 0,026590 mm, sau đó báo `Retries aborting: Probed points range is increasing`. Người vận hành tự chạy lại QGL, đạt 0,007354 mm. Trước lượt D, G28 và QGL chạy lại; QGL đạt 0,008128 mm ở retry 3.
- QGL live dùng vòng tinh `METHOD=scan HORIZONTAL_MOVE_Z=2`, tolerance 0,01; khác file Git hiện hành. Không deploy Git lên máy trong lượt này.
- Sau lượt D, người vận hành xác nhận tiếp tục vệ sinh và lắp lại toàn bộ tool. G28/QGL tiếp theo đạt 0,007406 mm, rồi đo thêm lượt đối chứng E.

## Kết quả PF2 sơ bộ (mm, T0 = 0)

| Lượt | Điều kiện | T0 trigger | T1 | T2 | T3 | T4 |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| A | Trước vệ sinh, chưa QGL | 1,451995 | -0,397595 | -0,293195 | -0,411995 | -0,159195 |
| B | Lặp 1, trước vệ sinh, chưa QGL | 1,447200 | -0,371200 | -0,290000 | -0,365200 | -0,171600 |
| C | Lặp 2, sau vệ sinh, G28/QGL | 1,591403 | -0,405003 | -0,289403 | -0,391803 | -0,219003 |
| D | Lặp 3, sau vệ sinh, G28/QGL | 1,616936 | -0,428936 | -0,325336 | -0,462536 | -0,226136 |
| E | Đối chứng sau vệ sinh lần hai, G28/QGL | 1,828376 | -0,335976 | -0,288376 | -0,371576 | -0,192376 |

Từng nhóm 5 lần kích PF2 trong log có dải 0,004–0,026 mm ở A–D. Sự khác nhau giữa các lượt lớn hơn: T2 ở D lệch khoảng -0,035 mm so với A/B/C/E, nên D là điểm lệch cần loại. T4 A/B khác C/D khoảng 0,05–0,067 mm; C/D chỉ khác 0,007133 mm, nhưng E lại khác C/D khoảng 0,027–0,034 mm. T1 và T3 chưa có cụm đo đủ ổn định để loại một điểm riêng lẻ rồi lấy trung bình. T0 trigger tuyệt đối đổi +0,025533 mm từ C sang D và +0,211440 mm từ D sang E sau G28/QGL; đây là tọa độ frame sau home, không được coi là dịch chuyển cơ khí riêng T0 khi chưa đối chứng.

Người vận hành được báo các điểm bất thường và đã vệ sinh một lần nữa trước E. Sau E, T2 còn cụm hợp lý quanh -0,29 mm; T1/T3/T4 vẫn dao động. Đã dừng để người vận hành kiểm tra nhựa rỉ trên mũi phun, ngàm và gá PF2. Chưa lấy trung bình cuối cho toàn bộ tool, chưa thay offset Z live/Git; Z production vẫn cần kiểm tra lớp đầu từng tool.

## Đối chứng không đổi frame sau lượt E

Người vận hành xác nhận không có nhựa rỉ, đầu phun sạch, ngàm và gá chắc. Không chạy thêm QGL/G28. Với T0 giữ trên shuttle tại 150°C, ba lệnh `PROBE_ZSWITCH SAMPLES=5` liên tiếp cho trigger 1,8200 / 1,8328 / 1,8364 mm (dải 0,0164 mm). Sau đó thả/gắp lại T0 và đo một lần: 1,8412 mm, chỉ +0,0048 mm so với lần trước.

Giữ T3 trên shuttle ở 150°C, ba lần `PROBE_ZSWITCH SAMPLES=5` liên tiếp cho trigger 1,4800 / 1,4896 / 1,4932 mm, tức offset tương đối với T0 đang lưu -0,3564 / -0,3468 / -0,3432 mm (dải 0,0132 mm). Sau khi trả T3 về dock, đo lại T0 như trên rồi gắp T3 lần nữa, T3 trigger 1,4208 mm và offset -0,4204 mm. So với lần T3 ngay trước khi thả/gắp, chênh -0,0772 mm; T0 tham chiếu chỉ chênh +0,0048 mm. Cảm biến vẫn xác nhận `detected_tool_number=3` cả hai lần gắp. Số liệu này chỉ ra thay đổi cao độ của T3 gắn trên shuttle sau chu trình dock, nhưng chưa xác định chi tiết cơ khí nào gây ra; người vận hành đang kiểm tra mặt ghép, ngàm, hotend/nozzle và đường gắp T3.

Người vận hành xác nhận T3 **rít khi lắp bằng tay vào shuttle**, không chỉ trong đường gắp/thả dock. Vì vậy không đổi tọa độ dock để xử lý hiện tượng này; chờ kiểm tra và chỉnh mặt ghép/chốt dẫn hướng T3–shuttle để T3 lắp nhẹ và ngồi phẳng lặp lại.

Người vận hành chưa xử lý được chỗ rít và yêu cầu đo thêm để xác minh khả năng sử dụng. Trong cùng frame, mỗi chu kỳ thả/gắp đo T0 rồi T3 (mỗi tool 5 lần chạm ở 150°C):

| Chu kỳ | T0 trigger | T3 trigger | T3 tương đối T0 |
| --- | ---: | ---: | ---: |
| 1 | 1,8104 | 1,4676 | -0,3428 |
| 2 | 1,8692 | 1,5176 | -0,3516 |
| 3 | 1,8196 | 1,5108 | -0,3088 |

Dải offset T3 qua ba lần gắp là 0,0428 mm, vượt xa dải khi giữ nguyên một lần gắp (0,0132 mm). Cả ba lần T3 được cảm biến nhận diện. Thêm đối chứng tái gắp trước đó có chênh 0,0772 mm. **T3 chưa đủ độ lặp cơ khí để dùng cho in hoặc lưu Z offset**; cần xử lý chỗ rít/mặt ghép rồi đo lại nhiều lần. Không lấy trung bình ba giá trị này làm offset.

Sau các đối chứng, `AXISCOPE_FINISH_GCODE` trả về T0, heater target 0, crash detection bật lại. Không áp bất kỳ số Z sơ bộ nào vào production.

## Đồng bộ dock với máy live

Các tọa độ dock đã được người vận hành căn trên máy và được live `configfile` xác nhận. Chỉ đồng bộ các giá trị này vào file Git `config/toolchanger/tools/T0.cfg` đến `T4.cfg`, để lần deploy sau không đưa dock về tọa độ cũ:

| Tool | Git cũ X/Y | Live và Git mới X/Y | Z giữ nguyên |
| --- | ---: | ---: | ---: |
| T0 | 30,20 / 0 | 30,70 / 0 | 333 |
| T1 | 104 / 0 | 102 / 0 | 330 |
| T2 | 176 / 0 | 175 / 0 | 331 |
| T3 | 249,5 / 0 | 247 / 0,5 | 331 |
| T4 | 321,5 / 0 | 319,5 / 0,5 | 332 |

Backup file Git trước sửa: `extras/backups/pre-dock-sync-20261127/`. Chưa reload hoặc triển khai production; tọa độ live đã có sẵn trước khi đo. Các lượt gắp/thả T0–T4 đều được xác nhận qua `detected_tool_number` trong phép đo.

## Trạng thái chờ

Sau ba chu kỳ T3: Klipper `ready`, `print_stats=standby`, `_PRINT_STATE=idle`, recovery=0, XYZ homed, QGL applied, T0 active/detected tại X30,7 Y120 Z15, mọi heater target 0. Chờ người vận hành xử lý hiện tượng T3 rít khi lắp tay và kiểm tra lại độ lặp sau gắp; T1/T4 còn dao động. Nếu không hội tụ, không áp offset sơ bộ vào production.
