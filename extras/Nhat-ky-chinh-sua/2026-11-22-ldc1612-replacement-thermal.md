# 2026-11-22 — Thay LDC1612, hiệu chuẩn đường cong Z và chuẩn bị bù nhiệt

## Bằng chứng live

- Người vận hành xác nhận chip vẫn là LDC1612, dây I²C Manta PA8/PC9, nhiệt PC5, offset X0/Y35 và gá PF2 đã tháo; đứng tại máy quan sát. Klipper ban đầu `ready`, bàn/vòi nguội, XYZ chưa home, shuttle trống; nhiệt cuộn khoảng 19,5°C.
- `LDC_CALIBRATE_DRIVE_CURRENT` khi Z chưa biết chỉ chứng minh I²C phản hồi, trả 17; đã `RESTART` để bỏ kết quả chờ. `QUERY_PROBE` không được loại đầu dò này hỗ trợ.
- Lượt G28 Z đầu sau G28 X/Y bị dừng khẩn khi chưa có kết quả probe. Người vận hành kiểm tra, xác nhận dây motor bước lỏng, đã cắm lại; vòi/bàn không hư hại. Sau đó người vận hành tự `FIRMWARE_RESTART`, G28 hai lần và QGL. QGL lạnh hội tụ từ dải 6,461489 mm xuống 0,004765 mm ở lượt tinh thứ tám; T0 sau đó được gắp và xác nhận active/detected=0.
- Ở X174/Y168/Z20 khi nguội, đo lại dòng kích được 17. Người vận hành dùng thử giấy với T0, gửi `ACCEPT` ở Z khoảng -0,2505 sau khi giấy rà nhẹ. `PROBE_EDDY_CURRENT_CALIBRATE` hoàn tất 101 điểm, nhiễu trung bình 0,000980 mm trên 4039 mẫu, dải tần 306132,630 Hz. `SAVE_CONFIG` đã ghi mô hình mới, `calibration_temp=22,057667°C`; Klipper trở lại `ready`, không warning. Tần số Z0,05 mới 11876524,669 Hz so với 11842282,605 Hz cũ.
- `printer.cfg` live trước thay đổi có mesh default 55×55 mới hơn Git 15×15, nhưng cả hai mesh thuộc đầu dò trước. `tap_threshold=24888,543` cũng thuộc đầu dò trước.

## Cấu hình Git chuẩn bị triển khai

- `config/printer.cfg`: lấy đúng mô hình Z mới và nhiệt hiệu chuẩn nền từ live; bỏ tap threshold và mesh cũ. Giữ các PID và offset tool đã lưu.
- `config/Printer-Setup/calibration-probe.cfg`: thêm vị trí hiệu chuẩn nhiệt X174/Y168/Z1, vòi T0 150°C ở Z50, bàn 100°C và `max_validation_temp=100`; giữ I²C/offset đã xác nhận.
- `extras/docs/huong-dan-ldc1612-scan-tap-mesh.vi.md`: cập nhật adaptive mesh và trình tự bù nhiệt từ nguội, lấy mẫu giấy mỗi 2°C tới nhiệt cuộn mục tiêu khoảng 58°C.
- Backup Git/live trước sửa: `extras/backups/pre-ldc1612-recalibration-20261122/`.

## Chưa xác minh

- CFG nhiệt mới chưa nạp production. Chưa chạy `TEMPERATURE_PROBE_CALIBRATE`, chưa có `drift_calibration` hoặc tap threshold của cảm biến mới, chưa mesh nóng/adaptive hay thử first layer. `PRINT_START` phải còn bị chặn do thiếu threshold mới.
- Lỗi MCU `Missed scheduling of next digital out event` từ ngày trước vẫn chưa có nguyên nhân xác định; theo dõi khi thử QGL/mesh nóng.
