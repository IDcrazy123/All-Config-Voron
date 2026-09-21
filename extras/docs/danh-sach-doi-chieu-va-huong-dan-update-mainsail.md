# Đối chiếu và Cập nhật qua Mainsail

Tài liệu này mô tả code hiện hành ngày 2026-09-21.

## Nguồn sở hữu

| Nhóm | Nguồn chuẩn | Ghi chú |
| --- | --- | --- |
| Config production | `config/` trong repository | Được `install.sh` triển khai |
| KTC readonly | `~/klipper-toolchanger-easy/` | Link trong `toolchanger/readonly-configs/`; không sửa từ repository |
| Axiscope | `~/axiscope` | Runtime ngoài repository, Moonraker quản lý; không phải backend Klipper active trong thử nghiệm SexBolt |
| Generated data | `Generated-Data/`, `ShakeTune_results/` | Giữ cục bộ, không bị rsync xóa |
| Offset tool | `config/printer.cfg` `SAVE_CONFIG` | Phải đối chiếu với máy thật trước khi deploy |

## Kiểm tra trước Update

1. Máy đang idle, không gia nhiệt và không đổi tool.
2. Commit đã được review/push lên `origin/main`.
3. `git status` ở checkout trên máy không có sửa đổi cục bộ cần giữ.
4. Sáu symlink KTC readonly tồn tại và không gãy.
5. Nếu thử SexBolt, xác nhận `[tools_calibrate]` được nạp và `SEXBOLT_QUERY` đổi đúng giữa `open`/`TRIGGERED` trước mọi chuyển động dò.

## Update

Trong Mainsail chọn **Settings → Machine → Update Manager → All-Config-Voron → Update**.

Moonraker pull repository rồi gọi `config/scripts/install.sh`. Script:

- từ chối chạy nếu link KTC readonly hỏng;
- kiểm tra/áp dụng patch active-tool cho `tool_crash.py`;
- sao lưu `~/printer_data/config` vào `~/printer_data/config_backups/config-install-<timestamp>`;
- rsync file do repository sở hữu, giữ runtime data và link KTC;
- xóa Markdown khỏi config root trên máy;
- giữ năm backup cài đặt gần nhất.

Script không cài hoặc xác thực binary/service Axiscope; Axiscope được quản lý riêng qua `[update_manager axiscope]`.

## Xác nhận sau Update

1. Restart Moonraker/Klipper khi máy idle.
2. Kiểm tra không có lỗi parse config hoặc duplicate section.
3. Chạy `CALIBRATION_STATUS` và `CHECK_OFFSETS`.
4. Đối chiếu offset T1–T4 với repository.
5. Kiểm tra heater/fan ở trạng thái an toàn.
6. Home có giám sát, sau đó thử detection/pickup từng tool ở tốc độ phù hợp.
7. Chỉ in sau khi test nhỏ xác nhận first layer và đổi tool.

## Trạng thái máy được quan sát ngày 2026-09-21

Checkout máy đã được fast-forward an toàn tới `origin/main`; trạng thái dirty cũ được giữ trong stash và installer đã tạo backup live trước deploy. Axiscope service vẫn được quản lý ngoài repository, nhưng thử nghiệm SexBolt thay section `[axiscope]` bằng `[tools_calibrate]` trong Klipper vì hai backend không thể cùng hoạt động trên PF2.
