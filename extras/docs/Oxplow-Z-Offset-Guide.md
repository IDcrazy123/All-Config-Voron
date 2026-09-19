# Hướng Dẫn Hiệu Chuẩn Z-Offset Đa Đầu In Bằng Phương Pháp Oxplow (Voron 5-Tool)

## 1. Giới thiệu Phương pháp Oxplow Nozzle Z-Offset Search

Phương pháp **Oxplow** (dựa trên thiết kế của Maxim7745) giải quyết triệt để nhược điểm của các phương pháp cũ:
- **So với đo cữ switch cơ học / Cartographer:** Cữ switch chỉ đo chiều dài kim loại nguội/ấm ở 150°C trong trạng thái tĩnh. Khi in thực tế ở 240–260°C, áp lực đùn nhựa nóng lên bàn in PEI vân tạo ra độ nén (squish) và độ giãn nở nhiệt khác biệt giữa các đầu in.
- **So với phương pháp Ellis First Layer Patch:** Ellis in các ô vuông Z cố định, mất nhiều thời gian, tốn nhựa và đòi hỏi cảm tính khi sờ tay hoặc dùng kính lúp.
- **Ưu điểm vượt trội của Oxplow:** In một dải các đường hatch song song với **chiều cao Z dốc đều (gradient ramp)** từ $0.150\text{ mm} \rightarrow 0.350\text{ mm}$ (bước nhảy siêu mịn chỉ $0.004\text{ mm}$ mỗi vạch). Bằng mắt thường, bạn có thể nhìn thấy ngay ranh giới chuyển tiếp từ vùng "quá đè/cày rãnh" sang "phẳng lỳ hoàn hảo" rồi sang "hở sợi", từ đó xác định chính xác $Z$-offset cơ học tối ưu chỉ trong **chưa đầy 1 phút** cho mỗi đầu in.

---

## 2. Bố cục 5 Thanh Test Trên Bàn In (File `Oxplow_5Tool_Z_Test_PETG.gcode`)

Trên bàn in $350 \times 350\text{ mm}$, 5 thanh in được dàn đều tại vùng trung tâm ($Y = 150 \rightarrow 170\text{ mm}$):

```
 Y=170 mm  [ +0.10 mm ] ---------------------------------------------------- (Z = 0.350 mm - Non/Hở sợi)
           [ +0.05 mm ] ----------------------------------------------------
 Y=160 mm  [  0.00 mm ] ==================================================== (Z = 0.250 mm - TÂM CHUẨN)
           [ -0.05 mm ] ----------------------------------------------------
 Y=150 mm  [ -0.10 mm ] ---------------------------------------------------- (Z = 0.150 mm - Cày rãnh/Đè)
               |
             Prime                [VẠCH ZIG-ZAG DỐC Z]              Vạch đối xứng
             Line                   (Ramp Patch 20x20mm)               (Tâm chuẩn)
               |
            [T0 / T1 / T2 / T3 / T4]  <- Nhãn số Tool in ở chân thanh
```

Mỗi thanh in bao gồm:
1. **Nhãn nhận diện Tool:** Chữ số `T0`, `T1`, `T2`, `T3`, `T4` in ở chân thanh ($Y = 143 \rightarrow 148\text{ mm}$) để phân biệt rõ ràng.
2. **Đường Prime xả nhựa:** Nằm song song ở mép trái ($X - 8\text{ mm}$) giúp đầu phun ổn định áp suất trước khi in.
3. **Thước đo vạch chia (Tick Marks):** Nằm ở mép trái ($X - 2\text{ mm}$):
   - Vạch tại $Y = 150\text{ mm}$: Ứng với sai số $\Delta Z = -0.10\text{ mm}$ ($Z = 0.150\text{ mm}$)
   - Vạch tại $Y = 155\text{ mm}$: Ứng với sai số $\Delta Z = -0.05\text{ mm}$ ($Z = 0.200\text{ mm}$)
   - **Vạch kép dài tại $Y = 160\text{ mm}$:** Ứng với $\Delta Z = 0.00\text{ mm}$ (**TÂM CHUẨN** danh nghĩa $Z = 0.250\text{ mm}$)
   - Vạch tại $Y = 165\text{ mm}$: Ứng với sai số $\Delta Z = +0.05\text{ mm}$ ($Z = 0.300\text{ mm}$)
   - Vạch tại $Y = 170\text{ mm}$: Ứng với sai số $\Delta Z = +0.10\text{ mm}$ ($Z = 0.350\text{ mm}$)

---

## 3. Cách Đọc Kết Quả Bằng Mắt Thường

Sau khi in xong (hoặc quan sát ngay khi in):
1. Nhìn nghiêng dưới ánh sáng đèn buồng in vào dải zig-zag của từng Tool:
   - **Vùng dưới ($Y < 160\text{ mm}$, $Z < 0.25\text{ mm}$):** Nhựa bị đè dẹt quá mức, bề mặt sần sùi, xuất hiện các rãnh cày do nozzle gạt vào nhựa (plowing / rough ridges).
   - **VÙNG ĐẸP NHẤT:** Bề mặt phẳng lỳ, bóng mịn, các đường nhựa tiếp giáp khít rịt thành một mảng đồng nhất, không có gờ nhô lên và không có khe hở.
   - **Vùng trên ($Y > 160\text{ mm}$, $Z > 0.25\text{ mm}$):** Các sợi nhựa tròn dần, không bị ép đủ dẹt, nhìn thấy rõ các khe hở li ti giữa các đường (under-squish / gaps).
2. Tìm **vị trí của đường in đẹp nhất** so với vạch tâm chuẩn $Y = 160\text{ mm}$ (vạch kép có vạch đối xứng ở cả 2 bên):

