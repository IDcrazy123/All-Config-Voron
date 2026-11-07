# QGL và hiệu chuẩn live ngày 07/11/2026

Đối chiếu máy `192.168.1.43` qua Moonraker, log Klipper và mã nguồn đang cài qua SSH. Giờ trong bảng là giờ Việt Nam, lấy từ console và khớp với log theo chuỗi range/retry. Chỉ đọc trên máy in. Các lệnh home, QGL, hiệu chuẩn và in trong log đến từ phiên vận hành đang diễn ra.

## QGL sau thay cụm Z

| Lệnh QGL | Điều kiện quan sát | Range lượt thô (mm) | Range lượt tinh đầu → cuối (mm) | Kết quả |
|---|---|---:|---:|---|
| 11:01:38 | Scan mới đã nạp, bàn target 100°C | 0,022000 | 0,024073 → 0,002693 | Đạt ở retry 4 |
| 11:13:54 | Bàn target 100°C, trước khi lưu Touch mới | 0,072000 | 0,045760 → 0,004628 | Đạt ở retry 9 |
| 11:30:08 và 11:34:59 | Sau khi lưu Touch mới | — | — | `No trigger on probe after full movement` |
| 11:35:11 | Sau G28, bàn báo khoảng 99,7°C ở lượt tinh | 0,150324 | 0,035230 → 0,063024 | Hủy ở retry 4 do range tăng |
| 11:38:21 | Sau T0→T3→T0 và G28, bàn báo khoảng 100°C | 0,956585 | 0,136299 → 0,009511 | Hết 10 retry |
| 11:40:32 | Sau G28, bàn đang nguội | 0,099863 | 0,035076 → 0,006638 | Đạt ở retry 5 |
| 11:44:03 | QGL lặp, bàn đang nguội | — | 0,012692 → 0,007056 | Đạt ở retry 6 |
| 11:46:31 | Sau T0→T3→T0 và G28, bàn đang nguội | — | 0,087862 → 0,028563 | Hủy ở retry 3 sau khi từng giảm còn 0,015755 |
| 11:48:14 | Sau G28, bàn đang nguội | 0,063991 | 0,033271 → 0,027663 | Hủy ở retry 5 sau khi từng giảm còn 0,008281 |
| 11:54 | `PRINT_START` của Voron Skirt, bàn target 105°C | 0,209424 | 0,032926 → 0,006351 | Đạt ở retry 2, Moonraker xác nhận `applied=true` |

Moonraker ghi bản `Voron Skirt_ABS_3m21s.gcode` hoàn tất lúc 11:59:35. File chỉ dùng T0, lớp đầu 0,24 mm. `PRINT_START` chờ ngâm nhiệt 90 giây. Trong QGL, NTC bàn báo 105,2–105,4°C và Z2 nhận bù +0,043083 mm ở lượt thô, so với +0,804969 mm sau đổi tool lúc 11:38. Console xác nhận T0 đã được chọn sẵn sau Touch/mesh và khi G-code bắt đầu in, nên không có vòng gắp lại trước lớp đầu. Các lượt khác nhau cả về lịch sử chuyển động lẫn nhiệt, chưa tách được tác động riêng của từng điều kiện.

Touch của bản hoàn tất cần 9 lần chạm. Toàn chuỗi trải 0,534 mm, trong khi ba mẫu được chấp nhận ở cuối nằm trong khoảng 0,002 mm. Mesh adaptive được nạp, với cảnh báo 6/110 nút lưới chỉ có hai mẫu. Bản hoàn tất xác nhận chuỗi chuẩn bị có thể vượt qua các phép đo dao động; Moonraker không đánh giá bề mặt lớp đầu.

