# Nhật ký thay đổi (Changelog)

Tất cả thay đổi đáng chú ý của cấu hình máy in được ghi nhận ở đây.
Định dạng theo [Keep a Changelog](https://keepachangelog.com/).

## [1.8.0] — 2026-09-16

### Thay đổi
- Đồng bộ cấu hình đèn buồng in `LIGHTS_ON` sang 100% công suất (`RED=1 GREEN=1 BLUE=1`) trong `config/Printer-Setup/fans-leds.cfg` khớp với thiết lập người vận hành trên máy in thực tế.
- Viết lại toàn diện tài liệu tổng quan dự án song ngữ: `README.md` (tiếng Anh) và `README.vi.md` (tiếng Việt), bao gồm bản đồ phần cứng, bảng tọa độ dock/offset, hướng dẫn cài đặt Lean deployment, tra cứu macro và phân tích chuyên sâu 10 thuật toán cốt lõi.
- Làm sạch và bảo mật tài liệu: loại bỏ toàn bộ địa chỉ IP mạng nội bộ và chi tiết SSH cá nhân, chuyển sang định dạng placeholder chuẩn.
- Cập nhật hệ thống tài liệu quy tắc `.agents/` phản ánh chính xác cấu trúc thư mục, hệ thống cân chỉnh Z kép và quy trình vận hành.

---

## [1.7.2] — 2026-09-15

### Thay đổi
- Triển khai và đánh giá thử nghiệm thực tế module thị giác máy tính Klipper-Camera-Vision (`tool_xy_vision.cfg`) trên máy in.
- Khôi phục cấu hình kTAMV production (`ktamv.cfg`) làm backend chính thức cho cân chỉnh camera XY có giám sát để đảm bảo độ tin cậy và ổn định cao nhất.

---

## [1.7.1] — 2026-09-13

### Thêm mới & Cải tiến
- Nâng cấp macro `CALIBRATE_ALL_Z_OFFSETS` của module Axiscope:
  - Thêm lệnh `M109 T0 S150` và `M109 S150` đảm bảo từng tool đạt đủ 150°C trước khi tiếp xúc công tắc, triệt tiêu sai số giãn nở nhiệt.
  - Thêm kiểm tra và nâng Z an toàn ($Z \ge 15\text{ mm}$) trước khi di chuyển về dock đổi tool để chống va chạm.
  - Cập nhật tọa độ công tắc microswitch chuẩn: `X=68, Y=-8, Z=2` (tiếp cận tại Z15).
- Tích hợp hệ số bù nén nhựa First Layer (Squish Factor: -0.04mm cho T1–T3, -0.03mm cho T4) trực tiếp vào giá trị `gcode_z_offset` của từng tool trong khối `#*# <SAVE_CONFIG>` của `printer.cfg`.

---

## [1.7.0] — 2026-09-13

### Thay đổi
- Gỡ bỏ hoàn toàn các module thử nghiệm KCC (Klipper-Camera-Calibration) và TKC (Tool-Klipper-Calibration) khỏi máy in thực tế và đưa cấu hình TKC vào `extras/retired-configs/2026-09-13-tkc-removal/`.
- Chuẩn hóa kTAMV làm backend chính thức cho cân chỉnh camera XY có giám sát.
- Triển khai macro `KTAMV_AUTO_CALIBRATE_ALL_TOOLS` và `_KTAMV_CALIBRATE_TOOL` trong `config/Printer-Setup/ktamv.cfg` sử dụng tọa độ camera được học (`printer.ktamv.camera_center_coordinates` từ T0), Z an toàn = 40 mm.
- Cập nhật tài liệu dự án, hệ thống quy tắc `.agents/`, các file README song ngữ, và đồng bộ giá trị PID, offset thực tế.

---

## [1.6.0] — 2026-08-31

### Thay đổi
- Gỡ ToolVision khỏi payload active và chuyển CFG cuối vào retired-configs.
- Cài kTAMV upstream được pin cho đối chiếu X/Y có giám sát; tắt cloud upload và
  dùng user service cổng 8086.
- Thay preflight deploy bằng kiểm tra commit, symlink và patch detector kTAMV.
- Bổ sung tài liệu song ngữ đối chiếu workflow kTAMV với ToolVision đã retired.

### An toàn
- Không gửi G-code, home, toolchange, gia nhiệt hoặc lệnh chuyển động; tool được
  giữ nguyên trên camera trong toàn bộ phiên cài đặt.
- Lưu snapshot đầy đủ trên repository và CM4 trước khi thay đổi.

## [1.5.0] — 2026-08-23

### Thay đổi
- Giao toàn quyền quản lý `toolchanger/readonly-configs/` cho KTC-Easy; All-Config chỉ deploy cấu hình người dùng và các override.
- Thêm preflight bắt buộc kiểm tra đủ sáu symlink KTC-Easy hợp lệ trước khi backup hoặc deploy.
- Xác nhận bộ Input Shaper production riêng cho T0–T4 và đồng bộ lại chú thích theo đúng giá trị đang dùng.
- Cập nhật tài liệu về Axiscope PF2 production, ToolVision inactive và kTAMV đã gỡ.

### Đã sửa
- Ghi nhận lỗi Cartographer và cảm biến T4 đã hết theo xác nhận của người vận hành.
- Sửa tài liệu nhầm `gcode_x_offset` của T2 thành Z-offset và loại bỏ hướng dẫn kTAMV không còn tồn tại.
- Bổ sung metadata submodule còn thiếu cho `extras/Axiscope-reference`.

## [1.4.0] — 2026-08-09

### Thêm mới
- Cấu hình module `[axiscope]` trong `Printer-Setup/calibration.cfg` hỗ trợ công tắc vi mô đo Z-offset cho các đầu in (T0–T4) tại tọa độ X:68, Y:-10, Z:7.
- Tự động loại trừ các file `README.md` và `*.md` trong `config/scripts/install.sh` và `config/scripts/update.sh` khi đồng bộ sang máy in.

### Thay đổi
- Cập nhật chân tín hiệu switch Z-offset sang `pin: ^PF2` trên Manta M8P V2 (khớp với kết nối thực tế PF2 + GND).
- Đồng bộ khối `SAVE_CONFIG` mới nhất từ máy in thực tế: Cartographer touch threshold mới `1819`, reference_temperature `42.44`, các hệ số scan model và PID calibration.
- Khôi phục bộ giá trị `gcode_z_offset` in thực tế đẹp cho các cụm đầu in (`T1: 0.228`, `T2: -0.295`, `T3: -0.268`, `T4: 0.086`).
- Làm mới và đồng bộ hóa toàn diện tài liệu dự án, hệ thống quy tắc `.agents/`, và các file README.

---

## [1.3.0] — 2026-07-02

### Thêm mới
- Nhật ký xử lý sự cố cho sự cố timeout CAN Cartographer.

### Đã sửa
- Timeout kết nối MCU Cartographer sau soft restart (giải pháp tạm: tắt nguồn hoàn toàn).

---

## [1.2.0] — 2026-06-30

### Thay đổi
- Cập nhật `zero_reference_position` trong `probe-mesh.cfg` từ `170, 203` sang `174, 168` để khớp vị trí homing nozzle.
- Cập nhật ngưỡng touch Cartographer từ `1968` lên `2594` sau khi hiệu chuẩn lại.
- Điều chỉnh Z-offset cho tool T1, T2, T3, T4 dựa trên hiệu chuẩn lại.
- Tinh chỉnh Z-offset T3 thêm -0.08mm dựa trên thử in thực tế.

### Thêm mới
- Quy tắc bảo mật trong `.gitignore` cho `*.secrets`, `moonraker.secrets`, `wpa_supplicant.conf`.

---

## [1.1.0] — 2026-06-23

### Thay đổi
- Tăng `check_gain_time` của `heater_bed` từ 120s lên 240s để ngăn shutdown giả từ nhiễu SSR.
- Điều chỉnh `retry_tolerance` QGL từ 0.005 lên 0.0075 để ngăn hủy giả do motor numbering.

### Thêm mới
- Cấu hình camera MF-500 ở độ phân giải 2K với chống nhấp nháy 50Hz.
- Hỗ trợ WebRTC qua camera-streamer.

---

## [1.0.0] — 2026-05-16

### Thêm mới
- Cấu hình production ban đầu cho Voron 2.4 StealthChanger 5-Tool.
- Cấu hình SexBolt Z endstop.
- Tất cả định nghĩa tool (T0–T4) với board EBB CAN bus.
- Cài đặt probe Cartographer v3.
- Bộ macro hoàn chỉnh (PRINT_START, PRINT_END, vệ sinh đầu phun, prime line).
