# Nhật ký — 2026-09-30

## 1. Hậu kiểm reboot sau cập nhật hệ thống

### Mục tiêu

Xác nhận máy trở lại trạng thái ổn định sau khi kernel và package hệ thống được cập nhật tuần tự ngày 2026-09-29.

### Kiểm tra

- Máy khởi động lúc 15:29:50 với kernel `6.12.109+rpt-rpi-v8`; không có failed unit.
- Klipper, Moonraker, nginx, Crowsnest, KlipperScreen và Tailscale active; Mainsail và camera snapshot trả HTTP 200.
- Sonar `inactive/dead` với lần thoát `0/SUCCESS`, đúng cấu hình mặc định `enable=False` do không có `sonar.conf`.
- `vcgencmd get_throttled` trả `0x0`.
- CAN ở `ERROR-ACTIVE`, queue length 128; cả main MCU, EBB0–EBB4 và Cartographer đều active với `rx_error=0`, `tx_error=0`, `tx_retries=0` tại thời điểm hậu kiểm.
- Klipper `ready/standby`; XYZ chưa home; heater target đều 0; virtual SD không active; T0 được nhận nhưng toolchanger chưa initialize, đúng trạng thái sau reboot.

### Kết quả

Không phát hiện regression hậu reboot. Không gửi G-code, không di chuyển và không gia nhiệt.

## 2. Chuyển quyền hiệu chuẩn sang Axiscope / PF2 / first-layer

### Mục tiêu

Chuẩn hóa workflow theo quyết định vận hành mới: Axiscope đo XY; công tắc vật lý PF2 tại X80/Y-8 đo Z tương đối sơ bộ trong vùng chạm quan sát Z0–2; test first-layer quyết định Z production cuối.

### File đã sửa đổi

- `config/Printer-Setup/calibration-probe.cfg` — thay `[tools_calibrate]` bằng `[axiscope]`, thêm macro Z sơ bộ có guard và chặn workflow XYZ cũ.
- `config/toolchanger/toolchanger-config.cfg` — lưu tọa độ công tắc X80/Y-8, vùng chạm Z0–2, probe start Z3, transit Z15 và cập nhật quyền sở hữu backend.
- `config/printer.cfg` — cập nhật comment include theo workflow mới.
- `README.md`, `README.vi.md`, `config/README.md`, `config/README.vi.md` — cập nhật tài liệu production.
- `extras/docs/huong-dan-he-thong-stealthchanger.md`, bản `.en.md` — cập nhật quy trình vận hành có người giám sát.

### Sao lưu

- [Bản sao trước thay đổi](<D:/Desktop/All-Config-Voron-main/Voron 5 Tool/extras/backups/pre-axiscope-calibration-workflow-20260930-160000/>)

### Chi tiết thay đổi

- Loại `[tools_calibrate]` để không còn xung đột `probe_multi_axis` với Axiscope.
- `[axiscope]` dùng `^PF2`, X80/Y-8, `zswitch_z_pos: 2`, `lift_z: 1`, vì vậy bắt đầu dò tại Z3; tốc độ Z 4 mm/s; năm mẫu. Macro nâng tới Z15 trước khi đi XY hoặc đổi tool.
- Không cấu hình `config_file_path`: Axiscope không thể tự ghi offset vào file production.
- `CALIBRATE_COARSE_Z_OFFSETS` yêu cầu XYZ đã home và toolchanger ready, rồi gọi chu trình Axiscope có người giám sát ở 150 °C. Kết quả chỉ là Z sơ bộ.
- `CALIBRATE_ALL_OFFSETS` cũ bị chặn bằng lỗi rõ ràng. Cartographer vẫn chỉ quản lý Z home/Touch và bed mesh.
- XY sau khi đo phải được xem lại và nhập thủ công có sao lưu; Z cuối chỉ được áp dụng sau test first-layer.

### Lý do

Source Axiscope xác nhận module chỉ báo Z tương đối, còn chức năng save có thể ghi trực tiếp section tool. Không cấp đường dẫn ghi giúp ngăn Z sơ bộ hoặc kết quả camera chưa review ghi đè offset first-layer đang chạy tốt.

### Kiểm tra

- `git diff --check`: đạt.
- Đối chiếu source Axiscope: `MOVE_TO_ZSWITCH` đi tới `zswitch_z_pos + lift_z`; `PROBE_ZSWITCH` dò xuống tối đa 10 mm; không tự lưu kết quả Z.
- Commit `93c60f8` đã push lên `origin/main`; máy thật fast-forward tới đúng commit.
- Installer tạo backup live `/home/voron/printer_data/config_backups/config-install-20260930-155541` trước khi đồng bộ.
- `FIRMWARE_RESTART` thành công; Klipper `ready`, không có config error/traceback. Object `axiscope` báo X80, Y-8, Z2 và `can_save_config=false`.
- `QUERY_ENDSTOPS` không chuyển động trả `Axiscope:open`; stepper Z vẫn `TRIGGERED` sau restart là trạng thái endstop Z riêng, không phải PF2 Axiscope.
- Không chạy chuyển động, heat hoặc calibration. Sau restart máy `standby`, heater target 0, XYZ chưa home và toolchanger uninitialized với T0 được sensor nhận.

### Vấn đề còn lại

- Trạng thái nhả `Axiscope:open` đã xác nhận. Trước lần đo đầu, người vận hành phải nhấn tay công tắc rồi chạy lại `QUERY_ENDSTOPS` để xác nhận `Axiscope:TRIGGERED`; quan sát đường tới X80/Y-8/Z3.
- Macro `CALIBRATE_COARSE_Z_OFFSETS` phải chạy có người giám sát, sẵn E-stop. Không dùng kết quả làm Z cuối nếu chưa in first-layer.
