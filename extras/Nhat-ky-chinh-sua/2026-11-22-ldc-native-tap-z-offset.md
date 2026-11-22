# 2026-11-22 — Bù lớp đầu bằng tap offset native

## Đối chiếu

- Người vận hành muốn dùng tham số trong `[probe_eddy_current ldc1612_eddy_coil]` để lưu bù Z lớp đầu và bỏ phần bù tùy biến không đúng. Bản hướng dẫn `tap_adjust_z` thuộc `eddy-ng` lưu trong `extras/LDC1612/`; production đang nạp Klipper native `probe_eddy_current.py`, không nạp plugin đó. Mã và `Config_Reference.md` trên máy chỉ nhận `tap_z_offset` (mặc định 0,0). Ghi `tap_adjust_z` vào section native sẽ không hợp lệ.
- Klipper native tính Z tap trả về bằng `z_contact - tap_z_offset`. `Z_OFFSET_APPLY_PROBE METHOD=tap` lưu `tap_z_offset_mới = tap_z_offset_cũ - Z_babystep`. Vì người vận hành đã nâng Z bằng babystep dương, giá trị offset native cần âm.
- Bản in lớp đầu cũ cần nâng ròng +0,10 mm, nhưng helper tap lúc đó không chạy do tên lệnh chứa số. Lần tap trước in báo contact Z=+0,059759 mm. Helper đã sửa tên sẽ dùng số này để nâng mốc Z khoảng +0,060 mm. Người vận hành chọn chỉ bù phần còn lại khoảng +0,040 mm, tương ứng `tap_z_offset: -0.04`. Nếu điều kiện nhiệt/lực chạm như cũ, tap sẽ trả khoảng +0,100 mm và helper áp dụng một lần. Đây là ước lượng, chưa phải kết quả bản in mới.
- `LDC_TAP_HOME` vẫn phải áp dụng kết quả tap vào tọa độ Z sau `PROBE METHOD=tap`; cấu hình `tap_z_offset` chỉ đổi số đo trả về, tự nó không tái lập gốc Z. Bỏ `_LDC_APPLY_TAP_Z` mà không thay thế bước này sẽ khiến offset mới không tác động đến in. Không thêm bù cố định riêng trong macro hoặc offset tool T0.

## Thay đổi và xác minh

- Thêm `tap_z_offset: -0.04` vào section native của `config/Printer-Setup/calibration-probe.cfg`. Các dây/pin, đường cong Z, threshold và offset tool được giữ nguyên. Cập nhật hướng dẫn phân biệt native với `eddy-ng`.
- Đã sao lưu Git và live `calibration-probe.cfg`/`printer.cfg` trước sửa ở `extras/backups/pre-tap-z-offset-20261122/`; các cặp file Git/live có hash trùng nhau. Sau deploy cần kiểm tra `configfile.settings` và Klipper `ready`.
- Chưa in lớp đầu sau đổi offset. Khi lỗi `Missed scheduling of next digital out event` còn tái diễn, không coi việc nạp cấu hình là kiểm chứng cơ khí hoặc chất lượng lớp đầu.
