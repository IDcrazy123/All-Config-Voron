# Nhật ký — 2026-09-15

## 1. Thử nghiệm Cài đặt & Vận hành Klipper-Camera-Vision, Đánh giá và Chỉ ra các Lỗi Cần Sửa lại

### Mục tiêu
- Vô hiệu hóa kTAMV (dừng `ktamv-server.service` và comment `[include Printer-Setup/ktamv.cfg]`).
- Cài đặt dự án `IDcrazy123/Klipper-Camera-Vision` theo đúng quy trình hướng dẫn của tác giả trên máy in `192.168.1.43`.
- Vận hành thử nghiệm đo bù trừ XY giữa các tool tại tọa độ an toàn `170:0:40` trong điều kiện camera hướng lên, nozzle trên camera, đèn LED chiếu nozzle đang bật, G28 an toàn.
- Kiểm nghiệm toàn diện quy trình cài đặt, phát hiện các lỗi phát sinh và phân tích sâu các điểm cần sửa lại của dự án.

### File đã sửa đổi
- `config/printer.cfg` — Comment `[include Printer-Setup/ktamv.cfg]`, thêm `[include Printer-Setup/tool_xy_vision.cfg]`
- `config/Printer-Setup/tool_xy_vision.cfg` — [NEW] Cấu hình Klipper-Camera-Vision với endpoint snapshot port 8080 và tọa độ camera an toàn (170, 0, 40)

### Sao lưu
- `extras/backups/pre-test-klipper-camera-vision-20260915-201000/printer.cfg`

### Chi tiết thay đổi
1. **kTAMV:**
   - Dừng và disable `ktamv-server.service` trên user systemd máy in.
   - Comment dòng include `Printer-Setup/ktamv.cfg` trong `printer.cfg`.
2. **Klipper-Camera-Vision:**
   - Clone repo `IDcrazy123/Klipper-Camera-Vision` vào `~/tool-xy-vision`.
   - Thực thi `bash scripts/install.sh` để kiểm nghiệm quy trình cài đặt chính thức.
   - Tạo systemd user service `~/.config/systemd/user/tool-xy-vision.service` chạy Vision Service port 8085.
   - Thêm `tool_xy_vision.cfg` vào `Printer-Setup/` và include vào `printer.cfg`.

### Các lỗi phát hiện và kiểm nghiệm thực tế

1. **Lỗi kịch bản cài đặt yêu cầu quyền root/sudo (Installer Permission Error):**
   - `install.sh` cố ghi file vào `/etc/systemd/system/` và chạy `sudo systemctl`, khiến script crash trên môi trường không có sudo nopasswd.
   - *Khắc phục:* Nên chuyển sang Systemd User Service (`~/.config/systemd/user/`) như kTAMV để không đòi hỏi quyền root.
2. **Lỗi thiếu module `requests` trong môi trường Klippy (Missing Klippy Dependency):**
   - `install.sh` chỉ cài phụ thuộc vào `tool-xy-vision-env`, nhưng extension `vision_client.py` chạy trực tiếp trong tiến trình Klippy (`klippy-env`). Khi nạp module, Klipper sập với lỗi: `Internal error during connect: No module named 'requests'`.
   - *Khắc phục:* Cần cài `requests` vào `klippy-env` trong installer hoặc chuyển `vision_client.py` sang dùng thư viện chuẩn `urllib.request`.
3. **Lỗi script chẩn đoán `doctor.py` (AttributeError):**
   - Dòng 64 trong `doctor.py` gọi `waitress.__version__` gây crash vì module `waitress` không có thuộc tính này.
   - *Khắc phục:* Dùng `getattr(waitress, "__version__", "installed")`.
4. **Lỗi không truyền `camera_url` trong `commands.py` (Vision Payload Bug):**
   - Các lệnh `detect_nozzle()` trong `commands.py` (dòng 34, 49) không truyền payload `camera_url`. Vision Service nhận request rỗng và cố mở trực tiếp `/dev/video0`, xung đột với `camera-streamer` và trả về lỗi 503 `Could not acquire frame from camera source`.
   - *Khắc phục:* Truyền đầy đủ `{"camera_url": self.controller.config.camera_url, "burst_frames": ...}`.
5. **Lỗi lệnh đổi tool `TT<id>` trên StealthChanger (KTC Adapter Bug):**
   - Trong `klipper_toolchanger.py`, hàm `discover_tools` trích xuất `tool_id = "T0"`, `"T1"`,... Sau đó `select_tool` gọi `f"T{tool_id}"` sinh ra lệnh `TT0`, `TT1` khiến Klipper báo `// Unknown command:"TT0"`. Lỗi bị khối try...except nuốt, khiến máy in không đổi đầu tool nhưng vẫn tiếp tục đo lặp lại tool cũ.
   - *Khắc phục:* Dùng `str(tool_id).lstrip("Tt")` trước khi phát lệnh `T<id>`.
6. **Lỗi kiến trúc nghẽn Klippy Reactor dẫn đến MCU Shutdown (Critical Architectural Flaw):**
   - Khi chạy `TOOL_XY_ALIGN_CAMERA` hoặc `TOOL_XY_MEASURE_ALL`, việc gọi HTTP đồng bộ `requests.post()` và chạy vòng lặp xử lý ảnh nặng trong tiến trình Klippy chiếm giữ Reactor liên tục 13-50 giây. Vi điều khiển Manta M8P bị timeout heartbeat qua CAN bus và kích hoạt: `Transition to shutdown state: MCU shutdown`.
   - *Khắc phục:* Giảm `max_center_iterations` xuống 2-3, chèn `reactor.pause()` / `toolhead.dwell()` nhường luồng trong từng chu kỳ, hoặc chia quy trình đo thành các macro G-code riêng lẻ cho từng tool như kTAMV.
7. **Lỗi giới hạn hành trình gán cứng 300mm (Hardcoded Axis Limits):**
   - Trong `navigator.py`, `AxisLimits` gán cứng 0-300mm, gây lỗi `MotionSafetyError` trên máy in khổ 350mm hoặc dock có Y âm.
   - *Khắc phục:* Đọc động giới hạn từ `toolhead.axis_minimum` và `toolhead.axis_maximum`.
8. **Hàm lưu offset chưa hoàn thiện (Unimplemented save_offsets):**
   - Phương thức `save_offsets` trong `klipper_toolchanger.py` chỉ là `pass`, chưa cập nhật các giá trị `gcode_x_offset`, `gcode_y_offset` vào KTC.

### Kết quả đo thử nghiệm
- Lệnh `TOOL_XY_ALIGN_CAMERA` sau khi vá lỗi reactor đã hoàn tất thành công:
  `Tool-XY-Vision: Captured camera station at X=170.00, Y=0.00, Z=40.00`
  `Tool-XY-Vision: Reference tool centered & Optical Origin locked at X=170.0000 Y=0.0000`
- Khả năng nhận diện quang học của mô hình Ensemble (`ktamv_triangle`, `ktamv_yuv_adaptive`, `hough`, `blob_otsu_dark`) bắt nozzle rất tốt ngay cả khi LED chiếu nozzle đang bật, độ không đảm bảo subpixel chỉ `0.387 px` (~0.005 mm).
