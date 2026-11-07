# Điều tra nozzle sát bàn ngày 01/11/2026

## Kết luận theo mức bằng chứng

- Đã truy cập Moonraker và SSH trên 192.168.1.43, chỉ đọc. Không phát lệnh G-code, home, gia nhiệt, calib, restart hoặc sửa cấu hình máy.
- Người vận hành xác nhận T0 màu xanh đã sát bàn ngay từ nét đầu, kể cả sau calib lại. Vì vậy không thể quy lỗi riêng cho offset T3.
- Cấu hình được Klipper nạp ở phiên in hình trụ buổi sáng và các phiên lỗi đầu buổi trưa giống nhau. Scan model, Touch threshold=1504, Touch z_offset=-0.05, tool offsets, macro, mesh settings và hình học QGL đều chưa đổi trong giai đoạn này. Không có bằng chứng lỗi khởi phát do thay cấu hình hoặc calib lại.
- Sau calib, model mới đã được lưu và nạp thực sự: scan reference_temperature=-18.26; Touch threshold=1379, speed=2, z_offset=-0.05, samples=3, sample_range=0.01. Không phải quên SAVE_CONFIG.
- Có bằng chứng trực tiếp Touch thiếu ổn định trong lần in sau calib: 7 mẫu trải từ -0.0469 đến +0.4951 mm, tức 0.5420 mm. Cuối cùng phần mềm tìm được 3 mẫu gần nhau và tiếp tục; điều này chỉ chứng minh cụm mẫu cuối đạt độ lặp, không chứng minh Z0 cơ khí đúng.
- Có khác biệt quy trình liên quan: hình trụ chỉ T0, giữ nguyên T0 từ Touch tới lớp đầu; các bản lỗi dùng nhiều tool, prime T3 rồi gắp lại T0 sau Touch/mesh. Độ ngồi lại của T0, độ cứng ngàm/nozzle, độ cố định Cartographer và khả năng thay đổi Z khi đi lên dock cần kiểm tra vật lý. Log không đo được độ ngồi ngàm hoặc bước Z bị mất, nên chưa chốt linh kiện gây lỗi.
- Nguyên nhân sát bàn chưa được chứng minh đến một phần cứng cụ thể. Hướng điều tra ưu tiên là độ tin cậy mốc chạm T0 và khả năng giữ mốc đó qua lần đổi tool sau Touch; không nên tiếp tục bù một offset cố định để coi như đã sửa.

## Dòng thời gian (giờ Việt Nam)

| Bắt đầu | Kết thúc | File / sự kiện | Bằng chứng |
|---|---|---|---|
| 09:36:46 | 10:36:33 | Hinh tru_ABS_52m32s.gcode | Completed, chỉ T0; Touch 3 mẫu 0.6190 / 0.6190 / 0.6170, range 0.0020 mm |
| 12:13:36 | 12:21:46 | Belt-Clam_ABS_29m57s.gcode | Lỗi gắp T2, Expected tool tool T2 but active is None; virtual-SD position=0, chưa in vật thể |
| 12:37:21 | 12:44:33 | Belt-Clam_ABS_29m57s.gcode | Touch, mesh, prime T3 rồi T0, bắt đầu in T0 và bị hủy |
| 12:45:37 | 13:01:57 | Belt-Clam_ABS_29m57s.gcode | Touch, mesh, prime T3 rồi T0, sau đó có đổi T0/T3 trong khi in |
| 13:11:28 | 13:19:09 | Belt-Clam_ABS_1h55m.gcode | Touch, mesh, prime T3 rồi T0, bắt đầu in và hủy |
| 13:59–14:35 | | Chỉnh QGL nhiều lần | Points/corners đổi sau khi lỗi đã xảy ra; không giải thích lần lỗi khởi phát |
| 14:37:27 | 14:45:01 | Belt-Clam_ABS_29m57s.gcode | T0 được gắp lại khoảng 14:44:41; watchdog detected crash of tool T0 lúc bắt đầu in |
| 14:52–14:53 | | Calib Scan và SAVE_CONFIG | Model scan thay đổi, được nạp lại |
| 14:58–15:03 | | Calib Touch và SAVE_CONFIG | Threshold 1504 -> 1379; xác minh báo 0.011 mm median range across 10 samples; z_offset vẫn -0.05 |
| 15:17:07 | 15:24:48 | Belt-Clam_ABS_27m27s.gcode | Vẫn lỗi sau calib; Touch có outlier 0.542 mm; người vận hành nâng Z 4 lần +0.05, tổng +0.20 mm |
| 15:29:53 | | Touch thủ công | adjusted z by +0.490 mm, so với +0.033 mm khi chuẩn bị bản in trước đó; có QGL/home/nhiệt và di chuyển xen kẽ nên không coi đây là phép đo độ lặp độc lập |
| 15:34:05 | | SAVE_CONFIG | Lưu mesh full-bed; cấu hình hiện tại đã nạp mesh mới |

Thời gian công việc lấy từ Moonraker history. Đồng hồ wall time lúc khởi động buổi sáng lệch với history; khi đối chiếu sự kiện trong phiên đó cần neo bằng monotonic và sự kiện kết thúc cùng job. Không dùng trực tiếp dòng Start printer at để gán giờ sự kiện buổi sáng.

## Những khả năng đã loại trừ hoặc chưa chứng minh

