# Quy trình làm việc — Bắt buộc tuân thủ từng bước

## Quy trình sửa đổi cấu hình

Luôn tuân thủ đúng thứ tự sau khi sửa đổi bất kỳ file cấu hình nào.
**Không được bỏ qua bất kỳ bước nào.**

```
 1  Đọc cấu hình hiện tại
 ↓
 2  Hiểu yêu cầu của người dùng
 ↓
 3  Giải thích kế hoạch cho người dùng
 ↓
 4  Tạo bản sao lưu (xem BACKUP.md)
 ↓
 5  Sửa đổi file cấu hình
 ↓
 6  Kiểm tra cú pháp (quy tắc cfg Klipper)
 ↓
 7  Cập nhật nhật ký hàng ngày (xem LOGGING.md)
 ↓
 8  Git commit (xem GIT_RULE.md)
 ↓
 9  Git push
 ↓
10  Báo cáo kết quả cho người dùng
```

### Chi tiết từng bước

| Bước | Hành động | Quy tắc |
|------|-----------|---------|
| 1 | **Đọc** | Luôn đọc trạng thái hiện tại của file trước khi sửa. Không bao giờ giả định giá trị hiện tại. |
| 2 | **Hiểu** | Làm rõ yêu cầu mơ hồ. Nếu người dùng nói "sửa", hãy hỏi cái gì hỏng hoặc đọc log trước. |
| 3 | **Giải thích** | Nói cho người dùng biết chính xác bạn sẽ thay đổi gì và tại sao, trước khi thực hiện. |
| 4 | **Sao lưu** | Bắt buộc. Tạo bản sao lưu trong `extras/backups/` với timestamp. Xem `BACKUP.md`. |
| 5 | **Sửa đổi** | Chỉ thay đổi những gì cần thiết. Không tổ chức lại hoặc format lại các phần không liên quan. |
| 6 | **Kiểm tra** | Kiểm tra lỗi cú pháp Klipper: dấu ngoặc, tên pin hợp lệ, header section đúng, giá trị số trong phạm vi cho phép. |
| 7 | **Ghi nhật ký** | Tạo hoặc cập nhật file nhật ký hàng ngày. Xem `LOGGING.md` để biết mẫu. |
| 8 | **Commit** | Stage các file đã thay đổi và commit với message tiếng Anh mô tả rõ ràng. Xem `GIT_RULE.md`. |
| 9 | **Push** | Push lên GitHub nếu có quyền truy cập terminal. |
| 10 | **Báo cáo** | Tóm tắt những gì đã thay đổi, đã sao lưu, và các hành động còn lại. |

---

## Quy trình xử lý sự cố

Khi người dùng báo cáo sự cố (crash, lỗi, treo máy...), tuân thủ thứ tự sau:

```
 1  Đọc file nhật ký (klippy.log, moonraker.log)
 ↓
 2  Xác định nguyên nhân gốc từ log
 ↓
 3  Giải thích phát hiện cho người dùng
 ↓
 4  Đề xuất cách sửa hoặc giải pháp tạm
 ↓
 5  Nếu cần thay đổi cấu hình → theo Quy trình sửa đổi cấu hình ở trên
 ↓
 6  Nếu không cần thay đổi cấu hình → ghi nhận sự cố vào nhật ký hàng ngày (xem LOGGING.md)
 ↓
 7  Cập nhật KNOWN_ISSUES.md nếu đây là sự cố đáng chú ý hoặc tái diễn
 ↓
 8  Git commit & push nhật ký
 ↓
 9  Báo cáo cho người dùng
```

---

## Quy tắc thay đổi nhiều file

Khi một tác vụ yêu cầu thay đổi nhiều file cấu hình:

1. **Sao lưu tất cả file trước** — trước khi sửa đổi bất kỳ file nào.
2. **Sửa đổi tất cả file** — thực hiện tất cả thay đổi như một đơn vị logic duy nhất.
3. **Một commit duy nhất** — commit tất cả thay đổi liên quan cùng nhau với một message mô tả.
4. **Một mục nhật ký duy nhất** — ghi tất cả thay đổi trong một section của nhật ký hàng ngày.

---

## Checklist đầu phiên làm việc

Mỗi khi bắt đầu phiên mới, assistant cần:

1. Đọc `PROJECT.md` để hiểu bối cảnh dự án.
2. Đọc `KNOWN_ISSUES.md` để nắm các vấn đề đang tồn tại.
3. Đọc `TODO.md` để biết công việc đang chờ.
4. Kiểm tra nhật ký hôm nay đã có chưa — nếu có thì bổ sung, nếu chưa thì tạo khi cần.
