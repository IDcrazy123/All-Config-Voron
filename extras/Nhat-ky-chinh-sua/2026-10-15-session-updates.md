# Nhật ký — 2026-10-15

## 1. Hướng dẫn đầu file cho 19 CFG production

### Mục tiêu
Theo yêu cầu người dùng, mở oxplow_runtime.cfg hoặc CFG khác là thấy ngay chức năng, phụ thuộc, cách dùng và phần cần cấu hình. Comment tiếng Anh theo quy ước tài liệu dự án; chat/nhật ký tiếng Việt.

### File đã sửa đổi
- `config/printer.cfg` — thêm hướng dẫn chức năng/cách nạp/lệnh chính/cấu hình cục bộ ở đầu file.
- `config/Printer-Setup/calibration-probe.cfg` — thêm hướng dẫn chức năng/cách nạp/lệnh chính/cấu hình cục bộ ở đầu file.
- `config/Printer-Setup/fans-leds.cfg` — thêm hướng dẫn chức năng/cách nạp/lệnh chính/cấu hình cục bộ ở đầu file.
- `config/Printer-Setup/filament-dryer.cfg` — thêm hướng dẫn chức năng/cách nạp/lệnh chính/cấu hình cục bộ ở đầu file.
- `config/Printer-Setup/hardware.cfg` — thêm hướng dẫn chức năng/cách nạp/lệnh chính/cấu hình cục bộ ở đầu file.
- `config/Printer-Setup/input-shaper.cfg` — thêm hướng dẫn chức năng/cách nạp/lệnh chính/cấu hình cục bộ ở đầu file.
- `config/Printer-Setup/nozzle-clean.cfg` — thêm hướng dẫn chức năng/cách nạp/lệnh chính/cấu hình cục bộ ở đầu file.
- `config/Printer-Setup/prime-lines.cfg` — thêm hướng dẫn chức năng/cách nạp/lệnh chính/cấu hình cục bộ ở đầu file.
- `config/Printer-Setup/print-macros.cfg` — thêm hướng dẫn chức năng/cách nạp/lệnh chính/cấu hình cục bộ ở đầu file.
- `config/Printer-Setup/test-speed.cfg` — thêm hướng dẫn chức năng/cách nạp/lệnh chính/cấu hình cục bộ ở đầu file.
- `config/Printer-Setup/tool-crash.cfg` — thêm hướng dẫn chức năng/cách nạp/lệnh chính/cấu hình cục bộ ở đầu file.
- `config/Printer-Setup/tool-temp-bench.cfg` — thêm hướng dẫn chức năng/cách nạp/lệnh chính/cấu hình cục bộ ở đầu file.
- `config/toolchanger/toolchanger-config.cfg` — thêm hướng dẫn chức năng/cách nạp/lệnh chính/cấu hình cục bộ ở đầu file.
- `config/toolchanger/tools/T0.cfg` — thêm hướng dẫn chức năng/cách nạp/lệnh chính/cấu hình cục bộ ở đầu file.
- `config/toolchanger/tools/T1.cfg` — thêm hướng dẫn chức năng/cách nạp/lệnh chính/cấu hình cục bộ ở đầu file.
- `config/toolchanger/tools/T2.cfg` — thêm hướng dẫn chức năng/cách nạp/lệnh chính/cấu hình cục bộ ở đầu file.
- `config/toolchanger/tools/T3.cfg` — thêm hướng dẫn chức năng/cách nạp/lệnh chính/cấu hình cục bộ ở đầu file.
- `config/toolchanger/tools/T4.cfg` — thêm hướng dẫn chức năng/cách nạp/lệnh chính/cấu hình cục bộ ở đầu file.
- `config/Printer-Setup/oxplow_runtime.cfg` — thêm hướng dẫn chức năng/cách nạp/lệnh chính/cấu hình cục bộ ở đầu file.
- `extras/Printables-Package/README.md`, `INTEGRATION.md` — ghi rõ runtime production có thêm comment hướng dẫn, logic giữ nguyên; upstream vẫn byte-identical.

