# Lọc cảm biến nhựa cho T0–T4 — 30/10/2026

Theo yêu cầu khắc phục T2 báo hết nhựa khi vẫn còn sợi, sau đó mở rộng cho cả năm tool, đã triển khai native **debounce_delay: 0.5** vào từng filament_switch_sensor. Giá trị hiệu lực trước đó là 0. Không tắt cảm biến hoặc bỏ chức năng dừng khi hết nhựa.

## Vì sao thay đổi này có ích

Log T2 trước đó có một lần pause giả và một lần tín hiệu tự hồi rồi được lọc. Cấu hình cũ chỉ có event_delay=0,5 và một phép kiểm tra lại sau 0,5 giây. Event delay không yêu cầu input ổn định liên tục. Ngoài ra, insert_gcode của Klipper đang cài chỉ chạy ngoài trạng thái idle_timeout Printing, nên không thể dựa vào callback cắm lại để hủy xác nhận khi đang in.

Native debounce chạy trước runout helper: chỉ chuyển trạng thái logic sau khi input giữ nguyên đủ 0,5 giây. Các xung ngắn và chuỗi chập chờn ngắn không lọt xuống handler. Cả chiều hết nhựa và cắm lại đều thêm thời gian ổn định; đường pause khi mất nhựa thật vẫn giữ, cùng delayed confirmation và guard tool active/đang in. Đây là cơ chế được mô tả trong [tài liệu Klipper](https://www.klipper3d.org/Config_Reference.html#filament_switch_sensor), đồng thời đã đối chiếu nguồn Python thực tế trên máy.

## Phạm vi thay đổi

| Tool | File production | Pin giữ nguyên | Debounce cũ→mới |
|---|---|---|---|
| T0 | toolchanger/tools/T0.cfg | ^EBB0:PB9 | 0→0,5 giây |
| T1 | toolchanger/tools/T1.cfg | ^EBB1:PB9 | 0→0,5 giây |
| T2 | toolchanger/tools/T2.cfg | ^EBB2:PB8 | 0→0,5 giây |
| T3 | toolchanger/tools/T3.cfg | ^EBB3:PB9 | 0→0,5 giây |
| T4 | toolchanger/tools/T4.cfg | ^EBB4:PB9 | 0→0,5 giây |

Mỗi file chỉ thêm một comment tiếng Anh và một dòng debounce_delay. Không đổi event_delay, pause_delay, delayed confirmation, macro runout/insert, tool guard, dock, offsets, heater hoặc Python runtime. Không triển khai nguyên repository vì các model/samples Cartographer, retries và heater limit live còn khác Git.

## Triển khai và kiểm tra

- Trước ghi/reload xác nhận máy thực sự idle, không pause/recovery/drying/heatup, không chuyển động chờ, tool active/detected khớp; mọi target/power heater bằng 0. Toolchanger rỗng/uninitialized sau reload trước được chấp nhận chỉ khi cả active và detected đều -1; không khởi tạo hay gắp tool để đổi cấu hình.
- Đọc lại file live, kiểm tra SHA256 trước ghi; backup mới tại máy và repo, ghi atomic và kiểm tra byte/diff. Recheck trạng thái và hash trước reload.
- T2 được triển khai trước lúc **21:04:48**, xác minh **21:05:22**, một RESTART. Khi người dùng mở rộng phạm vi, bốn file còn lại được triển khai lúc **21:07:55**, thêm một RESTART; T2 không bị ghi lại. Tổng hai lần reload theo hai giai đoạn, không có vòng tự lặp restart.
- **21:08:28 UTC+07:** Klipper Ready, không cảnh báo config, năm cảm biến đều enabled=true/filament_detected=true. QUERY_FILAMENT_SENSOR của T0–T4 đều báo có nhựa. Năm file live khớp byte với repo; so toàn bộ configfile.settings từ đầu tác vụ chỉ khác năm giá trị debounce_delay 0→0,5. Các settings khác giữ nguyên.
- ConfigParser và git diff --check đạt. Replay trực tiếp lớp DebounceButton đang cài với reactor giả lập đạt bốn trường hợp: xung giả 125 ms bị bỏ; chuỗi chập chờn bị bỏ; vắng liên tục được nhận sau 500 ms; có liên tục được nhận sau 500 ms. Không dùng replay làm bằng chứng đã thử cơ khí.

## Backup và dữ liệu

T2 ban đầu: `extras/backups/pre-t2-debounce-20261030-210250/`, remote `/home/voron/printer_data/config_backups/pre-t2-debounce-20261030-210250/`.

Trước mở rộng: `extras/backups/pre-all-tool-runout-debounce-20261030-210635/`, remote `/home/voron/printer_data/config_backups/pre-all-tool-runout-debounce-20261030-210635/`. Trong backup này T2 đã ở 0,5 giây; muốn khôi phục T2 về giá trị gốc phải dùng backup trước đó. Chỉ restore khi đã kiểm tra idle rồi reload một lần.

[JSON xác minh và kiểm tra native filter](filament-runout-debounce-2026-10-30-results.json). Nguồn, phản hồi API, hash, script và snapshot đầy đủ nằm trong TEMP `voron-t2-debounce-20261030` của phiên làm việc.

## Giới hạn còn lại

Không home, đổi tool, cấp nhiệt hay chạy bản in mới trong tác vụ này. Homed_axes rỗng sau RESTART là dự kiến. Chưa có phép rút/cắm nhựa vật lý hoặc kiểm chứng bản in T2 sau thay đổi. Nếu cảm biến báo vắng sai đủ lâu, đường pause vẫn có thể chạy; cần kiểm tra lực tác động của sợi, gá/PTFE, giắc và dây SIG/GND. Bộ lọc giảm nhiễu ngắn, không xác định hoặc sửa linh kiện hỏng.
