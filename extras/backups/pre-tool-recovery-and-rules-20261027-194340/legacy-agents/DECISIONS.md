# Nhật ký quyết định kỹ thuật

Ghi nhận các quyết định kỹ thuật quan trọng ở đây để các phiên làm việc trong tương lai hiểu **tại sao** một giá trị hoặc cách tiếp cận được chọn.

---

## Mẫu

```markdown
## YYYY-MM-DD — [Tiêu đề quyết định]

**Bối cảnh:** Điều gì dẫn đến quyết định này?
**Đã chọn:** Giá trị/cách tiếp cận được chọn
**Đã loại:** Các phương án thay thế đã xem xét và lý do loại bỏ
**Lý do:** Tại sao đây là lựa chọn tốt nhất?
```

## 2026-09-21 — Bật lại SexBolt tools_calibrate dưới dạng thử nghiệm có giám sát

**Bối cảnh:** Người vận hành lắp lại SexBolt và đo tâm nozzle trên quả bóng tại X80/Y-5.5/Z12. Guard Axiscope hiện tại khiến macro KTC chính báo lỗi; Axiscope và `[tools_calibrate]` cũng không thể nạp đồng thời trên PF2.

**Đã chọn:** Dùng `[tools_calibrate]` trên `^PF2`, tiếp cận tại Z18 và giảm `spread` từ 7 xuống 3.5 để điểm bắt đầu Y thấp nhất là -9.0, còn 1 mm so với `position_min: -10`. Bắt buộc kiểm tra `open`/`TRIGGERED` và đường tiếp cận trước chu trình đủ tool.

**Đã loại:** `spread: 7` vì lượt `y+` bắt đầu tại Y-12.5; bật đồng thời Axiscope và `tools_calibrate` vì Klipper chủ động từ chối cấu hình xung đột.

**Lý do:** Đây là backend hiệu chuẩn vật lý chính của KTC-Easy, đồng thời giữ phép thử trong giới hạn chuyển động đã cấu hình và không thay đổi vai trò Cartographer.

## 2026-09-17 — Gỡ bỏ hoàn toàn Axiscope và chuẩn hóa SexBolt tools_calibrate song song kTAMV

**Bối cảnh:** Module thử nghiệm Axiscope gây xung đột tài nguyên (`probe_multi_axis`) và không còn cần thiết khi hệ thống đã có giải pháp Cartographer Touch nhiệt độ cao và SexBolt chính thức. Cần đảm bảo hệ thống có quy trình cân chỉnh vật lý rõ ràng, tin cậy và không chồng chéo logic.
**Đã chọn:**
1. Gỡ bỏ hoàn toàn `[axiscope]` khỏi `calibration-probe.cfg`, dọn sạch file mã nguồn `axiscope.py` và bytecode cache trên máy in thật `192.168.1.43`.
2. Kích hoạt lại module SexBolt chính thức `[tools_calibrate]` của KTC-Easy trên chân `pin: ^PF2`.
3. Phân định ranh giới chức năng rõ ràng:
   - kTAMV: Chuyên trách đo quang học mặt phẳng XY (không tiếp xúc, độ chính xác dưới 10 micron).
   - SexBolt / Cartographer Touch: Chuyên trách đo độ cao tiếp xúc trục Z (Z-Offset).
   - Mở khóa macro `CALIBRATE_MOVE_OVER_PROBE`, `CALIBRATE_ALL_OFFSETS` và bổ sung `CALIBRATE_ALL_Z_OFFSETS`.
**Đã loại:** Giữ lại Axiscope hoặc duy trì các macro báo lỗi giả lập vô hiệu hóa tools_calibrate.
**Lý do:** Khôi phục tính năng nguyên bản của KTC-Easy, xóa bỏ mã nguồn không chính thức khỏi Klipper klippy/extras, đảm bảo độ ổn định cao nhất cho máy in production.

---

## 2026-09-16 — Viết lại toàn diện bộ đôi tài liệu README song ngữ và làm sạch thông tin nhạy cảm

