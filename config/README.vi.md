# Payload Cấu hình Klipper Active

[English](README.md) | [Tiếng Việt](README.vi.md) | [Tổng quan dự án](../README.vi.md)

Thư mục này chứa payload do repository sở hữu và triển khai sang `~/printer_data/config`. `scripts/install.sh` loại Markdown khi deploy, đồng thời giữ dữ liệu runtime, backup cục bộ, kết quả hiệu chuẩn và link readonly của KTC-Easy.

## Chuỗi include

`printer.cfg` nạp module active theo thứ tự:

```ini
[include mainsail.cfg]
[include toolchanger/readonly-configs/toolchanger-include.cfg]
[include Printer-Setup/calibration-probe.cfg]
[include Printer-Setup/hardware.cfg]
[include Printer-Setup/fans-leds.cfg]
[include Printer-Setup/input-shaper.cfg]
[include Printer-Setup/nozzle-clean.cfg]
[include Printer-Setup/prime-lines.cfg]
[include Printer-Setup/print-macros.cfg]
[include Printer-Setup/filament-dryer.cfg]
[include Printer-Setup/test-speed.cfg]
[include Printer-Setup/tool-temp-bench.cfg]
[include Printer-Setup/tool-crash.cfg]
```

Thử nghiệm SexBolt có người giám sát dùng `[tools_calibrate]` của KTC-Easy trong `Printer-Setup/calibration-probe.cfg`. Axiscope vẫn được cài ngoài repository nhưng section Klipper bị tắt vì hai backend cùng chiếm đầu vào hiệu chuẩn PF2 và không thể tồn tại đồng thời.

## Quyền sở hữu

| Đường dẫn | Chủ thể / mục đích |
| --- | --- |
| `printer.cfg` | Git/người dùng; include chính, động học, giới hạn và `SAVE_CONFIG` live |
| `Printer-Setup/*.cfg` | Git/người dùng; probe, phần cứng, quạt, LED và macro vận hành |
| `toolchanger/toolchanger-config.cfg` | Git/người dùng; workflow dock, input shaper và override tương thích |
| `toolchanger/tools/T0.cfg` … `T4.cfg` | Git/người dùng; EBB36, extruder, quạt, sensor và tọa độ dock |
| `toolchanger/readonly-configs/` | Installer KTC-Easy; không sửa thủ công |
| `scripts/` | Git/người dùng; deploy, update, cleanup và runtime patch đã review |
| `moonraker.conf` | Git/người dùng; API và Update Manager |

## Giá trị phần cứng chuẩn

| Chức năng | Giá trị active |
| --- | --- |
| MCU chính | CAN UUID `19b203d75137` |
| Cartographer | CAN UUID `da13d909ce34`; Touch home tại `(174, 168)` |
| Công tắc hiệu chuẩn SexBolt | `^PF2`; tâm `(80, -5.5)`; nozzle tiếp xúc quan sát gần Z12; tiếp cận an toàn Z18 |
| XY | X `PE6`/`PF0`, Y `PE2`/`PF1`; 350 mm/s, 7000 mm/s² |
| Z | `PG9`, `PB4`, `PG13`, `PB8`; 80 mm/s, 1000 mm/s² |
| Bàn nhiệt | Heater `PA1`, sensor `PB0`, tối đa 120 °C |
| Buồng in | Sensor `PB1`, quạt tuần hoàn `PF8` |
| Làm mát điện tử | TMC `PF9`, CM4 `PF6`, MCU/vỏ `PF7` |
| Đèn | LED buồng `PD15`; LED tool trên `PD3` của từng EBB36 |

## Quyền sở hữu hiệu chuẩn

- Cartographer: home Z, chuẩn Touch, adaptive bed mesh và ADXL345 trên shuttle.
- SexBolt `tools_calibrate`: đo XYZ tương đối giữa các tool có người giám sát trên PF2.
- Khối `SAVE_CONFIG` trong `printer.cfg`: nguồn chuẩn cho offset XYZ T1–T4.
- `CALIBRATE_MOVE_OVER_PROBE` và `CALIBRATE_ALL_OFFSETS` được bật với guard home/toolchanger; hiệu chuẩn offset probe vẫn bị chặn.
- kTAMV, ToolVision, TKC, KCC, Axiscope và các cấu hình SexBolt cũ chỉ còn là tài liệu lịch sử.

## Hành vi triển khai

`scripts/install.sh` từ chối deploy nếu sáu link readonly KTC-Easy thiếu hoặc hỏng. Script sao lưu config live, giữ đường dẫn runtime của máy, áp dụng patch `tool_crash` đã review khi cần và giữ năm backup cài đặt gần nhất trên máy in.

Máy thật có thể giữ dịch vụ Axiscope và entry update-manager được quản lý bên ngoài, nhưng dịch vụ này không phải backend hiệu chuẩn Klipper active trong lần thử.

Chỉ deploy khi máy in đang rảnh. Sau restart Moonraker/Klipper, kiểm tra `CALIBRATION_STATUS`, `CHECK_OFFSETS`, heater, quạt, homing và tool detection trước khi in.
