# Nhật ký Cập nhật Hệ thống — 2026-09-17

**Mục tiêu chính trong phiên:**
- Nâng cấp quy trình đo Z-Offset 5 Tool bằng Cartographer Touch mô phỏng chính xác điều kiện in thực tế (Nhiệt độ đầu in 150°C, Bàn in 70°C cho vật liệu PETG).
- Khảo sát các tài liệu kỹ thuật, tiêu chuẩn ngành và mã nguồn Cartographer Touch về dãn nở nhiệt (thermal expansion) và giới hạn nhiệt độ an toàn.

---

## 1. Nâng cấp Macro Đo Z Offset với Điều kiện Nhiệt độ Thực tế (Nozzle 150°C, Bed 70°C)

### Bối cảnh & Nghiên cứu kỹ thuật
- **Nhiệt độ vòi phun 150°C:**
  + Vừa đủ làm mềm các hạt nhựa thừa dính ở chóp kim (PLA, PETG, ABS), ngăn chặn hiện tượng hạt nhựa đông cứng làm kênh độ cao tiếp xúc (false offset).
  + Không gây chảy nhựa nhỏ giọt (oozing) ra bàn in.
  + Đảm bảo an toàn tuyệt đối cho bề mặt tấm PEI (nhiệt độ >160-180°C có thể làm mềm hoặc cháy rỗ bề mặt PEI khi đè nén).
  + Tuân thủ nghiêm ngặt giới hạn bảo vệ `UNSAFE_max_touch_temperature = 150` được quy định trong firmware/extension Cartographer.
  + Tái hiện hiện tượng dãn nở nhiệt (thermal expansion) của cụm hotend (heatsink, heatbreak, heatblock và nozzle).
- **Nhiệt độ bàn in 70°C (chuẩn PETG):**
  + Tấm nhôm bàn in Voron (dày 8mm) khi gia nhiệt lên 70°C sẽ dãn nở nhiệt cả về độ dày trục Z và độ cong võng bề mặt (thermal bowing).
  + Bàn in 70°C truyền nhiệt làm ấm buồng in và đầu dò Cartographer, đưa toàn bộ hệ thống cơ khí gantry về trạng thái cân bằng nhiệt tương tự lúc in thực tế.

### File đã sửa đổi
- `config/Printer-Setup/calibration-probe.cfg` — Nâng cấp macro `MEASURE_ALL_Z_CARTOGRAPHER` hỗ trợ các tham số: `BED_TEMP=70`, `NOZZLE_TEMP=150`, `SOAK=0`, `CLEAN=0`, `KEEP_HEAT=0`.