**Bối cảnh:** Tài liệu dự án trước đây chỉ mô tả mức độ hướng dẫn sử dụng cơ bản mà chưa phân tích sâu bản chất kỹ thuật của 10 thuật toán/logic cốt lõi đang vận hành trên máy in (ngâm nhiệt động $\Delta T$, bảo vệ đầu dò Z và khử gờ nhựa 2 giai đoạn, Homing bất biến Cartographer, sấy nhựa buồng in 4 vùng có xả ẩm, lọc thị giác đốm sáng kTAMV, mồi nhựa pipeline đa tool, watchdog rơi tool, rút sợi 2 nấc & nâng Z an toàn, máy trạng thái LED 10 mức, bộ đệm tham số Input Shaper). Ngoài ra, tài liệu chứa một số địa chỉ IP máy in cục bộ và lệnh SSH có thông tin người dùng.
**Đã chọn:**
1. Viết lại toàn diện `README.md` (tiếng Anh) và `README.vi.md` (tiếng Việt đồng bộ 1:1) với cấu trúc chuẩn 7 phần chi tiết, trong đó Mục 7 phân tích sâu 10 thuật toán cốt lõi bằng công thức toán học và sơ đồ luồng.
2. Ẩn toàn bộ địa chỉ IP mạng nội bộ và chi tiết SSH thành định dạng giữ chỗ chuẩn an toàn (`<printer-ip>`, `<username>@<printer-ip>`) trong tài liệu công khai.
**Đã loại:** Giữ nguyên tài liệu sơ sài cũ hoặc chỉ cập nhật một phần; để lộ thông tin IP/user khi public repo lên GitHub.
**Lý do:** Đảm bảo kho lưu trữ đạt chuẩn tài liệu chuyên nghiệp, hỗ trợ tối đa cho việc bảo trì, chuyển giao kỹ thuật và chia sẻ cộng đồng mà vẫn an toàn tuyệt đối về bảo mật.

---

## 2026-09-16 — Đồng bộ độ sáng đèn buồng in LIGHTS_ON 100% từ máy in thực tế

**Bối cảnh:** Người vận hành máy in đã tinh chỉnh macro `LIGHTS_ON` trên máy in thực tế sang độ sáng 100% (`RED=1 GREEN=1 BLUE=1`) để quan sát rõ nhất buồng in và camera giám sát, trong khi kho Git vẫn lưu mức 30% (`RED=0.3 GREEN=0.3 BLUE=0.3`).
**Đã chọn:** Đồng bộ trực tiếp `fans-leds.cfg` về kho Git: đặt `RED=1 GREEN=1 BLUE=1` và cập nhật chú thích macro thành `white 100%`.
**Đã loại:** Giữ nguyên 30% trong Git làm ghi đè cấu hình người dùng khi chạy `update.sh`.
**Lý do:** Nguyên tắc cốt lõi: kho Git phải phản ánh chính xác 100% cấu hình production đang vận hành thực tế.

---

## 2026-09-15 — Thử nghiệm Klipper-Camera-Vision và khôi phục kTAMV production

**Bối cảnh:** Thử nghiệm module thị giác máy tính thay thế Klipper-Camera-Vision (`tool_xy_vision.cfg`) nhằm đánh giá khả năng nhận diện tâm nozzle tự động.
**Đã chọn:** Sau khi triển khai và đánh giá thực tế trên máy in, quyết định gỡ bỏ cấu hình thử nghiệm `tool_xy_vision.cfg` và khôi phục cấu hình kTAMV production (`ktamv.cfg`) làm backend chính thức cho cân chỉnh camera XY có giám sát với macro `KTAMV_AUTO_CALIBRATE_ALL_TOOLS` sử dụng tọa độ đã học.
**Đã loại:** Giữ lại các cấu hình thử nghiệm chưa đạt độ tin cậy cao trong nhánh production chính.
**Lý do:** Đảm bảo tính ổn định cao nhất cho hệ thống sản xuất; không để mã nguồn thử nghiệm làm ảnh hưởng tới quy trình in ấn hàng ngày.

---

## 2026-09-13 — Cơ chế chờ đủ 150°C và nâng Z an toàn cho macro Axiscope CALIBRATE_ALL_Z_OFFSETS

