# Backup trước khi Bổ sung Macro Đo Z Offset bằng Cartographer Touch

**Thời gian:** 2026-09-16 21:58:00
**Mục đích:**
- Sao lưu cấu hình `calibration-probe.cfg` (cả bản local trong repo và bản live trên máy in 192.168.1.43) trước khi bổ sung macro `MEASURE_ALL_Z_CARTOGRAPHER`.
- Macro này cho phép đo độ cao Z chạm bàn thực tế của cả 5 đầu in (T0 -> T4) bằng Cartographer Touch để tính toán Z offset tương đối.

**Danh sách file sao lưu:**
- `calibration-probe.cfg.local`
- `calibration-probe.cfg.live`
