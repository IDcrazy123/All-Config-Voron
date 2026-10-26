# Nhật ký — 2026-10-26

## 1. Mở khóa và sửa triệt để cơ chế chốt an toàn phục hồi tool (Tool Recovery Latch Deadlock)

### Triệu chứng
- Người dùng gặp lỗi từ bản cập nhật gần nhất khi bắt đầu in hoặc cân bàn:
  - `gcode.CommandError: PRINT_START: finish/cancel the current operation and confirm any tool recovery first`
  - `gcode.CommandError: Preparation motion refused during printing, pause, recovery, drying or benchmarking` (khi chạy `QUAD_GANTRY_LEVEL` / `G32`)
  - `[CANCEL] Motion skipped: XYZ/toolchanger/recovery state is unsafe` (khi nhấn Hủy lệnh in `CANCEL_PRINT`)
- Người dùng đã gắp tool T0 lên shuttle thủ công thành công bằng `T0`, nhưng máy in vẫn bị kẹt cứng trong trạng thái khóa an toàn.

### Phân tích nhật ký
- Sau homing `G28`, `PRINT_START` gọi `_PRINT_START_SELECT_T0` để lấy T0. Quá trình kiểm tra phần cứng `verify: 1` tại dock T0 không nhận diện được tool (`No tool detected`), kích hoạt `[toolchanger] error_gcode: _TOOL_CRASH_SAFE_PAUSE`.
- `_TOOL_CRASH_SAFE_PAUSE` đặt biến chốt `_TOOL_RECOVERY.required = 1` và `_TOOL_RECOVERY.tool = -1`.
- Biến này được duy trì qua các lệnh `CANCEL_PRINT` để bảo vệ an toàn. Tuy nhiên:
  - `CONFIRM_TOOL_RECOVERY` bị lỗi logic khi `tool == -1` (do crash xảy ra khi shuttle rỗng trước đó), vì `-1 not in tool_numbers`.
  - Khi người vận hành gắp tool thủ công `T0` thành công và OptoTap đã xác thực có tool, hệ thống không tự xóa chốt an toàn.
  - Các thông báo lỗi không cung cấp câu lệnh phục hồi cụ thể khiến người vận hành bị bế tắc.

### File đã sửa đổi
- `config/Printer-Setup/tool-crash.cfg`:
  - Nâng cấp `CONFIRM_TOOL_RECOVERY`: tự động nhận diện tool đang gắn (`detected_tool_number` hoặc `tool_number`), hỗ trợ xác nhận cả trường hợp shuttle rỗng (`T=-1`).
  - Cập nhật `_TOOL_RECOVERY_CONFIRMED`: lưu lại `tool` đã xác nhận.
  - Bổ sung macro 1-click `RECOVER_TOOL` tiện lợi trên console/Mainsail.
- `config/toolchanger/toolchanger-config.cfg`:
  - Trong `after_change_gcode`: tự động xóa chốt `_TOOL_RECOVERY.required = 0` khi chu trình đổi/gắp tool thủ công đã chạy thành công và được xác thực phần cứng.
- `config/Printer-Setup/print-macros.cfg`:
  - Cập nhật thông báo lỗi trong `PRINT_START`, `_REQUIRE_MOTION_PREPARATION` và `_CUSTOM_CANCEL_CLEANUP`: chỉ rõ câu lệnh `CONFIRM_TOOL_RECOVERY CONFIRM=1` hoặc click `RECOVER_TOOL`.