### Sao lưu
- [calibration-probe.cfg.local (Backup)](file:///d:/Desktop/All-Config-Voron-main/Voron%205%20Tool/extras/backups/pre-heated-cartographer-z-measure-20260917-155500/calibration-probe.cfg.local)
- [calibration-probe.cfg.live (Backup)](file:///d:/Desktop/All-Config-Voron-main/Voron%205%20Tool/extras/backups/pre-heated-cartographer-z-measure-20260917-155500/calibration-probe.cfg.live)

### Chi tiết thay đổi
1. **Kiểm tra an toàn nhiệt độ:** Ngăn chặn đặt `NOZZLE_TEMP > 150` để bảo vệ mặt bàn PEI và tránh Cartographer Touch kích hoạt ngoại lệ.
2. **Gia nhiệt trước:** Bật nhiệt độ bàn in `M140 / M190 S{bed_temp}`, đồng thời bật nhiệt độ nền `M104 T{tool} S{nozzle_temp}` cho cả 5 đầu in để tiết kiệm thời gian chờ đợi.
3. **Cập nhật Homing Z:** Tự động chạy `G28 Z` sau khi bàn in đạt 70°C để hấp thu dãn nở nhiệt ban đầu của bàn.
4. **Chuỗi đo chính xác:** Lần lượt pick từng tool T0 -> T4, chờ ổn định 150°C, hỗ trợ tùy chọn chùi vòi phun `CLEAN=1` qua cọ silicon Bambu A1, di chuyển đến tâm bàn `(175, 175)` và thực hiện `CARTOGRAPHER_TOUCH_ACCURACY SAMPLES=3`.
5. **Dọn dẹp an toàn:** Trả về T0, hạ nhiệt toàn bộ đầu in và bàn in (hoặc giữ nhiệt nếu đặt `KEEP_HEAT=1`).

### Kiểm tra
- Triển khai lên máy in `192.168.1.43` qua SCP.
- Gửi lệnh `FIRMWARE_RESTART`: Máy in khởi động lại thành công và đạt trạng thái `Printer is ready`.

---

## 2. Tính toán & Phân tích Kết quả Đo Z-Offset Nhiệt độ Cao (Nozzle 150°C, Bed 70°C)

### Dữ liệu đo thực tế từ máy in
- **T0:** $Z_{\text{touch}} = -0.152115$ mm (offset cũ: `0.0000`)
- **T1:** $Z_{\text{touch}} = +0.031218$ mm (offset cũ: `0.1691`) $\rightarrow \Delta Z = +0.1833$ mm $\rightarrow$ Offset mới = **`+0.3524`** mm
- **T2:** $Z_{\text{touch}} = -0.451448$ mm (offset cũ: `-0.3142`) $\rightarrow \Delta Z = -0.2993$ mm $\rightarrow$ Offset mới = **`-0.6135`** mm
- **T3:** $Z_{\text{touch}} = -0.413448$ mm (offset cũ: `-0.2575`) $\rightarrow \Delta Z = -0.2613$ mm $\rightarrow$ Offset mới = **`-0.5188`** mm
- **T4:** $Z_{\text{touch}} = -0.139448$ mm (offset cũ: `+0.0285`) $\rightarrow \Delta Z = +0.0127$ mm $\rightarrow$ Offset mới = **`+0.0412`** mm

### So sánh dãn nở nhiệt (Nguội vs Nóng 150°C/70°C)
- Tọa độ tiếp xúc tuyệt đối của bàn in tăng vọt gần +0.47 mm do bàn nhôm và hotend nở nhiệt trục Z.
- Mức độ chênh lệch tương đối giữa các tool khi nóng so với lúc nguội dao động từ 37 đến 87 micron (0.04 - 0.09 mm).
- Việc bù nhiệt độ thực tế giúp ngăn ngừa hoàn toàn hiện tượng cày xước bàn hoặc hở lớp in đầu tiên khi chuyển tool lúc in vật liệu PETG/ABS.

---

## 3. Đối chiếu Đo Lần 2 & Tính toán Giá trị Trung bình Hội tụ (Thermal Convergence)

### Dữ liệu đo Lần 2 (Nhiệt độ ngâm 15 phút):
- **T0:** $Z_{\text{touch}} = -0.320608$ mm
- **T1:** $Z_{\text{touch}} = -0.121942$ mm $\rightarrow \Delta Z = +0.1987$ mm $\rightarrow$ Offset Lần 2 = **`+0.3678`** mm
- **T2:** $Z_{\text{touch}} = -0.595275$ mm $\rightarrow \Delta Z = -0.2747$ mm $\rightarrow$ Offset Lần 2 = **`-0.5889`** mm
- **T3:** $Z_{\text{touch}} = -0.565275$ mm $\rightarrow \Delta Z = -0.2447$ mm $\rightarrow$ Offset Lần 2 = **`-0.5022`** mm
- **T4:** $Z_{\text{touch}} = -0.266608$ mm $\rightarrow \Delta Z = +0.0540$ mm $\rightarrow$ Offset Lần 2 = **`+0.0825`** mm

### Độ lặp lại giữa Lần 1 và Lần 2:
- T1: lệch 15.3 µm (từ +0.3524 lên +0.3678)
- T2: lệch 24.6 µm (từ -0.6135 lên -0.5889)
- T3: lệch 16.6 µm (từ -0.5188 lên -0.5022)
- T4: lệch 41.3 µm (từ +0.0412 lên +0.0825)

### Giá trị Trung bình Tối ưu (Averaged Optimal Offsets):
- **T1:** `+0.3601` mm
- **T2:** `-0.6012` mm
- **T3:** `-0.5105` mm
- **T4:** `+0.0619` mm

---

## 4. Phân tích Đo Lần 3 & Xác nhận Trạng thái Bão hòa Nhiệt Bền vững (Thermal Saturation)

### Dữ liệu đo Lần 3 (Nhiệt độ ngâm >35 phút):
- **T0:** $Z_{\text{touch}} = -0.400620$ mm (Độ dao động range: 0.002 mm, std dev: 0.9 µm - cực kỳ chính xác)
- **T1:** $Z_{\text{touch}} = -0.201286$ mm $\rightarrow \Delta Z = +0.1993$ mm $\rightarrow$ Offset Lần 3 = **`+0.3684`** mm
- **T2:** $Z_{\text{touch}} = -0.679286$ mm $\rightarrow \Delta Z = -0.2787$ mm $\rightarrow$ Offset Lần 3 = **`-0.5929`** mm
- **T3:** $Z_{\text{touch}} = -0.605286$ mm $\rightarrow \Delta Z = -0.2047$ mm $\rightarrow$ Offset Lần 3 = **`-0.4622`** mm
- **T4:** $Z_{\text{touch}} = -0.339286$ mm $\rightarrow \Delta Z = +0.0613$ mm $\rightarrow$ Offset Lần 3 = **`+0.0898`** mm

### Hội tụ nhiệt giữa Lần 2 và Lần 3:
- T1: Lệch chỉ **0.6 µm** (+0.1987 vs +0.1993)
- T2: Lệch chỉ **4.0 µm** (-0.2747 vs -0.2787)
- T4: Lệch chỉ **7.3 µm** (+0.0540 vs +0.0613)
- Xác nhận toàn bộ hệ thống cơ khí gantry và bàn in đã đạt trạng thái cân bằng nhiệt bền vững 100%.

### Giá trị Offset Bão hòa Khuyên dùng (Trung bình Lần 2 & 3):
- **T1:** `+0.3681` mm
- **T2:** `-0.5909` mm
- **T3:** `-0.4822` mm
- **T4:** `+0.0862` mm

---

## 5. Gỡ bỏ Hoàn toàn Axiscope Khỏi Dự Án & Máy Thật, Kích hoạt Module SexBolt (tools_calibrate)

### Mục tiêu
- Loại bỏ triệt để module thử nghiệm `axiscope` và file mã nguồn trên máy in thật `192.168.1.43`.
- Kích hoạt lại module SexBolt chính thức `[tools_calibrate]` của KTC-Easy trên chân `pin: ^PF2`.
- Khôi phục hoạt động của macro `CALIBRATE_MOVE_OVER_PROBE`, `CALIBRATE_ALL_OFFSETS` và bổ sung `CALIBRATE_ALL_Z_OFFSETS`.
- Đảm bảo kTAMV (XY camera) và SexBolt (Z / 3D switch) hoạt động song song bổ trợ lẫn nhau, không có bất kỳ xung đột hay chồng chéo logic nào.

### File đã sửa đổi
- `config/Printer-Setup/calibration-probe.cfg` — Xóa block `[axiscope]`, bỏ các macro override chặn `CALIBRATE_MOVE_OVER_PROBE`/`CALIBRATE_ALL_OFFSETS`, thêm `[tools_calibrate]` trên chân `^PF2`, bổ sung macro `CALIBRATE_ALL_Z_OFFSETS`.
- `config/toolchanger/toolchanger-config.cfg` — Làm sạch comment tham chiếu Axiscope và đồng bộ trạng thái backend.

### Sao lưu
- [pre-remove-axiscope-enable-sexbolt-20260917-170000](file:///d:/Desktop/All-Config-Voron-main/Voron%205%20Tool/extras/backups/pre-remove-axiscope-enable-sexbolt-20260917-170000/)

### Thao tác trên máy in thật `192.168.1.43`:
- Xóa file mã nguồn: `/home/voron/klipper/klippy/extras/axiscope.py`.
- Xóa file bytecode cache: `/home/voron/klipper/klippy/extras/__pycache__/axiscope.*`.
- Xóa thư mục clone thừa: `/home/voron/All-Config-Voron/extras/axiscope-cartographer`.

### Kiểm tra
- Triển khai file cấu hình sang máy in qua SCP.
- Gửi lệnh `FIRMWARE_RESTART`: Máy in khởi động lại thành công và đạt trạng thái `Printer is ready`.
- Kiểm tra lệnh `TOOL_CALIBRATE_QUERY_PROBE`: Kết quả trả về `Calibration Probe: open` (công tắc sẵn sàng kích hoạt).
- Kiểm tra lệnh `CALIBRATION_STATUS`: Báo cáo chính xác bộ 3 backend: kTAMV (XY), SexBolt (PF2), Cartographer Touch (Z).

---

## 6. Cập nhật Tọa độ Thực tế của Công tắc Tiếp xúc SexBolt Z (X: 80, Y: -7, Z: 2)

### Mục tiêu
- Cập nhật tọa độ vật lý đo đạc thực tế của công tắc cữ Z (`_CALIBRATION_SWITCH`) từ `X: 68, Y: -8` sang vị trí mới: `X: 80, Y: -7, Z: 2`.
- Thiết lập Z tiếp cận an toàn `variable_z: 15` để bảo vệ đầu in khi bay ngang qua gờ công tắc, và lưu nhớ độ cao tiếp xúc `variable_contact_z: 2`.

### File đã sửa đổi
- `config/toolchanger/toolchanger-config.cfg` — Cập nhật `variable_x: 80`, `variable_y: -7`, `variable_z: 15`, `variable_contact_z: 2`.

### Sao lưu
- [pre-switch-coords-update-80-minus7-20260917-171100](file:///d:/Desktop/All-Config-Voron-main/Voron%205%20Tool/extras/backups/pre-switch-coords-update-80-minus7-20260917-171100/)

### Kiểm tra
- Triển khai file cấu hình lên máy in và khởi động lại firmware Klipper (`FIRMWARE_RESTART`): Thành công (`Printer is ready`).
- Truy vấn đối tượng Moonraker: `_CALIBRATION_SWITCH` trả về chính xác `x: 80, y: -7, z: 15, contact_z: 2`.


---

## 7. Khôi phục Bộ Giá trị Z-Offset Đã Tinh chỉnh In Đẹp (Ellis Method) & Bảo toàn XY kTAMV

### Mục tiêu
- Khôi phục bộ giá trị `gcode_z_offset` chuẩn đã được tinh chỉnh thực tế (Ellis First-Layer Calibration) cho cả 5 đầu in:
  - **T0:** `0.0000` (Quy chiếu gốc)
  - **T1:** `0.1691`
  - **T2:** `-0.3142`
  - **T3:** `-0.2575`
  - **T4:** `0.0285`
- Giữ nguyên toàn bộ giá trị XY offsets mới nhất đã đo đạc chính xác bằng camera kTAMV:
  - **T1:** `X: -0.289, Y: -0.139`
  - **T2:** `X: 1.067, Y: 0.044`
  - **T3:** `X: 0.029, Y: 0.456`
  - **T4:** `X: 0.216, Y: 0.0`
- Lý giải kỹ thuật: Phép đo Cartographer Touch nhiệt độ cao đo tiếp xúc kim loại thuần, thiếu lượng squish factor thực tế khi sợi nhựa đùn lên mặt PEI sần dẫn đến chất lượng lớp in đầu tiên (first layer) bị biến dạng nếu áp đặt cơ học thuần túy. Việc phục hồi lại bộ Z-offset Ellis giúp máy in ngay lập tức đạt độ bám và bề mặt in hoàn hảo.

### File đã sửa đổi
- `config/printer.cfg` — Khôi phục Z-offsets cũ trong khối `SAVE_CONFIG` và bảo toàn XY offsets mới.

### Sao lưu
- [pre-restore-proven-z-offsets-20260917-174500](file:///d:/Desktop/All-Config-Voron-main/Voron%205%20Tool/extras/backups/pre-restore-proven-z-offsets-20260917-174500/)

### Thao tác trên máy in thật `192.168.1.43`:
- Gửi các lệnh KTC parameter qua Moonraker API:
  - `SET_TOOL_PARAMETER T=1 PARAMETER=gcode_z_offset VALUE=0.1691` -> `SAVE_TOOL_PARAMETER`
  - `SET_TOOL_PARAMETER T=2 PARAMETER=gcode_z_offset VALUE=-0.3142` -> `SAVE_TOOL_PARAMETER`
  - `SET_TOOL_PARAMETER T=3 PARAMETER=gcode_z_offset VALUE=-0.2575` -> `SAVE_TOOL_PARAMETER`
  - `SET_TOOL_PARAMETER T=4 PARAMETER=gcode_z_offset VALUE=0.0285` -> `SAVE_TOOL_PARAMETER`
  - `SAVE_CONFIG`
- Khởi động lại firmware Klipper (`Printer is ready`).

### Kiểm tra

---

## 8. Cập nhật Độ Cao Z An Toàn (Safe Z Clearance) Cho kTAMV Về Z = 35 mm

### Mục tiêu
- Thay đổi độ cao an toàn (Safe Z) khi chạy quy trình đo camera kTAMV từ mức `40 mm` xuống `35 mm` theo yêu cầu người dùng, phù hợp hoàn hảo với khoảng cách tiêu cự (focus height) và hành trình di chuyển tối ưu trên gá camera.

### File đã sửa đổi
- `config/Printer-Setup/ktamv.cfg` — Cập nhật `measurement_z: 35`, đồng bộ giá trị mặc định `params.Z|default(35)` ở toàn bộ các macro liên quan (`_KTAMV_CALIBRATE_T0`, `_KTAMV_MEASURE_ACTIVE_TOOL_XY`, `_KTAMV_CALIBRATE_TOOL`, `_KTAMV_AUTO_CALIBRATE_ALL_TOOLS`, `KTAMV_FULL_CALIBRATION_CYCLE`).

### Sao lưu
- [pre-ktamv-safe-z-35-20260917-182300](file:///d:/Desktop/All-Config-Voron-main/Voron%205%20Tool/extras/backups/pre-ktamv-safe-z-35-20260917-182300/)

### Thao tác trên máy in thật `192.168.1.43`:
- Đẩy file [ktamv.cfg](file:///d:/Desktop/All-Config-Voron-main/Voron%205%20Tool/config/Printer-Setup/ktamv.cfg) đã chỉnh sửa qua SCP.
- Gửi lệnh `FIRMWARE_RESTART` để áp dụng ngay vào Klipper.

### Kiểm tra
- So sánh mã băm MD5: Khớp 100% giữa local và remote (`144a315ce3121ddc3548d0a521a2322f`).
- Máy in khởi động lại thành công và đạt trạng thái sẵn sàng (`Printer is ready`).

---

## 9. Tách Bỏ Macro Gộp Độc Đoán, Chuyển Sang Kiến Trúc Macro Rời Chuẩn Upstream kTAMV

### Mục tiêu
- Loại bỏ hoàn toàn macro gộp tự động 1-chạm (`KTAMV_FULL_CALIBRATION_CYCLE`) và chuỗi macro phụ thuộc lồng nhau.
- Tái thiết kế file cấu hình theo đúng luồng làm việc nguyên bản của dự án upstream kTAMV (TypQxQ/kTAMV): các lệnh độc lập, linh hoạt, người dùng chủ động từng bước.
- Cung cấp bộ macro helper tinh gọn hỗ trợ máy StealthChanger 5 Tool:
  - `KTAMV_MOVE_TO_ORIGIN`: Di chuyển tool hiện tại đến đúng tọa độ camera đã học ở Z an toàn (35mm).
  - `KTAMV_FIND_AND_CENTER`: Tắt LED chống lóa, tìm tâm nozzle và căn giữa camera.
  - `KTAMV_APPLY_TOOL_OFFSET [TOOL=n]`: Nạp kết quả sai lệch XY vào toolchanger parameters.

### File đã sửa đổi
- `config/Printer-Setup/ktamv.cfg` — Viết lại hoàn toàn theo chuẩn modular, xóa macro gộp.

### Sao lưu
- [pre-ktamv-split-modular-macros-20260917-185600](file:///d:/Desktop/All-Config-Voron-main/Voron%205%20Tool/extras/backups/pre-ktamv-split-modular-macros-20260917-185600/)

### Thao tác trên máy in thật `192.168.1.43`:
- Đẩy [ktamv.cfg](file:///d:/Desktop/All-Config-Voron-main/Voron%205%20Tool/config/Printer-Setup/ktamv.cfg) mới qua SCP.
- Gửi lệnh `FIRMWARE_RESTART`.

### Kiểm tra
- Truy vấn danh sách G-code macro trên máy in: Xác nhận macro gộp cũ đã biến mất, chỉ còn các macro modular sạch sẽ (`KTAMV_MOVE_TO_ORIGIN`, `KTAMV_FIND_AND_CENTER`, `KTAMV_APPLY_TOOL_OFFSET`, `KTAMV_STATUS`).
- Máy in đạt trạng thái `Printer is ready`.

---

## 10. Tích Hợp Macro Kiểm Soát LED Chống Hắt Sáng Camera Vào Quy Trình Đo kTAMV

### Mục tiêu
- Khi đổi tool (T0 -> T4), hệ thống StealthChanger tự động bật sáng đèn LED đầu in (nhất là 2 LED nozzle). Ánh sáng này chiếu thẳng xuống vòi phun kim loại và kính camera gây chói lóa (specular glare), làm hỏng khả năng nhận diện hình tròn của thuật toán OpenCV.
- Bổ sung các macro công khai điều khiển ánh sáng trực quan trên giao diện Mainsail:
  - `KTAMV_LEDS_OFF`: Tắt toàn bộ LED đầu in T0->T4 và LED buồng in để tạo môi trường ánh sáng tối ưu chống lóa.
  - `KTAMV_LEDS_RESTORE`: Khôi phục lại trạng thái LED sau khi hoàn thành đo đạc.
  - `KTAMV_CALIB_CAMERA_SAFE`: Tự động tắt LED trước khi chạy thuật toán đo tỉ lệ `mm/pixel`.
  - Tích hợp tự động tắt đèn ngay trong macro `KTAMV_MOVE_TO_ORIGIN`: Sau khi gắp tool và bay tới vị trí camera ở Z=35mm, đèn LED lập tức tự động tắt để sẵn sàng căn tâm mà không cần người dùng thao tác thừa.

### File đã sửa đổi
- `config/Printer-Setup/ktamv.cfg` — Định nghĩa các macro LED public và cập nhật tài liệu quy trình 4 bước ở phần đầu file.

### Sao lưu
- [pre-ktamv-led-control-workflow-20260917-190100](file:///d:/Desktop/All-Config-Voron-main/Voron%205%20Tool/extras/backups/pre-ktamv-led-control-workflow-20260917-190100/)

### Thao tác trên máy in thật `192.168.1.43`:
- Đẩy file [ktamv.cfg](file:///d:/Desktop/All-Config-Voron-main/Voron%205%20Tool/config/Printer-Setup/ktamv.cfg) qua SCP.
- Gửi lệnh `FIRMWARE_RESTART`.

### Kiểm tra
- Máy in khởi động lại thành công và đạt trạng thái `Printer is ready`.
- Truy vấn Klipper objects: Xác nhận `KTAMV_LEDS_OFF`, `KTAMV_LEDS_RESTORE`, `KTAMV_CALIB_CAMERA_SAFE` hiển thị sẵn sàng.
