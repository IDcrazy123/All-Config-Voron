# Thử nghiệm bốn cụm Z trên máy ngày 07/11/2026

Người vận hành xác nhận bàn trống, sạch và cụm cơ khí giữ nguyên. Chỉ dùng shuttle rỗng hoặc T0, T3, T4. T1 và T2 đang bảo trì. Kiểm tra Moonraker trước và sau các cụm lệnh để xác nhận trạng thái in, homing, tool active/detected và heater. Bàn nguội tự nhiên từ khoảng 73°C, target và công suất tất cả heater bằng 0. Giữ nguyên cấu hình, calib, ngưỡng QGL 0,0075 mm và runtime Python.

## Đo đứng yên tại bốn điểm QGL

Shuttle rỗng, đã home Z bằng Scan, giữ Z2,5. Các điểm dưới đây là XY của shuttle. Vị trí coil trên bàn lệch Y+35 mm. Mỗi ô là max−min của khoảng cách Scan trong một lượt đo. Thứ tự tại từng góc là 20, 100 rồi 20 mẫu thô cho mỗi nhóm median. Số nhóm tương ứng là 20, 10 rồi 20.

| Góc | XY (mm) | 20 mẫu lần 1 (mm) | 100 mẫu (mm) | 20 mẫu lần 2 (mm) |
|---|---|---:|---:|---:|
| Z trước trái | 20, 10 | 0,020160 | 0,021931 | 0,020235 |
| Z1 sau trái | 20, 280 | 0,031061 | 0,012400 | 0,024495 |
| Z2 sau phải | 330, 280 | 0,045859 | 0,031352 | 0,023187 |
| Z3 trước phải | 330, 10 | 0,013383 | 0,016525 | 0,018071 |

Median ba lượt ở Z2 giảm từ 2,187816 xuống 2,130324 mm khi vẫn ở cùng vị trí lệnh. Tăng số mẫu giúp một số lượt nhưng giá trị trung tâm vẫn đổi. Đây là độ lặp của chuỗi đo Scan, gồm cả probe, gá, biến dạng cơ khí và nhiệt trong thời gian đo. Ngưỡng QGL áp cho range giữa bốn điểm của một vòng, còn bảng này mô tả dao động theo thời gian ở từng điểm. Cả hai đại lượng cùng đơn vị và cho thấy khả năng dao động làm QGL khó đạt.

## Đối chứng chờ và hành trình Z với shuttle rỗng

Giữa các khảo sát không home hoặc QGL lại. Mỗi khảo sát đi qua bốn góc theo thứ tự xuôi rồi ngược để giảm ảnh hưởng drift tuyến tính. Số trong bảng được tính lại từ dữ liệu tần số thô bằng đúng polynomial Scan đang nạp. Mỗi cửa sổ chia nhóm 20 mẫu liên tiếp, lấy median của các nhóm. Các cột là thay đổi khoảng cách đo tại cùng XY/Z lệnh giữa hai khảo sát liên tiếp.

| Điều kiện giữa hai lần đo | Z (mm) | Z1 (mm) | Z2 (mm) | Z3 (mm) | Max−min độ dịch (mm) |
|---|---:|---:|---:|---:|---:|
| Chờ 25 giây tại tâm, ngoài các lần đi đo góc | +0,118 | +0,109 | +0,090 | +0,056 | 0,062 |
| Một vòng Z20→200→20, 15 mm/s | +0,208 | +0,209 | +0,224 | +0,264 | 0,056 |
| Hai vòng Z20→200→20, 80 mm/s | +0,097 | +0,115 | +0,171 | +0,151 | 0,074 |
| Một vòng Z20→315→20, 15 mm/s | +0,336 | +0,325 | +0,322 | +0,332 | 0,014 |

Các lượt có dịch chung lớn, kể cả đối chứng. Dấu và thứ tự độ lệch tương đối thay đổi giữa các lượt. Hành trình cao tới Z315 trên shuttle rỗng không tái tạo sai lệch riêng Z2 cỡ 0,8 mm từng thấy sau đổi tool.

## Đáp ứng từng motor

Ở mỗi góc, đo một bước tham chiếu +0,30 mm trên cả bốn motor. Sau đó kích riêng motor tương ứng ở tốc độ 0,5 mm/s bằng bước +0,20 rồi hồi vị và bước −0,20 rồi hồi vị. Đầu giữ nguyên XY, Z lệnh 2,5 khi kích riêng. Tính đáp ứng so với trung bình hai số đo trước và sau để giảm drift chậm. Home Z sau khi hồi vị hoàn tất ở mỗi góc. Cách đo này kiểm tra chiều và độ lặp dưới dịch chuyển nhỏ. Không dùng nó để quy đổi chính xác độ dịch tại trục motor vì lực truyền qua hình học gantry, và Scan chưa có tham chiếu độc lập.

