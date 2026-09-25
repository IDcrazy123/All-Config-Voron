# Cấu hình Production Voron 2.4 StealthChanger 5 Tool

[English](README.md) | [Tiếng Việt](README.vi.md) | [Cấu hình active](config/README.vi.md) | [Tài liệu](extras/docs/README.vi.md) | [Profile OrcaSlicer](Orca%20Config/README.vi.md)

Kho cấu hình Klipper production cho Voron 2.4 CoreXY 350 mm dùng năm đầu in StealthChanger. Hệ thống hiện tại dùng KTC-Easy để đổi tool, Cartographer V3 để home Z/quét mesh và thử nghiệm SexBolt `tools_calibrate` có người giám sát để đo offset tương đối giữa các tool.

## Kiến trúc production hiện tại

| Phân hệ | Cấu hình active |
| --- | --- |
| Controller / host | BTT Manta M8P V2.0 + BTT CM4, CAN `can0` |
| Toolhead | 5 × BTT EBB36 V1.2, extruder WW BMG, hotend TZ V6 2.0 |
| Toolchanger | KTC-Easy, năm dock phía sau, cảm biến hiện diện OptoTap |
| Home Z / mesh | Cartographer V3 Touch tại `(174, 168)`; mesh adaptive 55 × 55 |
| Hiệu chuẩn XYZ tool | SexBolt KTC-Easy trên `^PF2`; đế tháo rời giữa bàn tại tọa độ cấu hình `(174, 168)`; Z55 đã xác nhận an toàn để di chuyển; còn phải đo Z tiếp xúc/bắt đầu dò |
| Giới hạn chuyển động | XY 350 mm/s, 7000 mm/s²; Z 80 mm/s, 1000 mm/s² |
| Bàn nhiệt | Silicone AC 1000 W qua SSR chân `PA1`; sensor `PB0`; tối đa 120 °C |
| Làm mát | TMC `PF9`, CM4 `PF6`, MCU/vỏ `PF7`, tuần hoàn buồng `PF8` |
| Chiếu sáng | 40 × WS2812B chân `PD15` và 3 LED trên mỗi toolhead |
| Slicer | Profile OrcaSlicer đồng bộ từ `%APPDATA%\OrcaSlicer\user` |

## Bản đồ tool hiện tại

Các offset dưới đây lấy trực tiếp từ `config/printer.cfg` đang quản lý production.

| Tool | CAN UUID | Dock `(X, Y, Z)` | Offset `(X, Y, Z)` |
| --- | --- | --- | --- |
| T0 | `441e1484ac41` | `(30.2, 1.3, 343)` | `(0, 0, 0)` chuẩn |
| T1 | `6475b5b9e028` | `(104, 1.1, 343)` | `(-0.139, -0.341, 0.1665)` |
| T2 | `4ad9d622a836` | `(176, 1.6, 343)` | `(1.095, -0.090, -0.3515)` |
| T3 | `c2465b7c36f8` | `(249.5, 2.5, 343)` | `(0.003, 0.369, -0.3265)` |
| T4 | `28650279df58` | `(321.5, 2.6, 343)` | `(0.213, -0.007, 0.0279)` |

Ngày 2026-09-25, người vận hành xác nhận mức chỉnh thêm `-0.0800 mm` trên BTT/KlipperScreen cho từng tool T1-T4. Các giá trị đã lưu này đã cộng mức chỉnh đúng một lần vào bộ gốc khôi phục ngày 2026-09-23; giữ nguyên T0, X/Y và Cartographer. Không chỉnh lặp lại cùng mức babystep `-0.08 mm` sau khi nạp cấu hình này. Cần in first layer mới để kiểm chứng kết quả đã lưu.

Không chép offset lịch sử từ nhật ký, snapshot tải về, thí nghiệm hoặc cấu hình đã retired vào production.

## Cấu trúc repository

```text
config/                     Payload triển khai Klipper/Moonraker
  Printer-Setup/            Phần cứng và macro vận hành
  toolchanger/              KTC user config và readonly do installer quản lý
  scripts/                  Script cài đặt, cập nhật, dọn dẹp và patch runtime
Orca Config/                Profile OrcaSlicer active và script đồng bộ
extras/docs/                Tài liệu hiện hành và chỉ mục tài liệu lịch sử
extras/retired-configs/     Cấu hình không còn được printer.cfg nạp
extras/experiments/         Bằng chứng thử nghiệm bất biến
extras/backups/             Bản phục hồi trước thay đổi có timestamp
extras/Nhat-ky-chinh-sua/   Nhật ký kỹ thuật hàng ngày
```

`config/toolchanger/readonly-configs/` thuộc quyền sở hữu KTC-Easy; không sửa thủ công.

## Triển khai

Nên dùng sparse clone trên máy in để không tải các artifact lịch sử:

```bash
git clone --depth=1 --filter=blob:none --sparse \
  https://github.com/IDcrazy123/All-Config-Voron.git ~/All-Config-Voron
cd ~/All-Config-Voron
git sparse-checkout set config
bash config/scripts/install.sh
```

`install.sh` kiểm tra sáu symlink readonly của KTC-Easy, kiểm tra/áp dụng patch active-tool cho `tool_crash.py`, sao lưu config đang chạy, triển khai file do repository sở hữu và chỉ giữ năm backup cài đặt gần nhất trên máy.

