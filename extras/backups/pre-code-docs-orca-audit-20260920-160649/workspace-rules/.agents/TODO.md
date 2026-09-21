# Công việc đang chờ (TODO)

Theo dõi các công việc đang chờ, cải tiến và điều tra ở đây.
AI assistant nên kiểm tra file này khi bắt đầu mỗi phiên làm việc.

---

## Đang chờ xử lý

- [ ] **Tối ưu hóa quạt đầu in** — Xem xét biểu đồ quạt và đảm bảo làm mát đầy đủ cho từng đầu phun trong suốt quá trình in nhiều đầu phun.
- [ ] **Giám sát nhiệt độ Cartographer** — Thêm cơ chế giám sát/cảnh báo nhiệt độ cho chip Cartographer để tránh sự cố quá nhiệt.

## Đã hoàn thành

- [x] ~~Gỡ bỏ hoàn toàn kTAMV khỏi máy in và kho cấu hình, cài đặt dịch vụ Web Axiscope (port 3000) và cấu hình extension Klipper [axiscope] trên công tắc microswitch PF2 để đo bù trừ XYZ~~ (2026-09-18)
- [x] ~~Thử nghiệm và đánh giá Klipper-Camera-Vision, khôi phục cấu hình kTAMV production~~ (2026-09-15)
- [x] ~~Cải tiến macro Axiscope CALIBRATE_ALL_Z_OFFSETS: thêm cơ chế chờ nhiệt 150°C và nâng Z an toàn $\ge 15\text{ mm}$~~ (2026-09-13)
- [x] ~~Tích hợp hệ số bù nén nhựa First Layer (Squish Factor: -0.04mm T1–T3, -0.03mm T4) vào Z-offset của T1–T4 trong printer.cfg~~ (2026-09-13)
- [x] ~~Dọn dẹp các module thử nghiệm KCC và TKC, chuẩn hóa kTAMV camera XY alignment và tạo macro tự động KTAMV_AUTO_CALIBRATE_ALL_TOOLS bằng tọa độ đã học~~ (2026-09-13)
- [x] ~~Tinh chỉnh Pressure Advance cho từng loại nhựa trong OrcaSlicer~~ (2026-09-02) — Đã hiệu chuẩn và quản lý trực tiếp trong các profile filament của OrcaSlicer (`Orca Config/`), tự động chèn `SET_PRESSURE_ADVANCE` theo vật liệu/màu trong G-code.
- [x] ~~Chuyển quyền quản lý `toolchanger/readonly-configs/` hoàn toàn cho KTC-Easy~~ (2026-08-23)
- [x] ~~Hiệu chuẩn và xác nhận Input Shaper riêng cho T0–T4~~ (2026-08-23)
- [x] ~~Xác nhận lỗi cảm biến T4 đã hết~~ (2026-08-23)
- [x] ~~Xác nhận lỗi kết nối Cartographer đã hết~~ (2026-08-23)
- [x] ~~Cấu hình công tắc vi mô Z-offset trên PF2 tại X:68, Y:-10, Z:7~~ (2026-08-09)
- [x] ~~Đồng bộ khối SAVE_CONFIG (Cartographer threshold 1819, scan model, PID)~~ (2026-08-09)
- [x] ~~Cập nhật install.sh / update.sh tự động loại trừ README.md khỏi máy in~~ (2026-08-09)
- [x] ~~Khôi phục bộ Z-offsets in thực tế đẹp cho T1–T4~~ (2026-08-09)
- [x] ~~Cập nhật zero_reference_position khớp với vị trí homing nozzle~~ (2026-06-30)
- [x] ~~Tăng check_gain_time của heater_bed để sửa lỗi tắt máy giả~~ (2026-06-23)
- [x] ~~Điều chỉnh QGL retry_tolerance ngăn chặn hủy lệnh giả~~ (2026-06-28)
- [x] ~~Thêm quy tắc bảo mật .gitignore trước khi public repo~~ (2026-06-30)