- Lượt thô lúc 11:38:47 yêu cầu bù Z/Z1/Z2/Z3 lần lượt `−0,357029 / −0,131895 / +0,804969 / −0,316046 mm`. Z2 sau phải là góc bù lớn nhất, cùng dấu và gần độ lớn của lượt ngày 02/11 sau chạy dock T4. Đây là ưu tiên kiểm tra phần đệm, kẹp/đai và độ tự do khớp Z2 dưới tải khi lên xuống dock. Hôm 02/11 người vận hành xác định đã thay nhầm chi tiết đệm. Chưa có mã/vị trí chi tiết, mốc thay đúng hoặc số đo cơ khí độc lập để gán lần lặp lại này cho cùng chi tiết.
- Ở lượt 11:38, range giảm khoảng 86% từ lần thô đến lần tinh đầu. Các lượt tinh sau đó dao động và góc cần bù đổi theo vòng. Lượt 11:44 dù bắt đầu chỉ lệch 0,012692 mm vẫn có lúc lên 0,029569 mm. Trong lượt này cả bốn điểm cùng dịch xuống theo số đo Scan, trung bình mỗi vòng từ 1,94928 xuống 1,86065 mm. Dịch chung bị loại khỏi range nếu xảy ra đồng thời, nhưng bốn góc được đo nối tiếp trong khoảng 8,5 giây. Drift theo thời gian trong vòng đo có thể lọt vào chênh lệch giữa góc. Dữ liệu này cũng phù hợp với gá probe hoặc cơ khí dịch chuyển. Cần tham chiếu độc lập để phân biệt.
- Trong mã Klipper đang chạy, câu `Possibly Z motor numbering is wrong` được thêm khi bộ đếm lượt range tăng vượt ngưỡng. Cấu hình mapping, hướng, tỷ số `80:16`, `rotation_distance=32` và dòng chạy `0.8 A` của bốn Z khớp Git. Lượt QGL vẫn có thể giảm mạnh và đạt ngưỡng với mapping này. Việc đấu dây hoặc lắp pulley thực tế cần xác nhận tại máy.
- QGL sử dụng Cartographer Scan với `samples=20` mặc định và tính median từ các mẫu khoảng cách tại từng điểm. Git đang có override `200`, nên đó là một khác biệt cần giữ cố định khi so sánh cơ khí. Thử ngày 30/10 với 200 mẫu vẫn có các lượt ABS cần 6–8 retry. Touch threshold và offset Z riêng của T3 thuộc quy trình khác.
- Coil tiếp tục báo khoảng `−20°C` khi máy ấm và đường bù nhiệt không có hệ số đang nạp. Model Scan mới không phục hồi đường nhiệt coil. Tín hiệu bàn cũng tái diễn lỗi độc lập. Khoảng 10:59:29, cảm biến báo `109,0 → 44,3 → 106,2°C` trong khoảng hai giây, cùng target 100°C, với PWM chuyển giữa 1 và 0. Trước đó khoảng 10:54:41 log có `Heater heater_bed not heating at expected rate`. Lượt 11:35 vẫn hủy trong khi số đọc bàn quanh 99,7°C, nên sự cố bàn không giải thích hết các lần QGL kém.
- Phép thử phân biệt tiếp theo là đo bốn góc bằng đồng hồ so trước/sau một khoảng chờ đối chứng, một vòng lên xuống Z không đổi tool rồi một vòng T0→T3→T0, cùng điều kiện nhiệt và về đúng vị trí. Tránh home hoặc QGL giữa hai số đo trong mỗi cặp. Nếu đồng hồ so đổi cùng Scan, khoanh cụm Z và clearance đỉnh dock. Nếu đồng hồ so giữ trong khi Scan đổi, khoanh gá Cartographer và đường coil. Kiểm tra đường tín hiệu NTC trước khi gia nhiệt ABS để thử lại.

## Hiệu chuẩn đã lưu và đang nạp

