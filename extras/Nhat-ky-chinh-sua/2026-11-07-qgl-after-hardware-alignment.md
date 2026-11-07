# Thử lại QGL sau căn chỉnh phần cứng ngày 07/11/2026

Người vận hành xác nhận đã chỉnh dây GT2 dưới cụm truyền động motor Z sau [lượt thử bốn cụm Z](2026-11-07-z-corner-live-tests.md). Máy đã khởi động lại, chưa home, shuttle rỗng. Webcam xác nhận bàn trống và khu vực gantry thấp trước khi home. Dùng lại các bài thử Scan, hành trình Z, kích riêng từng motor và đổi tool T0/T3/T4. T1/T2 vẫn nằm ngoài bài thử.

Live giữ Scan 20 mẫu, Touch threshold 792, QGL tolerance 0,0075 mm, retries 10 và cùng điểm đo. Không sửa cấu hình hoặc calib. Bàn bắt đầu khoảng 44,5°C, nguội tự nhiên, so với khoảng 73°C ở lượt trước. Hai lượt khác nhiệt độ và trạng thái gantry ban đầu. Các so sánh trước/sau có thể chỉ ra thay đổi quan sát được, nhưng không tách riêng ảnh hưởng của việc căn chỉnh.

## QGL lúc bắt đầu và đo đứng yên

Sau `G28`, QGL với shuttle rỗng có range thô 0,066949 mm. Lượt tinh đi từ 0,034908 qua 0,009372 đến **0,003995 mm ở retry 2**. Lượt thô ra lệnh bù Z2 +0,037048 mm và Z3 −0,058511 mm. Sau đó home Z để lấy mốc Scan cho các phép thử.

Đo tại cùng bốn XY của lượt trước với Z lệnh 2,5 mm. Thứ tự nhóm mẫu vẫn là 20 / 100 / 20. Mỗi số dưới đây là max−min trong một cửa sổ, tính từ các giá trị median của từng nhóm mẫu.

| Góc | Lượt trước, range lớn nhất ở 20 mẫu (mm) | Sau căn, 20 mẫu lần 1 (mm) | 100 mẫu (mm) | 20 mẫu lần 2 (mm) |
|---|---:|---:|---:|---:|
| Z trước trái | 0,020235 | 0,024852 | 0,012331 | 0,008181 |
| Z1 sau trái | 0,031061 | 0,018878 | 0,008071 | 0,009345 |
| Z2 sau phải | 0,045859 | 0,021593 | 0,008067 | 0,009345 |
| Z3 trước phải | 0,018071 | 0,014026 | 0,008020 | 0,005946 |

Tại Z2, chênh lệch median từ cửa sổ đầu đến cuối giảm từ 0,0575 xuống 0,0158 mm. Z trước trái có chênh lệch median 0,0254 mm trong lượt mới. Dao động đứng yên tiếp tục xuất hiện ở nhiều góc và có thể đưa sai lệch vào bốn phép đo nối tiếp của QGL.

## Lần dừng MCU trong khi đo

Vòng Z20→315→20 đã kết thúc lúc 13:02:58. Đến 13:03:40, trong lượt đo lại ở vùng thấp, MCU chính dừng với `Timer too close`. Log ngay tại mốc dừng ghi `Reactor 743.944 busy for 0.367` ở `GarbageCollection._handle_idle`. CAN không báo lỗi đường truyền ở các dòng Stats gần đó. Heater target/power đều bằng 0. Đây là lỗi lập lịch trong bài thử, xảy ra ngoài QGL; không dùng nó để gán lỗi cho motor ở điểm đang được đo.

