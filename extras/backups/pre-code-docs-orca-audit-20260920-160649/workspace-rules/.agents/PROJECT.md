# Tổng quan dự án

## Tên dự án

**Voron 2.4 StealthChanger — Kho cấu hình 5-Tool**

## Mục đích

Kho lưu trữ này chứa **toàn bộ cấu hình đang vận hành (production)** cho máy in Voron 2.4 trang bị hệ thống StealthChanger 5-tool chạy firmware Klipper.

## Mục tiêu

Mọi hành động trong kho lưu trữ này phải phục vụ các mục tiêu cốt lõi sau:

1. **Ổn định** — Máy in phải hoạt động bình thường sau mỗi thay đổi. Không bao giờ đưa vào các sửa đổi chưa được kiểm tra hoặc mang tính suy đoán.
2. **Dễ hoàn tác** — Mọi thay đổi phải có khả năng đảo ngược. Sao lưu và kiểm soát phiên bản đảm bảo phục hồi tức thì.
3. **Dễ bảo trì** — Các file cấu hình phải sạch sẽ, có tài liệu đầy đủ và được tổ chức logic.
4. **Dễ hợp tác** — Bất kỳ AI assistant hoặc người nào cũng phải hiểu cấu trúc dự án trong vài phút.

## Thông số phần cứng & Kiến trúc hệ thống

| Thành phần | Chi tiết |
|---|---|
| **Máy in** | Voron 2.4 350mm — CoreXY |
| **Hệ thống đổi đầu** | StealthChanger — 5 tool (T0–T4) |
| **Firmware** | Klipper |
| **MCU chính** | BTT Manta M8P V2.0 (CAN bridge `mcu`, UUID: `19b203d75137`) |
| **Máy chủ (Host)** | BTT CM4 chạy MainsailOS (gắn trực tiếp trên Manta M8P) |
| **MCU đầu in** | 5× BTT EBB36 V1.2 (`EBB0`–`EBB4`) qua CAN bus |
| **Hotend** | 5× TZ V6 2.0 |
| **Extruder** | 5× WW BMG (TMC2209 trên EBB36) |
| **Hiệu chuẩn Tool XY** | Camera nhìn lên + Axiscope web interface cổng 3000 (căn tâm manual crosshair trực quan) |
| **Hiệu chuẩn Z-Offset kép** | • Z Homing: Cartographer Touch tại tâm bàn (174, 168)<br>• Tool Z-Offset: Công tắc Axiscope microswitch `pin: ^PF2` tại (X:80, Y:-5, Z:8) với gia nhiệt 150°C và nâng Z an toàn $\ge 15\text{ mm}$<br>• Tích hợp bù nén nhựa First Layer (Squish Factor: -0.04mm cho T1–T3, -0.03mm cho T4) trực tiếp trong `gcode_z_offset` của `printer.cfg` |
| **Mâm nhiệt bàn in** | AC Silicone 1000W 220V + Rơ-le bán dẫn SSR (Manta M8P `PA1`) |
| **Vệ sinh đầu phun** | Bambu A1 Silicone Brush + Purge Bucket (X: 277→312, Y: -7→-10, Z: 1.2mm) |
| **Sấy nhựa buồng in** | Chế độ sấy nhựa tích hợp 4 vùng (`filament-dryer.cfg`) kết hợp bàn nhiệt, quạt bed, quạt tản nhiệt và xung xả ẩm định kỳ |
| **Hệ thống LED** | LED trạng thái đầu in & thanh vỏ 10 mức ưu tiên hướng sự kiện + đèn chiếu sáng buồng in 100% độ sáng (`LIGHTS_ON`) |
| **Bảo vệ rơi tool** | Module watchdog `tool-crash.cfg` lọc nhiễu và pause an toàn không di chuyển trục |
| **Giao diện web** | Mainsail |
| **Màn hình** | KlipperScreen (Ngôn ngữ: Tiếng Việt) |
| **Slicer** | OrcaSlicer (Profile đa màu/đa đầu in, quản lý Pressure Advance theo từng cuộn nhựa) |

## Quy tắc quan trọng nhất

> **Đây là dự án đang vận hành (production).**
>
> Mọi thay đổi phải đảm bảo sự ổn định của máy in.
> Nếu không chắc chắn về bất kỳ sửa đổi nào — **DỪNG LẠI và hỏi người dùng.**
