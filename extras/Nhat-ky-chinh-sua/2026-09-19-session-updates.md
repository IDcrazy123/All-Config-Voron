# Nhật ký Cập nhật Hệ thống — 2026-09-19

**Mục tiêu chính trong phiên:**
- Đồng bộ cấu hình OrcaSlicer mới nhất từ AppData người dùng vào kho cấu hình `Voron 5 Tool/Orca Config/`.
- Phân tích và phát triển hệ thống bản in test Z-offset đa đầu in siêu tốc dựa trên nguyên lý dốc nghiêng Oxplow Gradient Ramp (thay thế phương pháp Ellis patch cảm tính và chậm).
- Tạo công cụ tự động phát sinh G-code test (`generate_oxplow_gcode.py`) cho 5 tool (T0–T4) và đẩy trực tiếp lên Moonraker máy in `192.168.1.43`.
- Soạn thảo tài liệu hướng dẫn và bảng tra cứu quy đổi Z-offset trực quan.

---

## 1. Đồng Bộ Tự Động Cấu Hình OrcaSlicer (Orca Config)

### Mục tiêu
- Sao chép các preset người dùng đang hoạt động trong AppData vào thư mục `Orca Config/` của kho lưu trữ để cập nhật profile máy in, profile in PETG/ABS và các loại sợi nhựa mới nhất.

### Nguồn
- Đường dẫn nguồn: `C:\Users\batca\AppData\Roaming\OrcaSlicer\user\838ce884-12ee-416b-9e1b-1c7503cf6b5f`

### File đã cập nhật
- `Orca Config/Voron Stealthchanger.json`
- `Orca Config/0.20mm PETG.json`
- `Orca Config/0.20mm Multicolor PetG.json`
- `Orca Config/PETG Bambu Basic Black.json`
- `Orca Config/PETG Kabber Blue.json`
- `Orca Config/PETG TPoimns Red.json`
- `Orca Config/PETG TPoimns Yellow.json`
- `extras/Orcasilcer setting/Printersetting.json`

### Sao lưu
- [pre-orcaslicer-profile-sync-20260919-160813](file:///d:/Desktop/All-Config-Voron-main/Voron%205%20Tool/extras/backups/pre-orcaslicer-profile-sync-20260919-160813/)

### Kết quả
- 8 file cấu hình JSON của OrcaSlicer đã được cập nhật chuẩn xác.

---

## 2. Phát Triển & Triển Khai Bản In Test Z-Offset Đa Đầu In Oxplow (T0–T4)

### Mục tiêu
- Khắc phục triệt để nhược điểm của việc căn chỉnh Z-offset bằng cữ switch tiếp xúc (chỉ đo chiều dài cơ học ở 150°C, không tính được độ squish và giãn nở thực tế ở nhiệt độ in 240–260°C) và phương pháp Ellis Patch (in ô vuông chậm, tốn nhựa và mang tính cảm tính cao).
- Thiết kế dải quét Z liên tục (Oxplow Ramp) từ $0.150\text{ mm} \rightarrow 0.350\text{ mm}$ (danh nghĩa $0.250\text{ mm}$) với bước nhảy $0.004\text{ mm}$ ($4\text{ \mu m}$ mỗi vạch), cho phép người dùng nhìn bằng mắt thường là phát hiện ngay vệt nén nhựa hoàn hảo và suy ra sai số Z-offset thực tế.

### File đã tạo
1. `extras/gcode/generate_oxplow_gcode.py` — Script Python tự động sinh file G-code test linh hoạt cho 1 hoặc nhiều đầu in, tùy biến vật liệu (PETG, ABS, PLA), nhiệt độ và dải quét.
2. `extras/gcode/Oxplow_5Tool_Z_Test_PETG.gcode` — Bản in test trọn bộ 5 đầu in T0 $\rightarrow$ T4 cho PETG (Bed 75°C, Nozzle 240°C, ~3.5 phút).
3. `extras/gcode/Oxplow_5Tool_Z_Test_ABS.gcode` — Bản in test trọn bộ 5 đầu in T0 $\rightarrow$ T4 cho ABS (Bed 100°C, Nozzle 245°C).
4. `extras/gcode/Oxplow_T0_Z_Test_PETG.gcode` đến `Oxplow_T4_Z_Test_PETG.gcode` — Các bản in test độc lập cho từng đầu in riêng biệt.
5. `extras/docs/Oxplow-Z-Offset-Guide.md` — Tài liệu hướng dẫn cách quan sát vệt in, ý nghĩa các vạch chia độ và công thức cập nhật `gcode_z_offset` vào Klipper `printer.cfg`.

### Sao lưu
- [pre-oxplow-multitool-generator-20260919-160930](file:///d:/Desktop/All-Config-Voron-main/Voron%205%20Tool/extras/backups/pre-oxplow-multitool-generator-20260919-160930/)

### Triển khai trên máy in thật `192.168.1.43`
- Đã đẩy thành công toàn bộ các file G-code test lên máy in qua Moonraker API `/server/files/upload`:
  - `Oxplow_5Tool_Z_Test_PETG.gcode`
  - `Oxplow_5Tool_Z_Test_ABS.gcode`
  - `Oxplow_T1_Z_Test_PETG.gcode`
  - `Oxplow_T2_Z_Test_PETG.gcode`
  - `Oxplow_T3_Z_Test_PETG.gcode`
  - `Oxplow_T4_Z_Test_PETG.gcode`
- Người dùng có thể truy cập giao diện web Mainsail và bấm **Print** ngay lập tức.
