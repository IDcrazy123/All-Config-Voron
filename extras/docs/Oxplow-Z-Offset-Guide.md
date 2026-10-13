# Oxplow 2.3.2 — hướng dẫn cho Voron

Bộ hiện hành nằm ở [Printables-Package](../Printables-Package/README.md), nguồn
[Printables của Công Dương](https://www.printables.com/model/1846885-universal-oxplow-first-layer-z-offset-calibration).
Ý tưởng Oxplow của Maxim7745; hướng dẫn upstream tiếng Việt nằm trong
[README của toolkit](../Printables-Package/upstream-2.3.2/README.md).

1. Dùng profile PETG từng tool trước, kiểm SVG và vật liệu trên máy.
2. In file trong `Printables-Package/output/` có người giám sát.
3. Mẫu hiện tại không in chữ/vạch phụ. Trái sang phải là T0 -> T4.
4. Row 0 nằm ở Y thấp nhất/phía trước: Z0.280 mm. Z giảm dần tới
   Z0.200 mm ở row 50; row 25 là tâm danh định Z0.240.
5. Chọn vùng các đường dính đều, không khe/gờ. Dùng đúng report của file đã in:

```bash
python generate_oxplow_gcode.py calculate --report output/Voron_Oxplow_2.3.2_PETG_T0-T4.report.json --tool 2 --row 35
```

Với profile này: `Delta Z = 0.040 - 0.0016 * row`. Số dương nâng nozzle,
số âm hạ. Nếu đo bằng thước, dùng `--distance` tính từ tâm dòng Y thấp nhất;
không áp công thức cũ `(Y - 10) * 0.010`. Toolkit không tự lưu offset.
Lưu qua quy trình offset đã xác minh của máy, rồi in xác nhận `ramp_range=0`.

Sau prime, tool bắt đầu in được bù 0.6 mm, các tool đã park được bù 5 mm
đúng một lần. PRINT_END sở hữu retract/nâng Z cuối bài. Offset trong
`printer.cfg` được giữ nguyên. File lịch sử trên máy có thể mang retract cũ;
hãy chọn bộ `Oxplow-2.3.2/` mới được đồng bộ.