Phiên thu mẫu Cartographer liên tục do bài thử mở có thể đã làm tăng số đối tượng phải thu gom. Giữ dữ liệu trước lỗi, khôi phục Klipper bằng một lần firmware restart, xác nhận shuttle rỗng và bàn trống trước khi home. Từ lần chạy lại Z315 trở đi dùng `CARTOGRAPHER_SCAN_ACCURACY` trong các cửa sổ ngắn, đóng stream trước khi chuyển động. Lượt Z315 đầu chỉ có một phần dữ liệu sau hành trình và không dùng trong bảng so sánh. [Tài liệu Klipper về thời gian thực](https://www.klipper3d.org/FAQ.html)

QGL shuttle rỗng sau khôi phục đạt 0,005819 mm ở retry 5, sau lượt thô 0,030589 mm và lượt tinh đầu 0,022934 mm. Các lượt home và QGL này diễn ra ở khoảng 41°C với heater tắt.

## Hành trình Z và từng motor

Số dưới đây là max−min của bốn độ dịch đo giữa hai khảo sát. Các lượt shuttle rỗng đo xuôi rồi ngược và giữ mốc home giữa hai khảo sát của cùng điều kiện. Lượt Z315 sau khôi phục lấy baseline mới trước khi lên cao. Lượt cũ tính bằng median nhóm tần số, lượt mới dùng các snapshot stream trước lỗi hoặc median Scan ngắn sau lỗi.

| Điều kiện | Trước căn (mm) | Sau căn (mm) |
|---|---:|---:|
| Chờ 25 giây ở tâm | 0,062 | 0,008 |
| Z20→200→20 ở 15 mm/s | 0,056 | 0,016 |
| Hai vòng Z20→200→20 ở 80 mm/s | 0,074 | 0,011 |
| Z20→315→20 ở 15 mm/s | 0,014 | 0,013 |

Kích riêng từng motor +0,20 và −0,20 mm ở 0,5 mm/s, có hồi vị và home Z sau khi hoàn tất mỗi góc. Bước tham chiếu đồng bộ +0,30 mm trên bốn motor cho thay đổi Scan 0,678–0,692 mm ở lượt mới, so với 0,378–0,420 mm trước. Đây là đáp ứng của phép đo với lệnh chuyển động, chưa phải đo hành trình thật. Giữ số liệu hồi vị riêng và không suy hiệu chỉnh `rotation_distance` từ bảng này.

| Góc | Scan khi kích +0,20 / −0,20 (mm) | Hồi vị trước căn (mm) | Hồi vị sau căn (mm) |
|---|---:|---:|---:|
| Z | +0,297 / −0,293 | +0,028 / −0,002 | −0,013 / −0,039 |
| Z1 | +0,246 / −0,259 | −0,002 / −0,016 | +0,015 / −0,051 |
| Z2 | +0,235 / −0,247 | −0,030 / −0,049 | −0,008 / −0,049 |
| Z3 | +0,334 / −0,310 | −0,018 / −0,003 | −0,004 / −0,004 |

Cả bốn motor đáp ứng đúng chiều. Hồi vị Z2 cải thiện ở một lượt, lượt còn lại gần như cũ. Z1 có residual lớn nhất ở lượt mới, sát Z2. Đo Scan chưa xác nhận được motor, dây GT2 hay cơ khí tại một góc cố định là nguyên nhân.

## Gắp T0, chạy Z có tải và đổi tool

Đo với T0 trước và sau các vòng đổi tool, giữ mốc home. So sánh cùng thứ tự lấy điểm như lượt cũ. Mỗi ô là max−min của bốn độ dịch. Thời gian giữa các điểm có khác do lần này dùng Scan ngắn thay cho stream liên tục sau lỗi MCU.

| Điều kiện | Trước căn (mm) | Sau căn (mm) |
|---|---:|---:|
| Shuttle rỗng → gắp T0 | 0,069 | 0,027 |
| Gắn T0, Z20→330→20 ở 15 mm/s | 0,060 | 0,068 |
| T0→T3→T0, lượt 1 | 0,169 | 0,117 |
| T0→T4→T0, lượt 1 | 0,035 | 0,019 |
| T0→T3→T0, lượt 2 | 0,230 | 0,151 |
| T0→T4→T0, lượt 2 | 0,024 | 0,010 |

Sau T3, độ dịch lớn nhất vẫn xuất hiện tại điểm đọc đầu khi đổi thứ tự khảo sát: Z3 ở lượt ngược và Z ở lượt xuôi. Hai lượt T3 đều giảm so với trước căn, nhưng vẫn lớn hơn T4 và lượt chỉ lên Z330 có T0. T3 là điều kiện dễ tái hiện chênh lệch nhất. Thứ tự đọc và sự ổn định theo thời gian cần được xét trước khi quy sai lệch cho một góc.

## Vị trí đo, độ dốc Scan và chờ sau đổi tool

- Khi giữ đầu đứng yên, range ngắn tại điểm QGL Z2 là 0,019 và 0,010 mm trong hai lượt. Dời vào X305 Y255 cho 0,016 mm và tâm cho 0,021 mm. Đổi điểm đo vào trong chưa cho thấy lợi ích nhất quán.
- Tại tâm, Z lệnh 2,5→2,8→3,1→2,8→2,5 cho median Scan 3,073→3,795→4,678→3,789→3,031 mm. Hai bước lệnh +0,30 mm cho hai đáp ứng Scan +0,722 và +0,883 mm. Khi quay về Z2,5, số đọc lệch −0,042 mm. Chưa có đồng hồ so để tách độ dốc model, sai lệch nhiệt và chuyển động thật.
- Đo đứng yên tại X330 Y280 Z2,5 sau khi về T0, bảy cửa sổ trong khoảng 26 giây tính từ tâm cửa sổ đầu tới cuối. Median dịch −0,034 mm ở đối chứng, −0,061 mm sau T3 và −0,074 mm sau T4. Ba cửa sổ cuối vẫn trải 0,013 mm sau T3 và 0,016 mm sau T4. Thời gian chờ này chưa đưa cả hai lượt về độ lặp 0,0075 mm. T3 có chênh lệch bốn góc lớn hơn trong bài khảo sát, trong khi T4 cũng trôi rõ tại điểm giữ cố định.

## QGL theo macro production

| Lượt | Bàn (°C) | Range thô (mm) | Range tinh đầu → cuối (mm) | Retry đạt |
|---|---:|---:|---:|---:|
| Shuttle rỗng sau home đầu | 44,45 | 0,066949 | 0,034908 → 0,003995 | 2 |
| Shuttle rỗng sau khôi phục | 40,98 | 0,030589 | 0,022934 → 0,005819 | 5 |
| Có T0, sau chuỗi đổi tool | 36,67 | — | 0,083651 → 0,006247 | 6 |
| Shuttle rỗng, sau trả T0 vào dock | 36,42 | — | 0,035443 → 0,004776 | 6 |

Bốn lượt đều hội tụ theo ngưỡng production. Hai lượt cuối vẫn dao động giữa các retry. QGL có T0 trước căn bắt đầu ở 0,252136 mm và đạt ở retry 5, còn lần shuttle rỗng bắt đầu ở 0,047485 mm và đạt ở retry 3. Range đầu sau căn nhỏ hơn, nhưng lượt mới không rút ngắn đều số vòng.

## Đối chứng A/B và các biến thể QGL

Chạy hai vòng XY theo đường chéo ở Z20, yêu cầu tốc độ 120 rồi 200 mm/s. Max−min của bốn độ dịch sau chuyển động là 0,013509 mm. Hai TMC2209 A/B đều đọc `cs_actual=25, stst=1` trước và sau. Đây là kiểm tra hai motor phối hợp trên CoreXY và trạng thái driver, không phải đo hành trình từng motor A/B độc lập.

Với shuttle rỗng và bàn khoảng 34,8–35,7°C, gọi lượt tinh `_QUAD_GANTRY_LEVEL` hai lần cho mỗi chế độ theo thứ tự chuẩn → chậm → Z3 → Z3 → chậm → chuẩn. Mỗi lượt bắt đầu từ kết quả cơ khí của lượt trước. Hạ giới hạn vận tốc/gia tốc trong RAM khi thử chậm. Giữ ngưỡng 0,0075 mm và khôi phục giới hạn 350 mm/s, 7.000 mm/s² sau thử. Z2 và Z3 ở bảng này là độ cao di chuyển giữa điểm, không phải tên motor.

| Chế độ | Range đầu hai lượt (mm) | Range cuối hai lượt (mm) | Retry đạt | Thời gian hai lượt |
|---|---:|---:|---:|---:|
| Z2, tốc độ production | 0,018987 / 0,013567 | 0,006452 / 0,007420 | 5 / 1 | 52 / 19 s |
| Z2, giới hạn 80 mm/s và 1.200 mm/s² | 0,031672 / 0,017565 | 0,005908 / 0,005080 | 6 / 3 | 122 / 70 s |
| Z3, tốc độ production | 0,008102 / 0,006432 | 0,005175 / 0,006432 | 1 / 0 | 25 / 13 s |

Giảm giới hạn tốc độ/gia tốc không cho lợi ích rõ trong nhóm đo này. Hai lượt Z3 có ít retry nhất và range đầu nhỏ hơn, nên cần đối chứng ngay sau đường T3 trước khi gán lợi ích cho độ cao.

Với T0, làm QGL chuẩn để lấy mốc, rồi chạy một vòng T0→T3→T0 trước mỗi biến thể. Cùng giới hạn production, bàn khoảng 35,5°C. Sau mỗi lượt đạt, home Z để lấy lại mốc Scan. Kết quả sau vòng T3:

| Độ cao di chuyển | Range đầu → cuối (mm) | Retry đạt |
|---|---:|---:|
| 2 mm | 0,024901 → 0,004788 | 4 |
| 3 mm | 0,015787 → 0,004801 | 2 |

Độ cao 3 mm là biến thể đáng kiểm chứng tiếp. Nó cần 0–2 retry trong ba lượt nguội, trong khi 2 mm tốc độ production cần 1–5 retry trong ba lượt so sánh. Range đầu khác nhau và thứ tự chỉ có một cặp sau T3, nên chưa coi đây là bằng chứng đủ để đổi macro production. Cần đối chứng ở nhiệt vận hành sau khi xác minh đường NTC bàn.

## Kết luận và trạng thái cuối

- Sau căn dây GT2, đối chứng chờ, hành trình Z200 và độ phân tán sau T3 đều thấp hơn lượt trước. Hành trình Z315 và Z330 gần mức cũ. Các phép kích riêng đều đúng chiều, nhưng hồi vị Z1 và Z2 còn lệch tới khoảng 0,05 mm trên Scan. Chưa khoanh được một motor bị lỗi hoặc mức cải thiện chỉ do dây GT2.
- Sai lệch đọc tăng sau đổi tool và giảm theo thời gian khi giữ đầu đứng yên. Kết quả vẫn ưu tiên tách độ ổn định của Cartographer, gá/dây và gantry đang thư giãn khỏi sai lệch truyền động. Dùng đồng hồ so gần Z2, cùng mốc home và cùng nhiệt, để đối chiếu trước/sau T0→T3→T0. QGL 3 mm là ứng viên thử tiếp. Giảm tốc/gia tốc XY không cho kết quả đều hơn ở lượt nguội này.
- QGL production cuối với shuttle rỗng đi từ 0,074962 đến **0,005091 mm ở retry 8**. Klipper Ready, XYZ homed, `applied=true`, đỗ X174 Y316 Z20, tất cả heater tắt. T1/T2 không được chọn. Khôi phục đèn khoang và giới hạn chuyển động ban đầu. So file live với Git, cấu hình và calib khớp bản trước thử. Lỗi MCU không tái diễn sau khi chuyển sang Scan ngắn.

Log lệnh, trạng thái lúc dừng và các mẫu đo lưu cục bộ trong thư mục TEMP `voron-20261107-z-retest`.
