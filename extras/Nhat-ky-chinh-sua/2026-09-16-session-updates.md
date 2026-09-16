# Nhật ký — 2026-09-16

## 1. Đồng bộ Thay đổi Đèn Buồng in từ Máy in và Viết lại Toàn diện Tài liệu README

### Mục tiêu
- Kết nối tới máy in đang vận hành thực tế để đối chiếu toàn bộ cấu hình đang chạy với kho mã nguồn.
- Đồng bộ thay đổi macro `LIGHTS_ON` (bật 100% độ sáng thay vì 30%) được người vận hành thực hiện trực tiếp trên máy in lúc 17:09 vào repo.
- Đọc và phân tích sâu toàn bộ mã nguồn thực tế của dự án (Klipper configs, macros, python patches, shell scripts, OrcaSlicer presets).
- Viết lại hoàn chỉnh, toàn diện tài liệu `README.md` (tiếng Anh) và `README.vi.md` (tiếng Việt) bao gồm đầy đủ 6 phần: Giới thiệu hệ thống & bản đồ phần cứng, Hướng dẫn cài đặt & cập nhật tinh gọn, Hướng dẫn sử dụng & tra cứu macro, Hướng dẫn gỡ cài đặt & hoàn tác, Phần ghi công các tác giả/dự án mã nguồn mở, và Phân tích chuyên sâu 10 thuật toán/logic vận hành cốt lõi.

### File đã sửa đổi
- `config/Printer-Setup/fans-leds.cfg` — Đồng bộ macro `LIGHTS_ON` sang 100% độ sáng (`RED=1 GREEN=1 BLUE=1`).
- `README.md` — Viết lại toàn diện tài liệu tổng quan dự án bằng tiếng Anh theo mã nguồn thực tế.
- `README.vi.md` — Viết lại toàn diện tài liệu tổng quan dự án bằng tiếng Việt đồng bộ 1:1 với bản tiếng Anh.

