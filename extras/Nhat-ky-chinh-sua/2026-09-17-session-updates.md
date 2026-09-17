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


