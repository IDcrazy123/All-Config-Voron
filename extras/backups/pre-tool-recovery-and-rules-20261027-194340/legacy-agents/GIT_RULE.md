# Quy tắc Git

## Thông tin kho lưu trữ

- **Thư mục gốc git:** `Voron 5 Tool/`
- **Remote:** `origin` → GitHub (`IDcrazy123/All-Config-Voron`)
- **Nhánh:** `main`

## Định dạng commit message

```
<loại>: <mô tả ngắn gọn bằng tiếng Anh>
```

### Các loại commit

| Loại | Sử dụng khi |
|---|---|
| `config` | Thay đổi giá trị cấu hình máy in (offset, nhiệt độ, chân pin, threshold...) |
| `feat` | Thêm tính năng mới (macro mới, công tắc mới, cấu hình tool mới) |
| `fix` | Sửa lỗi hoặc giải quyết vấn đề kỹ thuật |
| `refactor` | Tái cấu trúc cấu hình mà không thay đổi hành vi hoạt động |
| `docs` | Thay đổi tài liệu (README, nhật ký hàng ngày, changelog, .agents/) |
| `chore` | Tác vụ bảo trì (dọn dẹp, script triển khai, format code) |

### Ví dụ commit message

```
config: update Z-offset switch pin to PF2 and sync machine printer.cfg
config: update tool Z-offsets with average of 3 Axiscope switch runs
config: restore good print Z-offsets and exclude markdown files from deployment scripts
feat: configure Axiscope Z-offset microswitch at X:68 Y:-10 Z:7
fix: resolve cartographer touch threshold and bed mesh zero reference
docs: refresh project documentation and AI rules across repository
```

### Quy tắc commit

1. **Ngôn ngữ:** Commit message phải bằng tiếng Anh.
2. **Tiền tố chữ thường:** Luôn viết thường (`config:` không phải `Config:`).
3. **Không chấm cuối** câu.
4. **Thì hiện tại:** Dùng "add" thay vì "added", "update" thay vì "updated", "fix" thay vì "fixed".
5. **Mô tả rõ ràng:** Message phải giải thích *cái gì* đã thay đổi, không chỉ viết chung chung.

---

## Quy tắc Auto-Push

### Nếu môi trường cho phép truy cập terminal và người dùng không cấm:

Sau khi hoàn tất tất cả sửa đổi và ghi nhật ký, tự động thực thi:

```bash
git add <các file đã thay đổi>
git commit -m "<loại>: <mô tả>"
git push origin main
```

### Nếu không có quyền truy cập terminal:

Chuẩn bị danh sách đầy đủ lệnh git và trình bày cho người dùng chạy thủ công:

```bash
# Sao chép và chạy các lệnh sau:
cd "Voron 5 Tool"
git add config/path/to/changed/file.cfg
git add extras/Nhat-ky-chinh-sua/YYYY-MM-DD-session-updates.md
git commit -m "config: description of changes"
git push origin main
```

---

## Quy tắc Gitignore & Bảo mật

Các file nhạy cảm tuyệt đối **không bao giờ được commit** lên GitHub (đã định nghĩa trong `.gitignore`):

- `*.secrets` — File thông tin nhạy cảm
- `moonraker.secrets` — API key Moonraker
- `wpa_supplicant.conf` — Thông tin mật khẩu WiFi
- `*.key`, `*.pem`, `*.env` — Khóa bí mật và biến môi trường
- `*.log` — File log hệ thống lớn

---

## Quy tắc Staging

1. **Chỉ stage file liên quan** — Không stage thay đổi không liên quan vào cùng một commit.
2. **Bao gồm nhật ký hàng ngày** — Khi commit thay đổi cấu hình, luôn bao gồm file nhật ký tương ứng.
3. **Bao gồm thư mục sao lưu** — Giữ lịch sử sao lưu đồng bộ trên Git.