1. **Slicer tự hạ Z:** Các file hiện còn trên máy đều first_layer_height=0.25, z_offset=0, nozzle first layer=260 C, bed=105 C, TOOL=0. Không tìm thấy lệnh SET_GCODE_OFFSET/G92 Z trong các file này. Lớp đầu T0 đều ra lệnh Z0.25. File Belt-Clam cùng tên từng được ghi đè: bản đầu dùng T2 được xác nhận từ log thực thi, không suy từ nội dung file hiện tại.
2. **Offset T3 rò sang T0:** Mã KTC đang cài dùng transform theo tool đang chọn. T0 Z mặc định 0; T3=-0.3865 đã có từ trước buổi sáng. Chưa thấy bằng chứng offset T3 bị cộng tồn dư vào T0. Chọn T0 thành công chỉ xác nhận cảm biến hiện diện, không đo được độ ngồi cơ khí.
3. **Scan drift bằng đúng độ sát bàn:** Các số adjusted z by của Touch là phần sửa lại mốc home trước đó. Không được lấy chênh lệch các số này làm độ nozzle lún bàn. Model scan hoặc tần số có thể drift mà Touch vẫn sửa đúng; cần kiểm tra khe hở vật lý sau Touch và sau đổi tool.
4. **Calib thành công nghĩa là lớp đầu đúng:** Mã Cartographer 1.10.1 đang cài tìm threshold/speed và tạo model với z_offset mặc định. Chu trình đó không in kiểm chứng khe hở T0 nóng sau lần gắp lại. Trong ca này z_offset trước/sau đều -0.05.
5. **Cartographer đã hết lỗi nhiệt:** Snapshot live vẫn báo nhiệt coil âm, khoảng -13.43 C; bù nhiệt coil đang bỏ trống. Đây là lỗi đo tồn tại từ trước và chưa được sửa bằng việc fit lại scan model. Chưa có bằng chứng đủ để khẳng định riêng lỗi coil gây ra độ sát bàn này.
6. **Bàn ổn định vì target 105 C:** Log raw vẫn có bước nhiệt bất thường. Ví dụ phiên 12:37 có bước 104.5 -> 113.1 C trong khoảng 1 giây trước Touch. Bản sáng tốt cũng có bước bất thường, nên không quy riêng lỗi lớp đầu cho NTC từ tương quan này. Không suy nhiệt thật mặt bàn từ bước nhảy tín hiệu.
7. **QGL đạt nghĩa là Z0 đúng:** Các bản trên đều vượt qua QGL, nhưng QGL chỉ so độ lệch các điểm; không xác minh mốc chạm nozzle hoặc ngàm T0 sau lần đổi tool.

## Phép kiểm tra tiếp theo để tách nguyên nhân

Chưa thực hiện trong lượt điều tra này. Snapshot đầu máy chưa home và trước đó có sự kiện mất nhận diện T0 khi in; cần người vận hành quan sát ngàm/dock và mặt bàn trước chuyển động. Snapshot cuối máy standby, homed xyz, T0 active/detected=0, homing_origin Z=0; gcode store ghi QGL từ client khác lúc 15:41, không phải lệnh của lượt điều tra này. Nhiệt coil cuối vẫn âm, khoảng -15.69 C.

1. Kiểm tra T0 gài cứng, nozzle/hotend không lỏng, ngàm không có nhựa/cặn, gá Cartographer không dịch chuyển; kiểm tra đường dây/đầu nối coil vì nhiệt âm vẫn còn.
2. Khi bàn/gantry ổn định và nozzle sạch, kiểm tra mốc Touch lặp lại trên T0 **không đổi tool**, rồi đo khe hở tại cùng XY/Z an toàn. Không chỉ nhìn thông báo ba mẫu đạt.
3. Với cùng điều kiện, đo lại khe hở trước/sau **một chu trình T0 -> T3 -> T0**. Nếu thay đổi qua chu trình này, kiểm tra độ ngồi ngàm và chuyển động Z tới dock; calib Scan/Touch thêm sẽ không giải quyết nguồn thay đổi đó.
4. Nếu khe hở đã sai trước đổi tool, ưu tiên chất lượng Touch/độ cứng gá/nozzle và bước mesh. Có thể đối chiếu mẫu T0 đơn tool với cùng nhiệt, cùng XY và cùng luồng chuẩn bị để tách yếu tố nhiều tool.
5. Chỉ chỉnh offset sau khi mốc chạm và độ gắp lại lặp ổn định. Tổng +0.20 mm người dùng đã thử là bằng chứng can thiệp, chưa phải offset đã xác minh để lưu production.

## Dữ liệu

- `history.json`, `status.json`, `gcode_store.json`, `files_config.json`, `machine.json`, `objects.json`: API snapshots.
- `klippy.log`, `moonraker.log`: bản tải về để bảo toàn bằng chứng; klippy có đoạn NUL từ file live.
- `printer.live.cfg`, `printer-20261101_*.cfg`: cấu hình và backup trên máy.
- `Printer-Setup__*.cfg`, `toolchanger__tools__*.cfg`: file live liên quan.
- Bốn file G-code tải trực tiếp từ máy; lịch sử có thể chứa phiên bản đã bị ghi đè.
- `config-at-logline-*.json`: cấu hình Klipper in vào từng phiên log, so sánh cấu hình thực sự được nạp.

Mã nguồn đã đọc qua SSH: `/home/voron/klipper-toolchanger-easy/klipper/extras/toolchanger.py` và package `/home/voron/klippy-env/lib/python3.11/site-packages/cartographer/`, đặc biệt `macros/touch/home.py`, `macros/touch/calibrate.py`, `macros/bed_mesh/scan_mesh.py`. Không chỉnh runtime.
