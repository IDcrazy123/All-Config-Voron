# 2026-11-14 — Tạm tắt T2–T4 lần hai để tiếp tục bảo trì

## Trạng thái và bằng chứng

- Người vận hành yêu cầu tạm tắt lại T2–T4. Lúc đầu máy không phản hồi ping, SSH hay Moonraker; người vận hành xác nhận vừa rút điện. Không ghi production khi máy mất kết nối.
- Sau khi máy lên mạng, Moonraker báo `startup`, `print_stats=standby`, không pause, `idle_timeout=Idle`, `_PRINT_STATE=idle`, không sấy/benchmark, active/detected rỗng, chưa home và mọi heater target bằng 0. File `printer.cfg` live khớp repository và bản năm tool trước bảo trì, SHA-256 `a5bf84212ee4dde36a001ad9f7d401d5c67d7d3a21c26fc21e1ee09bab83d6ad`.
- Sao lưu `printer.cfg` Git/live vào `extras/backups/pre-second-t2-t4-maintenance-20261114-122627/` và bản live trên máy ở `/home/voron/printer_data/config_backups/pre-second-t2-t4-maintenance-20261114-122627/`.

## Thay đổi và kiểm tra

- Khôi phục đúng bản T0/T1 đã dùng sáng cùng ngày vào `config/printer.cfg`: include KTC core và T0/T1 riêng; tạm bỏ 6 section SAVE_CONFIG PID `extruder2`–`extruder4` và offset `tool T2`–`tool T4`. Không sửa T2–T4.cfg, readonly KTC hoặc macro.
- Parser Klipper trên máy: 201 → 168 section, đúng 33 section T2–T4 bị loại, không thêm section hoặc đổi option của section còn lại. File mới có SHA-256 `9f620f3cfc1226d12de5e7ff0e0634351deb6ae9395e3589e27a5e3dc05cf534`.
- Sau khi kiểm tra lại hash live, ghi atomically một file `printer.cfg`; Moonraker `RESTART` trả `ok`. Sau restart: Klipper `ready`, registry `[0,1]`, `print_stats=standby`, `configfile.warnings=[]`, target bàn/T0/T1 đều 0, chưa home. Không gắp tool, gia nhiệt hay in thử trong bước này.

## Khôi phục sau bảo trì

- Đối chiếu cấu hình/calibration live với bản sao lưu trước khi khôi phục. Nối lại và xác nhận CAN T2–T4; khôi phục include KTC tổng và 6 section SAVE_CONFIG đã bỏ từ backup, chỉ reload lúc máy idle.
- Xác minh registry, cảm biến T2, dock/ngàm và gắp/thả có giám sát trước bản in T2. T1 vẫn có các lưu ý về dock từ nhật ký 13/11.
