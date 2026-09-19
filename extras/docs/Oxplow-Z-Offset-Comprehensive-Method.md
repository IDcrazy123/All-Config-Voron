# BÁO CÁO TỔNG HỢP: PHƯƠNG PHÁP HIỆU CHUẨN Z-OFFSET DỐC NGHIÊNG OXPLOW
## (OXPLOW GRADIENT RAMP NOZZLE Z-OFFSET CALIBRATION METHOD)

---

## 1. Bối cảnh & Vấn đề của các phương pháp truyền thống

Trong in 3D FDM (đặc biệt là hệ thống đa đầu in Toolchanger như StealthChanger, Voron, IDEX, Prusa XL), việc xác định chính xác **Z-offset** của từng đầu phun là yếu tố quyết định độ bám dính của lớp đầu tiên (first layer squish) và chất lượng toàn bộ bản in.

### Nhược điểm của các phương pháp cũ:
1. **Cữ switch tiếp xúc cơ học (Sexbolt / Microswitch / Cartographer Touch):**
   - Chỉ đo chiều dài cơ học ở trạng thái tĩnh và nhiệt độ thấp (150°C).
   - Khi in thực tế ở 230–260°C với áp lực đùn nhựa nóng lên bề mặt bàn PEI vân, độ giãn nở nhiệt của hotend, độ lún của bàn in và độ nén nở của nhựa nóng làm cho Z-offset thực tế bị sai lệch từ $0.03 \rightarrow 0.10\text{ mm}$.
2. **Phương pháp Ellis First Layer Patch (in ô vuông phẳng cố định):**
   - Phải in từng ô vuông phẳng riêng biệt, mỗi ô thử một Z-offset khác nhau.
   - Tốn nhiều thời gian (10–15 phút mỗi lần thử), tốn nhựa.
   - Mang tính cảm tính cao: người dùng phải dùng móng tay cào hoặc soi kính lúp để phỏng đoán xem ô nào "mịn hơn".

---

## 2. Nguyên lý hoạt động của phương pháp Oxplow

Phương pháp **Oxplow** (dựa trên ý tưởng tiên phong của Maxim7745 và được tối ưu hóa cho hệ thống tự động) thay thế hoàn toàn các ô vuông phẳng bằng **một con dốc nghiêng liên tục (Continuous Gradient Ramp)** in chỉ trong **chưa đầy 1 phút**:

```text
               MẶT CẮT NGHIÊNG CỦA BẢN IN TEST (Nhìn từ cạnh bên)

  Độ cao Z (mm)
      ^
0.350 |                                            / (Mép sau: Y = 20mm) -> Quá cao (hở sợi)
      |                                          /
      |                                        /
0.250 | ----------------- [ VẠCH TÂM ] ------ / (Chính giữa: Y = 10mm) -> Vị trí chuẩn lý tưởng
      |                                     /
      |                                   /
0.150 | (Mép trước: Y = 0mm) ------------/  -> Quá sát bàn (cày rãnh / nén bẹp)
      +----------------------------------------------------> Chiều dài Y (mm)
      0mm               5mm              10mm              15mm              20mm
```

### Thông số hình học bản in:
* **Kích thước dải test:** Hình vuông $20.0 \times 20.0\text{ mm}$ (gồm 51 đường in song song, mỗi bước dịch trục Y là $0.40\text{ mm}$).
* **Độ cao Z biến thiên liên tục:**
  * Tại mép trước ($Y = 0.0\text{ mm}$): $Z = 0.150\text{ mm}$ (vòi phun đè rất sát bàn $\implies$ cày rãnh, sần sùi).
  * Tại vạch tâm chính giữa ($Y = 10.0\text{ mm}$): $Z = 0.250\text{ mm}$ (**Độ cao danh nghĩa chuẩn**, có vạch chia kép dài nhô ra 2 bên).
  * Tại mép sau ($Y = 20.0\text{ mm}$): $Z = 0.350\text{ mm}$ (vòi phun cách xa bàn $\implies$ không đủ nén, sợi nhựa tách rời).
