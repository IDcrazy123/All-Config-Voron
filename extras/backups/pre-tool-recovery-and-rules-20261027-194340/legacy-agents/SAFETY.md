# Quy tắc an toàn

## Các hành động bị cấm tuyệt đối

**Không bao giờ** làm bất kỳ điều nào sau đây:

- ❌ **Xóa** bất kỳ file cấu hình nào (`.cfg`, `.conf`)
- ❌ **Ghi đè** các file sao lưu đã tồn tại
- ❌ **Sửa đổi** các section không rõ chức năng mà chưa hiểu rõ mục đích
- ❌ **Đoán mò** giá trị tham số — luôn sử dụng giá trị từ tài liệu hoặc dữ liệu đo thực tế
- ❌ **Bịa ra** tham số không tồn tại trong tài liệu Klipper
- ❌ **Bỏ qua** quy tắc cú pháp Klipper (header section, đặt tên pin, phạm vi giá trị)
- ❌ **Sắp xếp lại** thứ tự các section trừ khi được yêu cầu rõ ràng
- ❌ **Xóa** comment trong file cấu hình trừ khi được yêu cầu rõ ràng
- ❌ **Sửa** các file trong `toolchanger/readonly-configs/` — đây là file do plugin quản lý
- ❌ **Thay đổi** giá trị PID heater, dòng điện stepper, hoặc giới hạn chuyển động mà không có chỉ thị rõ ràng từ người dùng

## Khi không chắc chắn

```
Nếu không chắc chắn về BẤT KỲ thay đổi nào:

  → DỪNG LẠI
  → Giải thích sự không chắc chắn cho người dùng
  → Hỏi xác nhận rõ ràng
  → Chỉ tiến hành sau khi được phê duyệt
```

Áp dụng cho:
- Tham số Klipper không quen thuộc
- Giá trị có vẻ sai nhưng có thể là cố ý
- Thay đổi có thể ảnh hưởng đến hệ thống chuyển động, nhiệt, hoặc an toàn
- Bất kỳ yêu cầu nào có thể gây hỏng phần cứng

## Các section có rủi ro cao

Các section cấu hình sau trực tiếp điều khiển an toàn phần cứng. **Yêu cầu thận trọng đặc biệt:**

| Section | Rủi ro | Quy tắc |
|---------|--------|---------|
| `[stepper_*]` | Hỏng motor, trượt dây đai | Không bao giờ đặt `run_current` vượt thông số nhà sản xuất |
| `[extruder*]` | Tắc đầu phun, quá nhiệt | Không bao giờ đặt `max_temp` vượt giới hạn an toàn |
| `[heater_bed]` | Nguy cơ cháy, hỏng SSR | Không bao giờ tắt kiểm tra `verify_heater` |
| `[tmc*]` | Cháy driver | Không bao giờ thay `run_current` mà không có chỉ thị người dùng |
| `[safe_z_home]` | Đầu phun đâm vào bàn | Xác nhận tọa độ khớp với vị trí vật lý |
| `[bed_mesh]` | Đầu phun va chạm khi dò | Xác nhận điểm dò nằm trong ranh giới bàn in |

## Thao tác nhận biết quyền hạn (Permission-Aware)

### Quyền ghi file
- Nếu môi trường cho phép ghi file: tiến hành sao lưu và sửa đổi bình thường.
- Nếu môi trường chỉ đọc hoặc giới hạn quyền ghi: **thông báo rõ cho người dùng** và cung cấp nội dung hoặc lệnh chính xác cần thực hiện thủ công.

### Quyền terminal
- Nếu môi trường cho phép truy cập terminal và người dùng không cấm: thực thi lệnh git tự động.
- Nếu không có quyền terminal: **chuẩn bị danh sách đầy đủ các lệnh git** để người dùng chạy thủ công.

### Quyền sao lưu
- Nếu assistant có quyền ghi vào `extras/backups/`: tạo sao lưu tự động trước mỗi sửa đổi.
- Nếu quyền ghi bị giới hạn: **thông báo** rằng không thể tạo sao lưu tự động và đề xuất thao tác thủ công tương đương trước khi tiến hành.
