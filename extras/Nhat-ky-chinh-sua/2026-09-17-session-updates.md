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
