# Cấu hình Production Voron 2.4 StealthChanger 5 Tool

[English](README.md) | [Tiếng Việt](README.vi.md) | [Cấu hình active](config/README.vi.md) | [Tài liệu](extras/docs/README.vi.md) | [Profile OrcaSlicer](Orca%20Config/README.vi.md)

Kho cấu hình Klipper production cho Voron 2.4 CoreXY 350 mm dùng năm đầu in StealthChanger. KTC-Easy quản lý đổi tool, Cartographer V3 quản lý home Z/quét mesh, Axiscope đo XY, công tắc PF2 đo Z tương đối sơ bộ và test first-layer quyết định Z production cuối cùng.

## Kiến trúc production hiện tại

| Phân hệ | Cấu hình active |
| --- | --- |
| Controller / host | BTT Manta M8P V2.0 + BTT CM4, CAN `can0` |
| Toolhead | 5 × BTT EBB36 V1.2, extruder WW BMG, hotend TZ V6 2.0 |
| Toolchanger | KTC-Easy, năm dock tại tọa độ đã đo, cảm biến hiện diện OptoTap |
| Home Z / mesh | Cartographer V3 Touch tại `(174, 168)`; mesh adaptive 55 × 55 |
| Hiệu chuẩn tool | Camera Axiscope cho XY; công tắc PF2 tại `(80, -8)` cho Z sơ bộ từ Z3 trên vùng chạm quan sát Z0–2; test first-layer cho Z cuối |
| Giới hạn chuyển động | XY 350 mm/s, 7000 mm/s²; Z 80 mm/s, 1000 mm/s² |
| Bàn nhiệt | Silicone AC 1000 W qua SSR chân `PA1`; sensor `PB0`; tối đa 120 °C |
| Làm mát | TMC `PF9`, CM4 `PF6`, MCU/vỏ `PF7`, tuần hoàn buồng `PF8` |
| Chiếu sáng | 40 × WS2812B chân `PD15` và 3 LED trên mỗi toolhead |
| Slicer | Profile OrcaSlicer đồng bộ từ `%APPDATA%\OrcaSlicer\user` |

## Bản đồ tool hiện tại

Các offset dưới đây lấy trực tiếp từ `config/printer.cfg` đang quản lý production.

| Tool | CAN UUID | Dock `(X, Y, Z)` | Offset `(X, Y, Z)` |
| --- | --- | --- | --- |
| T0 | `441e1484ac41` | `(30.2, 1.8, 343)` | `(0, 0, 0)` chuẩn |
| T1 | `6475b5b9e028` | `(104, 1.5, 343)` | `(-0.139, -0.341, 0.1665)` |
| T2 | `4ad9d622a836` | `(176, 2.1, 343)` | `(1.095, -0.090, -0.3515)` |
| T3 | `c2465b7c36f8` | `(249.5, 2.5, 343)` | `(0.003, 0.369, -0.3265)` |
| T4 | `28650279df58` | `(321.5, 3.1, 343)` | `(0.213, -0.007, 0.0279)` |

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

## Điều chỉnh cho máy khác

Đọc [hướng dẫn thông số cần đổi](extras/docs/machine-adaptation.md) để biết từng giá trị nằm ở đâu và phần logic nào dùng chung. [Báo cáo rà soát 2026-10-09](extras/docs/project-audit-2026-10-09.md) ghi các lỗi đã xác nhận và việc cần kiểm chứng tiếp. Đây là profile của một máy thật; người dùng khác phải thay MCU, pin, dock và dữ liệu hiệu chuẩn của chính máy họ.

## Triển khai

Nên dùng sparse clone trên máy in để không tải các artifact lịch sử:

```bash
git clone --depth=1 --filter=blob:none --sparse \
  https://github.com/IDcrazy123/All-Config-Voron.git ~/All-Config-Voron
cd ~/All-Config-Voron
git sparse-checkout set config
bash config/scripts/install.sh
```

