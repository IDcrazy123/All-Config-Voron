# 2026-11-15 — Tạm tắt T3 để bảo trì, T4 vẫn tắt

## Trạng thái trước sửa

- Người vận hành yêu cầu tắt T3 để bảo trì; không cung cấp nguyên nhân hoặc linh kiện cụ thể. T4 đang tắt từ đợt bảo trì cảm biến nhựa sáng cùng ngày.
- Moonraker `192.168.1.43:7125`: Klipper `ready`, bản in trước `complete`, không pause, `idle_timeout=Ready`, `_PRINT_STATE=idle`, không sấy/benchmark, shuttle active/detected rỗng, đã home `xyz`, target bàn/T0–T3 đều 0; registry `[0,1,2,3]`, không cảnh báo.
- Live `printer.cfg` và T3.cfg khớp Git. File `printer.cfg` khớp bản T0–T3 đã lưu, SHA-256 `af24a88f0ec9aa5272b3b96b3b52cc7c944b749eddc2e43b090a8cf9e547e656`.

## Sao lưu, thay đổi và kiểm tra

- Sao lưu bản Git/live giống nhau vào `extras/backups/pre-t3-maintenance-20261115-163710/` và bản live trên máy ở `/home/voron/printer_data/config_backups/pre-t3-maintenance-20261115-163710/`.
- `config/printer.cfg`: bỏ include riêng `toolchanger/tools/T3.cfg` và hai section SAVE_CONFIG `[extruder3]` PID / `[tool T3]` offset. Giữ T0–T2; T4 tiếp tục không được nạp. Không sửa T3.cfg, T4.cfg, macro hoặc readonly KTC.
- Parser Klipper trên máy: 190 → 179 section, đúng 11 section T3 bị loại, không thêm/đổi option của section khác. SAVE_CONFIG chỉ bỏ hai section T3. File mới có SHA-256 `000c9a1ee7d1570bd4c105721e41df27988a264872ab04e87f6f824fae72fe52`.

## Triển khai và khôi phục

- Kiểm tra lại máy idle, shuttle rỗng, target 0 và hash live trước khi ghi atomically một file `printer.cfg`. Moonraker `RESTART` trả `ok`; Klipper sau restart `ready`, registry `[0,1,2]`, không còn `tool T3`/`extruder3` hoặc `tool T4`/`extruder4`, `configfile.warnings=[]`, `print_stats=standby`, chưa home, target bàn/T0–T2 đều 0. File live khớp Git.
- Chưa gắp tool, gia nhiệt hoặc in thử sau reload. Macro `PRINT_START` hiện hữu chặn yêu cầu T3/T4 khi chưa đăng ký; G-code dùng những tool đó phải slice lại.
- Khi bảo trì T3 xong, xác nhận CAN, đối chiếu calibration mới rồi khôi phục riêng include T3 và hai section SAVE_CONFIG T3 từ backup. Chỉ reload lúc máy idle, kiểm tra detection/dock và gắp/thả T3 có giám sát. Không bật T4 cùng lúc nếu bảo trì cảm biến nhựa T4 chưa hoàn tất.
