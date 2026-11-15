# 2026-11-15 — tháo T0, dùng T1 tạm để in

## Yêu cầu và bằng chứng

Người vận hành muốn tháo hoàn toàn T0 để bảo trì; T1 đã gắn trên shuttle. Dock T1 chưa căn, không được tự cất tool sau khi in.

Trước thay đổi, Moonraker báo Klipper `ready`, print `standby`, không pause/sấy, heater targets đều 0, KTC registry `[0,1,2,3,4]`, `detected_tool_number=1`, chưa khởi tạo. Cảm biến nhựa T1 báo `false`. Ba file live sắp sửa trùng nội dung Git. Bản sao trước thay đổi ở `extras/backups/pre-t0-removal-t1-only-20261115-195358/`; bản sao trên Pi ở `/home/voron/printer_data/config-backups/t0-removal-t1-only-20261115-195358/`.

## Thay đổi

- `config/printer.cfg`: nạp KTC core và duy nhất `tools/T1.cfg`, bỏ T0/T2/T3/T4 khỏi cấu hình đang nạp. Chuyển PID 28.787/9.596/21.590 của T1 sang `[extruder]`, bỏ các SAVE_CONFIG không còn nạp; giữ XY offset T1 và tạm đặt Z offset 0 để Touch bằng T1. Bản năm-tool/PID/offset gốc nằm trong backup.
- `config/toolchanger/tools/T1.cfg`: đổi T1 từ `extruder1` thành `extruder` ở motor, heater fan và KTC để đáp ứng thứ tự nạp extruder của Klipper. UUID CAN, pin, nhiệt giới hạn và dock không đổi.
- `config/Printer-Setup/print-macros.cfg`: khi không có T0, yêu cầu T1 đã được cảm biến nhận trên shuttle trước chuyển động; không gọi CLEAN_NOZZLE của T0; chờ T1 ở 148–150°C trước Touch; chỉ prime tool có trong registry. Khi kết thúc/hủy, tắt nhiệt và nâng Z nếu trạng thái an toàn, giữ T1 trên shuttle, không gọi UNSELECT_TOOL/đi dock. Nhánh năm-tool dùng T0 được giữ cho lúc khôi phục.

## Kiểm tra

- Preflight trên Pi: Klipper parse 158 sections, tất cả G-code template biên dịch được; registry chỉ còn T1 và extruder mapping đúng; SAVE_CONFIG đúng với chế độ tạm.
- Live sau `RESTART`: Klipper `ready`, không cảnh báo, registry `[1]`. `INITIALIZE_TOOLCHANGER` không di chuyển và cho `ready`, active/detected đều 1, toolhead extruder là `extruder`.
- Gọi thử `PRINT_START TOOL=1 ...` khi cảm biến nhựa T1 trống bị chặn ngay với thông báo nạp nhựa; print vẫn standby, chưa home, heater targets vẫn 0.
- Render nhánh kết thúc T1-only xác nhận không sinh `UNSELECT_TOOL` hoặc lệnh đi dock.

## Cần kiểm tra tại máy

Tắt nguồn trước khi tháo giắc CAN/nguồn của T0. T1 chưa có nhựa theo cảm biến; nạp nhựa và kiểm tra cảm biến chuyển sang `true`. Làm sạch đầu phun T1 bằng tay trước khi in vì trạm lau chỉ đo cho T0. Người vận hành theo dõi lượt G28/QGL/Touch và lớp đầu tiên; chưa thử chuyển động, gia nhiệt, in hoặc tháo T0 vật lý trong phiên này. Không chạy thử thả/gắp T1 bằng tọa độ dock tạm.