**Bối cảnh:** Khi thực thi `CALIBRATE_ALL_Z_OFFSETS`, lệnh `M104 T{tool} S150` chỉ phát nhiệt độ mục tiêu mà không chờ, dẫn đến T0 (tool quy chiếu) tiếp xúc công tắc ngay khi nozzle còn nguội, gây sai lệch do giãn nở nhiệt. Ngoài ra, việc di chuyển về dock đổi tool ở Z thấp có nguy cơ va quẹt.
**Đã chọn:**
1. Thêm `M109 T0 S150` trong `start_gcode` để chờ T0 đạt 150°C trước khi bắt đầu đo.
2. Thêm `M109 S150` trong `after_pickup_gcode` để đảm bảo mỗi tool sau khi gắp đạt đủ 150°C trước khi chạm công tắc.
3. Thêm kiểm tra và nâng Z lên $15\text{ mm}$ (`before_pickup_gcode`) nếu $Z < 15\text{ mm}$ trước khi di chuyển về dock.
4. Cập nhật tọa độ công tắc chuẩn: `X=68, Y=-8, Z=2` (với Z15 là khoảng cách tiếp cận an toàn).
**Đã loại:** Đo ở nhiệt độ phòng (nozzle nguội không phản ánh chiều dài giãn nở nhiệt thực tế khi in).
**Lý do:** Triệt tiêu hoàn toàn sai số giãn nở nhiệt giữa các đầu in và bảo đảm an toàn cơ học tuyệt đối khi chuyển đổi tool.

---

## 2026-09-13 — Tích hợp hệ số bù nén nhựa First Layer (Squish Factor) vào Z-Offset của Toolchanger

**Bối cảnh:** Cartographer Touch đo đạc tiếp xúc cơ học thuần của đầu phun khi chạm vào bàn in (ở 70°C bàn và 150°C hotend). Tuy nhiên, khi in thực tế lớp đầu tiên (First Layer) trên bàn in PEI sần, sợi nhựa nóng chảy đòi hỏi một độ nén cơ học bổ sung (squish) sâu hơn khoảng $0.03 - 0.04\text{ mm}$ để ép phẳng và bám chắc. Nếu giữ nguyên số đo tiếp xúc thuần, người dùng sẽ phải baby-step thủ công từng tool mỗi khi in đa màu.
**Đã chọn:** Tích hợp trực tiếp hệ số bù nén nhựa thực tế (-0.04 mm cho T1–T3, -0.03 mm cho T4) vào tham số `gcode_z_offset` của từng tool trong khối `#*# <SAVE_CONFIG>`:
- T0: `0.0000 mm` (Tool quy chiếu)
- T1: `0.2091 + (-0.04) = 0.1691 mm`
- T2: `-0.2742 + (-0.04) = -0.3142 mm` (trùng khớp với giá trị in đẹp cũ `-0.3160 mm`)
- T3: `-0.2175 + (-0.04) = -0.2575 mm`
- T4: `0.0585 + (-0.03) = 0.0285 mm`
**Đã loại:**
- Giữ nguyên số đo vật lý thuần của Cartographer và yêu cầu baby-step thủ công khi in.
- Cấu hình hạ Z toàn cục qua Slicer (làm lệch tương quan tương đối giữa các tool khác nhau).
**Lý do:** Tự động hóa hoàn toàn chất lượng first layer cho tất cả các tool mà không cần sự can thiệp thủ công của người dùng trong quá trình in đa vật liệu/đa màu.

---

## 2026-09-13 — Nghỉ hưu KCC/TKC, chuẩn hóa cân chỉnh camera XY bằng kTAMV với tọa độ học

