# Nhật ký — 2026-09-13

## 1. Dọn dẹp KCC/TKC, đồng bộ cấu hình máy in và tích hợp macro tự động đo kTAMV XY

### Mục tiêu
- Dọn dẹp sạch toàn bộ các dịch vụ, file tạm, thư mục thử nghiệm của KCC (Klipper-Camera-Calibration) và TKC (Tool-Klipper-Calibration) trên máy in thực tế `192.168.1.43`.
- Nghỉ hưu module `tool_calibrator` khỏi cây cấu hình active và đưa vào `extras/retired-configs/2026-09-13-tkc-removal/`.
- Đồng bộ thông số PID thực tế mới nhất của `extruder1` đến `extruder4` và các giá trị offset của 4 tool (`T1`–`T4`) từ máy thật về repository.
- Chuẩn hóa cấu hình, làm sạch comment và xây dựng macro đo tự động tuần tự 5 tool `KTAMV_AUTO_CALIBRATE_ALL_TOOLS` tại tọa độ an toàn `X: 170, Y: 0, Z: 40`.
- Cập nhật Git repository lên `origin/main`.

### File đã sửa đổi
- `config/printer.cfg` — Đồng bộ PID extruder 1–4, cập nhật tool offsets T1–T4 thực tế, gỡ bỏ include và comment liên quan tới TKC/KCC.
- `config/moonraker.conf` — Gỡ bỏ update_manager `tool_calibrator` và include KCC.
- `config/Printer-Setup/calibration-probe.cfg` — Làm sạch các tham chiếu tới TKC, làm sạch comment và tập trung vào kTAMV.
- `config/Printer-Setup/ktamv.cfg` — Bổ sung macro `_KTAMV_CALIBRATE_TOOL` và `KTAMV_AUTO_CALIBRATE_ALL_TOOLS` với tọa độ an toàn `X: 170, Y: 0, Z: 40`.
- `config/scripts/install.sh` — Gỡ bỏ các bước preflight check và exclude rule của TKC.
- `config/tool_calibrator/` — Chuyển toàn bộ vào `extras/retired-configs/2026-09-13-tkc-removal/`.

