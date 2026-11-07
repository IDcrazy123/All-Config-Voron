# Khắc phục hiển thị Estimate / ETA bằng tùy chọn Mainsail — 04/11/2026

## Phạm vi và kết quả

Theo yêu cầu không sửa file Python và tránh ảnh hưởng lâu dài, chỉ đổi hai
tùy chọn có sẵn tại Interface Settings > General trong tab Mainsail đang mở.
Không tạo/sửa/chạy file .py trong tác vụ khắc phục này. Không sửa CFG, G-code,
runtime, macro, slicer, tốc độ, nhiệt hoặc quy trình chuẩn bị in.

| Tùy chọn | Trước (mặc định, chưa có key DB) | Sau |
|---|---|---|
| general.calcEtaTime | file, filament, slicer | slicer |
| general.calcEstimateTime | file, filament | mảng rỗng |

ETA dùng thời gian còn lại từ Slicer. Estimate sẽ hiện `--` khi đang in,
thay vì ngoại suy từ File/Filament. Ô Slicer vẫn hiển thị thời gian còn lại.
Đây là cách bỏ các dự báo gây dao động khỏi giao diện, không sửa thuật toán
Estimate hoặc biến nó thành một dự báo chính xác hơn. Mainsail v2.19.0 không
cung cấp Slicer làm lựa chọn cho ô Estimate.

## Kiểm chứng

- Giao diện xác nhận Estimate không có nguồn được chọn, ETA chỉ chọn Slicer.
- Đọc lại Moonraker DB xác nhận `calcEtaTime=["slicer"]`,
  `calcEstimateTime=[]`.
- So toàn bộ namespace trước/sau sau khi bỏ đúng hai key trên: các tùy chọn
  khác giống nhau. Print progress vẫn là File position (relative).
- Không gửi G-code điều khiển, restart/reload dịch vụ hoặc khởi chạy bản in.
- Trong lúc chuẩn bị thao tác, máy/giao diện đã trải qua một lần disconnect
  và trở về standby, trước khi đổi hai tùy chọn. Agent chỉ bấm TRY AGAIN để
  nối lại giao diện. Console có FIRMWARE_RESTART/G28 từ thao tác ngoài tác vụ;
  agent không gửi các lệnh đó. Cuối kiểm tra API báo standby, filename rỗng.
  Vì vậy chưa xác nhận ETA trên một bản in live sau thay đổi; chờ lần in kế.

Hai tùy chọn được lưu trong namespace Mainsail của Moonraker nên tồn tại sau
refresh và có thể áp dụng cho các trình duyệt khác nối cùng máy. Chúng không
thay đổi điều khiển Klipper. Không cần restart để áp dụng hoặc hoàn tác.

## Giới hạn

ETA còn phụ thuộc độ chính xác ước tính slicer và print_duration. Chuẩn bị,
chờ nhiệt, đổi tool, pause hoặc đổi speed factor có thể gây sai lệch giờ
kết thúc. Khi thời gian đã vượt dự báo slicer, ETA có thể hiện `--`. Cách này
loại bỏ dao động do ngoại suy file/nhựa, không cam kết thời điểm hoàn thành.

## Sao lưu và hoàn tác

Backup tại `extras/backups/pre-mainsail-time-display-20261104-170302/` gồm
namespace Mainsail trước/sau và KNOWN_ISSUES trước lần cập nhật này.
Không restore toàn bộ namespace vì có thể ghi đè các tùy chọn đổi về sau.

Hoàn tác qua Interface Settings > General:

1. Estimate time calculation: chọn File và Filament.
2. ETA calculation: chọn File, Filament và Slicer.

Ảnh xác minh:
`extras/diagnostics/20261104-time-estimate/mainsail-time-settings-after.png`.

Tham chiếu chức năng gốc:
[SettingsGeneralTab.vue v2.19.0](https://github.com/mainsail-crew/mainsail/blob/v2.19.0/src/components/settings/SettingsGeneralTab.vue).