**Bối cảnh:** Các module thử nghiệm KCC (Klipper-Camera-Calibration) và TKC (Tool-Klipper-Calibration) để lại nhiều file tạm, log, service không cần thiết và gây xung đột/phức tạp trong vận hành. Máy in cần quy trình cân chỉnh XY camera sạch sẽ, ổn định và an toàn sau mỗi lần bảo dưỡng cơ khí nhẹ.
**Đã chọn:**
1. Dọn dẹp triệt để các module, service daemon, symlink và cấu hình KCC/TKC khỏi máy in thực tế `192.168.1.43`; chuyển toàn bộ cấu hình TKC sang thư mục nghỉ hưu `extras/retired-configs/2026-09-13-tkc-removal/`.
2. Chuẩn hóa kTAMV làm backend chính thức cho cân chỉnh camera XY có giám sát.
3. Triển khai macro cân chỉnh tự động `KTAMV_AUTO_CALIBRATE_ALL_TOOLS` với cơ chế tọa độ camera được học (`printer.ktamv.camera_center_coordinates` từ `KTAMV_SET_ORIGIN` trên T0), tuyệt đối không hardcode tọa độ cố định. Chiều cao Z an toàn trong suốt quá trình đổi tool và đo được thiết lập tại Z=40 mm.
**Đã loại:**
- Giữ song song daemon TKC/KCC trên host Raspberry Pi/CM4.
- Hardcode tọa độ camera X170 Y0 vào macro tự động (gây nguy cơ va chạm nếu vị trí camera hoặc khung máy thay đổi).
**Lý do:** Giữ hệ thống gọn gàng, giảm thiểu tiến trình chạy ngầm không cần thiết, tăng tính an toàn và tự thích ứng khi vị trí camera thay đổi.

---

## 2026-09-02 — Quản lý Pressure Advance theo Filament Profile trong OrcaSlicer

**Bối cảnh:** Máy in Voron StealthChanger 5-tool sử dụng nhiều loại nhựa (PETG, ABS...) từ nhiều nhà sản xuất khác nhau với độ nhớt và tính chất dòng chảy khác biệt. Việc gán cứng giá trị Pressure Advance cố định cho từng đầu in trong Klipper không linh hoạt khi một tool có thể nạp các cuộn nhựa khác nhau theo từng bản in.
**Đã chọn:** Kích hoạt và cấu hình thông số `pressure_advance` riêng biệt trong từng profile filament của OrcaSlicer (trong `Orca Config/`, ví dụ: PETG 0.060–0.074, ABS 0.030–0.060). OrcaSlicer tự động chèn lệnh `SET_PRESSURE_ADVANCE ADVANCE=...` vào G-code mỗi khi đổi tool/filament. Trong Klipper `T0.cfg`–`T4.cfg`, tham số `pressure_advance` tĩnh tiếp tục để trống/comment.
**Đã loại:** Gán cứng giá trị PA tĩnh vào file cấu hình Klipper của từng tool (`tools/T0.cfg`–`T4.cfg`) hoặc tạo macro ghi đè phức tạp.
**Lý do:** Tách biệt rõ ràng: Klipper quản lý phần cứng cơ khí (kinematics, offsets, shaper), còn Slicer quản lý đặc tính vật liệu in (nhiệt độ, lưu lượng, PA). Khi thay đổi loại nhựa trên tool bất kỳ, chỉ cần chọn đúng profile trong OrcaSlicer mà không phải sửa cấu hình Klipper hay khởi động lại firmware.

## 2026-08-31 — Gỡ ToolVision và dùng kTAMV để đối chiếu XY

**Bối cảnh:** Người dùng yêu cầu gỡ toàn bộ tích hợp ToolVision, cài lại kTAMV
upstream và đối chiếu cách sử dụng trong khi tool đang đứng trên camera, tuyệt
đối không được làm máy chuyển động. Upstream kTAMV vẫn ở commit `72421f2` từ
2024 và lần thử trước với MF-500 đã thất bại vì phản xạ/blob giả.
**Đã chọn:** Archive đầy đủ ToolVision trước khi gỡ; nạp
`Printer-Setup/ktamv.cfg`, pin checkout `~/kTAMV`, dùng venv và user service cổng
8086, tắt cloud upload, áp patch chọn nhiều vật thể đã review. kTAMV chỉ dùng để
đối chiếu X/Y có giám sát; Axiscope và tools_calibrate tiếp tục tắt nên không có
backend tool-offset Z active.
**Đã loại:** Chạy installer upstream, bật auto-update cho checkout có patch,
dùng chung port với unit ToolVision cũ, tăng tolerance để ép detector pass hoặc
chạy camera calibration trong phiên cài đặt.
**Lý do:** Giữ máy đứng yên, tránh sửa package/giờ/config ngoài kiểm soát, cho
phép so sánh đúng hành vi source và giữ rollback đầy đủ. Sau khi gỡ phần user,
operator đã cấp sudo tương tác để disable/xóa unit hệ thống ToolVision và reload
systemd; chỉ archive lịch sử còn được giữ.