* **Dải quét Z:** $0.200\text{ mm}$ (tương ứng $\pm 0.100\text{ mm}$ xung quanh độ cao chuẩn $0.250\text{ mm}$).
* **Tỷ lệ biến thiên tuyến tính:**
  $$\mathbf{\text{Tỷ lệ dốc}} = \frac{0.200\text{ mm Z}}{20.0\text{ mm Y}} = \mathbf{0.010\text{ mm Z / mm Y}} \quad (10\text{ \mu m}\text{ cho mỗi 1mm chiều dài Y})$$
  *(Hoặc mỗi 1 đường hatch $0.4\text{ mm}$ tương đương độ cao Z nhích lên đúng $0.004\text{ mm} = 4\text{ \mu m}$)*.

---

## 3. Quy trình đọc kết quả & Công thức tính toán Z-Offset

Sau khi in xong dải test, quan sát dưới ánh sáng nghiêng:
1. **Vùng dưới ($Y < 10\text{ mm}$):** Bề mặt có gờ nhựa nổi lên, cày rãnh do vòi phun ép quá sát bàn.
2. **VÙNG ĐẸP NHẤT:** Bề mặt phẳng lì như gương, các đường in hòa quyện liền mạch, không có khe hở và không có gờ nhám.
3. **Vùng trên ($Y > 10\text{ mm}$):** Các sợi nhựa tròn riêng biệt, nhìn thấy rõ các khe hở li ti giữa các đường in do vòi phun quá cao.

Dùng thước kẹp hoặc thước kẻ đo khoảng cách từ **mép trước** đến **tâm vùng in phẳng đẹp nhất** ($Y_{\text{đo}}$):

```text
       Mép trước (0mm)                 TÂM (10mm)                 Mép sau (20mm)
             |------------------------------|----------------------------|
             <------ VÙNG TRỪ BỚT Z -------> <------ VÙNG CỘNG THÊM Z --->
             (Đầu in đang bị QUÁ CAO)        (Đầu in đang bị QUÁ THẤP)
             Cần HẠ đầu in xuống (-)         Cần NÂNG đầu in lên (+)
```

### Công thức tổng quát:
$$\Delta Z = \mathbf{(Y_{\text{đo}} - 10.0\text{ mm}) \times 0.010\text{ mm/mm}}$$
$$Z_{\text{offset\_mới}} = Z_{\text{offset\_hiện\_tại}} + \Delta Z$$

* **Nếu $Y_{\text{đo}} > 10.0\text{ mm}$ (Vùng đẹp nằm sau tâm):**
  * Đầu in đang ở quá sát bàn, phải leo dốc cao mới đẹp.
  * $\implies$ **CỘNG THÊM (+)** $\Delta Z$ vào Z-offset để nâng đầu in lên.
* **Nếu $Y_{\text{đo}} < 10.0\text{ mm}$ (Vùng đẹp nằm trước tâm):**
  * Đầu in đang ở quá cao xa bàn, phải tụt dốc thấp mới bám dính.
  * $\implies$ **TRỪ BỚT (-)** $\Delta Z$ vào Z-offset để hạ đầu in xuống.
* **Nếu $Y_{\text{đo}} = 10.0\text{ mm}$ (Vùng đẹp nằm ngay vạch tâm):**
  * $\Delta Z = 0.000\text{ mm} \implies$ **Z-offset đã đạt độ chính xác tuyệt đối!**

---

## 4. Bảng tra cứu trực tiếp bằng thước đo (Không cần tính toán)

| Vị trí đo được từ mép trước | Độ lệch so với tâm | Hành động Z-offset | Giá trị điều chỉnh ($\Delta Z$) |
| :---: | :---: | :---: | :---: |
| **0.0 mm** (Mép trước) | $-10.0\text{ mm}$ | **TRỪ BỚT (-)** | **$-0.100\text{ mm}$** |
| **2.0 mm** | $-8.0\text{ mm}$ | **TRỪ BỚT (-)** | **$-0.080\text{ mm}$** |
| **4.0 mm** | $-6.0\text{ mm}$ | **TRỪ BỚT (-)** | **$-0.060\text{ mm}$** |
| **6.0 mm** | $-4.0\text{ mm}$ | **TRỪ BỚT (-)** | **$-0.040\text{ mm}$** |
| **8.0 mm** | $-2.0\text{ mm}$ | **TRỪ BỚT (-)** | **$-0.020\text{ mm}$** |
| **9.0 mm** | $-1.0\text{ mm}$ | **TRỪ BỚT (-)** | **$-0.010\text{ mm}$** |
| **10.0 mm (Vạch tâm chuẩn)** | **$0.0\text{ mm}$** | **CHUẨN TUYỆT ĐỐI** | **$0.000\text{ mm}$ (Giữ nguyên)** |
| **11.0 mm** | $+1.0\text{ mm}$ | **CỘNG THÊM (+)** | **$+0.010\text{ mm}$** |
| **12.0 mm** | $+2.0\text{ mm}$ | **CỘNG THÊM (+)** | **$+0.020\text{ mm}$** |
| **13.5 mm** | $+3.5\text{ mm}$ | **CỘNG THÊM (+)** | **$+0.035\text{ mm}$** |
| **15.0 mm** | $+5.0\text{ mm}$ | **CỘNG THÊM (+)** | **$+0.050\text{ mm}$** |
| **16.0 mm** | $+6.0\text{ mm}$ | **CỘNG THÊM (+)** | **$+0.060\text{ mm}$** |
| **18.0 mm** | $+8.0\text{ mm}$ | **CỘNG THÊM (+)** | **$+0.080\text{ mm}$** |
| **20.0 mm** (Mép sau) | $+10.0\text{ mm}$ | **CỘNG THÊM (+)** | **$+0.100\text{ mm}$** |

