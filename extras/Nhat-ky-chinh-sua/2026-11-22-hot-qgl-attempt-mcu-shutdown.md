# 2026-11-22 — Thử QGL ở điều kiện in bị MCU shutdown trước khi đo

## Chuẩn bị và diễn biến

- Theo yêu cầu người vận hành, chuẩn bị đo QGL với bàn 100°C và T0 150°C. Người vận hành đã xác nhận đang quan sát máy. Trước phép thử, `print_stats=standby`, T0 active/detected, XYZ homed, đầu in ở X330 Y280 Z10, QGL chưa applied, Klipper không warning.
- Gửi `M140 S100` và `M104 S150`; không gửi lệnh QGL, tap hoặc mesh. Bàn tăng từ khoảng 53°C tới 100°C, vòi giữ quanh 150°C. Dự kiến giữ nhiệt ngắn trước QGL.
- Khi đang giữ nhiệt và không ra lệnh chuyển động, main MCU shutdown: `Missed scheduling of next digital out event`. Dòng Stats cuối trước lỗi: bàn target 100, thực tế 100,2°C, PWM 0,684; T0 target 150, thực tế 150,0°C, PWM 0,108; nhiệt cuộn LDC 43,8°C. CAN main MCU báo active, rx_error=0, tx_error=0, tx_retries=0. Luồng LDC trước shutdown báo `possible_overflows=0`.
- Sau lỗi, Moonraker báo `webhooks.state=shutdown`, firmware cắt PWM heater. Đầu in vẫn X330 Y280 Z10. Không firmware restart hoặc lặp lại gia nhiệt; target hiển thị vẫn 100/150 nhưng PWM sau shutdown bằng 0.

## Kết luận

- **Không có kết quả QGL nóng mới** vì máy shutdown trước khi lệnh QGL được gửi. Không thể dùng lượt này để đánh giá trực tiếp hội tụ tại bàn 100°C/vòi 150°C.
- Lỗi xuất hiện khi máy đứng yên và cả hai heater đang điều khiển PWM, nên không có bằng chứng liên hệ nó với motor Z, chuyển động QGL hoặc việc đọc các điểm LDC. Trạng thái CAN và LDC không chỉ ra mất gói tại thời điểm này. Mã `Missed scheduling of next digital out event` xác định tầng MCU/output timing, nhưng log chưa đủ xác định linh kiện hay đường điện cụ thể.
- Các lần QGL nóng trước đó vẫn cho thấy hội tụ kém (xem `extras/diagnostics/2026-11-22-qgl/REPORT.vi.md`), song phép thử có kiểm soát ở trạng thái nhiệt ổn định phải chờ xử lý lỗi MCU. Giữ nguyên tolerance QGL và cấu hình LDC/stepper; không nới ngưỡng để che sự cố.