## 2026-08-23 — KTC-Easy sở hữu toàn bộ readonly-configs

**Bối cảnh:** Payload All-Config vẫn chứa bản tham chiếu của các file KTC readonly
và installer cũ chỉ bảo vệ thư mục này khi nó đã tồn tại. Trên máy thật, các file
không phải symlink có thể khiến All-Config ghi đè macro upstream hoặc làm cập nhật
KTC không nhất quán.
**Đã chọn:** Yêu cầu đủ sáu symlink hợp lệ do installer KTC-Easy tạo trước mọi
deploy; luôn loại trừ `toolchanger/readonly-configs/` khỏi `rsync`. All-Config chỉ
quản lý `toolchanger-config.cfg`, `tools/T*.cfg` và override riêng.
**Đã loại:** Deploy bản readonly đóng gói trong repository hoặc chỉ cảnh báo sau
khi đã thay đổi cấu hình.
**Lý do:** Xác lập một chủ sở hữu duy nhất, giữ luồng update KTC chính thức và
dừng an toàn trước khi chạm máy nếu KTC chưa được cài đúng.

## 2026-08-22 — Kết thúc thử nghiệm camera và quay về Axiscope PF2

**Bối cảnh:** kTAMV không nhận ổn định lỗ nozzle dưới ánh sáng hiện tại; cả
kTAMV và ToolVision đều gặp nhiều vật thể/phản xạ giống nozzle. Người dùng chọn
quay về công tắc cơ học.
**Đã chọn:** Gỡ toàn bộ kTAMV và kích hoạt `[axiscope]` với `pin: ^PF2`, tọa độ
`X=68, Y=-10, Z=7`, 10 mẫu. Không đặt `config_file_path`; kết quả chỉ được báo
để duyệt vì năm tool được định nghĩa trong năm file riêng.
**Đã loại:** Tăng dung sai detector camera hoặc cho Axiscope tự ghi vào
`printer.cfg`.
**Lý do:** Microswitch đã có dữ liệu lặp lại thực tế, không phụ thuộc ánh sáng;
chế độ báo cáo tránh section tool trùng và giữ nguyên offset production đã kiểm
chứng bằng bản in.

## 2026-08-22 — Dọn clone Home cũ nhưng giữ runtime rollback

**Bối cảnh:** Home của máy còn `~/All-Config-Voron`, `~/axiscope`,
`~/axiscope.bak`, `~/Tool-Vision` và `~/tool-vision-env`, dễ bị hiểu nhầm là
trùng lặp sau khi chuyển sang kTAMV.
**Đã chọn:** Archive rồi xóa `~/All-Config-Voron` và `~/axiscope.bak` vì không
có service, process, symlink, cron hoặc updater sử dụng. Giữ `~/axiscope`,
`~/Tool-Vision` và `~/tool-vision-env` vì service/symlink rollback vẫn trỏ vào
đó. Recovery archive nằm ngoài config active tại
`~/printer_data/config_backups/home-folder-cleanup-20260822-213300/`.
**Đã loại:** Xóa thẳng cả năm folder hoặc giữ hai clone legacy trong Home.
**Lý do:** Làm gọn danh sách Home mà không tạo symlink hỏng hoặc phá khả năng
quay lại Axiscope/ToolVision sau thử nghiệm kTAMV.

## 2026-08-22 — Tạm chuyển backend hiệu chuẩn XY sang kTAMV