`install.sh` kiểm tra sáu symlink readonly của KTC-Easy, kiểm tra/áp dụng patch active-tool cho `tool_crash.py`, sao lưu config đang chạy, triển khai file do repository sở hữu và giữ các file riêng tại đích cùng mọi backup hiện có. Script từ chối ghi khi Moonraker chưa xác nhận máy rảnh, yêu cầu runtime/patch chống rơi tool và hỗ trợ `VORON_DEPLOY_DRY_RUN=1`.

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
| Hiệu chuẩn/báo cáo | `QUERY_ENDSTOPS`, `CALIBRATE_MOVE_OVER_PROBE`, `CALIBRATE_COARSE_Z_OFFSETS`, `CALIBRATION_STATUS`, `CHECK_OFFSETS` |
| Kiểm tra chuyển động/nhiệt | `TEST_SPEED`, `TEST_Z_SPEED`, `MEASURE_TOOL_HEATUP` |
| Đèn/quạt | `LIGHTS_ON`, `LIGHTS_OFF`, `BED_FAN_ON`, `BED_FAN_OFF` |

Axiscope là backend `probe_multi_axis` duy nhất đang hoạt động. Workflow camera của Axiscope đo XY; công tắc PF2 tại `(80, -8)` chỉ cho kết quả Z tương đối sơ bộ. Đường dò bắt đầu tại Z3, cao hơn 1 mm so với mép trên của vùng chạm quan sát Z0–2, dùng năm mẫu và gia nhiệt từng nozzle đã chọn tới 150 °C. Z15 vẫn là độ cao di chuyển XY/đổi tool an toàn. Sau khi dùng `QUERY_ENDSTOPS` xác nhận `Axiscope:open` và `Axiscope:TRIGGERED`, phải chủ động gọi `CALIBRATE_COARSE_Z_OFFSETS CONFIRM=1` trong khi có người giám sát. Cố ý không cho Axiscope tự ghi file cấu hình: phải xem lại kết quả, nhập XY thủ công sau khi sao lưu, và chốt từng Z production bằng test first-layer. `CALIBRATE_ALL_OFFSETS` tiếp tục bị chặn để tránh dùng nhầm workflow XYZ đã nghỉ hưu.

Trước mỗi lần đổi tool, chu trình hiệu chuẩn nâng thẳng lên ít nhất Z15 để đường đi tới dock rời công tắc ở độ cao an toàn.

Tháo đế trước `G28`, QGL, bed mesh, Cartographer Touch hoặc in. Home khi mặt bàn thông thoáng, nâng tới Z15, lắp đế, xác nhận X80/Y-8 và trạng thái công tắc rồi mới chạy phép đo Z sơ bộ có giám sát. Xem [quy trình hiệu chuẩn tool](extras/docs/huong-dan-he-thong-stealthchanger.md#hiệu-chuẩn-tool).

## An toàn và hoàn tác

- Đây là cấu hình firmware production.
- Sao lưu mọi `.cfg`, `.conf`, `.sh` trước khi sửa.
- Không đổi PID, dòng motor, giới hạn chuyển động/nhiệt hoặc hình học probe khi chưa có dữ liệu đo.
- Không triển khai trong lúc in hoặc đang đổi tool.
- Mỗi lần chạy `install.sh` tạo snapshot tại `~/printer_data/config_backups/`.

Đọc [`extras/docs/legacy-calibration-troubleshooting.md`](extras/docs/legacy-calibration-troubleshooting.md) để nhận biết nhanh lỗi từ ToolVision, kTAMV, TKC/KCC, các lần thử SexBolt trước và Axiscope.

## Ghi công

Cấu hình này sử dụng [Voron Design](https://vorondesign.com/), [StealthChanger](https://stealthchanger.com/), [KTC-Easy](https://github.com/jwellman80/klipper-toolchanger-easy), [Axiscope](https://github.com/nic335/Axiscope), [Cartographer](https://cartographer3d.com/), [Mainsail](https://mainsail.xyz/) và [Klippain Shake&Tune](https://github.com/Frix-x/klippain-shaketune).
