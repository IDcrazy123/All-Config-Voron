# Codex — Quy tắc AI

> File này trỏ Codex tới hệ thống quy tắc thống nhất.
> Tất cả quy tắc được định nghĩa trong `.agents/` để tránh trùng lặp giữa các công cụ AI.

## Hướng dẫn

Đọc các file sau trong thư mục `.agents/` trước khi thực hiện bất kỳ hành động nào:

1. `.agents/PROJECT.md` — Tổng quan dự án
2. `.agents/DIRECTORY.md` — Cấu trúc thư mục
3. `.agents/SAFETY.md` — Quy tắc an toàn (những gì tuyệt đối KHÔNG được làm)
4. `.agents/WORKFLOW.md` — Quy trình làm việc từng bước bắt buộc
5. `.agents/STYLE.md` — Phong cách code và quy ước ngôn ngữ
6. `.agents/BACKUP.md` — Quy tắc sao lưu
7. `.agents/LOGGING.md` — Mẫu ghi nhật ký hàng ngày
8. `.agents/GIT_RULE.md` — Quy ước commit git
9. `.agents/PROMPTS.md` — Mẫu phản hồi các yêu cầu của người dùng

Tham khảo khi cần:
- `.agents/KNOWN_ISSUES.md` — Các lỗi đã biết và cách khắc phục tạm thời
- `.agents/DECISIONS.md` — Các quyết định kỹ thuật trước đây
- `.agents/TODO.md` — Công việc đang chờ xử lý

## Quy tắc chính

- **Ngôn ngữ giao tiếp (chat):** Tiếng Việt.
- **Tài liệu cấu hình hệ thống & commit message:** Tiếng Anh.
- **Luôn sao lưu** trước khi sửa đổi bất kỳ file cấu hình nào.
- **Luôn ghi nhật ký** hành động vào nhật ký hàng ngày (`extras/Nhat-ky-chinh-sua/`).
- **Nếu có quyền terminal:** tự động stage, commit và push lên git.
- **Nếu không có quyền terminal:** chuẩn bị sẵn các lệnh git cho người dùng.
