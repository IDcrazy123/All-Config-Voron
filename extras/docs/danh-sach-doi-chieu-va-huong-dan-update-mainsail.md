# Đối chiếu và Cập nhật qua Mainsail

Tài liệu này mô tả code hiện hành ngày 2026-09-21.

## Nguồn sở hữu

| Nhóm | Nguồn chuẩn | Ghi chú |
| --- | --- | --- |
| Config production | `config/` trong repository | Được `install.sh` triển khai |
| KTC readonly | `~/klipper-toolchanger-easy/` | Link trong `toolchanger/readonly-configs/`; không sửa từ repository |
| Axiscope | `~/axiscope` | Runtime ngoài repository, Moonraker quản lý |
| Generated data | `Generated-Data/`, `ShakeTune_results/` | Giữ cục bộ, không bị rsync xóa |
| Offset tool | `config/printer.cfg` `SAVE_CONFIG` | Phải đối chiếu với máy thật trước khi deploy |

## Kiểm tra trước Update

1. Máy đang idle, không gia nhiệt và không đổi tool.
2. Commit đã được review/push lên `origin/main`.
3. `git status` ở checkout trên máy không có sửa đổi cục bộ cần giữ.
4. Sáu symlink KTC readonly tồn tại và không gãy.
5. Axiscope service đang active nếu cần hiệu chuẩn.

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

Máy thật truy cập SSH được; Klipper và Axiscope đều active. Checkout `~/All-Config-Voron` trên máy đang ở commit cũ và dirty, trong khi `~/printer_data/config` chứa phần lớn config mới hơn. Vì vậy phải làm sạch/đồng bộ checkout bằng Update Manager trước khi coi checkout trên máy là nguồn chuẩn. Không dùng checkout cũ để ghi đè config live.
