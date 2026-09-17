# Backup trước khi Khôi phục lại Z-Offset Cũ Tinh chỉnh First-Layer

**Thời gian:** 2026-09-17 17:45:00
**Mục đích:**
- Khôi phục lại toàn bộ giá trị `gcode_z_offset` cũ đã được cân chỉnh chuẩn theo phương pháp Ellis First-Layer:
  + T0: 0.0000
  + T1: 0.1691
  + T2: -0.3142
  + T3: -0.2575
  + T4: 0.0285
- Lý do: Giá trị Z-offset đo tiếp xúc cơ học thuần của Cartographer Touch thiếu hệ số bù nén nhựa thực tế (squish factor) trên bàn in PEI sần, dẫn đến lớp in đầu tiên khi in thực tế không đẹp bằng giá trị đã tinh chỉnh.

**Danh sách file:**
- `printer.cfg.local`
- `printer.cfg.live`
