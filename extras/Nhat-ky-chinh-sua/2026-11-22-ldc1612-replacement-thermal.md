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

## Triển khai và thử bù nhiệt

- Commit `4b9e6a9` đã được push và triển khai khi máy idle bằng `config/scripts/install.sh`; backup production ở `/home/voron/printer_data/config_backups/config-install-20261122-065344-eBgz9Q`. Kiểm tra lại live: Klipper `ready`, đường cong Z nguội và `calibration_temp=22,057667` có hiệu lực; tap threshold và mesh cũ đã xóa. Tùy chọn bù nhiệt T0 150°C/bàn 100°C đã nạp. `PRINT_START` đã dùng adaptive mesh theo vùng vật thể, nhưng vẫn bị chặn trước khi gia nhiệt do chưa có threshold mới.
- G28 với đường cong mới thành công; T0 active/detected=0. Bắt đầu `TEMPERATURE_PROBE_CALIBRATE PROBE=ldc1612_eddy_coil TARGET=58 STEP=2`. Lượt giấy đầu được người vận hành `ACCEPT` ở nhiệt cuộn khoảng 24,03°C; Klipper tự đặt bàn 100°C và vòi 150°C. Người vận hành tiếp tục `ACCEPT` lượt hai khoảng 27,31°C và lượt ba khoảng 30,80°C.
- Khi bàn khoảng 86,4°C, vòi khoảng 149,4°C, cuộn khoảng 31,2°C, MCU chính shutdown `Missed scheduling of next digital out event` (`klippy.log` dòng 27081/27285 của phiên 2026-11-22). Lượt hiệu chuẩn bị hủy trước khi tới 100°C; không có `drift_calibration` được lưu, trạng thái `compensation_enabled=false`. Người vận hành tự `FIRMWARE_RESTART`, G28, QGL; QGL đạt dải 0,006297 mm. Kiểm tra sau đó: `ready`, XYZ homed, T0 active/detected=0, vòi ở X173,2/Y169,5/Z35, cả hai heater target 0, không in.
- Ở thời điểm shutdown, log cho thấy gói `queue_digital_out oid=31` cuối trên MCU chính lúc 2621,944883; lệnh hết hạn đúng khoảng 3 giây sau. Cảm biến ADC và LDC1612 vẫn trả dữ liệu, CAN không có lỗi/retransmit, tải CPU khoảng 0,67. `heaters.py` thiết lập giới hạn gia hạn đầu ra 3 giây; `gpiocmds.c` shutdown khi hàng đợi digital output rỗng. OID 31 nhiều khả năng là điều khiển SSR bàn PA5, nhưng chưa có ánh xạ OID độc lập nên chưa coi là kết luận cuối. Không tăng watchdog hoặc nới bảo vệ heater để che lỗi. Lỗi từng lặp khi bàn ổn định quanh 100°C, nên không thể quy riêng cho giai đoạn tăng nhiệt.

## Còn chờ

- Cần xác định và xử lý lỗi lịch digital output trước khi chạy tiếp bù nhiệt nóng. Sau đó chạy lại từ bàn/vòi/cuộn nguội, hoàn tất các lượt giấy đến nhiệt cuộn mục tiêu, `SAVE_CONFIG`, kiểm tra `compensation_enabled=true`, rồi mới hiệu chuẩn tap threshold, mesh nóng và first layer.