- `CARTOGRAPHER_SCAN_CALIBRATE` lưu lần đầu lúc 10:40 với nhiệt tham chiếu −35,14°C. Lần `SAVE_CONFIG` lúc 11:01:06 thay hệ số, domain và nhiệt tham chiếu thành −22,15°C. `z_offset=0`, plugin 1.10.1, firmware Cartographer V3 6.1.0.
- Hai lượt Touch sáng nay cùng tìm được threshold `792`. `SAVE_CONFIG` lúc 11:29:01 thay threshold `1379 → 792`, giữ `speed=2` và `z_offset=−0,05 mm`, với `samples=3` và `sample_range=0,01 mm`. Moonraker xác nhận cả hai model đã nạp và không có thay đổi chờ lưu.
- Offset Z T0/T1/T2/T3/T4 đang là `0 / +0,1665 / −0,3515 / −0,4865 / +0,0279 mm`. T3 đã là −0,4865 trong bản trước lần lưu Scan 11:01. Bản chụp 02/11 là −0,3865, Git trước đồng bộ là −0,3265. Không gán thay đổi T3 cho lượt Touch sáng nay.
- Mesh `default` 55×55 đã lưu trước hai lần `SAVE_CONFIG` 11:01 và 11:29, cùng dữ liệu trong cả ba file so sánh. Range toàn lưới là 0,301738 mm. Không có mesh active trong snapshot QGL kiểm tra. Bản ghi coil calibration cũ không còn trên máy, và section axis twist đang nạp với danh sách hệ số trống.

## Thay đổi trong repository

Đồng bộ nguyên khối `SAVE_CONFIG` từ file live vào `config/printer.cfg`. Phần trước khối được giữ nguyên. So sánh theo section xác nhận sáu khác biệt là Scan, Touch, mesh default, Z T3 và việc bỏ hệ số coil/axis twist cũ. Kiểm tra offline đọc được toàn bộ khối và đối chiếu với Moonraker từng tham số model, 3.025 điểm mesh và offset tool. Bản sao trước chỉnh nằm ở `extras/backups/pre-live-calibration-sync-20261107-115256/`. Việc đồng bộ lưu lại trạng thái đã nạp, chưa xác nhận kết quả cơ khí hay lớp đầu của các calib này.

Sau khi bản in hoàn tất, đồng bộ `calibration-probe.cfg` và `print-macros.cfg` từ live vào Git. Section Scan để mặc định 20 mẫu trên plugin 1.10.1, thay override 200 trong Git. QGL lấy retries 10 thay 5, góc thứ hai (350,350) thay (353,350), Y hai điểm trước 10 thay 0. Tolerance vẫn 0,0075 mm. Sao lưu hai file cũ ở `extras/backups/pre-live-qgl-sync-20261107-120124/`. Các giá trị này đang nạp trên máy, nên việc đồng bộ checkout không cần reload Klipper.

Đối chiếu toàn bộ CFG/CONF và script do Git theo dõi, sau các cập nhật trên chỉ còn `heater_bed.max_temp` khác nhau: 150°C live và 120°C Git. Quy tắc dự án yêu cầu xác nhận giới hạn phần cứng trước khi đưa giới hạn cao hơn vào Git. Giữ riêng khác biệt này và tránh triển khai nguyên config vì có thể đổi giới hạn đang chạy.

Bộ kiểm tra offline trước đây khóa `SAVE_CONFIG` theo bản sao tháng 10. Sau khi đối chiếu lại file live, cập nhật checksum kỳ vọng sang khối ngày 07/11. Kiểm tra tiếp tục phát hiện mọi thay đổi ngoài snapshot đã xác minh.

Cần đo vị trí tác động đai thật theo tọa độ bàn có tính offset probe Y+35 trước khi chỉnh `gantry_corners`. Thông tin bốn góc và thử nghiệm cũ ở [báo cáo ngày 02/11](../diagnostics/2026-11-02-first-layer-qgl/REPORT.vi.md) và [thử nghiệm ngày 30/10](../docs/qgl-thermal-trial-2026-10-30.md).

Nguồn kỹ thuật: [Klipper QGL](https://www.klipper3d.org/Config_Reference.html#quad_gantry_level), [Cartographer Scan và Touch](https://docs.cartographer3d.com/cartographer-probe/classic-vs-survey-touch), [Cartographer FAQ về coil âm](https://docs.cartographer3d.com/cartographer-probe/faq), [Voron V2 Gantry Squaring](https://docs.vorondesign.com/build/mechanical/v2_gantry_squaring.html).
