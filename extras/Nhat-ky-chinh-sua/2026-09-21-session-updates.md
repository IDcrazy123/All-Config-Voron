# Nhật ký — 2026-09-21

## 1. Rà soát code, đồng bộ tài liệu và dọn dữ liệu cũ

### Mục tiêu
Đối chiếu code production với README/comment, cập nhật profile OrcaSlicer từ AppData, chặn đường hiệu chuẩn KTC cũ không còn backend, phân loại tài liệu retired và dọn bản sao trùng mà không làm mất bằng chứng độc nhất.

### File đã sửa đổi
- `config/printer.cfg` — thay comment include thử nghiệm cũ bằng mô tả Axiscope Klipper extra.
- `config/Printer-Setup/calibration-probe.cfg` — chuẩn hóa comment tiếng Anh; giữ nguyên toàn bộ giá trị production X80/Y-5/Z8.
- `config/Printer-Setup/fans-leds.cfg` — bỏ tuyên bố sai rằng trạng thái LED calibration được gọi bởi `CALIBRATE_ALL_OFFSETS`.
- `config/toolchanger/toolchanger-config.cfg` — sửa ownership backend và override `CALIBRATE_MOVE_OVER_PROBE`/`CALIBRATE_ALL_OFFSETS` bằng lỗi rõ ràng.
- `config/toolchanger/tools/T0.cfg`, `T2.cfg`, `T3.cfg` — sửa comment offset theo Axiscope + `SAVE_CONFIG`.
- `config/scripts/install.sh` — không còn tuyên bố đã xác thực Axiscope khi script không thực hiện preflight đó.
- `README.md`, `README.vi.md`, `config/README.md`, `config/README.vi.md` — viết lại theo code Axiscope/Cartographer/KTC hiện tại, pinout và offset live.
- `Orca Config/*.json` — đồng bộ 18 profile active; cập nhật machine `z_hop` 0.6 → 0.4 và process PETG 2.4.0.2.
- `Orca Config/Sync-OrcaProfiles.ps1` — đổi alias phân tích từ preset PETG Multimaterial đã cũ sang `0.20mm Multicolor PetG.json` active.
- `Orca Config/README.md`, `README.vi.md` — cập nhật inventory và thay đổi vừa đồng bộ.
- `extras/docs/` — cập nhật index/guide active, chuyển tài liệu kTAMV/TKC sang `history/`, thêm `legacy-calibration-troubleshooting.md`.
- `.agents/PROJECT.md`, `DIRECTORY.md`, `KNOWN_ISSUES.md`, `TODO.md` — cập nhật baseline AI ngoài Git repo theo Axiscope và trạng thái công việc.

### Sao lưu
- `D:/Desktop/All-Config-Voron-main/Voron 5 Tool/extras/backups/pre-code-docs-orca-audit-20260920-160649/`
- `D:/Desktop/All-Config-Voron-main/Voron 5 Tool/extras/backups/pre-orcaslicer-profile-sync-20260920-160720/`
- `D:/Desktop/All-Config-Voron-main/Voron 5 Tool/extras/backups/pre-orcaslicer-profile-sync-20260921-192813/`

### Chi tiết thay đổi
- Xác nhận `readonly-configs/calibrate-offsets.cfg` vẫn chứa macro `tools_calibrate`; comment “disabled” trước đây không chặn code. Override user-owned hiện báo lỗi và hướng người vận hành sang Axiscope cổng 3000.
- Orca đã ghi thêm `prime_tower_brim_width: 10` vào process PETG trong lúc phiên đang chạy; lượt đồng bộ cuối đã lấy đúng byte mới nhất từ AppData.
- Không đổi PID, dòng motor, giới hạn chuyển động, heater, tọa độ dock hoặc offset production.
- Xóa sáu JSON chỉ còn trong repository sau khi xác nhận profile active không kế thừa chúng; bản gốc nằm trong backup và Git history.
- Xóa mười ZIP snapshot, tổng 43.928.538 byte (41,89 MiB), sau khi so sánh SHA-256 từng entry và xác nhận trùng hoàn toàn với thư mục giải nén được giữ lại.
- Giữ `config-20260903-080600.zip` vì có sáu file ShakeTune không có trong thư mục giải nén; giữ các ZIP độc lập và toàn bộ `extras/backups/`.
- Tổng hợp dấu hiệu lỗi cũ từ ToolVision, kTAMV, TKC/KCC, SexBolt, Cartographer và TMC vào một bảng tra cứu ngắn.

### Đối chiếu máy thật
- SSH read-only thành công; Klipper và Axiscope đều active.
- `~/printer_data/config` khớp phần lớn code production hiện tại ngoài các comment/guard vừa sửa.
- Checkout `~/All-Config-Voron` trên máy đang ở commit cũ, behind và dirty; `install.sh` live vẫn chứa preflight kTAMV cũ. Không ghi file, không deploy và không restart máy trong phiên rà soát.
- Sau khi push, cần dùng Mainsail Update Manager khi máy idle để đồng bộ checkout và payload an toàn.

### Kiểm tra
- Orca JSON: đạt `ConvertFrom-Json`; byte source AppData được chép nguyên vẹn.
- KTC readonly: không có file nào bị sửa.
- So sánh ZIP/thư mục: 10/10 ZIP đã xóa trùng SHA-256 từng file.
- PowerShell parse: đạt; ba shell script đạt `bash -n` trên host Linux qua stdin, không ghi file lên máy.
- Include Klipper: mọi target tồn tại; guard macro cũ và toàn bộ offset/tọa độ production đạt assertion.
- Link Markdown hiện hành: đạt; không còn đường dẫn kTAMV active hoặc địa chỉ host trong tài liệu mới.
- `git diff --check`: đạt; chỉ có cảnh báo chuyển line ending theo `.gitattributes`, không có whitespace error.

### Kết quả
Code, comment và tài liệu hiện hành thống nhất trên Axiscope + Cartographer + KTC-Easy; profile Orca active đã đồng bộ; dữ liệu trùng giảm 41,89 MiB; kiến thức lỗi lịch sử được giữ trong tài liệu tra cứu và bằng chứng bất biến.

### Vấn đề còn lại
- Máy thật chưa nhận commit mới; chỉ cập nhật qua Mainsail khi đang idle.
- Checkout cũ/dirty trên máy cần được Update Manager xử lý cẩn thận; không dùng nó làm nguồn ghi đè config live trước khi review trạng thái.