### Sao lưu
- [Snapshot trước sửa](</D:/Desktop/All-Config-Voron-main/Voron 5 Tool/extras/backups/pre-cfg-header-guides-20261015-194238/README.md>) — sao chép đủ 19 CFG và hai tài liệu trước khi ghi, đối chiếu SHA-256 đạt.
- Snapshot máy in trước ghi đủ 19 file: `/home/voron/printer_data/config_backups/pre-cfg-header-guides-20261015-194523-jqw78p92`.
- Các backup, file lịch sử, Mainsail do bên ngoài quản lý, KTC readonly và upstream Oxplow được giữ nguyên.

### Chi tiết thay đổi
- Khối FILE GUIDE giải thích Purpose, Loading, Main commands và Local setup theo vai trò thực tế của từng file. Giữ các comment chia sẻ/hardware đã có bên dưới.
- Oxplow: giải thích mục đích _OXPLOW_CHECK, include Printer-Setup, version, lệnh install không cần home/nhiệt; vai trò stage install/config/ready/selected/print; native preflight_token; các tham số và đơn vị; mapping/offset guard; ranh giới giữa runtime, generator và macro máy.
- Nêu rõ STAGE=install chỉ xác nhận runtime/version, không chứng nhận máy đủ điều kiện in; generated G-code cần chạy dạng virtual-SD.
- Sửa comment sai trong print-macros.cfg: `Slicer must pass INITIAL_TOOL` → `Slicer must pass TOOL`, vì PRINT_START đọc params.TOOL và chỉ truyền INITIAL_TOOL nội bộ cho PRIME_LINES. Không sửa lệnh thực thi.
- Review độc lập xác định generator cũng trực tiếp set/wait nhiệt và TURN_OFF_HEATERS; header Oxplow được viết đúng vai trò này.
- Không thay giá trị, tên macro, section, include, Jinja/G-code, version, SAVE_CONFIG, PID, offsets, current, limits hoặc tọa độ.

### Lý do
Header cũ phần lớn tập trung vào việc chia sẻ CFG; file Oxplow chỉ có ba dòng giới thiệu. Thêm hướng dẫn tại chỗ để người đọc hiểu chức năng trước khi chỉnh hoặc gọi macro. Đây là cải thiện tài liệu theo yêu cầu, không phải bản sửa lỗi thuật toán cho dự án Printables.

### Kiểm tra
- Đọc code, đối chiếu header và review độc lập các nhóm Printer-Setup/tool/printer.
- Xác minh phần thêm chỉ gồm comment đầu file; toàn bộ body cũ giữ nguyên byte trong working tree, ngoại trừ một comment tham số đã sửa có chủ đích.
- Parse cả trước/sau: thứ tự section, mọi option/value và khối G-code/Jinja của 19 file khớp hoàn toàn; SAVE_CONFIG không đổi.
- Body macro Oxplow khớp upstream; manifest SHA-256 của 22 file release upstream vẫn đạt. Không sửa dự án nguồn độc lập hoặc profile/G-code/report.
- `git diff --check`: đạt.
- Trước ghi máy in: print standby, unpaused, motion Ready, toolchanger không đổi đầu, print-state idle, dryer/benchmark dừng; đủ file live khớp baseline trước sửa, không có drift.
- Sau ghi: GET lại đủ 19 file khớp repo sau chuẩn hóa LF/CRLF; Klipper `ready`, print standby.
- Khởi động lại Klipper: không cần cho comment; không restart hoặc gửi G-code.
- Thử in: không cần cho thay đổi tài liệu; không phát lệnh chuyển động/nhiệt/hiệu chuẩn.

### Kết quả
Hướng dẫn đã có trên 19 CFG local và máy in, có backup trước ghi. Commit của tác vụ bao gồm CFG, hai tài liệu, backup và nhật ký; các file untracked không liên quan được giữ nguyên.

### Vấn đề còn lại
Không có thay đổi chức năng cần thử nghiệm. Có thể mang phần hướng dẫn Oxplow sang dự án gốc như cải thiện tài liệu; điều chỉnh ví dụ include/link theo bố cục gói nguồn và giữ nguyên logic/version.
