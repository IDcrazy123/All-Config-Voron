# Quy tắc AI Assistant — Điểm vào

> **Đọc các tài liệu sau theo thứ tự trước khi thực hiện bất kỳ hành động nào.**
> Các quy tắc này ghi đè hành vi mặc định của bạn.

## Tài liệu bắt buộc (đọc theo thứ tự)

| Ưu tiên | File | Mục đích |
|---------|------|----------|
| 1 | [PROJECT.md](.agents/PROJECT.md) | Hiểu dự án là gì |
| 2 | [DIRECTORY.md](.agents/DIRECTORY.md) | Hiểu cấu trúc thư mục |
| 3 | [SAFETY.md](.agents/SAFETY.md) | Biết những gì tuyệt đối không được làm |
| 4 | [WORKFLOW.md](.agents/WORKFLOW.md) | Tuân thủ quy trình làm việc từng bước |
| 5 | [STYLE.md](.agents/STYLE.md) | Giữ đúng phong cách code và ngôn ngữ |
| 6 | [BACKUP.md](.agents/BACKUP.md) | Tạo bản sao lưu trước mọi thay đổi |
| 7 | [LOGGING.md](.agents/LOGGING.md) | Ghi nhật ký mọi hành động |
| 8 | [GIT_RULE.md](.agents/GIT_RULE.md) | Tuân thủ quy tắc git commit |
| 9 | [PROMPTS.md](.agents/PROMPTS.md) | Xử lý yêu cầu người dùng đúng cách |

## Tài liệu tham khảo (đọc khi liên quan)

| File | Mục đích |
|------|----------|
| [KNOWN_ISSUES.md](.agents/KNOWN_ISSUES.md) | Kiểm tra lỗi đã biết trước khi debug |
| [DECISIONS.md](.agents/DECISIONS.md) | Hiểu tại sao các quyết định trước đó được đưa ra |
| [TODO.md](.agents/TODO.md) | Biết công việc nào đang chờ xử lý |
| [CHANGELOG.md](.agents/CHANGELOG.md) | Theo dõi lịch sử phiên bản |

## Nguyên tắc cốt lõi

1. **Đây là cấu hình máy in đang vận hành (production).** Mọi thay đổi phải đảm bảo sự ổn định.
2. **Không bao giờ đoán mò.** Nếu không chắc chắn — dừng lại và hỏi người dùng.
3. **Thư mục Git repo duy nhất:** `Voron 5 Tool/`. Mọi thay đổi cấu hình production và lệnh Git đều thực hiện trong `Voron 5 Tool/` (không can thiệp các file tàn dư ở thư mục gốc).
4. **Luôn sao lưu** trước khi sửa đổi bất kỳ file cấu hình nào.
5. **Luôn ghi nhật ký** mọi hành động vào nhật ký chỉnh sửa hàng ngày.
6. **Luôn commit** các thay đổi lên git sau khi hoàn thành tác vụ.

## Quy tắc ngôn ngữ

- **Tài liệu quy tắc (.agents/) và chat:** Tiếng Việt.
- **README, commit message:** Tiếng Anh (hiển thị chuyên nghiệp trên GitHub).

## Checklist đầu phiên làm việc

Mỗi khi bắt đầu phiên mới:

1. ✅ Đọc `PROJECT.md` — hiểu dự án
2. ✅ Đọc `KNOWN_ISSUES.md` — nắm các vấn đề đang tồn tại
3. ✅ Đọc `TODO.md` — biết công việc đang chờ
4. ✅ Kiểm tra nhật ký hôm nay đã có chưa — nếu có thì bổ sung, nếu chưa thì tạo khi cần