### Sao lưu
- [tool-crash.cfg (Backup)](file:///d:/Desktop/All-Config-Voron-main/Voron%205%20Tool/extras/backups/pre-recovery-deadlock-fix-20261026-134100/tool-crash.cfg)
- [toolchanger-config.cfg (Backup)](file:///d:/Desktop/All-Config-Voron-main/Voron%205%20Tool/extras/backups/pre-recovery-deadlock-fix-20261026-134100/toolchanger-config.cfg)
- [print-macros.cfg (Backup)](file:///d:/Desktop/All-Config-Voron-main/Voron%205%20Tool/extras/backups/pre-recovery-deadlock-fix-20261026-134100/print-macros.cfg)
- [Thư mục sao lưu](file:///d:/Desktop/All-Config-Voron-main/Voron%205%20Tool/extras/backups/pre-recovery-deadlock-fix-20261026-134100/)

### Kiểm tra & Xác minh
- Bộ kiểm thử tự động `Test-ProductionCfg.ps1`: Đạt 78/78 tests (13 skip POSIX PTY/Bash), toàn bộ boundary/recovery assertions đều pass.
- Đã triển khai trực tiếp 3 file cấu hình lên máy in thực tế `192.168.1.43` qua Moonraker File Upload API.
- Thực hiện soft reload Klipper (`RESTART`): Trạng thái `ready` ("Printer is ready").
- Thử nghiệm lệnh `RECOVER_TOOL` trực tiếp trên máy in thật qua Moonraker: Thành công ngay lập tức, `status` trở về `ready`, `tool` nhận diện chính xác `tool T0`, `_TOOL_RECOVERY.required = 0`.

### Kết quả
- Máy in đã được mở khóa hoàn toàn, thoát khỏi tình trạng deadlock.
- Từ nay về sau, khi có bất kỳ sự cố tool nào, người dùng có thể gắp tool thủ công (tự động xóa chốt) hoặc chỉ cần gõ/click `RECOVER_TOOL` 1 lần là máy in hoạt động bình thường trở lại.

### Vấn đề còn lại
- Không có.

---

## 2. Tinh gọn điều kiện kiểm tra bắt đầu in trong PRINT_START

### Mục tiêu
Rà soát, loại bỏ các điều kiện kiểm tra trùng lặp và nới lỏng ràng buộc bắt buộc nạp nhựa T0 khi in bằng các tool khác (T1–T4).

### File đã sửa đổi
- `config/Printer-Setup/print-macros.cfg` — Tinh giản các khối `elif` thừa và tối ưu kiểm tra cảm biến nhựa.

### Sao lưu
- [print-macros.cfg (Backup)](file:///d:/Desktop/All-Config-Voron-main/Voron%205%20Tool/extras/backups/pre-streamline-print-start-20261026-145300/print-macros.cfg)
- [Thư mục sao lưu](file:///d:/Desktop/All-Config-Voron-main/Voron%205%20Tool/extras/backups/pre-streamline-print-start-20261026-145300/)

### Chi tiết thay đổi
1. **Chỉ kiểm tra nhựa trên tool thực tế sử dụng (`requested > 0`):**
   - Trước: `(requested > 0 or tn == 0)` ép buộc cuộn T0 phải luôn có nhựa ngay cả khi bản in chỉ dùng T1, T2, T3 hoặc T4.
   - Sau: Chỉ kiểm tra `requested > 0`.
2. **Thích ứng làm sạch T0 thông minh:**
   - Tại bước làm sạch T0 trước khi Cartographer Touch: Nếu T0 có nhựa thì xả 40mm (`MODE=DEEP PURGE=40`). Nếu T0 không có nhựa (và không dùng để in), tự động chuyển sang chế độ lau khô chổi silicone (`MODE=TOUCH PURGE=0`), không gây báo lỗi dừng in vô lý.
3. **Loại bỏ trùng lặp:**
   - Xóa bỏ kiểm tra `printer.print_stats.state` phòng vệ dư thừa (đã được kiểm tra qua `phase` và `pause_resume.is_paused`).
   - Xóa bỏ kiểm tra `T0_PURGE_TEMP` lần 2 (đã được kiểm tra đầy đủ ở đầu macro).

### Lý do
Nâng cao trải nghiệm người dùng (UX), cho phép in linh hoạt các đầu in độc lập mà không bị ép buộc nạp nhựa cho T0, đồng thời tinh gọn cấu hình macro.

### Kiểm tra & Xác minh
- Bộ kiểm thử tự động `Test-ProductionCfg.ps1`: Đạt 78/78 tests (13 skip POSIX PTY/Bash), toàn bộ test suites đều pass.
- Đã upload `print-macros.cfg` lên máy in thật `192.168.1.43` qua Moonraker File Upload API.
- Thực hiện soft reload Klipper (`RESTART`): Trạng thái `ready` ("Printer is ready").

### Kết quả
Quy trình `PRINT_START` trở nên thông minh, tinh gọn và thân thiện hơn, loại bỏ hoàn toàn các lỗi phiền toái.

### Vấn đề còn lại
- Không có.
