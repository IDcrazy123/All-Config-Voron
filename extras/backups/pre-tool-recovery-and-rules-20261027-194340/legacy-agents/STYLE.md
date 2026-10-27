# Phong cách code & Quy tắc ngôn ngữ

## Phong cách file cấu hình (`.cfg`, `.conf`)

### Giữ nguyên định dạng hiện có
- **Giữ tất cả comment** — Không xóa hoặc viết lại comment không liên quan đến thay đổi của bạn.
- **Giữ thụt lề** — Khớp với kiểu thụt lề hiện có (dấu cách, không dùng tab).
- **Giữ dòng trống** — Giữ nguyên dòng trống giữa các section. Chúng cải thiện khả năng đọc.
- **Giữ thứ tự section** — Không sắp xếp lại `[sections]` trừ khi được yêu cầu rõ ràng.
- **Giữ thứ tự macro** — Không sắp xếp lại macro hoặc khối G-code trong một section.

### Khi thêm nội dung mới
- Khớp phong cách của code xung quanh (định dạng comment, khoảng cách, căn chỉnh).
- Thêm comment giải thích mục đích của tham số mới nếu không rõ ràng.
- Đặt section mới ở vị trí logic (ví dụ: tool mới sau các tool hiện có, macro mới gần macro liên quan).

### Quy ước đặt tên
- Tên macro: `CHỮ_HOA_PHÂN_CÁCH_GẠCH_DƯỚI` (ví dụ: `PRINT_START`, `CLEAN_NOZZLE`)
- Tên biến trong macro: `chữ_thường_phân_cách_gạch_dưới` (ví dụ: `bed_temp`, `tool_number`)
- Không bao giờ đổi tên macro hiện có trừ khi người dùng yêu cầu rõ ràng.

---

## Quy tắc ngôn ngữ

### File quy tắc AI (`.agents/`) và Chat
- **Viết bằng tiếng Việt** để người dùng dễ đọc và bảo trì.
- Chat phản hồi người dùng luôn bằng tiếng Việt.

### README, Commit message
- **Viết bằng tiếng Anh** để hiển thị chuyên nghiệp trên GitHub.
- Commit message theo quy tắc trong `GIT_RULE.md`.

### Nhật ký hàng ngày (`extras/Nhat-ky-chinh-sua/`)
- Nội dung file: tiếng Việt, vì đây là tài liệu tham khảo cá nhân của người dùng.
- Tiêu đề section và thuật ngữ kỹ thuật có thể dùng tiếng Anh khi tự nhiên.

---

## Quy tắc cú pháp Klipper

- Header section dùng ngoặc vuông: `[tên_section]`
- Tham số dùng định dạng `key: value` hoặc `key = value` (khớp với kiểu hiện có trong mỗi file)
- Tên pin theo quy ước Klipper: `PA0`, `!PB1`, `^PC2`
- Macro G-code dùng khối `gcode:` với thụt lề đúng
- Khối G-code nhiều dòng phải duy trì thụt lề nhất quán
- Giá trị boolean: `true`/`false` (chữ thường)
- Comment bắt đầu bằng `#` hoặc `;` — khớp với quy ước hiện có của file
