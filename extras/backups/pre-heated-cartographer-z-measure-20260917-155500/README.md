# Backup trước khi Nâng cấp Đo Z Offset với Điều kiện Nhiệt độ Thực tế (Nozzle 150C, Bed 70C)

**Thời gian:** 2026-09-17 15:55:00
**Mục đích:**
- Sao lưu `calibration-probe.cfg` trước khi nâng cấp macro `MEASURE_ALL_Z_CARTOGRAPHER` hỗ trợ các điều kiện nhiệt độ thực tế:
  + Gia nhiệt bàn in `BED_TEMP=70` (chuẩn PETG).
  + Gia nhiệt đầu phun `NOZZLE_TEMP=150` (chuẩn mềm nhựa, chống cộm dơ, dãn nở nhiệt hotend và an toàn cho mặt bàn PEI/Cartographer Touch).
  + Tùy chọn ngâm nhiệt `SOAK` và chùi vòi phun qua bàn chải silicon `CLEAN=1`.
  + Tự động tắt nhiệt hoặc duy trì nhiệt sau khi hoàn tất chuỗi đo.

**Danh sách file:**
- `calibration-probe.cfg.local`
- `calibration-probe.cfg.live`
