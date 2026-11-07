# Thử hai bộ tọa độ gantry QGL trên máy ngày 07/11/2026

Sau khi người vận hành chỉnh dây GT2 dưới cụm truyền động Z, so bộ production A `(-10, -10)` / `(350, 350)` với bộ thử B `(-52, 1)` / `(417, 423)`. Bộ B là ước tính từ CAD Voron 2.4r2 và khoảng cách đo từ mép ngoài khung tới nozzle tại X0 Y0, 70–75 mm từ trái và 40–45 mm từ trước.

Chỉ thay hai dòng `gantry_corners` của `config/Printer-Setup/print-macros.cfg` trên máy. Giữ nguyên bốn tọa độ lệnh XY `(20, 10)`, `(20, 280)`, `(330, 280)`, `(330, 10)`. Với offset Cartographer Y+35, vị trí cảm biến có Y45 và Y315. Giữ macro production với lượt thô Z10 khi QGL chưa áp dụng và lượt tinh Z2, tolerance 0,0075 mm, tối đa 10 retry, speed 200 mm/s, Scan 20 mẫu và Touch threshold 792. Mọi heater có target và power bằng 0, bàn khoảng 33°C. QGL chạy với T0 đã xác thực bằng cảm biến, T3 chỉ dùng trong hai vòng đổi tool của bộ A. Không thao tác T1/T2.

## Kết quả trên máy

| Bộ | Lượt | Range tinh đầu → cuối (mm) | Retry cuối | Kết quả |
|---|---|---:|---:|---|
| A | Lấy mốc sau `G28` | 0,019600 → 0,003654 | 3 | Đạt |
| A | QGL lặp, giữ T0 | 0,030384 → 0,004704 | 4 | Đạt |
| A | Kích Z2 sau phải +0,20 mm rồi home Z | 0,200590 → 0,003827 | 9 | Đạt |
| A | Kích Z0 trước trái −0,20 mm rồi home Z | 0,204960 → 0,006628 | 8 | Đạt |
| A | T0 → T3 → T0 lần 1 | 0,019315 → 0,006991 | 1 | Đạt |
| A | T0 → T3 → T0 lần 2 | 0,015353 → 0,004003 | 6 | Đạt |
| B | Lấy mốc sau reload và `G28` | 0,038795 → 0,011457 | 10 | `Too many retries` |
| B | Khởi tạo lại T0, home Z và thử lại | 0,032007 → 0,013433 | 10 | `Too many retries` |
| A | Xác nhận sau khôi phục, reload và `G28` | 0,043233 → 0,004915 | 3 | Đạt |

A đạt 5/5 lượt đánh giá, trung vị 6 retry và tối đa 9. B dừng trước chuỗi kích motor và đổi tool vì hai lượt lấy mốc đều thất bại. Range thô của hai lượt B lần lượt là 0,084643 và 0,020968 mm. Hai lượt B bắt đầu với trạng thái gantry khác nhau và không tạo được bộ A/B đủ cặp. Cảm biến tiếp tục nhận T0 sau lỗi. KTC chuyển active tool về chưa khởi tạo theo `_handle_command_error` trong runtime đang chạy, rồi `INITIALIZE_TOOLCHANGER` xác thực lại T0.

Trong lượt B đầu, bù Z3 trước phải đổi dấu ở tất cả vòng tinh liên tiếp. Nếu tính hai bộ tọa độ trên cùng bốn số đo của vòng tinh đầu, Klipper yêu cầu bù Z3 +0,042126 mm với B và +0,032894 mm với A, tăng khoảng 28%. Đây là lệnh bù ngoại suy từ các điểm đo. Chưa có phép đo độc lập để tách đáp ứng thật của cụm Z3 khỏi sai lệch của phép đo Scan.

## Khôi phục

Đã khôi phục nguyên file production, đối chiếu SHA-256 và xác nhận Klipper nạp lại `(-10, -10)` / `(350, 350)`. Lượt xác nhận bắt đầu với bàn 32,95°C và range thô 0,026321 mm. Sau QGL, máy đứng yên với T0 active/detected tại X174 Y168 Z20, heater tắt và đèn khoang trắng như lúc bắt đầu. Khi kết thúc thử nghiệm, GitHub và checkout trên máy đều ở `75221b7`. Bản trước thử nằm trong `extras/backups/pre-qgl-gantry-corners-test-20261107-144025/` và trên máy tại `~/printer_data/config_backups/qgl-corners-trial-20261107-144025/`. Bản B nằm tại `~/printer_data/config_backups/qgl-corners-rollback-20261107-144804/`.

## Rà soát comment trước khi đồng bộ GitHub

Đối chiếu các CFG, CONF và script do repository theo dõi với thư mục live. Sai khác hiện hành duy nhất là `heater_bed.max_temp`, 120°C trong Git và 150°C trên máy. Giữ nguyên sai khác đã ghi trong `KNOWN_ISSUES.md`. Cập nhật comment ở `calibration-probe.cfg` theo Scan 20 mẫu mặc định của Cartographer 1.10.1 và chú thích trong `print-macros.cfg` để phân biệt tọa độ nozzle với vị trí coil Y+35. Cấu hình QGL, Scan, Touch và toàn bộ `SAVE_CONFIG` giữ nguyên. Sao lưu hai file trước khi sửa tại `extras/backups/pre-qgl-comment-sync-20261107-150148/`.
