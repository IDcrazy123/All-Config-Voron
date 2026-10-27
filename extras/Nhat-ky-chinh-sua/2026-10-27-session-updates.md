# Nhật ký — 2026-10-27

## 1. Nới lỏng chốt an toàn và tinh gọn điều kiện di chuyển chuẩn bị (QGL / Motion Preparation Guard)

### Triệu chứng
- Người dùng gặp chuỗi lỗi liên hoàn sau khi gắp tool T0 thất bại lúc bắt đầu in:
  - `Expected tool tool T0 but active is None`
  - `Tool crash detected outside an active print; no shutdown or motion was requested`
  - Sau khi người dùng hủy in (`CANCEL_PRINT`) và thực hiện Home `G28` thành công bằng Cartographer trên shuttle rỗng, người dùng chạy `QUAD_GANTRY_LEVEL` thì bị chặn cứng:
    `Error evaluating 'gcode_macro _REQUIRE_MOTION_PREPARATION:gcode': gcode.CommandError: Preparation motion refused: tool recovery is required. Run CONFIRM_TOOL_RECOVERY CONFIRM=1 or select a tool`
  - Người dùng phải gõ `CONFIRM_TOOL_RECOVERY CONFIRM=1` mới có thể chạy tiếp QGL.

### Phân tích nguyên nhân gốc
1. **Lỗi gắp tool ban đầu:**
   - Trong `_PRINT_START_SELECT_T0`, lệnh `T0` nhặt toolhead 0. Tại tọa độ chốt ngàm dock T0, lệnh `VERIFY_TOOL_DETECTED T=0` đọc chân `detection_pin: ^!EBB0:PB6` nhưng công tắc chưa đóng dứt khoát. KTC kích hoạt `error_gcode: _TOOL_CRASH_SAFE_PAUSE`.
   - `_TOOL_CRASH_SAFE_PAUSE` đặt `_TOOL_RECOVERY.required = 1`.
2. **Khắt khe quá mức trong macro `_REQUIRE_MOTION_PREPARATION`:**
   - Cảm biến Cartographer gắn cố định trên shuttle (carriage), không nằm trên toolhead.
   - Khi shuttle rỗng (`active is None`) và máy đang `idle` (không in), việc cân gantry bằng `QUAD_GANTRY_LEVEL` hay `G32` là hoàn toàn an toàn và lý tưởng.
   - Việc `_REQUIRE_MOTION_PREPARATION` chặn cứng `QUAD_GANTRY_LEVEL` chỉ vì cờ `_TOOL_RECOVERY.required` cũ khiến người vận hành bị deadlock sau sự cố.

### File đã sửa đổi
- `config/Printer-Setup/print-macros.cfg`:
  - Trong `_REQUIRE_MOTION_PREPARATION`: Nới lỏng điều kiện chặn `recovery`. Chỉ chặn khi đang trong `PRINT_START` (`phase == "starting"`) hoặc khi đang gắp một tool chưa được xác minh (`is_active_tool == True`). Khi shuttle rỗng ở trạng thái `idle`, cho phép chạy `QUAD_GANTRY_LEVEL` / `G32` bình thường.
  - Trong `QUAD_GANTRY_LEVEL`: Khi QGL hoàn tất với shuttle rỗng, tự động xóa chốt `_TOOL_RECOVERY.required = 0` và thông báo `"Gantry leveled; recovery latch cleared for empty shuttle"`.
  - Tinh giản thông báo lỗi điều hướng: gợi ý rõ ràng `RECOVER_TOOL` (1-click) hoặc `CONFIRM_TOOL_RECOVERY`.

### Sao lưu
- [print-macros.cfg (Backup)](file:///d:/Desktop/All-Config-Voron-main/Voron%205%20Tool/extras/backups/pre-streamline-recovery-conditions-20261027-192500/print-macros.cfg)
- [tool-crash.cfg (Backup)](file:///d:/Desktop/All-Config-Voron-main/Voron%205%20Tool/extras/backups/pre-streamline-recovery-conditions-20261027-192500/tool-crash.cfg)
- [Thư mục sao lưu](file:///d:/Desktop/All-Config-Voron-main/Voron%205%20Tool/extras/backups/pre-streamline-recovery-conditions-20261027-192500/)

### Kiểm tra & Xác minh
- Bộ kiểm thử tự động `Test-ProductionCfg.ps1`: Đạt 78/78 tests (13 skip POSIX PTY/Bash), toàn bộ test suites đều pass (`OK`).
- Đã triển khai trực tiếp 2 file cấu hình lên máy in thực tế `192.168.1.43` qua Moonraker File Upload API.
- Thực hiện soft reload Klipper (`restart`): Trạng thái `ready` ("Printer is ready").

### Kết quả
- Loại bỏ hoàn toàn điều kiện chặn vô lý đối với `QUAD_GANTRY_LEVEL` khi shuttle rỗng.
- Người vận hành có thể tự do Home và QGL mà không bao giờ bị kẹt lỗi `Preparation motion refused: tool recovery is required`.
- Gantry cân bằng xong tự động giải phóng chốt an toàn cho shuttle rỗng.

### Vấn đề còn lại
- Không có.