Axiscope là runtime ngoài repository, được quản lý bởi Moonraker Update Manager. Script triển khai không cài hoặc sửa Axiscope.

Cập nhật bình thường bằng cách push repository, sau đó chọn **Mainsail → Cài đặt → Máy → Trình quản lý cập nhật → All-Config-Voron → Update**. Chỉ restart khi máy in đang rảnh.

## Start G-code OrcaSlicer

```gcode
PRINT_START TOOL_TEMP={first_layer_temperature[initial_tool]} {if is_extruder_used[0]}T0_TEMP={first_layer_temperature[0]}{endif} {if is_extruder_used[1]}T1_TEMP={first_layer_temperature[1]}{endif} {if is_extruder_used[2]}T2_TEMP={first_layer_temperature[2]}{endif} {if is_extruder_used[3]}T3_TEMP={first_layer_temperature[3]}{endif} {if is_extruder_used[4]}T4_TEMP={first_layer_temperature[4]}{endif} BED_TEMP=[first_layer_bed_temperature] TOOL=[initial_tool] MATERIAL={filament_type[initial_tool]}
```

Danh sách profile active và quy trình đồng bộ nằm trong [`Orca Config/README.vi.md`](Orca%20Config/README.vi.md).

## Lệnh vận hành chính

| Khu vực | Lệnh |
| --- | --- |
| Vòng đời bản in | `PRINT_START`, `PRINT_END`, `PAUSE`, `RESUME`, `CANCEL_PRINT`, `G32` |
| Vệ sinh đầu phun | `CLEAN_NOZZLE`, `PURGE_AND_CLEAN`, `PRIME_LINES` |
| Sấy nhựa | `START_DRYER`, `STOP_DRYER`, `DRYER_STATUS` |
| Hiệu chuẩn/báo cáo | `SEXBOLT_QUERY`, `CALIBRATE_MOVE_OVER_PROBE`, `CALIBRATE_ALL_OFFSETS`, `CALIBRATION_STATUS`, `CHECK_OFFSETS` |
| Kiểm tra chuyển động/nhiệt | `TEST_SPEED`, `TEST_Z_SPEED`, `MEASURE_TOOL_HEATUP` |
| Đèn/quạt | `LIGHTS_ON`, `LIGHTS_OFF`, `BED_FAN_ON`, `BED_FAN_OFF` |

Thử nghiệm SexBolt có người giám sát dùng giá trị mặc định upstream `spread: 5.0` và `lower_z: 0.5`. `_CALIBRATION_SWITCH.z: 55` là khoảng hở di chuyển đã được người vận hành xác nhận. Mặc định, `CALIBRATE_MOVE_OVER_PROBE` đi tới tâm cấu hình ở Z55 hoặc cao hơn, không dò chạm. `contact_z: -1` và `probe_z: -1` của đế mới vẫn đánh dấu chưa đo: `CALIBRATE_ALL_OFFSETS` từ chối trước khi chọn tool, gia nhiệt hoặc di chuyển cho đến khi cả hai giá trị hợp lệ. Chế độ tiếp cận nội bộ `PROBE=1` chỉ được hạ thấp hơn độ cao di chuyển sau khi vượt qua kiểm tra các chiều cao này. `CALIBRATION_STATUS` báo giá trị đang cấu hình. `CALIBRATE_NOZZLE_PROBE_OFFSET` vẫn bị chặn để lần thử không ghi lại offset probe Cartographer.

Trước mỗi lần đổi tool, chu trình hiệu chuẩn nâng thẳng lên ít nhất Z55 để đường đi tới dock rời vùng đế ở độ cao di chuyển an toàn.

Tháo đế trước `G28`, QGL, bed mesh, Cartographer Touch hoặc in vì các thao tác này sử dụng hoặc đi qua vùng giữa bàn. Home khi mặt bàn thông thoáng, sau đó đưa đầu in tới khoảng hở Z55 đã xác nhận và tránh đường lắp trước khi lắp đế. Xác nhận nozzle T0 nằm trên tâm bi và đo Z tiếp xúc/bắt đầu dò trước khi bật hiệu chuẩn. Xem [quy trình hiệu chuẩn tool](extras/docs/huong-dan-he-thong-stealthchanger.md#hiệu-chuẩn-tool).

## An toàn và hoàn tác

- Đây là cấu hình firmware production.
- Sao lưu mọi `.cfg`, `.conf`, `.sh` trước khi sửa.
- Không đổi PID, dòng motor, giới hạn chuyển động/nhiệt hoặc hình học probe khi chưa có dữ liệu đo.
- Không triển khai trong lúc in hoặc đang đổi tool.
- Mỗi lần chạy `install.sh` tạo snapshot tại `~/printer_data/config_backups/`.

Đọc [`extras/docs/legacy-calibration-troubleshooting.md`](extras/docs/legacy-calibration-troubleshooting.md) để nhận biết nhanh lỗi từ ToolVision, kTAMV, TKC/KCC, các lần thử SexBolt trước và Axiscope.

## Ghi công

Cấu hình này sử dụng [Voron Design](https://vorondesign.com/), [StealthChanger](https://stealthchanger.com/), [KTC-Easy](https://github.com/jwellman80/klipper-toolchanger-easy), [Axiscope](https://github.com/nic335/Axiscope), [Cartographer](https://cartographer3d.com/), [Mainsail](https://mainsail.xyz/) và [Klippain Shake&Tune](https://github.com/Frix-x/klippain-shaketune).