| Góc | Đo khi cả Z đi +0,30 (mm) | Đáp ứng riêng +0,20 (mm) | Đáp ứng riêng −0,20 (mm) | Sai lệch hồi vị hai lượt (mm) |
|---|---:|---:|---:|---:|
| Z | +0,383 | +0,168 | −0,193 | +0,028 / −0,002 |
| Z1 | +0,378 | +0,149 | −0,155 | −0,002 / −0,016 |
| Z2 | +0,383 | +0,142 | −0,132 | −0,030 / −0,049 |
| Z3 | +0,420 | +0,183 | −0,194 | −0,018 / −0,003 |

Cả bốn lệnh riêng đều làm khoảng cách tại góc tương ứng thay đổi đúng chiều. Z2 có đáp ứng tương đối nhỏ nhất và sai lệch hồi vị lớn nhất. Hai sai lệch của Z2 cùng chiều dù đảo chiều kích, phù hợp với drift hoặc thư giãn tại vị trí đo. Bốn TMC2209 đọc `GSTAT=0`, `DRV_STATUS=80190000` ở trạng thái đứng yên trước và sau bài thử. Kết quả thanh ghi không đo được việc trượt dây hay bỏ bước.

## Hành trình cao có tải và đi qua dock

Dùng đường gắp/thả KTC hiện hành và xác nhận active/detected sau từng lần. Các lần đổi qua T3/T4 đều đo với T0 trước và sau, cùng offset. Dùng cùng Z lệnh 2,5 và không home hoặc QGL giữa hai khảo sát. Bảng ghi thay đổi của từng điểm. Các lượt ở đoạn này đo mỗi góc một lần và đổi thứ tự theo cặp, vì vậy thứ tự lấy mẫu và drift vẫn ảnh hưởng đến chênh lệch biểu kiến.

| Điều kiện | Z (mm) | Z1 (mm) | Z2 (mm) | Z3 (mm) | Max−min độ dịch (mm) |
|---|---:|---:|---:|---:|---:|
| Shuttle rỗng → gắp T0 | +0,143 | +0,074 | +0,130 | +0,079 | 0,069 |
| T0 gắn sẵn, Z20→330→20 ở 15 mm/s | +0,264 | +0,258 | +0,242 | +0,204 | 0,060 |
| T0→T3→T0, đo từ Z3 đến Z | +0,106 | +0,132 | +0,200 | +0,276 | 0,169 |
| T0→T4→T0, lần 1 | +0,145 | +0,144 | +0,155 | +0,180 | 0,035 |
| T0→T3→T0, đo từ Z đến Z3 | +0,246 | +0,174 | +0,139 | +0,016 | 0,230 |
| T0→T4→T0, lần 2 | +0,117 | +0,093 | +0,106 | +0,110 | 0,024 |

Hai vòng T3 tạo chênh lệch lớn hơn đối chứng chạy Z với T0 và hai vòng T4. Góc dịch nhiều nhất là điểm đo đầu tiên ở cả hai thứ tự đối nghịch, Z3 ở lượt ngược và Z ở lượt xuôi. Kết quả khoanh đường đổi T3 hoặc quá trình ổn định của gantry/đầu dò sau đường đó. Chưa thấy dấu hiệu một góc cố định giữ sai lệch lớn nhất sau mỗi vòng T3.

## Vị trí coil và đáp ứng Scan ở tâm

Đo đứng yên với T0, mỗi cửa sổ khoảng 7 giây. Range của các median 20 mẫu tại X330 Y280 là 0,025 và 0,030 mm ở hai lượt. Dời vào X305 Y255 cho range 0,022 mm. Tâm X174 Y168 có range 0,042 mm. Dời khỏi góc bàn không loại dao động trong phép thử này.

Tại tâm, lệnh Z2,5→2,8→3,1→2,8→2,5 cho median Scan lần lượt 2,656 / 3,094 / 3,578 / 3,072 / 2,599 mm. Mỗi bước lệnh 0,30 mm cho mức thay đổi Scan lớn hơn 0,30 mm. Mốc quay lại Z2,5 chênh khoảng 0,057 mm so với ban đầu. Dữ liệu này gồm độ dốc của model Scan và chuyển động cơ khí thật. Chưa có số đo độc lập để suy ra bước truyền động hoặc hệ số hiệu chuẩn mới.

