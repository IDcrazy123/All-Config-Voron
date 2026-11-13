# Lỗi Cartographer khi thử in T0 ngày 2026-11-13

## Bằng chứng live

- Job `A4T Stealthchanger_ABS_17m48s.gcode`, Moonraker job `0003F8`, bắt đầu khoảng 15:14:02 và bị hủy lúc 15:21:21 (Asia/Saigon). Đây là lần in mới sau khi nạp chế độ T0-only.
- Log cho thấy `toolchanger initialized, active tool T0`, QGL hoàn tất ở range 0,006573 mm, rồi `CARTOGRAPHER_TOUCH_HOME` có 3 mẫu 1,0693/1,0753/1,0733 mm, range 0,0060 mm.
- `BED_MESH_CALIBRATE ADAPTIVE=1` thu 2880 raw samples trong 8,37 giây. Cartographer báo `Mesh scan failed: 195/195 grid points have no valid samples`; 1237 mẫu được gán vào lưới. Lỗi xảy ra trước prime và trước khi in lớp đầu.
- Cấu hình live: scan model `default`, miền nghịch đảo tần số `2.993089036223377e-07` đến `3.0634782799867333e-07`, reference temperature `-21.41`°C, `mesh_height=3`, không có section calibration bù nhiệt cuộn. Model này có trong backup trước chế độ T0-only; lần đổi include không sửa nó.
- `cartographer_coil` báo khoảng −25°C quanh lần quét lỗi, trong khi `heater_bed` khoảng 105°C và Cartographer board khoảng 63°C. Lần mesh thành công trước trong log có coil khoảng −21,9°C. Theo FAQ chính thức của Cartographer, nhiệt cuộn âm là dấu hiệu có thể hỏng điện trở trên coil; cần kiểm tra linh kiện, không suy nhiệt độ vật lý từ giá trị này.
- Sau khi hủy: Klipper `ready`, `configfile.warnings=[]`, `tool_numbers=[0]`, `print_stats=cancelled`, toolchanger `uninitialized`, `tool=None`, `detected_tool=tool T0`; heater target đã về 0. Trạng thái nhận diện tool này không đủ để tự động chạy lại pickup hay mesh.

## Phân tích và hướng xử lý

Mã Cartographer đang cài đặt đánh dấu một điểm lưới vô hiệu khi trung vị khoảng cách của các mẫu không hữu hạn. Từng điểm trong lỗi đều có sample count, nên đường quét và thu mẫu đã chạy nhưng scan model không trả ra khoảng cách hợp lệ. Mã model trả `inf`/`-inf` nếu tần số nằm ngoài miền hiệu chuẩn. Đây là cơ chế giải thích trực tiếp lỗi; chưa có raw frequency của chính lần quét để chứng minh nguyên nhân cuối cùng của việc vượt miền.

Chưa sửa production. Không hạ scan height, nới miền model hoặc bỏ mesh để che lỗi. Tắt nguồn và kiểm tra probe Cartographer, điện trở coil, đầu nối/cáp trước; sau đó đọc lại nhiệt coil ở trạng thái nguội và kiểm tra hiệu chuẩn Scan ở nhiệt độ vận hành với người quan sát. Nếu phần cứng ổn, hiệu chuẩn lại Scan/temperature compensation theo quy trình của Cartographer, rồi xác minh mesh và lớp đầu có giám sát. Không tái sử dụng job bị hủy để `RESUME`.

Tài liệu nhà sản xuất: [FAQ về nhiệt cuộn âm](https://docs.cartographer3d.com/cartographer-probe/faq/), [Scan Calibration](https://docs.cartographer3d.com/cartographer-probe/installation-and-setup/software-configuration/scan-calibration/), [Coil Temperature Offset Calibration](https://docs.cartographer3d.com/cartographer-probe/features/coil-temperature-offset-calibration/).
