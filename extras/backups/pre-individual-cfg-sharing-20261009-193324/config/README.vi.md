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

`Printer-Setup/calibration-probe.cfg` bật Axiscope làm backend `probe_multi_axis` duy nhất. Axiscope quản lý đo XY bằng camera; công tắc PF2 tháo rời cho Z tương đối sơ bộ; test first-layer quyết định Z production cuối.

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
| Công tắc hiệu chuẩn Z sơ bộ | `^PF2`; đế tại `(80, -8)`; vùng chạm quan sát Z0–2; Axiscope bắt đầu tại Z3 và di chuyển an toàn ở Z15 |
| XY | X `PE6`/`PF0`, Y `PE2`/`PF1`; 350 mm/s, 7000 mm/s² |
| Z | `PG9`, `PB4`, `PG13`, `PB8`; 80 mm/s, 1000 mm/s² |
| Bàn nhiệt | Heater `PA1`, sensor `PB0`, tối đa 120 °C |
| Buồng in | Sensor `PB1`, quạt tuần hoàn `PF8` |
| Làm mát điện tử | TMC `PF9`, CM4 `PF6`, MCU/vỏ `PF7` |
| Đèn | LED buồng `PD15`; LED tool trên `PD3` của từng EBB36 |

## Quyền sở hữu hiệu chuẩn

- Cartographer: home Z, chuẩn Touch, adaptive bed mesh và ADXL345 trên shuttle.
- Axiscope: đo XY bằng camera và đo Z tương đối sơ bộ có người giám sát trên PF2.
- Khối `SAVE_CONFIG` trong `printer.cfg`: nguồn chuẩn cho offset XYZ T1–T4.
- `_CALIBRATION_SWITCH.z: 15` là độ cao di chuyển XY/đổi tool an toàn. Axiscope bắt đầu tại Z3 trên vùng chạm quan sát Z0–2. Sau khi kiểm tra cả hai trạng thái PF2 bằng `QUERY_ENDSTOPS`, dùng `CALIBRATE_COARSE_Z_OFFSETS CONFIRM=1`; lệnh chỉ báo Z sơ bộ. Axiscope và helper KTC cũ không được tự ghi file cấu hình; XY được xem lại rồi nhập thủ công, còn Z cuối luôn lấy từ test first-layer. `CALIBRATE_ALL_OFFSETS` cũ và hiệu chuẩn offset probe tiếp tục bị chặn.
- kTAMV, ToolVision, TKC, KCC và các cấu hình SexBolt cũ chỉ còn là tài liệu lịch sử.

Trước mỗi lần đổi tool trong chu trình hiệu chuẩn, `_CALIBRATE_SAFE_TRANSIT` nâng thẳng lên ít nhất độ cao di chuyển Z15 đã cấu hình; macro không di chuyển XY.

Phải tháo đế trước `G28`, QGL, bed mesh, Cartographer Touch hoặc in. Home khi mặt bàn thông thoáng, nâng tới Z15, lắp đế rồi xác nhận X80/Y-8 và trạng thái công tắc PF2 trước khi dò có người giám sát.

## Thông số để dùng trên máy khác

Xem [hướng dẫn điều chỉnh](../extras/docs/machine-adaptation.md). Chỉnh các block biến của macro và thông số phần cứng tại file sở hữu chúng; không chép PID, dock hay offset của máy này sang máy khác. Chạy thử đồng bộ khi máy đích rảnh bằng `VORON_DEPLOY_DRY_RUN=1 bash config/scripts/install.sh`; lệnh chỉ xem trước.

## Hành vi triển khai

`scripts/install.sh` từ chối deploy nếu sáu link readonly KTC-Easy thiếu hoặc hỏng. Script sao lưu config live, giữ đường dẫn runtime của máy, áp dụng patch `tool_crash` đã review khi cần và giữ toàn bộ backup hiện có cùng file riêng tại đích. Script kiểm tra trạng thái máy qua Moonraker trước khi ghi và dừng nếu thiếu runtime/patch chống rơi tool.

Dịch vụ và Klipper extra Axiscope được Moonraker quản lý bên ngoài; repository chỉ triển khai phần tích hợp `.cfg`.

Chỉ deploy khi máy in đang rảnh. Sau restart Moonraker/Klipper, kiểm tra `CALIBRATION_STATUS`, `CHECK_OFFSETS`, heater, quạt, homing và tool detection trước khi in.
