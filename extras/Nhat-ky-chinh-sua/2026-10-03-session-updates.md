# Nhật ký — 2026-10-03

## 1. Đảo mapping driver motor X/Y trên Manta M8P V2.0

### Mục tiêu
Khôi phục homing X/Y sau khi hai giắc motor bị cắm chéo giữa hai cổng driver trên Manta M8P V2.0.

### File đã sửa đổi
- `config/Printer-Setup/hardware.cfg` — đảo mapping step/dir/enable/UART giữa X và Y; cập nhật chú thích motor.

### Sao lưu
- [hardware.cfg (Backup)](file:///D:/Desktop/All-Config-Voron-main/Voron%205%20Tool/extras/backups/pre-swap-xy-motor-drivers-20261003-123246/hardware.cfg)

### Chi tiết thay đổi
- `[stepper_x]`: `PE6/PE5/!PC14` → `PE2/PE1/!PE4`; UART `PC13` → `PE3`.
- `[stepper_y]`: `PE2/PE1/!PE4` → `PE6/PE5/!PC14`; UART `PE3` → `PC13`.
- Giữ nguyên endstop `PF0`/`PF1`, hướng home, hành trình, dòng motor và các thông số chuyển động.

### Lý do
Ban đầu người vận hành báo đã cắm chéo hai giắc motor X/Y tại Manta; sau đó đính chính rằng chưa cắm lại giắc và chúng không bị đảo. Klipper log có báo `No trigger on stepper_x after full movement` và `No trigger on stepper_y after full movement`; các lỗi này không xác nhận việc đổi chéo dây.

### Kiểm tra
- Kiểm tra cấu trúc và mapping cấu hình: đạt.
- Tải cấu hình lên máy `192.168.1.43`; nội dung live khớp repo.
- `FIRMWARE_RESTART`: thành công; Klipper trở lại `ready`, máy ở `standby`.
- Homing chuyển động X/Y và in thử: chưa chạy; chưa xác minh chuyển động thực tế.

### Kết quả
Mapping driver X/Y đã được đảo trong repo và trên máy. Klipper nạp cấu hình thành công; các trục hiện vẫn chưa home.

### Vấn đề còn lại
Cần người vận hành đứng cạnh máy kiểm tra home X rồi Y. Nếu carriage đi xa endstop hoặc hướng di chuyển sai, dừng ngay và báo lại trước khi tiếp tục.
## 2. Đính chính và khôi phục mapping motor X/Y gốc

### Mục tiêu
Khôi phục mapping ban đầu sau khi người vận hành đính chính rằng hai giắc motor chưa được cắm lại và không bị đảo chéo.

### File đã sửa đổi
- `config/Printer-Setup/hardware.cfg` — khôi phục mapping step/dir/enable/UART ban đầu.
- `extras/Nhat-ky-chinh-sua/2026-10-03-session-updates.md` — đính chính nguyên nhân và ghi kết quả khôi phục.

### Sao lưu
- [hardware.cfg (Backup)](file:///D:/Desktop/All-Config-Voron-main/Voron%205%20Tool/extras/backups/pre-restore-xy-motor-mapping-20261003-123813/hardware.cfg)

### Chi tiết thay đổi
- `[stepper_x]`: `PE2/PE1/!PE4` → `PE6/PE5/!PC14`; UART `PE3` → `PC13`.
- `[stepper_y]`: `PE6/PE5/!PC14` → `PE2/PE1/!PE4`; UART `PC13` → `PE3`.
- Giữ nguyên endstop `PF0`/`PF1` và mọi thông số còn lại.

### Lý do
Hai giắc motor không bị cắm chéo; mapping production ban đầu cần được giữ nguyên.

### Kiểm tra
- Kiểm tra mapping trong cấu hình: đạt.
- Cấu hình live khớp repo sau khi nạp.
- `FIRMWARE_RESTART`: thành công; Klipper trở lại `ready`, máy ở `standby`.
- Home X/Y: chưa chạy; `homed_axes` vẫn rỗng.

### Kết quả
Mapping ban đầu đã được khôi phục trong repo và trên máy in.

### Vấn đề còn lại
Máy vẫn chưa home X/Y; cần home lại trước khi di chuyển/in.
## 3. Kiểm tra loa tích hợp BTT HDMI5 V1.2

### Triệu chứng
- Phát thử WAV qua HDMI hiện dòng `Playing WAVE...` nhưng người vận hành không nghe thấy âm thanh.
- Ảnh bo mạch HDMI5 V1.2 có cụm loa tròn tích hợp ở mặt sau.

### Phân tích
- ALSA HDMI device `hdmi:CARD=vc4hdmi0,DEV=0` chấp nhận luồng âm thanh; điều đó chưa chứng minh loa vật lý phát được tiếng.
- Cấu hình boot có `hdmi_drive=1`, giá trị được tài liệu Raspberry Pi mô tả là DVI/no sound; `vcgencmd get_config hdmi_drive` trả `unknown` trên hệ thống KMS này nên chưa xác minh dòng đó có hiệu lực.

### Hướng kiểm tra tiếp theo
- Đề xuất phát sóng sine 1 kHz qua HDMI bằng `speaker-test -D hdmi:CARD=vc4hdmi0,DEV=0 -c 2 -t sine -f 1000 -l 3`.
- Nếu vẫn im lặng, thử tai nghe có dây ở jack 3,5 mm của màn hình để phân biệt lỗi luồng HDMI với loa/amplifier tích hợp.

### Kết quả
Chưa xác nhận loa phát được âm thanh; chưa sửa cấu hình hoặc bật cảnh báo.
