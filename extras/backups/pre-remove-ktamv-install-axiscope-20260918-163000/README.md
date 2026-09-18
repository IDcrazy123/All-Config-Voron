# Bản ghi sao lưu

- **Ngày:** 2026-09-18 16:30:00
- **Tác vụ:** Gỡ bỏ hoàn toàn kTAMV và cài đặt Axiscope đo XYZ offset
- **File đã sao lưu:**
  - `printer.cfg` — Gỡ bỏ include `Printer-Setup/ktamv.cfg`
  - `calibration-probe.cfg` — Chuyển từ `[tools_calibrate]` sang `[axiscope]` trên chân `^PF2`
  - `ktamv.cfg` — Cấu hình kTAMV cũ sắp di chuyển sang retired-configs
  - `moonraker.conf` — Thêm `[update_manager axiscope]`
  - `install.sh` — Gỡ bỏ ràng buộc preflight kTAMV
- **Nhật ký liên quan:** `extras/Nhat-ky-chinh-sua/2026-09-18-session-updates.md`
