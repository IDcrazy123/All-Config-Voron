# Nhật ký — 2026-10-07

## 1. Đồng bộ cấu hình đang chạy từ máy in về PC và GitHub

### Mục tiêu
Đối chiếu cấu hình trên máy in `192.168.1.43` với working tree và `origin/main`, xác định nguồn sai lệch, rồi lưu đúng các giá trị runtime vào Git.

### File đã sửa đổi
- `config/Printer-Setup/hardware.cfg` — khôi phục nội dung đúng bản live; mapping X/Y trong Git đã trùng máy in, chỉ còn khác ký tự xuống dòng cuối file.
- `config/toolchanger/tools/T0.cfg`, `T1.cfg`, `T2.cfg`, `T4.cfg` — cập nhật `params_park_y` theo máy in.

### Sao lưu
- [Bản sao trước khi đồng bộ](file:///D:/Desktop/All-Config-Voron-main/Voron%205%20Tool/extras/backups/pre-sync-live-config-20261007-182329/README.md) — chứa cả năm file trên PC, gồm thay đổi `hardware.cfg` chưa commit trước phiên này.

### Chi tiết thay đổi
- Working tree PC trước đồng bộ đã đảo mapping: X dùng Motor 2 (`PE2/PE1/!PE4`, UART `PE3`), Y dùng Motor 1 (`PE6/PE5/!PC14`, UART `PC13`). Bản live và `origin/main` dùng X Motor 1 (`PE6/PE5/!PC14`, UART `PC13`), Y Motor 2 (`PE2/PE1/!PE4`, UART `PE3`). Không thay đổi dòng motor, giới hạn hành trình hoặc tham số nhiệt.
- Dock Y: T0 `1.3 → 1.8`, T1 `1.1 → 1.5`, T2 `1.6 → 2.1`, T4 `2.6 → 3.1`. Giá trị sau dấu `#` trong từng dòng là giá trị cũ, khớp với Git trước đồng bộ; comment mô tả vị trí dock trong hệ tọa độ nozzle vẫn đúng.
- `filament-dryer.cfg`, `print-macros.cfg`, `test-speed.cfg` chỉ khác kiểu xuống dòng, không khác nội dung sau khi bỏ qua whitespace cuối dòng; không sửa.

### Lý do và nguyên nhân sai lệch
- `hardware.cfg` trên PC có thay đổi chưa commit và trái với bản live. Nhật ký 2026-10-03, mục 2 ghi đã khôi phục mapping gốc trên máy in. Không có bằng chứng ai tạo lại bản đảo mapping trên PC; không suy đoán nguyên nhân thao tác.
- Bốn tọa độ dock Y trên máy in được sửa ngày 2026-10-03 theo thời gian file, nhưng chưa được đưa vào Git. Chưa có bằng chứng thử nghiệm cơ khí tương ứng; đồng bộ theo bản đang được Klipper nạp, không coi đây là xác nhận độ chính xác cơ khí.
- `origin/main` trước phiên ở commit `05046b0`, bằng với `HEAD` PC; không có merge conflict từ remote. Đây là sai lệch giữa runtime, working tree và commit Git.

### Kiểm tra
- SHA-256 của năm file sau đồng bộ khớp byte với snapshot tải từ máy in.
- `git diff --check` và kiểm tra cấu trúc header section: đạt.
- Moonraker báo Klipper `ready`, `configfile.settings` xác nhận mapping X/Y và bốn `params_park_y` đúng các giá trị trên; `warnings` rỗng.
- Không chạy homing, toolchange hoặc in thử trong phiên này.

### Kết quả
PC đã khớp bản cấu hình đang chạy về nội dung. Thay đổi, nhật ký và bản sao lưu được đưa vào cùng một commit.

### Vấn đề còn lại
- Độ chính xác cơ khí của mapping X/Y và vị trí dock chưa được xác minh bằng phép thử có người giám sát. Không tự đổi dây, restart, home hay chạy toolchange trong tác vụ đồng bộ chỉ đọc trên máy in này.