| Vị trí vệt in đẹp nhất | Khoảng cách so với vạch tâm ($Y=160$) | Độ lệch $\Delta Z_{error}$ | Nhận định trạng thái đầu in | Hướng điều chỉnh Z-offset |
| :---: | :---: | :---: | :---: | :---: |
| **Tại mép dưới cùng** | $-10.0\text{ mm}$ (tại vạch $-0.10$) | **$-0.10\text{ mm}$** | Đầu in thực tế đang ở **quá cao** $0.10\text{ mm}$ | **Hạ đầu in xuống** $-0.10\text{ mm}$ |
| **Giữa mép dưới và tâm** | $-5.0\text{ mm}$ (tại vạch $-0.05$) | **$-0.05\text{ mm}$** | Đầu in thực tế đang ở **quá cao** $0.05\text{ mm}$ | **Hạ đầu in xuống** $-0.05\text{ mm}$ |
| **Đúng vạch tâm chuẩn** | **$0.0\text{ mm}$ (tại vạch tâm $0.00$)** | **$0.00\text{ mm}$** | **Z-OFFSET HOÀN HẢO!** | **Giữ nguyên!** |
| **Giữa tâm và mép trên** | $+5.0\text{ mm}$ (tại vạch $+0.05$) | **$+0.05\text{ mm}$** | Đầu in thực tế đang ở **quá sát bàn** $0.05\text{ mm}$ | **Nâng đầu in lên** $+0.05\text{ mm}$ |
| **Tại mép trên cùng** | $+10.0\text{ mm}$ (tại vạch $+0.10$) | **$+0.10\text{ mm}$** | Đầu in thực tế đang ở **quá sát bàn** $0.10\text{ mm}$ | **Nâng đầu in lên** $+0.10\text{ mm}$ |

> **Quy tắc đếm đường siêu mịn:**
> Mỗi đường hatch cách nhau $0.40\text{ mm}$, tương ứng với bước nhảy đúng **$0.004\text{ mm}$ ($4\text{ \mu m}$)** Z-height.
> - Lệch 2 đường so với tâm: $\Delta Z = \pm 0.008\text{ mm}$
> - Lệch 5 đường so với tâm: $\Delta Z = \pm 0.020\text{ mm}$
> - Lệch 10 đường so với tâm: $\Delta Z = \pm 0.040\text{ mm}$

---

## 4. Công Thức Cập Nhật Vào Klipper (`printer.cfg`)

### A. Đối với Tool 0 (T0 — Reference Tool):
T0 là đầu in tham chiếu Z Homing chạm bàn bằng Cartographer Touch:
- Nếu T0 bị lệch $\Delta Z_{error}$:
  - Bạn có thể điều chỉnh trực tiếp `z_offset` của `[cartographer touch_model default]` trong khối `SAVE_CONFIG` của `printer.cfg`:
    $$Z_{touch\_new} = Z_{touch\_current} - \Delta Z_{error}$$
  *(Lưu ý: Với Cartographer touch, số âm hơn nghĩa là đầu phun chạm sâu hơn/sát bàn hơn).*

### B. Đối với các Tool T1, T2, T3, T4:
Các đầu in T1–T4 được định nghĩa bằng tham số `gcode_z_offset` trong `[tool T1]` đến `[tool T4]` ở khối `SAVE_CONFIG` cuối file `printer.cfg`.

Quy ước của Klipper Toolchanger:
- Giá trị `gcode_z_offset` biểu thị khoảng cách tương đối của tool đó so với T0.
- **Công thức cập nhật:**
  $$Z_{offset\_new} = Z_{offset\_current} - \Delta Z_{error}$$
  *Trong đó:* $\Delta Z_{error} = Z_{best} - 0.250\text{ mm}$.

**Ví dụ thực tế:**
- Giả sử **T1** hiện tại có `gcode_z_offset = 0.1315`.
- Khi in thanh Oxplow của T1, vạch đẹp nhất nằm ở $Y = 156\text{ mm}$ (cách tâm $-4\text{ mm}$, tương ứng với $Z_{best} = 0.210\text{ mm} \rightarrow \Delta Z_{error} = -0.040\text{ mm}$).
- Nghĩa là nozzle T1 đang bị cao hơn $0.04\text{ mm}$. Cần hạ T1 xuống thêm $0.04\text{ mm}$.
- Giá trị mới cần nhập:
  $$Z_{offset\_new} = 0.1315 - (-0.040) = 0.1715\text{ mm}$$

---

## 5. Danh Sách File In Đã Nạp Sẵn Trên Máy In (`192.168.1.43`)

Các file sau đã được tạo và đẩy trực tiếp lên Moonraker của máy in, bạn chỉ cần mở Mainsail và bấm **Print**:

1. **`Oxplow_5Tool_Z_Test_PETG.gcode`** (Khuyên dùng):
   - In trọn bộ 5 đầu in T0 $\rightarrow$ T4 trong một lần in duy nhất (~3.5 phút).
   - Nhiệt độ: Bed 75°C, Nozzle 240°C.
2. **`Oxplow_5Tool_Z_Test_ABS.gcode`**:
   - In trọn bộ 5 đầu in cho nhựa ABS (Bed 100°C, Nozzle 245°C).
3. **Các file test riêng lẻ từng Tool (`Oxplow_T1_Z_Test_PETG.gcode`, `T2...`, `T3...`, `T4...`)**:
   - Dùng khi bạn chỉ muốn in kiểm tra lại đúng 1 đầu in vừa điều chỉnh mà không cần chạy lại cả 5 đầu.
