# Backup trước khi Gỡ bỏ Axiscope và Kích hoạt SexBolt (tools_calibrate)

**Thời gian:** 2026-09-17 17:00:00
**Mục đích:**
- Sao lưu cấu hình `calibration-probe.cfg` và `toolchanger-config.cfg` trước khi:
  + Gỡ bỏ hoàn toàn module `[axiscope]` khỏi dự án và máy in thật.
  + Kích hoạt module SexBolt / SexBall chính thức `[tools_calibrate]` của KTC-Easy trên chân `pin: ^PF2`.
  + Khôi phục các macro chuẩn `CALIBRATE_MOVE_OVER_PROBE` và `CALIBRATE_ALL_OFFSETS`.

**Danh sách file:**
- `calibration-probe.cfg.local`
- `calibration-probe.cfg.live`
- `toolchanger-config.cfg.local`
- `toolchanger-config.cfg.live`