**Bối cảnh:** Người dùng cần tạm gỡ ToolVision để thử nghiệm trực tiếp kTAMV với
camera MF-500. Installer kTAMV upstream tại commit `72421f2` đã cũ, tự chạy
`apt`/chỉnh giờ, dùng trùng port 8085 và sinh sai header Moonraker.
**Đã chọn:** Không chạy installer upstream. Cài checkout `~/kTAMV` được pin,
venv riêng, user service port 8086 và cấu hình
`Printer-Setup/ktamv.cfg`; tắt upload cloud. ToolVision service/config/updater
bị vô hiệu hóa tạm, nhưng source, venv, symlink, PF2 state và kết quả được giữ.
**Đã loại:** Purge `~/Tool-Vision`, xóa dữ liệu đã học hoặc cho hai server dùng
chung port 8085.
**Lý do:** Cho phép thử kTAMV có giám sát mà vẫn rollback nhanh, tránh thay đổi
package hệ thống và tránh mất dữ liệu ToolVision.

## 2026-08-22 — Tách runtime ToolVision khỏi cây cấu hình Mainsail

**Bối cảnh:** Installer ToolVision từng tạo `config/Tool-Vision/` để chứa file
cấu hình Klipper, include Moonraker và backup cũ, khiến root cấu hình lộn xộn và
dễ bị hiểu nhầm với repository runtime `~/Tool-Vision`.
**Đã chọn:** Quản lý cấu hình máy tại
`config/Printer-Setup/tool_vision.cfg`, đặt `[update_manager tool-vision]` trực
tiếp trong `moonraker.conf`, lưu backup dưới
`~/printer_data/config_backups/tool-vision/` và dữ liệu sinh tự động dưới
`config/Generated-Data/ToolVision/`.
**Đã loại:** Xóa `~/Tool-Vision` hoặc gom source runtime vào `config/`. Thư mục
`~/Tool-Vision` là Git checkout production mà `tool-vision.service`, Moonraker
Update Manager và các symlink `klippy/extras/tool_vision*.py` sử dụng trực tiếp.
**Lý do:** Mainsail chỉ hiển thị cấu hình cần chỉnh, trong khi runtime Git vẫn
có thể cập nhật độc lập và không làm hỏng service/Klipper module.

## 2026-08-09 — Tự động loại trừ file Markdown khi đồng bộ sang máy in

**Bối cảnh:** Thư mục `config/` chứa file `README.md` hướng dẫn. Khi người dùng chạy script đồng bộ `install.sh` hoặc `update.sh`, các file `.md` bị copy vào `~/printer_data/config/` của Klipper, gây lộn xộn giao diện quản lý file của Mainsail.
**Đã chọn:** Thêm `--exclude "README.md" --exclude "*.md"` vào lệnh `rsync` trong cả `install.sh` và `update.sh`.
**Đã loại:** Xóa hoàn toàn file README khỏi kho Git (làm mất tài liệu hướng dẫn trên GitHub).
**Lý do:** Giữ trọn vẹn tài liệu đẹp trên GitHub cho người phát triển, đồng thời giữ thư mục cấu hình trên máy in hoàn toàn sạch sẽ.

## 2026-08-09 — Chiến lược Z-Offset: Giá trị In Thực Tế + Mốc Tham Chiếu Công Tắc

**Bối cảnh:** Kết quả đo Z-offset bằng công tắc tự động (Axiscope switch) cho thấy độ lặp lại tốt nhưng khi in thực tế lớp 1 không phẳng đẹp bằng bộ thông số đã tinh chỉnh khi in (`T1: 0.228, T2: -0.295, T3: -0.268, T4: 0.086`) do các yếu tố lực đẩy đàn hồi của switch, vị trí đo $Y=-10$ và giãn nở nhiệt ở nhiệt độ in.
**Đã chọn:** Sử dụng bộ giá trị đã kiểm chứng in thực tế đẹp làm cấu hình sản xuất trong `printer.cfg`. Sử dụng giá trị đo của công tắc làm mốc tham chiếu phần cứng (Baseline Delta) để kiểm tra độ trôi sau này.
**Đã loại:** Ép dùng giá trị đo công tắc thô chưa bù lực cản (gây hở sợi ở T1/T4 và cào bàn ở T3).
**Lý do:** Đảm bảo 100% chất lượng bản in lớp đầu tiên hoàn hảo mà vẫn tận dụng được công tắc cơ học để kiểm tra phần cứng nhanh khi thay thế nozzle.

