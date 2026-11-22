# 2026-11-22 — Khoanh vùng nguyên nhân QGL nóng mất hội tụ sau thay LDC1612

## So sánh theo mốc thay cảm biến

- Đọc log Klipper ngày 21/11 và 22/11, phân tích các phiên QGL tinh tolerance 0,0075 mm với bàn ít nhất 95°C. Cảm biến ban đầu ngày 21/11 đạt 15/18 phiên trước khi đổi QGL tinh sang `METHOD=scan`, và 3/4 phiên sau khi đổi; tổng 18/22. Cảm biến thay thế ngày 22/11 sau khi lưu mô hình Z nóng đạt 7/26 phiên trong bản log chụp lúc 12:25. Hai lượt scan kế tiếp lúc 12:26/12:29 lần lượt hủy và đạt 0,005877 mm. Các lượt là lịch sử vận hành, không phải thí nghiệm đối chứng cùng nhiệt/gá/gantry.
- Đường cong Z nóng của cảm biến đầu được lưu ở nhiệt cuộn 58,509932°C. Trong khoảng quét cuối khoảng 35 giây, log ghi cuộn 58,8–59,2°C khi bàn giữ 100°C. Cảm biến thay thế được lưu mô hình ở 46,683760°C khi cuộn **đang tăng từ 45,6 lên 48,3°C trong khoảng 38 giây**, bàn 100°C; các QGL nóng sau đó thường chạy khi cuộn 60–66°C. Live `compensation_enabled=false`, không có mô hình drift đã lưu. Hiệu chuẩn khi nhiệt thay đổi có thể trộn sai lệch nhiệt vào bảng Z; mức chênh nhiệt lúc dùng sau đó lớn hơn cảm biến đầu. Đây là nguyên nhân cấu hình/điều kiện hiệu chuẩn có bằng chứng thời gian rõ nhất, nhưng chưa có phép đối chứng chuẩn để định lượng phần gây ra riêng trong dải bốn góc.
- Dòng kích vẫn là 17, I²C vẫn cùng PA8/PC9 và 100 kHz. Cảnh báo `Amplitude Low/High` xuất hiện cả ở các phiên QGL đạt của cả hai đầu, nên không thể chỉ dựa cảnh báo để kết luận chip/bo mới hỏng. Bốn motor Z đáp ứng đúng chiều với các chỉnh lớn, không có một motor cụ thể bị chỉ ra bởi log.

## Đối chứng PWM bàn tại một điểm cố định

- Người vận hành xác nhận T0/bàn không hư hại sau tap lỗi và quan sát máy. Máy idle, XYZ homed, T0 active/detected; đầu được đưa tới X174 Y168 Z2. Giữ vòi 150°C, bàn quanh 100°C, cuộn khoảng 67–69°C. Đọc trực tiếp stream LDC1612 khoảng 400 mẫu/giây bằng `capture_ldc.py`, không ra lệnh trục trong lúc lấy mẫu. Ba cửa sổ mỗi cửa sổ khoảng 12 giây theo thứ tự PWM bàn **bật → tắt → bật lại**:

| PWM bàn | Số mẫu hợp lệ | Độ lệch chuẩn Z sau bỏ xu hướng tuyến tính | Xu hướng Z |
| --- | ---: | ---: | ---: |
| Bật, PID 100°C | 4.788 | 0,007950 mm | -0,003880 mm/s |
| Tắt, bàn bắt đầu nguội | 4.824 | 0,002079 mm | -0,006262 mm/s |
| Bật lại, PID 100°C | 4.824 | 0,010209 mm | -0,005244 mm/s |

- Nhiễu nhanh giảm còn khoảng 1/4–1/5 khi tắt công suất bàn và tăng lại khi bật. Điều này **xác nhận sự tương quan trực tiếp giữa trạng thái cấp điện bàn và độ ổn định số đo LDC tại cùng vị trí**. Chưa tách được nhiễu điện do SSR/dây heater/nguồn/ground khỏi đáp ứng nhiệt cơ học do bàn đổi công suất; phép đo ngắn và bỏ xu hướng tuyến tính không chứng minh đường nhiễu cụ thể. Khi tắt PWM, độ trôi chậm tăng vì bàn nguội, nên tắt bàn suốt QGL không tự động giải quyết vấn đề.
- `errors` của LDC tăng gần mỗi mẫu trong cả ba cửa sổ; cảnh báo biên độ không phân biệt được PWM bật/tắt. Không đổi drive current hoặc I²C theo kết quả này.

## So sánh cách dò QGL

- Cấu hình hiện dùng QGL tinh `METHOD=scan HORIZONTAL_MOVE_Z=2`. [Tài liệu Klipper](https://www.klipper3d.org/Eddy_Probe.html) khuyên dùng phương pháp mặc định cho QGL; scan chủ yếu cho mesh và cũng chịu drift nhiệt. Khi người vận hành tiếp tục quan sát, đã chạy một lượt `_QUAD_GANTRY_LEVEL` native không truyền `METHOD` tại bàn 100°C/vòi 150°C/cuộn khoảng 67°C. Dải 0,034962 → 0,024716 → 0,007641 → 0,016174 → **0,005078 mm**, đạt sau bốn chỉnh. Một lượt đạt nhưng vẫn có vòng tăng lại, nên phương pháp scan là yếu tố làm bài toán khó hơn chứ chưa được chứng minh là nguyên nhân duy nhất.
- Lần in ngay trước đó QGL scan đạt 0,005877 mm nhưng tap sau đó báo `no contact found`; người vận hành xác nhận không có vết chạm/hư hại. Lỗi tap riêng, không dùng nó làm bằng chứng motor QGL.

## Kết luận và trạng thái

- Suy giảm sau thay cảm biến phù hợp nhất với **đường đo LDC mới nhạy với trạng thái cấp điện bàn, cộng với mô hình Z được lưu khi cuộn chưa ổn định và hiện dùng xa nhiệt hiệu chuẩn mà không có bù drift**. QGL scan ở Z2 và tolerance 0,0075 mm làm sai số dễ vượt ngưỡng. Không có bằng chứng xác định `stepper_z`, `z1`, `z2` hoặc `z3` hỏng/đấu nhầm; chưa chứng minh linh kiện gây nhiễu cụ thể.
- Không nới tolerance hoặc tăng dòng kích tùy ý. Trước khi hiệu chuẩn lại, kiểm tra thực tế giắc/cuộn/tụ, đường dây LDC và thermistor so với dây heater AC/SSR, mass và nguồn. Sau khi xử lý đường nhiễu/lỗi MCU digital output, mới quyết định hiệu chuẩn Z nóng tại nhiệt cuộn ổn định hoặc hoàn tất bù nhiệt nếu người vận hành yêu cầu tiếp. Có thể đánh giá đổi QGL tinh về phương pháp mặc định bằng nhiều lượt đối chứng cùng điều kiện; chưa thay production chỉ từ một lượt.
- Kết thúc test: `ready`, `print_stats=cancelled`, XYZ homed, T0 active/detected, QGL applied, đầu X330 Y10 Z10; target bàn/vòi bằng 0. Không sửa CFG production. Live `tap_z_offset=+0,10` khác Git `-0,04` do thay đổi ngoài lượt chẩn đoán, không liên quan QGL scan và không được ghi đè.
