# Bản ghi sao lưu

- **Ngày:** 2026-10-26 13:41:00
- **Tác vụ:** Sửa triệt để cơ chế thoát phục hồi chốt an toàn (tool recovery latch) chống deadlock
- **File đã sao lưu:**
  - `config/Printer-Setup/tool-crash.cfg` — Hỗ trợ tự động nhận diện tool, cho phép xác nhận shuttle rỗng và thêm macro shortcut RECOVER_TOOL
  - `config/toolchanger/toolchanger-config.cfg` — Tự động xóa chốt recovery khi đổi/gắp tool thủ công thành công trong after_change_gcode
  - `config/Printer-Setup/print-macros.cfg` — Chỉ rõ câu lệnh xử lý trong thông báo lỗi PRINT_START, _REQUIRE_MOTION_PREPARATION và CANCEL_PRINT
- **Nhật ký liên quan:** `extras/Nhat-ky-chinh-sua/2026-10-26-session-updates.md`
