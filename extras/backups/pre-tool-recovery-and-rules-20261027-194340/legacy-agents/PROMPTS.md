# Mẫu xử lý yêu cầu (Prompt Patterns)

## Cách phản hồi các yêu cầu phổ biến của người dùng

Tài liệu này định nghĩa hành vi mong đợi khi người dùng sử dụng các từ khóa hoặc mẫu yêu cầu cụ thể.

---

## Khi người dùng nói: "fix" / "sửa" / "lỗi"

```
 1  Đọc file nhật ký liên quan (klippy.log, moonraker.log)
 ↓
 2  Tìm nguyên nhân gốc từ log
 ↓
 3  Giải thích vấn đề rõ ràng cho người dùng
 ↓
 4  Đề xuất cách sửa — xin phê duyệt nếu liên quan đến section rủi ro cao
 ↓
 5  Sao lưu các file bị ảnh hưởng
 ↓
 6  Áp dụng cách sửa
 ↓
 7  Kiểm tra cú pháp
 ↓
 8  Cập nhật nhật ký hàng ngày (dùng mẫu Xử lý sự cố trong LOGGING.md)
 ↓
 9  Cập nhật KNOWN_ISSUES.md nếu đáng chú ý
 ↓
10  Git commit & push
```

**Quy tắc chính:** Không bao giờ đoán nguyên nhân. Luôn đọc log trước.

---

## Khi người dùng nói: "optimize" / "tối ưu" / "tune"

```
 1  Đọc giá trị hiện tại
 ↓
 2  Giải thích chức năng của từng giá trị
 ↓
 3  Giải thích sự đánh đổi (trade-off) khi thay đổi
 ↓
 4  Đề xuất giá trị mới cụ thể kèm lý do
 ↓
 5  Chờ phê duyệt của người dùng
 ↓
 6  Theo Quy trình sửa đổi cấu hình (WORKFLOW.md)
```

**Quy tắc chính:** Không bao giờ tối ưu mù quáng. Luôn giải thích sự đánh đổi trước. Người dùng quyết định.

---

## Khi người dùng nói: "add" / "thêm"

```
 1  Hiểu tính năng hoặc thành phần cần thêm
 ↓
 2  Kiểm tra xung đột với cấu hình hiện có
 ↓
 3  Giải thích kế hoạch thêm
 ↓
 4  Theo Quy trình sửa đổi cấu hình (WORKFLOW.md)
```

**Quy tắc chính:** Kiểm tra xung đột với macro, pin, và section hiện có trước khi thêm.

---

## Khi người dùng nói: "calibrate" / "hiệu chuẩn"

```
 1  Xác định loại hiệu chuẩn (PID, pressure advance, Z-offset, input shaper...)
 ↓
 2  Cung cấp lệnh Klipper chính xác cần chạy trên máy in
 ↓
 3  Chờ người dùng chạy lệnh và báo cáo kết quả
 ↓
 4  Cập nhật cấu hình với giá trị hiệu chuẩn mới
 ↓
 5  Theo Quy trình sửa đổi cấu hình (WORKFLOW.md)
```

**Quy tắc chính:** Assistant không thể chạy lệnh hiệu chuẩn trên máy in. Cung cấp lệnh chính xác và chờ kết quả.

---

## Khi người dùng nói: "check" / "kiểm tra" / "đọc log"

```
 1  Đọc file nhật ký được yêu cầu
 ↓
 2  Phân tích lỗi, cảnh báo, hoặc bất thường
 ↓
 3  Báo cáo phát hiện rõ ràng
 ↓
 4  Nếu tìm thấy vấn đề → đề xuất cách sửa
 ↓
 5  Nếu không có vấn đề → xác nhận hệ thống hoạt động bình thường
```

**Quy tắc chính:** Đây là thao tác chỉ đọc. Không sửa đổi bất kỳ file nào trừ khi người dùng yêu cầu rõ ràng.

---

## Khi người dùng nói: "rollback" / "hoàn tác" / "undo"

```
 1  Xác định bản sao lưu gần nhất cho file bị ảnh hưởng
 ↓
 2  Hiển thị nội dung sao lưu so với nội dung hiện tại
 ↓
 3  Xác nhận hoàn tác với người dùng
 ↓
 4  Khôi phục file sao lưu về vị trí gốc
 ↓
 5  Ghi nhận hoàn tác vào nhật ký hàng ngày
 ↓
 6  Git commit & push
```

**Quy tắc chính:** Luôn xác nhận với người dùng trước khi khôi phục. Cho họ xem chính xác những gì sẽ thay đổi.

---

## Khi người dùng cung cấp giá trị thô (con số, dữ liệu hiệu chuẩn)

```
 1  Xác định tham số cấu hình mà giá trị thuộc về
 ↓
 2  Hiển thị giá trị hiện tại so với giá trị mới
 ↓
 3  Xác nhận với người dùng
 ↓
 4  Theo Quy trình sửa đổi cấu hình (WORKFLOW.md)
```

**Quy tắc chính:** Không bao giờ giả định giá trị thuộc về tham số nào. Luôn xác nhận.

---

## Nguyên tắc phản hồi chung

1. **Đọc trước khi viết** — Luôn đọc trạng thái hiện tại của file trước khi sửa đổi.
2. **Giải thích trước khi hành động** — Nói cho người dùng biết bạn định làm gì trước khi thực hiện.
3. **Thay đổi tối thiểu** — Chỉ thay đổi những gì cần thiết. Không chạm vào phần không liên quan.
4. **Phản hồi bằng tiếng Việt** — Tất cả phản hồi chat với người dùng phải bằng tiếng Việt.
5. **Tài liệu commit bằng tiếng Anh** — README và commit message phải bằng tiếng Anh.
