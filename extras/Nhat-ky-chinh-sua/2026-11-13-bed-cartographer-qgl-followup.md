# Đồng bộ cảm biến bàn, hiệu chuẩn và đánh giá QGL — 13/11/2026

Đọc cấu hình/trạng thái live và log trên `192.168.1.43` trước khi sửa Git. Lúc bắt đầu bản `Cube_ABS_2m5s.gcode` đang in; chỉ đọc cho đến khi Moonraker xác nhận `complete`, toolchanger `ready`, tool rỗng, heater bàn target/power bằng 0 và QGL `applied=true`. Không gửi lệnh home, QGL, heat, reload hoặc deploy. Kết quả phân tích chi tiết và bảng bảy lượt QGL nóng nằm ở [báo cáo QGL](../diagnostics/2026-11-13-qgl/REPORT.vi.md).

## Bằng chứng

- Người vận hành xác nhận đã thay cảm biến bàn cũ có dấu hiệu hỏng khi dùng và đã hiệu chuẩn lại Cartographer cùng PID bàn. Log trước thay có nhiều bước nhiệt hàng chục độ khi gia nhiệt. Log 28/10 cũng có một bước 49,7→4,4→49,8°C lúc target/PWM bằng 0, nên không thể xác nhận điều kiện "chỉ lúc heater bật". Log 11 và 13/11 sau thay không ghi bước >=2°C giữa các mẫu Stats liên tiếp có target >0.
- `PID_CALIBRATE` 11/11 đã lưu Kp/Ki/Kd mới 64,710/2,713/385,835. Scan model cuối lưu 11/11 lúc 20:28:42 với `reference_temperature=-21.41°C`; Touch sau đó vẫn threshold 792. Moonraker xác nhận các giá trị này đang nạp. `axis_twist_compensation` không nạp, không có hệ số coil temperature compensation.
- Sau hiệu chuẩn cuối, QGL tinh ở target 105°C đạt 4/7 lượt, hủy 3/7. Ngày 13/11 một lượt hủy ở retry 5 sau khi range tăng lên 0,353690 mm dù bàn báo 105,1–105,2°C. Lượt của bản Cube sau đó đạt 0,003413 mm ở retry 2 và bản in hoàn tất. Mã Python live không dùng NTC bàn làm đầu vào Scan; thông báo `Possibly Z motor numbering is wrong` phát ra từ quy tắc range tăng, không chứng minh đấu dây sai.

## File và giá trị đồng bộ

| File | Trước | Sau |
|---|---|---|
| `config/printer.cfg` | PID 47.596/1.244/455.140; Scan model 07/11, reference -22.15°C | PID 64.710/2.713/385.835; hệ số/domain Scan model live 11/11, reference -21.41°C |
| `config/Printer-Setup/hardware.cfg` | Override `smooth_time=3.0`, `pwm_cycle_time=0.2` | Dùng mặc định live 1.0/0.1 bằng cách comment override |
| `config/Printer-Setup/calibration-probe.cfg` | Section axis twist trống đang bật | Section được comment như live; không có hệ số lưu |
| `extras/tests/Test-ProductionCfg.ps1` | Hash SAVE_CONFIG cũ; kỳ vọng `PA1` lỗi thời | Hash dữ liệu hiệu chuẩn mới; kỳ vọng `PA5` live/Git |

Ba CFG trước sửa được sao lưu ở `extras/backups/pre-qgl-live-sync-20261113-085432/`. `KNOWN_ISSUES.md` và `AGENTS.md` được cập nhật theo trạng thái hiện tại. QGL points, tolerance, retries, Touch, mesh, giới hạn nhiệt, chân PA5/PB0 và các offset tool không đổi. Đây là đồng bộ repository, không cần restart vì live đã nạp những giá trị đó.

Kiểm tra `git diff --check` đạt; bộ `Test-ProductionCfg.ps1` chạy 83 test, đạt, 13 test bỏ qua do điều kiện Bash/POSIX. So `config/printer.cfg` với file live không còn sai khác; hai CFG còn lại chỉ khác comment, section active khớp live.

Còn chờ đo đồng hồ so bốn góc tại nhiệt vận hành và đối chiếu với Cartographer Scan sau di chuyển Z/đổi T0↔T3. Chưa kết luận cụm Z, gá probe hay coil là nguyên nhân duy nhất; cũng chưa xác nhận độ chính xác nhiệt tuyệt đối hoặc chất lượng lớp đầu của bản Cube.
