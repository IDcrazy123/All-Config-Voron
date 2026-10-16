# Nhật ký — 2026-10-16

## 1. Rà soát CFG production và phần mềm liên quan

### Mục tiêu
Theo yêu cầu đọc dự án, xác định phần cần cải tiến/nâng cấp, ưu tiên phần mềm và CFG. Đây là đánh giá; chưa thay đổi hành vi máy in.

### Phạm vi và phương pháp
- Đọc quy tắc workspace/repository, vấn đề đã biết, TODO, quyết định, nhật ký và audit liên quan.
- Rà soát toàn bộ include chain production: 26 CFG, 195 section hiệu lực, 127 template; kiểm tra SAVE_CONFIG, host CONF, script triển khai, 20 profile JSON Orca và script đồng bộ.
- Đọc runtime tham chiếu Axiscope/tool_crash; đối chiếu nguồn primary Klipper, Axiscope và KTC tại revision e881fe4 từng được ghi nhận. Không coi revision lịch sử là trạng thái live hôm nay.
- Backup/lịch sử/ảnh/G-code lớn chỉ được kiểm kê hoặc đọc chọn lọc làm bằng chứng, không tuyên bố đã audit từng byte toàn bộ lịch sử hay generator upstream độc lập.
- Không kết nối máy in, gửi G-code, gia nhiệt, chuyển động, restart hoặc triển khai.

### File tạo mới
- `extras/docs/project-audit-2026-10-16.md` — báo cáo tiếng Anh gồm 13 nhóm phát hiện, mức ưu tiên, điều kiện tái hiện, hướng sửa và tiêu chí kiểm chứng.
- `extras/audits/2026-10-16/evidence.json` — kết quả render/check và SHA-256 của 56 file cấu hình/script/patch/profile đã rà soát.
- Nhật ký này — ghi nhận phiên đánh giá.

### Phát hiện chính
- PRINT_END tại Z345/max347 vẫn phát G1 Z5 trước clamp; cần chặn lift đầu và thống nhất hệ tọa độ.
- Crash pause không di chuyển nhưng custom cancel vẫn lift/dock/park nếu homed. Đính chính audit cũ: park Mainsail mặc định false; nguồn chuyển động hiện tại là custom cleanup.
- Axiscope gọi T0 cuối trước finish hook nâng Z; multi-tool exclude-object vẫn cần sửa runtime/kiểm chứng.
- RESUME chưa kiểm tra filament sensor theo tool đang gắn; PRINT_START còn thiếu guard gọi lại và kiểm tra sớm toàn bộ heater limits.
- Shaper global damping0,124/0,080 vẫn bị giá trị kế thừa KTC0,1/0,1 ưu tiên.
- Script sync Orca tạo backup nhưng không đưa backup vào scoped commit. Giữ nguyên thư mục backup untracked có từ trước phiên.
- Test so với backup cũ chưa cập nhật sau thay đổi cleaner và di chuyển lifecycle ngày15/10; tài liệu còn PF1 thay vì PF4, inventory19 thay vì20 và TODO TEST_Z_SPEED chưa phản ánh implementation hiện tại.
- Các đề xuất khác: bảo vệ calibration drift khi deploy, vùng prime/mesh/route cho vật cao, đồng hồ monotonic, tách state khỏi setter LED và quản lý phiên bản runtime/patch.

### Kiểm tra
- Python hệ thống có Jinja2 3.1.6; lần đầu dùng Python bundled thiếu Jinja2 nên chuyển interpreter sẵn có, không cài package.
- `python -m unittest discover -s extras/tests -v`: 38 bài,32 đạt,2 lỗi kỳ vọng cũ,4 bỏ qua vì cần LinuxPTY. Hai lỗi cụ thể: KeyError gcode_macro _PRINT_STATE và guard cleaner cũ0,5–1,0 không nhận fixture0,2 mới. Không quy kết hai lỗi này là CFG production không chạy.
- Harness cleaner:14/14 đạt. Parse20JSON, compile127template, bash -n từng script và parse PowerShell đạt.
- Render offline tái hiện lift quáZ; RESUME với sensor filament false vẫn phát RESUME_BASE; PRINT_START với trạng thái printing+paused vẫn phát CLEAR_PAUSE/G28; nhiệt vượt giới hạn chưa bị chặn tại entry.
- Không sửa CFG/CONF/script/profile, không sửa PID/current/limits/offset/dock hoặc KTCreadonly. Không cần backup cấu hình vì không ghi các file này.

### Kết quả và bước tiếp
Ưu tiên khôi phục test baseline đáng tin rồi sửa end/cancel/runout/start, tiếp theo Axiscope/exclude/shaper và backup/deploy. Giữ bố cục module hiện có. Mọi sửa đổi chức năng sau này cần backup và kiểm chứng theo từng nhóm; chưa thực hiện trong phiên đánh giá này.

Stage/commit/push chỉ báo cáo, evidence và nhật ký của phiên theo quy tắc Git; giữ nguyên AGENTS.md và ba thư mục backup untracked có từ trước.