---

## 5. Minh chứng kết quả thực tế trên máy Voron 2.4 StealthChanger 5-Tool

Quá trình hiệu chỉnh thực tế trên máy in:
1. **Toolhead T1 (2 lần tinh chỉnh):**
   * *Lần 1:* Ban đầu $Z_{\text{offset}} = 0.1315\text{ mm}$. Đo được vùng đẹp ở $18.0\text{ mm}$ ($\Delta Y = +8.0\text{ mm} \implies \Delta Z = +0.080\text{ mm}$). Nâng lên $0.1315 + 0.080 = 0.2115\text{ mm}$.
   * *Lần 2:* Đo được vùng đẹp dịch chuyển về $12 \rightarrow 15\text{ mm}$ (tâm $13.5\text{ mm} \implies \Delta Z = +0.035\text{ mm}$). Nâng lên $0.2115 + 0.035 = \mathbf{0.2465\text{ mm}}$. Điểm đẹp rơi trúng vạch tâm.
2. **Toolhead T2:**
   * Ban đầu $Z_{\text{offset}} = -0.3215\text{ mm}$. Đo được vùng đẹp ở $14 \rightarrow 16\text{ mm}$ (tâm $15.0\text{ mm} \implies \Delta Z = +0.050\text{ mm}$).
   * Nâng lên: $-0.3215 + 0.0500 = \mathbf{-0.2715\text{ mm}}$.
3. **Toolhead T3:**
   * Ban đầu $Z_{\text{offset}} = -0.2365\text{ mm}$. Đo được vùng đẹp ở $8 \rightarrow 10\text{ mm}$ (tâm $9.0\text{ mm} \implies \Delta Z = -0.010\text{ mm}$).
   * Hạ xuống: $-0.2365 + (-0.0100) = \mathbf{-0.2465\text{ mm}}$.
4. **Toolhead T4:**
   * Ban đầu $Z_{\text{offset}} = 0.0579\text{ mm}$. Đo được vùng đẹp ở $14 \rightarrow 16\text{ mm}$ (tâm $15.0\text{ mm} \implies \Delta Z = +0.050\text{ mm}$).
   * Nâng lên: $0.0579 + 0.0500 = \mathbf{0.1079\text{ mm}}$.

---

## 6. Công cụ phát sinh G-Code vạn năng (`generate_oxplow_gcode.py`)

Đi kèm phương pháp là bộ công cụ script mã nguồn mở hoàn chỉnh:
* **Hỗ trợ mọi loại máy:** Tích hợp sẵn preset cho Voron StealthChanger (300/350mm), Voron Single-Tool, Ender 3, Prusa MK3/MK4, Prusa XL (5 Tools), Bambu Lab X1/P1/A1.
* **Font vector nét vẽ:** In trực tiếp nhãn nhận diện tool (`T0`, `T1`, `T2`,...) dưới chân thanh test.
* **Tự thích ứng kích thước đầu phun (0.2, 0.4, 0.6, 0.8mm):** Tự động tính lại thể tích đùn và bước nhảy dốc.
* **Chuỗi gia nhiệt an toàn chống lỗi toolchange:** Tự động nung sớm trong dock, chờ đủ nhiệt trước khi đùn nhựa, hạ về nhiệt độ chờ standby sau khi in xong.