### Sao lưu
- [pre-cleanup-kcc-tkc-and-ktamv-autocalib-20260913-171300](file:///d:/Desktop/All-Config-Voron-main/Voron%205%20Tool/extras/backups/pre-cleanup-kcc-tkc-and-ktamv-autocalib-20260913-171300/)

### Chi tiết thay đổi
- **Trên máy chủ `voron@192.168.1.43`**:
  - Dừng và xóa `klipper-camera-calibration.service`.
  - Xóa 2 symlink KCC trong `/home/voron/klipper/klippy/extras/`.
  - Xóa sạch các thư mục và file bundle/log/tar.gz của KCC và TKC trong `/home/voron/`.
  - Xóa thư mục `camera_calibration/` và `tool_calibrator/` trong `printer_data/config/`.
  - Gỡ bỏ khối include KCC trong `printer.cfg` và `moonraker.conf`.
- **Trong cấu hình Klipper**:
  - Khởi tạo macro `KTAMV_AUTO_CALIBRATE_ALL_TOOLS` cho phép tự động chuyển tool tuần tự từ T1 đến T4, kiểm tra trạng thái toolchanger, tiếp cận tọa độ an toàn `X170 Y0 Z40`, tắt LED toolhead, lặp căn tâm kTAMV 3 lần, kiểm tra spread $\le 0.12\text{ mm}$ và tự động stage offset.

### Kiểm tra
- Khởi động lại firmware Klipper (`FIRMWARE_RESTART`): Thành công (`ready`).
- Khởi động lại Moonraker: Thành công (`klippy_connected: true`, không có failed component hay cảnh báo).
- Đăng ký macro Klipper: `gcode_macro KTAMV_AUTO_CALIBRATE_ALL_TOOLS` đã được nạp thành công.

### Kết quả
- Hệ thống máy in và kho mã nguồn đã được dọn dẹp sạch sẽ, không còn tàn dư của các dự án thử nghiệm KCC và TKC.
- Hệ thống kTAMV sẵn sàng thực hiện chu trình đo tự động XY an toàn.

---

## 2. Cập nhật Macro đo tự động kTAMV sử dụng tọa độ camera đã học (Learned Origin)

### Mục tiêu
- Thay thế việc hardcode tọa độ `X170 Y0` trong macro `_KTAMV_CALIBRATE_TOOL` và `KTAMV_AUTO_CALIBRATE_ALL_TOOLS` bằng tọa độ động đã học `printer.ktamv.camera_center_coordinates` từ bước thiết lập gốc quy chiếu T0 (`KTAMV_SET_ORIGIN`).

### File đã sửa đổi
- `config/Printer-Setup/ktamv.cfg` — Sử dụng `printer.ktamv.camera_center_coordinates` làm điểm đích tiếp cận tại độ cao `safe_z` (Z40).

### Sao lưu
- [pre-ktamv-learned-origin-20260913-172000](file:///d:/Desktop/All-Config-Voron-main/Voron%205%20Tool/extras/backups/pre-ktamv-learned-origin-20260913-172000/)

### Chi tiết thay đổi
- Macro `_KTAMV_CALIBRATE_TOOL`: Sau khi gắp tool từ dock, đầu in nâng lên `safe_z` ngay tại vị trí hiện tại để đảm bảo an toàn, sau đó bay tới tọa độ camera đã học `origin = printer.ktamv.camera_center_coordinates`.
- Không nhúng bất kỳ tọa độ XY tĩnh nào vào macro, giúp hệ thống hoàn toàn linh hoạt trước mọi thay đổi cơ khí camera.

### Kiểm tra
- Nạp lại firmware Klipper (`FIRMWARE_RESTART`): Thành công (`ready`).

---

## 3. Cập nhật tài liệu kỹ thuật Markdown và chuẩn hóa comment trong hệ thống

### Mục tiêu
- Cập nhật toàn bộ các file `.md` chính của dự án dựa trên việc đọc code thực tế, tuyệt đối không đoán mò.
- Đảm bảo các comment trong các file cấu hình `.cfg` và tài liệu khớp 100% với hiện trạng vận hành.

### File đã sửa đổi
- `README.md` & `README.vi.md` — Cập nhật bảng offset thực tế mới nhất, ghi nhận việc nghỉ hưu của TKC/KCC và macro tự động `KTAMV_AUTO_CALIBRATE_ALL_TOOLS`.
- `config/README.md` & `config/README.vi.md` — Cập nhật chuỗi include của `printer.cfg`, làm rõ vai trò kTAMV là backend cân chỉnh XY duy nhất hiện hành.
- `extras/docs/README.md` & `extras/docs/README.vi.md` — Thêm thư mục nghỉ hưu `extras/retired-configs/2026-09-13-tkc-removal/` và snapshot rollback mới.
- `.agents/PROJECT.md` — Cập nhật hiện trạng hệ thống cân chỉnh, bỏ các plugin cũ.
- `.agents/DIRECTORY.md` — Cập nhật cấu trúc thư mục, ghi nhận `retired-configs/2026-09-13-tkc-removal/` và bỏ `tool_calibrator/`.
- `.agents/KNOWN_ISSUES.md` — Khôi phục cấu trúc file sạch sẽ, ghi chú trạng thái nghỉ hưu của các issue TKC ngày 2026-09-13.
- `.agents/TODO.md` — Đánh dấu hoàn thành các hạng mục gỡ KCC/TKC, macro đo tự động và dọn dẹp tài liệu.
- `.agents/DECISIONS.md` — Bổ sung quyết định kỹ thuật ngày 2026-09-13 về việc chuẩn hóa kTAMV và cơ chế tọa độ học.
- `.agents/CHANGELOG.md` — Bổ sung phiên bản [1.7.0] — 2026-09-13.

### Kiểm tra
- Toàn bộ các file `.md` và `.cfg` đã được kiểm tra cú pháp, đường dẫn và tính nhất quán với code thực tế.

---

## 4. Cập nhật tọa độ công tắc Axiscope Z và rút gọn/ẩn các macro kTAMV phụ

### Mục tiêu
- Cập nhật tọa độ vật lý mới của công tắc vi mô đo Z (Axiscope switch): `X: 68.0, Y: -8.0, Z: 2.0`.
- Kích hoạt lại module `[axiscope]` trong `calibration-probe.cfg` để hỗ trợ đo tự động chênh lệch Z bằng lệnh `CALIBRATE_ALL_Z_OFFSETS`.
- Rút gọn bảng macro trên giao diện Mainsail: ẩn các macro phụ trợ kTAMV bằng tiền tố `_` (`_KTAMV_SETUP`, `_KTAMV_MEASURE_ACTIVE_TOOL_XY`, `_KTAMV_APPLY_ACTIVE_TOOL_XY`), chỉ giữ lại macro chính `KTAMV_AUTO_CALIBRATE_ALL_TOOLS` và macro kiểm tra `KTAMV_STATUS`.

### File đã sửa đổi
- `config/Printer-Setup/calibration-probe.cfg` — Kích hoạt `[axiscope]` với tọa độ `zswitch_x_pos: 68.0`, `zswitch_y_pos: -8.0`, `zswitch_z_pos: 2.0`.
- `config/Printer-Setup/ktamv.cfg` — Đổi tên các macro helper thành `_KTAMV_SETUP`, `_KTAMV_MEASURE_ACTIVE_TOOL_XY`, `_KTAMV_APPLY_ACTIVE_TOOL_XY`.

### Sao lưu
- [pre-axiscope-update-20260913-174800](file:///d:/Desktop/All-Config-Voron-main/Voron%205%20Tool/extras/backups/pre-axiscope-update-20260913-174800/)

### Kiểm tra
- Nạp cấu hình sang máy in `192.168.1.43` và khởi động lại firmware Klipper (`FIRMWARE_RESTART`): Thành công (`ready`).
- Lệnh Moonraker help xác nhận: các lệnh `CALIBRATE_ALL_Z_OFFSETS`, `MOVE_TO_ZSWITCH`, `PROBE_ZSWITCH` đã sẵn sàng; các macro helper kTAMV đã được ẩn khỏi bảng điều khiển Mainsail.

---

## 5. Thêm cơ chế chờ nhiệt độ 150°C cho từng tool và nâng Z an toàn trong quy trình đo Axiscope

### Mục tiêu
- Khắc phục sự cố: Khi chạy lệnh `CALIBRATE_ALL_Z_OFFSETS`, lệnh `M104 T{tool} S150` chỉ phát nhiệt độ mục tiêu mà không chờ, khiến T0 bắt đầu gõ công tắc ngay cả khi nhiệt độ còn nguội (chưa kịp đạt 150°C), gây sai lệch giãn nở nhiệt.
- Đảm bảo an toàn cơ khí: Nâng Z lên mức an toàn (Z $\ge 15\text{ mm}$) trước khi chuyển tool về dock.

### File đã sửa đổi
- `config/Printer-Setup/calibration-probe.cfg`:
  - `start_gcode`: Thêm lệnh `M109 T0 S150` để chờ T0 (tool quy chiếu) đạt đủ 150°C trước khi bất kỳ thao tác đo nào bắt đầu.
  - `before_pickup_gcode`: Thêm kiểm tra và nâng Z lên $15\text{ mm}$ nếu $Z < 15\text{ mm}$ trước khi di chuyển về dock đổi tool.
  - `after_pickup_gcode`: Thêm `M109 S150` để đảm bảo từng tool sau khi gắp từ dock phải đạt đủ 150°C trước khi tiếp cận công tắc.
- `config/toolchanger/toolchanger-config.cfg`: Đồng bộ tọa độ trong macro `_CALIBRATION_SWITCH` thành `variable_y: -8` và `variable_z: 15`.

### Sao lưu
- [pre-axiscope-temp-wait-20260913-175800](file:///d:/Desktop/All-Config-Voron-main/Voron%205%20Tool/extras/backups/pre-axiscope-temp-wait-20260913-175800/)

### Kiểm tra
- Nạp cấu hình sang máy in `192.168.1.43` và khởi động lại firmware Klipper (`FIRMWARE_RESTART`): Thành công (`ready`).

---

## 6. Cập nhật Z-offset cho các Tool T1–T4 từ dữ liệu đo Cartographer Touch (Bàn 70°C, Hotend 150°C)

### Mục tiêu
- Áp dụng bộ thông số Z-offset mới nhất được đo đạc và lấy trung bình 3 lần liên tiếp qua lệnh `CARTOGRAPHER_TOUCH_PROBE` tại điều kiện nhiệt độ in thực tế (Bàn 70°C, Hotend 150°C).
- Lưu cấu hình vĩnh viễn trên máy in thật `192.168.1.43` qua `SET_TOOL_PARAMETER` + `SAVE_TOOL_PARAMETER` + `SAVE_CONFIG`.
- Đồng bộ cấu hình về kho lưu trữ Git và cập nhật tài liệu dự án.

### File đã sửa đổi
- `config/printer.cfg` — Cập nhật `gcode_z_offset` cho T1 (0.2091), T2 (-0.2742), T3 (-0.2175), T4 (0.0585) trong khối `#*# <SAVE_CONFIG>`.
- `README.md` — Cập nhật bảng offset cơ khí XYZ của 5 tool.
- `README.vi.md` — Cập nhật bảng offset cơ khí XYZ của 5 tool.
- `extras/Nhat-ky-chinh-sua/2026-09-13-session-updates.md` — Bổ sung ghi nhận phiên làm việc.

### Sao lưu
- [pre-apply-carto-touch-z-offsets-20260913-191400](file:///d:/Desktop/All-Config-Voron-main/Voron%205%20Tool/extras/backups/pre-apply-carto-touch-z-offsets-20260913-191400/)
- Snapshot trên máy in: `/home/voron/printer_data/config/printer.cfg.bak-carto-touch-20260913`

### Chi tiết thay đổi
- **T0**: Mốc quy chiếu chuẩn (Z=0.0000).
- **T1**: `0.2360` → `0.2091` ($\Delta = -0.0269\text{ mm}$, độ tản mạn 3 lần đo: $14\,\mu\text{m}$).
- **T2**: `-0.3160` → `-0.2742` ($\Delta = +0.0418\text{ mm}$, độ tản mạn 3 lần đo: $14\,\mu\text{m}$).
- **T3**: `-0.1896` → `-0.2175` ($\Delta = -0.0279\text{ mm}$, độ tản mạn 3 lần đo: $8\,\mu\text{m}$).
- **T4**: `0.1200` → `0.0585` ($\Delta = -0.0615\text{ mm}$, độ tản mạn 3 lần đo: $12\,\mu\text{m}$).

### Kiểm tra
- Thực thi lệnh KTC `SET_TOOL_PARAMETER` & `SAVE_TOOL_PARAMETER` thành công trên máy in qua Moonraker API.
- Lệnh `CHECK_OFFSETS` xác nhận runtime offsets:
  - T0: Z=0.0
  - T1: Z=0.2091
  - T2: Z=-0.2742
  - T3: Z=-0.2175
  - T4: Z=0.0585
- Thực hiện `SAVE_CONFIG`: Klipper tự động khởi động lại và báo trạng thái `ready`.
- Kiểm tra tính nguyên vẹn cấu hình: Khớp 100% giữa host `192.168.1.43` và Git repo.

### Kết quả
- Toàn bộ 4 tool đã được nạp bộ số Z-offset thực nghiệm chuẩn xác nhất, sẵn sàng cho các bài in thử nghiệm đa màu / đa vật liệu.

---

## 7. Tích hợp hệ số bù nén nhựa First Layer (Squish Factor) vào Z-offset của Toolchanger

### Mục tiêu
- Áp dụng kinh nghiệm in thực tế của người dùng: sợi nhựa nóng chảy ở First Layer cần một độ nén cơ học sâu hơn tiếp xúc bề mặt khoảng $-0.03\text{ mm}$ đến $-0.04\text{ mm}$ để bám chắc và ép phẳng vào vân PEI sần.
- Cập nhật trực tiếp các giá trị Z-offset đã bù nén nhựa vào cấu hình máy in và đồng bộ tài liệu, tránh phải can thiệp baby-step thủ công cho từng tool khi in đa màu.

### File đã sửa đổi
- `config/printer.cfg` — Cập nhật `gcode_z_offset`: T1 (0.1691), T2 (-0.3142), T3 (-0.2575), T4 (0.0285).
- `README.md` & `README.vi.md` — Cập nhật bảng offset cơ khí XYZ và thêm TIP lưu ý về First-Layer Squish Factor.
- `.agents/DECISIONS.md` — Bổ sung quyết định kỹ thuật ghi nhận việc bù squish vào toolchanger Z-offset.
- `extras/Nhat-ky-chinh-sua/2026-09-13-session-updates.md` — Bổ sung ghi nhận phiên làm việc.

### Sao lưu
- [pre-apply-squish-compensated-z-offsets-20260913-202800](file:///d:/Desktop/All-Config-Voron-main/Voron%205%20Tool/extras/backups/pre-apply-squish-compensated-z-offsets-20260913-202800/)
- Snapshot trên máy in: `/home/voron/printer_data/config/printer.cfg.bak-presquish-20260913`

### Chi tiết thay đổi
- **T0**: `0.0000 mm` (Tool chuẩn quy chiếu).
- **T1**: $0.2091 + (-0.0400) = \mathbf{0.1691\text{ mm}}$.
- **T2**: $-0.2742 + (-0.0400) = \mathbf{-0.3142\text{ mm}}$ (trùng khớp với giá trị in đẹp thực nghiệm cũ `-0.3160 mm`).
- **T3**: $-0.2175 + (-0.0400) = \mathbf{-0.2575\text{ mm}}$.
- **T4**: $0.0585 + (-0.0300) = \mathbf{0.0285\text{ mm}}$.

### Kiểm tra
- Thực thi `SET_TOOL_PARAMETER` & `SAVE_TOOL_PARAMETER` thành công trên máy in `192.168.1.43` qua Moonraker API.
- Lệnh `CHECK_OFFSETS` xác nhận runtime offsets:
  - T0: Z=0.0
  - T1: Z=0.1691
  - T2: Z=-0.3142
  - T3: Z=-0.2575
  - T4: Z=0.0285
- Thực hiện `SAVE_CONFIG`: Klipper tự động khởi động lại và báo trạng thái `ready`.
- Đồng bộ `printer.cfg` từ máy in về kho mã nguồn cục bộ.

### Kết quả
- Máy in đã sẵn sàng in First Layer đa màu với độ nén nhựa tối ưu tự động cho toàn bộ 5 đầu in.




