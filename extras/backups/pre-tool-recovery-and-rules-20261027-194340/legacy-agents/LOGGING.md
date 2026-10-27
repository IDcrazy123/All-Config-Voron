# Quy tắc nhật ký hàng ngày

## Mục đích

Mỗi phiên làm việc phải tạo ra một mục nhật ký. Điều này tạo lịch sử có thể tìm kiếm cho:
- Hiểu tại sao một tham số bị thay đổi
- Tái tạo cách sửa khi cùng vấn đề xảy ra lại
- Theo dõi những gì đã sửa đổi và khi nào

## Vị trí file nhật ký

```
Voron 5 Tool/extras/Nhat-ky-chinh-sua/YYYY-MM-DD-session-updates.md
```

- Mỗi ngày một file.
- Nếu file hôm nay đã tồn tại, **bổ sung** vào — không ghi đè.
- Mỗi tác vụ hoặc sự cố có section đánh số riêng trong file.

---

## Mẫu: Cập nhật cấu hình

Sử dụng mẫu này khi các file cấu hình được sửa đổi:

```markdown
# Nhật ký — YYYY-MM-DD

## [N]. [Tiêu đề tác vụ ngắn gọn]

### Mục tiêu
Mục tiêu của thay đổi này là gì?

### File đã sửa đổi
- `đường/dẫn/tới/file.cfg` — đã thay đổi gì

### Sao lưu
- [file.cfg (Backup)](file:///đường/dẫn/tuyệt/đối/tới/backup/file.cfg)

### Chi tiết thay đổi
- Tham số `giá_trị_cũ` → `giá_trị_mới`
- Thêm/xóa section `[tên_section]`

### Lý do
Tại sao thay đổi này cần thiết? Nó giải quyết vấn đề gì?

### Kiểm tra
- Kiểm tra cú pháp: đạt/không đạt
- Khởi động lại Klipper: thành công/thất bại
- Thử in: nếu áp dụng

### Kết quả
Thay đổi có đạt được mục tiêu không?

### Vấn đề còn lại
Có cần thực hiện hành động tiếp theo nào không?
```

---

## Mẫu: Xử lý sự cố

Sử dụng mẫu này khi xử lý sự cố máy in (kể cả khi không thay đổi cấu hình):

```markdown
# Nhật ký — YYYY-MM-DD

## [N]. [Tiêu đề sự cố ngắn gọn]

### Triệu chứng
Người dùng quan sát được gì? (thông báo lỗi, hành vi máy in, trạng thái Mainsail)

### Phân tích nhật ký
- File nhật ký liên quan: [klippy.log](file:///đường/dẫn/tuyệt/đối/tới/klippy.log)
- Các thông báo lỗi chính trích xuất từ log
- Dòng thời gian sự kiện

### Nguyên nhân gốc
Nguyên nhân gây ra sự cố? (đã xác nhận hoặc nghi ngờ)

### Hướng khắc phục đã thực hiện
Hành động nào đã giải quyết sự cố?

### Kết quả
Cách khắc phục có hiệu quả không? Máy in đã hoạt động lại chưa?

### Phòng ngừa
Làm thế nào để ngăn sự cố này trong tương lai? (nếu áp dụng)

### Vấn đề còn lại
Có cần thực hiện hành động tiếp theo nào không?
```

---

## Quy tắc

1. **Luôn tạo nhật ký** — Kể cả khi phiên làm việc chỉ bao gồm đọc log và chẩn đoán mà không thay đổi cấu hình nào.
2. **Link tới bản sao lưu** — Mỗi mục nhật ký có sửa đổi cấu hình phải có link tuyệt đối tới thư mục sao lưu.
3. **Link tới file nhật ký hệ thống** — Mỗi mục xử lý sự cố phải có link tuyệt đối tới file log liên quan (klippy.log, moonraker.log).
4. **Cụ thể** — Ghi chính xác giá trị tham số (cũ → mới), thông báo lỗi chính xác, timestamp chính xác.
5. **Đánh số section liên tục** — Nếu làm nhiều tác vụ trong một ngày, đánh số `## 1.`, `## 2.`, v.v.
