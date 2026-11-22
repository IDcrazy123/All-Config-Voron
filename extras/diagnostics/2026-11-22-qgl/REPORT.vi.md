# 2026-11-22 — QGL LDC1612 khó hội tụ

## Phạm vi và trạng thái

- Người vận hành đứng cạnh máy trong phép thử có chuyển động. Máy `ready`, T0 được nhận diện trên shuttle; đã G28 rồi đo tĩnh ở hai góc QGL tại Z2. Kết thúc, đầu in được nâng lên Z10 tại X330 Y280. Bàn và vòi có target 0.
- Nhật ký Klipper hiện hành được tải về thư mục tạm, phân tích bằng `analyze_qgl.py`. Có 206 vòng đo trong 54 phiên QGL (gồm cả vòng thô và tinh). Đây là lịch sử nhiều chế độ nhiệt, không phải phép thử lặp có kiểm soát ở một nhiệt độ cố định.

## Đáp ứng của bốn motor Z

- Ở các vòng tinh dùng tolerance 0,0075 mm: bàn dưới 50°C có 3/3 phiên đạt; 50–95°C có 2/5; từ 95°C có 7/23. Trung vị dải nhỏ nhất mỗi phiên nóng là 0,011137 mm. Trên 150 vòng tinh sau chỉnh, trung vị dải là 0,015311 mm và bách phân vị 95 là 0,025311 mm.
- Có 11 cặp vòng tinh liên tiếp bắt đầu với dải ít nhất 0,030 mm và có lệnh chỉnh bốn Z; cả 11 cặp đều giảm dải ở lần đo kế tiếp. Trung vị trước/sau là 0,039891/0,016498 mm. Vì vậy không có dấu hiệu rõ của một motor không chạy hoặc thứ tự Z bị đảo. Vòng tinh vẫn thường đổi dấu và không có một góc luôn sai theo cùng chiều; không đủ dữ liệu để quy cho một stepper cụ thể.
- `DUMP_TMC` của `stepper_z`, `stepper_z1`, `stepper_z2`, `stepper_z3` khi idle đều báo `GSTAT=00000000`, `DRV_STATUS=80190000`, `cs_actual=25`, `stst=1`. Đây chỉ là kiểm tra trạng thái driver tại thời điểm đọc, không chứng minh dây/khớp nối không trượt dưới tải. Sự cố dây step lỏng đã được người vận hành tìm và sửa trước các thử nghiệm này.

## Tín hiệu LDC khi không có lệnh cho motor Z

Đọc trực tiếp stream `ldc1612/dump_ldc1612` từ Klipper bằng `capture_ldc.py`, khoảng 400 mẫu/s mỗi vị trí. Cả hai lần đều lấy 4.836 mẫu hợp lệ trong 12,09 giây ở Z2; không ra lệnh chuyển động trong lúc lấy mẫu.

| Vị trí vòi | Bàn / cuộn | Dải Z min–max | Độ lệch chuẩn sau bỏ xu hướng tuyến tính | Xu hướng Z | Cờ lỗi tích lũy |
| --- | --- | ---: | ---: | ---: | ---: |
| X20 Y10, góc trước trái | Bàn khoảng 61°C, cuộn 51°C, đang nguội | 0,0263 mm | 0,00468 mm | +0,000538 mm/s | 31.680 → 36.480 |
| X330 Y280, góc sau phải | Bàn khoảng 58°C, cuộn 50°C, đang nguội | 0,0307 mm | 0,00227 mm | −0,001907 mm/s | 46.500 → 51.300 |

Chỉ số lỗi tăng khoảng 4.800 trong mỗi lần 4.836 mẫu. Log đồng thời có cảnh báo biên độ dao động của LDC. Cảnh báo này cho thấy điều kiện kích cuộn/tín hiệu cần kiểm tra, nhưng bản thân nó không chứng minh chip LDC1612 hỏng: khoảng cách cuộn–bàn, nhiệt độ, dòng kích và mạch LC đều có thể ảnh hưởng. Khi bàn đang nguội, dịch chuyển cơ học do nhiệt cũng có thể góp phần vào xu hướng Z đo được.

## Kết luận và bước tiếp theo

- **Giới hạn hội tụ hiện tại nằm ở phép đo theo thời gian và trạng thái nhiệt của bàn/cuộn, chưa có bằng chứng quy cho riêng `stepper_z`, `z1`, `z2` hay `z3`.** Đáp ứng tốt với lệnh chỉnh lớn là bằng chứng chống lại lỗi đấu nhầm hoặc một motor hoàn toàn không đáp ứng. Sai số tĩnh và trôi trong vài giây đã cùng cỡ hoặc lớn hơn tolerance QGL 0,0075 mm.
- Không nới tolerance QGL để che sai số. Không tiếp tục hiệu chuẩn trôi nhiệt vì người vận hành đã yêu cầu dừng. Khi kiểm tra phần cứng: xem dây/giắc cuộn, tụ cộng hưởng và khoảng cách cuộn với bàn; xác nhận drive current phù hợp tại khoảng cách và nhiệt độ quét thực tế. Một phép đo giữ bàn ổn định ở 100°C sau khi khắc phục lỗi MCU sẽ giúp tách drift nhiệt bàn khỏi tín hiệu cảm biến.
- Bản in tiếp theo cần thử lại lớp đầu sau khi helper hiệu chỉnh gốc Z sau tap đã được deploy. Chưa lưu cố định +0,10 mm cho T0 từ bản in cũ vì khi đó helper không chạy.