### Sao lưu
- [fans-leds.cfg (Backup)](file:///d:/Desktop/All-Config-Voron-main/Voron%205%20Tool/extras/backups/pre-sync-live-lights-and-rewrite-readme-20260916-172200/fans-leds.cfg)
- [README.md.orig (Backup)](file:///d:/Desktop/All-Config-Voron-main/Voron%205%20Tool/extras/backups/pre-sync-live-lights-and-rewrite-readme-20260916-172200/README.md.orig)
- [README.vi.md.orig (Backup)](file:///d:/Desktop/All-Config-Voron-main/Voron%205%20Tool/extras/backups/pre-sync-live-lights-and-rewrite-readme-20260916-172200/README.vi.md.orig)

### Chi tiết thay đổi
1. **Đồng bộ cấu hình đèn buồng in (`fans-leds.cfg`):**
   - Macro `LIGHTS_ON`: Thay đổi `RED=0.3 GREEN=0.3 BLUE=0.3` thành `RED=1 GREEN=1 BLUE=1` và cập nhật mô tả macro từ `white 30%` sang `white 100%`, đồng nhất với cấu hình người vận hành đã chỉnh sửa trên máy in thực tế.
2. **Viết lại toàn diện `README.md` và `README.vi.md`:**
   - **Mục 1 - Thông số kỹ thuật & Kiến trúc phần cứng:** Bảng ánh xạ đầy đủ bo mạch Manta M8P V2, CM4, 5x EBB36 CAN, Cartographer V3 fw6.1.0, kTAMV camera MF-500, cọ Bambu A1 + bucket, bàn nhiệt AC 1000W và các quạt tản nhiệt.
   - **Mục 2 - Sơ đồ 5 Tool StealthChanger & Bản đồ Offset:** Bảng tọa độ dock và mechanical offset của T0–T4 khớp 100% với SAVE_CONFIG trong `printer.cfg`. Giải thích chi tiết hệ số nén nhựa squish factor và cơ chế đệm silicon chống rỉ nhựa tại dock.
   - **Mục 3 - Hướng dẫn Cài đặt & Triển khai:** Triển khai Lean Deployment bằng sparse checkout (tiết kiệm 97.7% dung lượng trên CM4, từ 610MB xuống 14MB); phân tích chi tiết quy trình 6 bước an toàn của `install.sh`; hướng dẫn cập nhật 1-click qua Moonraker Update Manager trong Mainsail và cập nhật không cần Git qua `update.sh`.
   - **Mục 4 - Hướng dẫn Vận hành & Sử dụng:** Mẫu lệnh Start G-code trong OrcaSlicer; bảng tra cứu chi tiết toàn bộ các macro vận hành (`PRINT_START`, `PRINT_END`, `PAUSE`, `RESUME`, `CANCEL_PRINT`, `START_DRYER`, `CLEAN_NOZZLE`, `PRIME_LINES`, `KTAMV_AUTO_CALIBRATE_ALL_TOOLS`, `MEASURE_TOOL_HEATUP`, `TEST_SPEED`, `TEST_Z_SPEED`, `LIGHTS_ON/OFF`, `BED_FAN_ON/OFF`).
   - **Mục 5 - Hướng dẫn Gỡ cài đặt, Hoàn tác & Bảo trì:** Dọn dẹp hệ thống bằng `cleanup-voron.sh`; quy trình hoàn tác (Rollback) từ thư mục sao lưu timestamped; quy trình gỡ cài đặt hoàn toàn (Decoupling) gỡ bỏ service và hoàn tác các bản vá mã nguồn Klipper.
   - **Mục 6 - Ghi công & Lời cảm ơn:** Ghi nhận đầy đủ bản quyền và công lao của các tác giả/dự án: StealthChanger, KTC-Easy, kTAMV, tool_crash, Cartographer 3D, Mainsail, ShakeTune, Ellis Print Tuning, Voron Design.
   - **Mục 7 - Phân tích Chuyên sâu 10 Thuật toán & Logic Vận hành Cốt lõi:**
     1. Thuật toán ngâm nhiệt co giãn động (`_PRINT_START_HEAT_SOAK`) theo hàm chênh lệch nhiệt độ $\Delta T$.
     2. Logic bảo vệ đầu dò Z và khử gờ nhựa 2 giai đoạn (lau ở 150 °C ngay trước khi Touch Home để chống võng ngàm).
     3. Nguyên tắc bất biến Homing an toàn với Cartographer cố định trên shuttle.
     4. Thuật toán điều tiết nhiệt và quạt sấy nhựa 4 vùng kết hợp xung xả ẩm định kỳ (Moisture Flush Pulse) và bảo vệ quá nhiệt.
     5. Thuật toán thị giác máy tính nhận diện đốm sáng tâm và bộ lọc phân tán 3 mẫu lặp lại kTAMV.
     6. Thuật toán mồi nhựa đa tool dạng pipeline (`PRIME_LINES`) chia slot động và nung trước tool tiếp theo.
     7. Watchdog chống rơi tool có lọc xung nhiễu và tạm dừng không di chuyển trục (`_TOOL_CRASH_SAFE_PAUSE`).
     8. Thuật toán rút sợi 2 nấc (-10mm) kết hợp nâng Z an toàn tối thiểu 50mm trước khi trả tool về dock.
     9. Máy trạng thái LED 10 mức ưu tiên hướng sự kiện kết hợp gom khung SPI và điều tiết bus CAN (`G4 P10`).
     10. Bộ đệm tham số Input Shaper động (`_ACTIVE_INPUT_SHAPER`) chống nghẽn log và cơ sở dữ liệu Moonraker.

### Lý do
- Đồng bộ thay đổi từ máy in thực tế để tránh ghi đè thiết lập của người dùng khi update.
- Cung cấp tài liệu hoàn chỉnh, chuẩn xác và sâu sắc nhất cho kho lưu trữ, phản ánh đúng 100% logic mã nguồn đang chạy thực tế trên máy in thay vì chỉ tổng kết tài liệu hướng dẫn bên ngoài.

### Kiểm tra
- Kiểm tra kết nối và tải toàn bộ file cấu hình từ máy in thực tế: Thành công.
- Đối chiếu hash và diff toàn bộ file cấu hình: Hoàn thành, chỉ có 1 khác biệt duy nhất ở `fans-leds.cfg` và đã được đồng bộ.
- Kiểm tra cú pháp Markdown của `README.md` và `README.vi.md`: Đạt, không có lỗi định dạng.
- Khớp nối các đường link tài liệu và file code: Đầy đủ, chính xác.

### Kết quả
- Toàn bộ cấu hình cục bộ và máy in thực tế đã đồng bộ hoàn hảo.
- Tài liệu README.md và README.vi.md đã được viết lại toàn diện, chuyên nghiệp, mô tả chính xác và sâu sắc mọi ngóc ngách của hệ thống.

### Vấn đề còn lại
- Không còn vấn đề tồn đọng. Hệ thống sẵn sàng để commit và push lên GitHub.