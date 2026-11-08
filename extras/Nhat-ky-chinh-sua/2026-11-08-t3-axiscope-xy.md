# 2026-11-08 — Cập nhật offset XY T3 bằng Axiscope

- Lấy T0 làm mốc. Ảnh đo Axiscope ghi vị trí T0 là X180.750/Y184.140, T3 là X180.880/Y184.670. Hiệu số đo là X+0.130/Y+0.530 mm. Áp dụng đúng cột **New X / New Y** cho T3.
- Trong `config/printer.cfg`, block `SAVE_CONFIG` của `[tool T3]`: X `0.003 → 0.133`, Y `0.369 → 0.899` mm. Giữ Z `-0.4865` mm và offset các tool khác. Cập nhật checksum của snapshot cấu hình đã duyệt trong bộ kiểm tra.
- Sao lưu bản Git và bản live tại `extras/backups/pre-t3-axiscope-xy-20261108-205852/`. Trên máy chỉ vá hai dòng trong file live để giữ các khác biệt còn lại; bản sao trước khi ghi nằm tại `~/printer_data/config_backups/pre-t3-axiscope-xy-20261108-205852/printer.cfg`.
- Máy đã in xong, không pause, không sấy và toolchanger báo T3 đang gắn trước lúc nạp lại. Sau `RESTART`, Klipper báo MCU `EBB0` đang ở trạng thái shutdown. Một lần `FIRMWARE_RESTART` đưa Klipper về `ready`, không có cảnh báo cấu hình. Moonraker xác nhận đúng XYZ của T3 và offset T0/T1/T2/T4 vẫn giữ nguyên.
- Bộ kiểm tra production chạy 83 test, không lỗi (6 test bỏ qua theo điều kiện sẵn có). Chưa chạy lệnh di chuyển hay in test sau khi nạp; cần home lại trước khi di chuyển và dùng mẫu in hai màu T0/T3 để kiểm tra độ khớp XY.