## Giữ tại Z2 sau đổi tool

Giữ T0 ở X330 Y280 Z2,5 và lấy bốn cửa sổ liên tiếp, khoảng 2,7 giây mỗi cửa sổ. Sau mỗi vòng đổi tool, về đúng vị trí này và để đầu đứng yên. Không chỉnh bất kỳ motor nào giữa bốn cửa sổ của một lượt.

| Điều kiện | Median các cửa sổ (mm) | Cửa sổ cuối trừ đầu (mm) |
|---|---|---:|
| Đối chứng, T0 gắn sẵn | 2,612 / 2,605 / 2,599 / 2,592 | −0,020 |
| Sau T0→T3→T0 | 2,884 / 2,863 / 2,850 / 2,837 | −0,048 |
| Sau T0→T4→T0 | 3,066 / 3,056 / 3,027 / 3,016 | −0,050 |

Cả hai đường dock đều có số đo còn trôi khi lệnh vị trí đã đứng yên. Vì QGL đọc các góc nối tiếp, trôi cỡ này có thể tạo sai khác giữa các góc trong cùng một vòng. T4 cũng có trôi tại điểm giữ Z2, dù hai lượt khảo sát bốn góc sau T4 ít phân tán hơn sau T3. Cần phép đo cơ khí độc lập để tách gantry hoặc gá probe đang thư giãn khỏi sai lệch điện/nhiệt của Cartographer.

## QGL xác nhận và kết luận

- Với T0, QGL từ 0,252136 xuống **0,006024 mm** ở retry 5. Lượt đầu yêu cầu bù dương lớn nhất ở Z1 (+0,209977 mm). Sau khi trả T0 vào dock, QGL shuttle rỗng từ 0,047485 xuống **0,005934 mm** ở retry 3. Lượt đầu của lần này yêu cầu bù dương lớn nhất ở Z2 (+0,034385 mm). Cả hai dùng ngưỡng 0,0075 mm. Cờ `applied=true` được đọc lại sau lượt QGL cuối.
- Z2 là góc ưu tiên kiểm tra thực tế. Nó có đáp ứng tương đối nhỏ và hồi vị kém nhất trong phép kích riêng, đồng thời là góc có độ lặp Scan kém nhất trong loạt đứng yên ban đầu. Cả bốn motor vẫn chuyển động đúng chiều ở góc tương ứng. Chu kỳ Z20→200 ở 80 mm/s và các lượt Z315/Z330 không tái hiện một góc lệch rõ, lặp lại qua các điều kiện. QGL cuối cũng đổi góc bù lớn nhất theo lượt.
- Sai lệch Scan theo thời gian đã được đo khi đứng yên, và đủ lớn để góp phần làm QGL tinh khó hội tụ. Đường đổi T3 là điều kiện tái hiện chênh lệch bốn góc rõ nhất hôm nay. Hướng kiểm chứng tiếp theo là đặt đồng hồ so tham chiếu khung/bàn tại gantry gần Z2, so độ cao trước và sau một vòng T0→T3→T0 với số Scan cùng thời điểm. Nếu đồng hồ so cũng dịch, kiểm tra kẹp đai, pulley, chi tiết đệm và độ tự do khớp Z2. Nếu đồng hồ so giữ, kiểm tra gá Cartographer, dây và coil.
- Cuối lượt, máy dừng tại X174 Y316 Z20, shuttle rỗng, XYZ homed, tất cả heater target/power bằng 0, bàn khoảng 49°C. Tổng cộng chọn T0 bảy lần, T3 và T4 mỗi tool ba lần. T1/T2 không được chọn. Không chạy bài thử cấp nhiệt ABS vì tín hiệu NTC bàn đã có bước nhảy trong phiên sáng. File calib và các macro live vẫn khớp Git, không có SAVE_CONFIG chờ lưu.

Log lệnh và dữ liệu tần số thô lưu cục bộ trong thư mục TEMP `voron-20261107-z-corner-tests`. Tham chiếu [Klipper FORCE_MOVE](https://www.klipper3d.org/G-Codes.html#force_move), [Cartographer Scan Accuracy](https://docs.cartographer3d.com/cartographer-probe/reference/macros-reference) và [Voron Gantry Squaring](https://docs.vorondesign.com/build/mechanical/v2_gantry_squaring.html).