## 2026-08-09 — Cấu hình chân Microswitch Z-Offset sang PF2 (Manta M8P V2)

**Bối cảnh:** Người dùng lắp đặt công tắc vi mô để đo Z-offset giữa các tool tại tọa độ X:68, Y:-10, Z:7 và đấu nối vào cổng PF2 + GND trên bo mạch BTT Manta M8P V2 thay vì PF4.
**Đã chọn:** `pin: ^PF2` trong section `[axiscope]` của `calibration.cfg`.
**Đã loại:** `pin: ^PF4` — không khớp với đấu nối thực tế trên phần cứng.
**Lý do:** Khớp chính xác với sơ đồ chân thực tế, cổng PF2 hoàn toàn độc lập và không trùng với bất kỳ endstop nào của stepper X/Y/Z.

## 2026-08-06 — Đồng bộ thư mục sao lưu và cấu hình tải về lên GitHub

**Bối cảnh:** Người dùng yêu cầu đồng bộ toàn bộ lịch sử sao lưu (`extras/backups/`) và bản tải cấu hình (`extras/Config download/`) lên GitHub để phòng ngừa rủi ro hỏng máy tính cá nhân.
**Đã chọn:** Bỏ bỏ qua (un-ignore) `extras/backups/` và `extras/Config download/` trong `.gitignore`, tiếp tục bảo mật nghiêm ngặt các file nhạy cảm (`*.secrets`, `moonraker.secrets`, `wpa_supplicant.conf`, `*.key`, `*.pem`, `*.env`, `*.log`).
**Đã loại:** Chỉ giữ sao lưu cục bộ (mất dữ liệu nếu phần cứng máy tính hỏng).
**Lý do:** Đáp ứng nhu cầu an toàn dữ liệu trên cloud của người dùng mà vẫn đảm bảo 100% không lộ thông tin nhạy cảm.

## 2026-06-30 — Vị trí tham chiếu Zero cho Bed Mesh

**Bối cảnh:** `zero_reference_position` của bed mesh được đặt thành `170, 203` (vị trí probe), nhưng Klipper định nghĩa đây là vị trí *nozzle*, không phải vị trí probe.
**Đã chọn:** `174, 168` — tâm vật lý của bàn in 350x350 nơi nozzle đứng khi homing Z.
**Đã loại:** `170, 203` — đây là vị trí vật lý của probe, gây sai lệch Z-offset do bề mặt bàn in không đồng nhất.
**Lý do:** Khi nozzle ở `174, 168` và probe Cartographer có Y offset +35mm, probe đo Z0 tại Y=203. Điều này đảm bảo điểm zero của bed mesh khớp chính xác với điểm homing Z, loại bỏ trôi Z-offset.

## 2026-06-28 — Tăng QGL Retry Tolerance lên 0.0075

**Bối cảnh:** Quad Gantry Leveling (QGL) bị hủy với lỗi giả "đánh số motor" (motor numbering).
**Đã chọn:** `retry_tolerance: 0.0075`
**Đã loại:** `retry_tolerance: 0.005` (giá trị gốc) — quá chặt, gây lỗi QGL giả.
**Lý do:** Dung sai gốc quá nghiêm ngặt cho độ chính xác cơ khí của máy in, gây thử lại và hủy QGL không cần thiết. 0.0075 vẫn nằm trong phạm vi độ chính xác cân bằng chấp nhận được.

## 2026-06-23 — Tăng check_gain_time Heater Bed lên 240s

**Bối cảnh:** Nhiễu điện từ SSR gây xung ADC trên thermistor bàn in, kích hoạt shutdown giả "không gia nhiệt đúng tốc độ mong đợi".
**Đã chọn:** `check_gain_time: 240` (4 phút)
**Đã loại:** `check_gain_time: 120` (2 phút gốc) — quá ngắn; xung nhiễu SSR trong giai đoạn gia nhiệt ban đầu kích hoạt shutdown giả.
**Lý do:** Tăng cửa sổ giám sát cho heater đủ thời gian thể hiện tăng nhiệt độ ngay cả khi có xung nhiễu ADC tạm thời từ SSR.
