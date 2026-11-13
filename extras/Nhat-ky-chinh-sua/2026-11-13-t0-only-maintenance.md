# 2026-11-13 — Chế độ T0-only khi bảo trì T1–T4

## Yêu cầu và trạng thái trước sửa

- Người vận hành báo T1 lỗi cảm biến và yêu cầu ngắt T1–T4 để có thể in bằng T0. Không dùng số nhiệt T1 báo khoảng 114°C để suy ra nhiệt độ thực của hotend.
- Moonraker `192.168.1.43:7125`: bản in trước đã hoàn tất, `print_stats=complete`, `idle_timeout=Idle`, không pause, `_PRINT_STATE=idle`, toolchanger `ready` nhưng shuttle rỗng (active/detected đều `None`), mọi heater target bằng 0; máy chưa home. `configfile.warnings=[]`.
- Nội dung `printer.cfg` trước SAVE_CONFIG và khối SAVE_CONFIG của live khớp repository theo dòng. `print-macros.cfg` live cũng khớp Git. Include KTC do installer quản lý dùng glob `../tools/T*.cfg`, nên nếu rút EBB1–4 mà giữ include này thì Klipper vẫn đợi các MCU mất kết nối.

## Thay đổi đã nạp

- `config/printer.cfg`: thay include tổng `toolchanger/readonly-configs/toolchanger-include.cfg` bằng đúng thứ tự các include KTC core, include riêng `toolchanger/tools/T0.cfg`, rồi `toolchanger/toolchanger-config.cfg`. Không sửa file readonly do KTC quản lý và không sửa T1–T4.cfg.
- Trong SAVE_CONFIG của cùng file, tạm bỏ 8 section `[extruder1]`–`[extruder4]` và `[tool T1]`–`[tool T4]`. Nếu giữ các section đó mà không nạp file tool tương ứng, Klipper sẽ thấy section thiếu cấu hình phần cứng. PID T0, heater_bed, bed mesh và model Cartographer vẫn nguyên. Bản gốc đầy đủ nằm trong backup.
- `config/Printer-Setup/print-macros.cfg`: thêm kiểm tra `PRINT_START` cho Tn_TEMP dương của tool không còn đăng ký; G-code cũ nhiều màu bị từ chối trước nhiệt và chuyển động. `TOOL>0` đã bị nhánh kiểm tra tool registry hiện hữu chặn.
- Sao lưu bản Git và live trước sửa ở `extras/backups/pre-t0-only-20261113-150049/`. Sao lưu live trên máy ở `/home/voron/printer_data/config_backups/pre-t0-only-20261113-3L1jG9/`.

## Kiểm tra và triển khai

- Parser Klipper trên máy đọc bản thử trong `/tmp/t0-only-preflight.3mhoTA`: 204 section cũ thành 160; đúng 44 section thuộc T1–T4 bị loại, không thêm section mới và mọi section còn lại giữ nguyên giá trị. T0 MCU, extruder, tool và macro vẫn có mặt.
- Jinja guard được thử offline: T0-only được chấp nhận, `T3_TEMP=260` bị từ chối khi registry chỉ `[0]`, và được chấp nhận khi registry đủ năm tool. `git diff --check` sạch.
- Trước khi ghi, kiểm tra lại trạng thái idle, shuttle rỗng, mọi target 0 và hash hai file live; backup trên máy được kiểm tra hash. Chỉ hai file `printer.cfg` và `Printer-Setup/print-macros.cfg` được thay atomically. Một `RESTART` qua Moonraker trả `ok`.
- Sau restart: Klipper `ready`, `configfile.warnings=[]`, `toolchanger.tool_numbers=[0]`, không có `[tool T1]` hoặc `extruder1` loaded, `print_stats=standby`, homing trống, bed/T0 target=0. Không chạy G28, gắp T0, gia nhiệt hoặc in thử.

## Sử dụng và khôi phục

- Trong Orca, chỉ gán vật thể cho filament/tool 1 tương ứng T0, slice lại, kiểm tra Start G-code có `TOOL=0`, `T0_TEMP` và không có `T1_TEMP`–`T4_TEMP` hoặc lệnh `T1`–`T4`. Không dùng lại G-code nhiều tool đã tải lên trước đây. Máy hiện ở trạng thái cần home như sau restart.
- Trước khi rút/nối CAN hoặc tháo tool, cắt nguồn máy và xác nhận hotend nguội bằng phép kiểm tra độc lập vì cảm biến T1 không tin cậy. Kiểm tra T0 trong dock, đầu dò Cartographer/shuttle và đường đi trống trước khi in thử T0 có giám sát.
- Để phục hồi năm tool: sửa xong cảm biến T1, nối lại T1–T4 và kiểm tra CAN; đối chiếu mọi calibration phát sinh trong thời gian T0-only, sau đó khôi phục include tổng cùng 8 section SAVE_CONFIG từ backup, bỏ guard không cần thiết nếu muốn, nạp lại lúc máy idle và xác minh từng tool. Không ghi đè mù toàn bộ backup nếu T0, bed hoặc Scan đã được hiệu chuẩn thêm.
