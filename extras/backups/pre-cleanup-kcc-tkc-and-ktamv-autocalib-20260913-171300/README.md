# Bản ghi sao lưu

- **Ngày:** 2026-09-13 17:13:00
- **Tác vụ:** Dọn sạch các thành phần thử nghiệm KCC và TKC, đồng bộ cấu hình từ máy in thực tế 192.168.1.43, nghỉ hưu config/tool_calibrator và xây dựng quy trình đo tự động kTAMV tại X170 Y0 Z40.
- **File đã sao lưu:**
  - `printer.cfg` — Đồng bộ PID mới của extruder1-4, offset tool mới từ máy thật và làm sạch comment
  - `moonraker.conf` — Làm sạch các mục include thử nghiệm
  - `Printer-Setup/calibration-probe.cfg` — Loại bỏ tham chiếu TKC, làm sạch comment
  - `Printer-Setup/ktamv.cfg` — Bổ sung macro đo tự động tuần tự tất cả các tool KTAMV_AUTO_CALIBRATE_ALL_TOOLS
  - `scripts/install.sh` — Bỏ kiểm tra module TKC
  - `tool_calibrator/tool_calibrator.cfg` — Di chuyển sang retired-configs
  - `tool_calibrator/tool_offsets.cfg` — Di chuyển sang retired-configs
- **Nhật ký liên quan:** `extras/Nhat-ky-chinh-sua/2026-09-13-session-updates.md`
