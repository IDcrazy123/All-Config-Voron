# Yêu cầu sửa upstream Tool-Klipper-Calibration

Ngày lập: 2026-09-08. Đây là tài liệu bàn giao sửa mã, tài liệu và kiểm thử;
không phải xác nhận rằng các kết quả đo đã đủ điều kiện ghi vào máy.

**Repository duy nhất cần sửa:**
[IDcrazy123/Tool-Klipper-Calibration](https://github.com/IDcrazy123/Tool-Klipper-Calibration).
Mọi đường dẫn mã nguồn, tests, `docs/`, `agent/` và script được yêu cầu sửa dưới đây
đều thuộc repository TKC này. Bản sửa phải hoạt động như tính năng/sửa lỗi của TKC,
không hardcode địa chỉ máy, số tool, tọa độ hay offset của máy thử nghiệm.

**All-Config-Voron chỉ là nguồn bằng chứng sử dụng.** Không sửa repository cấu hình
này, không đưa workaround vào macro của máy để thay cho sửa TKC. Các giá trị máy
trong báo cáo là dữ liệu tái hiện và fixture kiểm thử, không phải mặc định mới của TKC.

## 1. Prompt giao việc

> Hãy làm việc trong repository https://github.com/IDcrazy123/Tool-Klipper-Calibration.
> Đọc hướng dẫn dành cho agent của chính repository TKC và toàn bộ báo cáo này,
> rồi sửa mã nguồn, tests và tài liệu của Tool-Klipper-Calibration theo các mục
> TKC-01 đến TKC-11. Trước tiên so sánh HEAD hiện tại với commit được khảo sát;
> chỉ sửa những vấn đề còn tồn tại. Ưu tiên cache XY, phục hồi toolchanger và
> tính hợp lệ của baseline. Viết regression test bằng API sát Klipper/KTC thật,
> cập nhật các tài liệu .md liên quan và báo cáo từng yêu cầu đã xử lý.
> Không nới dung sai hoặc bỏ mẫu xấu để làm phép đo đạt. Không thay PID, threshold,
> offset production hay giảm clearance toàn cục dựa trên suy đoán. Tách phần sửa
> phần mềm khỏi điều tra nhiễu cơ khí/nhiệt. Tài liệu này không yêu cầu tự kết nối
> và chạy máy thật; kiểm thử phần cứng phải là bước riêng có người vận hành.
> All-Config-Voron chỉ chứa bằng chứng: không sửa hoặc commit vào repository đó,
> không triển khai lên 192.168.1.43. Bàn giao patch/commit trong TKC và kế hoạch
> kiểm thử phần cứng để người dùng thực hiện riêng.

## 2. Phiên bản, môi trường và giới hạn bằng chứng

- Upstream: [Tool-Klipper-Calibration tại commit khảo sát](https://github.com/IDcrazy123/Tool-Klipper-Calibration/tree/f68dc99ff5bdc7307b2157532d9c97d25a3fc67f).
- Máy: Voron 2.4, KTC-Easy, năm tool T0–T4; host `192.168.1.43`.
- Cartographer V3, plugin Python `cartographer3d` **1.9.0**. Đo bằng **Touch**:
  tiếp xúc nozzle; không đánh đồng với Scan khi đánh giá cảm biến gắn trên shuttle.
- Source upstream không patch; cài bằng `scripts/install.sh --user-service`,
  service `tool_calibrator`, port 8090. Bộ unittest có **140 test đạt** trên host.
- Touch model giữ nguyên threshold `1819`, model `z_offset=-0.05`.
- Điểm tham chiếu T0 X174/Y168; secondary có bù XY. Home dùng
  `CARTOGRAPHER_TOUCH_HOME EXPERIMENTAL_RANDOM_RADIUS=0`; probe dùng
  `CARTOGRAPHER_TOUCH_PROBE` tường minh.
- Thử nghiệm không lưu kết quả mới: `SAVE_CONFIG=0`, `CLEAN_NOZZLE=0`.
  Convenience macro đã đặt mặc định không lưu; không suy rộng mặc định này sang
  lệnh upstream `CALIBRATE_TOOL_OFFSETS` vốn vẫn có mặc định lưu.
- Bộ XYZ production và khối SAVE_CONFIG giữ nguyên. Kết thúc phiên máy ready,
  XYZ homed, active/detected T0, tất cả heater target 0.
- Bộ cấu hình và bằng chứng đã lưu trong repository All-Config-Voron, commit
  `8879af6`. Xem [báo cáo đầy đủ](https://github.com/IDcrazy123/All-Config-Voron/blob/8879af6/extras/experiments/tkc-f68dc99-20260908/REPORT.vi.md),
  [hướng dẫn tích hợp](https://github.com/IDcrazy123/All-Config-Voron/blob/8879af6/extras/docs/tkc-commissioning-20260908.md) và
  [xác minh cuối phiên](https://github.com/IDcrazy123/All-Config-Voron/blob/8879af6/extras/experiments/tkc-f68dc99-20260908/evidence/verification-after-hot.json).

Các nhãn trong bảng phân biệt: **thực tế** = thấy trên máy;
**offline** = tái hiện bằng chương trình không điều khiển máy;
**đọc mã** = rủi ro hoặc thiếu sót cần kiểm chứng, chưa phải sự cố thực tế đã chứng minh.
P1 cần giải quyết trước khi chấp nhận hiệu chuẩn production; P2 cải thiện quy trình,
tương thích và tài liệu. Mức ưu tiên không khẳng định mọi mục đều đã gây hỏng đo.

## 3. Danh sách yêu cầu sửa

| ID | Ưu tiên | Vấn đề | Mức bằng chứng |
|---|---|---|---|
| TKC-01 | P1 | Cache Z-only làm mất bù XY ở lượt tiếp theo | Offline + đọc mã |
| TKC-02 | P1 | Recovery báo thành công dù toolchanger còn uninitialized | Thực tế + đọc mã |
| TKC-03 | P1 | Baseline cache thiếu cơ chế vô hiệu hóa theo thay đổi hệ tọa độ | Đọc mã |
| TKC-04 | P1 | Fallback Touch có thể gọi home trên secondary; thiếu kiểm tra kết quả mới | Đọc mã |
| TKC-05 | P1 | Thiếu dữ liệu và tiêu chí đánh giá độ lặp giữa các lượt | Thực tế; nguyên nhân nhiễu chưa rõ |
| TKC-06 | P2 | Lượt đo riêng T3 vẫn đổi về T0/nâng Z35 | Thực tế + chính sách hiện tại |
| TKC-07 | P2 | Điều kiện nhiệt và giới hạn backend chưa khớp quy trình đo | Thực tế + đọc mã |
| TKC-08 | P2 | File offsets mới chưa lấy được XY từ tool production | Đọc mã; đã workaround khi tích hợp |
| TKC-09 | P2 | Tham số mẫu Touch chưa đảm bảo tương thích plugin 1.9.0 | Đọc mã |
| TKC-10 | P2 | Tuyên bố abort tức thời chưa được chứng minh | Đọc mã/tài liệu; chưa thử live bản này |
| TKC-11 | P2 | Tài liệu và báo cáo cài/gỡ chưa phản ánh đủ hành vi | Đối chiếu tài liệu/hiện trạng |

### TKC-01 — Giữ XY khi cache chỉ có Z

**Hiện tượng:** khi cache rỗng, T2 lấy XY từ file và tới X174.820/Y168.240.
Sau khi cache thành `{2: {"z": -0.316}}`, cùng phép đo tới X174/Y168,
mất bù X0.820/Y0.240. Điểm tiếp xúc thay đổi giữa các lượt nên không còn so sánh
đúng cùng vị trí trên bed.

**Vị trí:** `klippy/extras/tool_calibrator.py`, `_execute_z_calibration`
(khoảng dòng 1136, nhánh lấy XY khoảng 1150); cuối quy trình gán
`self.cached_offsets = results` (khoảng 1580). Số dòng ứng với commit khảo sát.

**Tái hiện:** [reproduce_xy_cache.py](https://github.com/IDcrazy123/All-Config-Voron/blob/8879af6/extras/experiments/tkc-f68dc99-20260908/reproduce_xy_cache.py),
[kết quả offline](https://github.com/IDcrazy123/All-Config-Voron/blob/8879af6/extras/experiments/tkc-f68dc99-20260908/evidence/xy-cache-reproduction.txt). Chạy từ thư mục source TKC
bằng Python của env, với `PYTHONPATH=.`. Script không gửi lệnh tới máy thật.

**Yêu cầu:** merge theo từng trục, không thay toàn bộ bản ghi XYZ bằng kết quả Z;
phân biệt giá trị 0 hợp lệ và trục chưa có; xác định thứ tự nguồn dữ liệu và giữ
thông tin nguồn. Khi cache thiếu X/Y phải lấy nguồn hợp lệ tiếp theo.

**Nghiệm thu:** test cache rỗng, cache chỉ Z, thiếu riêng X hoặc Y, XY bằng 0,
override tường minh, chuỗi Z→Z và XY→Z→Z. T2 phải giữ cùng XY đã bù ở các lượt.

### TKC-02 — Recovery có kiểm chứng trạng thái

**Hiện tượng:** sau lỗi T3, thông báo cho rằng đã reconcile, nhưng trạng thái
vẫn `uninitialized`, tool number `-1`, sensor phát hiện T3. Lệnh chọn `T3` lỗi.
Standard `G28` đã khôi phục được trong phiên; đây không phải lý do để luôn tự G28.

**Vị trí:** `_reconcile_toolchanger_state` khoảng dòng 906. Kiểm tra
`gcode.commands`, giả định `active_tool` và fallback `Tn` không khớp API thực tế;
thông báo thành công không phụ thuộc hậu điều kiện.

**Yêu cầu:** adapter cho API Klipper/KTC thực; phân biệt thiếu thuộc tính với
thật sự uninitialized. Chỉ initialize theo trạng thái/sensor đã xác minh, không
đoán tool hoặc đổi tool mù. Kiểm tra trạng thái sau lệnh; nếu chưa phục hồi thì
báo lỗi rõ, dừng chuỗi và giữ thông tin lỗi ban đầu.

**Nghiệm thu:** mô phỏng API thực, sensor T3/tool=-1, lỗi initialize, sensor mâu thuẫn,
command không tồn tại, phục hồi thành công và thất bại. Không được báo thành công
khi hậu điều kiện chưa đạt; test không dựa vào MagicMock tự sinh thuộc tính.
Xem [trạng thái group thất bại](https://github.com/IDcrazy123/All-Config-Voron/blob/8879af6/extras/experiments/tkc-f68dc99-20260908/evidence/all-run1-final.json) và
[log đo](https://github.com/IDcrazy123/All-Config-Voron/blob/8879af6/extras/experiments/tkc-f68dc99-20260908/evidence/final-measurement-klippy-excerpt.txt).

### TKC-03 — Baseline phải thuộc đúng phiên/hệ tọa độ

**Rủi ro:** `cached_reference_z_result` tồn tại nhưng chưa có cơ chế đầy đủ để
vô hiệu hóa sau homing, đổi Z origin, model hoặc điều kiện tham chiếu. Chưa cố ý
gây phép đo sai bằng stale baseline trên máy.

**Yêu cầu:** quản lý hiệu lực baseline theo sự kiện/epoch thực có thể quan sát;
ghi model, điểm XY, thời điểm, nhiệt độ và trạng thái tham chiếu. Khi không thể
xác minh còn hợp lệ, yêu cầu đo T0 mới. Xác định rõ những sự kiện phải invalidate.

**Nghiệm thu:** baseline mới được dùng trong cùng điều kiện; home/origin/model
thay đổi phải làm cache hết hiệu lực; restart và lỗi giữa chuỗi không tái dùng
dữ liệu không hợp lệ. Không biến cache nhiệt độ thành bảo đảm heat-soak giả.

### TKC-04 — Bảo toàn ngữ nghĩa Touch và freshness

**Rủi ro:** fallback probe có các tên lệnh Touch/Home có thể đổi Z origin khi đo
secondary; `_get_last_z_result` đọc nhiều trường nhưng cần kiểm tra kết quả mới.
Phiên này cấu hình lệnh tường minh nên chưa thấy sự cố do fallback.

**Yêu cầu:** adapter phân biệt home tham chiếu và probe secondary; không tự chọn
lệnh reset Z cho secondary. Kết quả phải mới, hữu hạn và thuộc đúng lần gọi.
Không dùng giá trị cũ nếu command lỗi hoặc không tạo mẫu.

**Nghiệm thu:** test command không hỗ trợ, kết quả cũ/NaN/không có, command lỗi,
model khác 0; secondary probe không đổi origin. Công thức không trừ model offset
hai lần: với `m` đã được plugin tính vào kết quả, biểu thức
`hn - (h0 - m) - m = hn - h0`. Giữ kiểm thử dấu XY: chuyển động raw dùng **cộng**
XY offset production trong cách triển khai đã khảo sát.

### TKC-05 — Đánh giá mẫu nhiễu và độ lặp giữa các lượt

**Quan sát:** T2 có mẫu lệch lớn nhưng bộ mẫu chọn vẫn đạt; T3 thất bại trong group,
sau đó native probe riêng đạt. Đây chưa chứng minh lỗi số học TKC hoặc lỗi cảm biến.

**Yêu cầu:** lưu toàn bộ raw samples, mẫu được chọn/loại, số lần thử, range toàn bộ
và range được chọn; thời gian, XY, tool, sự kiện tháo/lắp và nhiệt độ thực.
Tách kiểm tra độ lặp trong một lần probe khỏi độ lặp giữa các lượt/đổi tool.
Nếu upstream không cung cấp raw samples qua API, ghi rõ thiếu dữ liệu và bổ sung
adapter/log phù hợp; không dựng dữ liệu giả từ median.

**Nghiệm thu:** kết quả không che mẫu xấu; tolerance hiện tại không bị nới để pass.
Báo cáo so sánh chỉ coi tương đương khi điều kiện đo đủ tương đương. Tiêu chí
chấp nhận production giữa các lượt cần được xác định riêng trước thử máy.

### TKC-06 — Giảm nâng Z35 thừa khi đo riêng cùng tool

**Quan sát:** `safe_z` đã bỏ cấu hình để dùng Carto speedup cục bộ, nhưng bước đổi
tool vẫn gọi `move_to_safe_z`. `CALIBRATE_TOOL_Z TOOL=3` kết thúc trả về T0,
gây thêm đổi tool và nâng Z35. Native probe lặp cùng T3 không có các lượt nâng này.
Người vận hành xác nhận bàn trống trong phiên; không suy rộng thành mọi đường dock
đều an toàn ở Z thấp.

**Yêu cầu:** tách clearance probe cục bộ, clearance đổi tool và clearance khi lỗi;
ghi lý do nâng Z. Cho phép chế độ đo lặp/giữ tool hiện tại với baseline hợp lệ và
chính sách kết thúc rõ ràng. Không tự bỏ bước T0 cần thiết để thiết lập baseline.

**Nghiệm thu:** đo lặp cùng T3 không đổi tool thì không nâng Z35 chỉ vì vòng lặp;
đổi tool vẫn giữ clearance yêu cầu; trạng thái/đường đi không rõ xử lý bảo thủ.
Không sửa bằng cách đặt safe_z toàn cục về 0 hoặc bỏ bảo vệ dock/camera.

### TKC-07 — Đo và so sánh ở điều kiện nhiệt có ghi nhận

**Quan sát:** bộ lưu đo tại nozzle150°C/bed70°C; nhóm đầu chỉ đo nhiệt độ thường.
Khi thử nóng, backend TKC kiểm tra ngưỡng 150°C trong khi target150 có overshoot;
native plugin có giới hạn riêng max + epsilon2°C. Không sửa giới hạn trong phiên.
Bed từng báo 75.41°C với target70, chưa xác định dao động thật hay lỗi đọc.

**Yêu cầu:** khai báo khả năng backend theo phiên bản; chờ nguội/ổn định có timeout,
báo lý do từ chối, không âm thầm nâng giới hạn hoặc bỏ kiểm tra sensor. Ghi target
và nhiệt độ thực, thời gian giữ nhiệt, tiêu chí ổn định và kết quả đạt/chưa đạt.
Tách điều tra PID/ADC/phần cứng khỏi bản sửa TKC.

**Nghiệm thu:** overshoot, sensor thiếu/không hợp lệ, timeout, hủy chờ và nhiệt ổn
định được xử lý rõ; không ghi nhãn “ổn định” chỉ vì đã đợi đủ thời gian.

### TKC-08 — Lấy XY production khi file TKC mới

File TKC mới chưa tự đọc XY từ các đối tượng `[tool Tn]` của máy. Phiên tích hợp
đã seed XY production vào `[tool_offsets]` để khắc phục tại cấu hình.
Yêu cầu adapter lấy theo từng trục, không ghi đè giá trị người dùng tường minh,
không coi 0 là thiếu, nêu nguồn dữ liệu trong status. Test khởi tạo mới với
file rỗng và tool production có XY; phối hợp với TKC-01 để tránh hai logic fallback.

### TKC-09 — Tham số số mẫu Touch theo phiên bản

Nhánh `carto_max_samples`/samples có thể thêm `MAX_SAMPLES`, trong khi
`TouchProbeMacroParams` của plugin1.9.0 không khai báo tham số tương ứng và Touch
dùng `TouchModeConfiguration`. Đây là kết luận đọc mã, không phải đã kiểm thử mọi
phiên bản. Yêu cầu phát hiện capability hoặc từ chối tùy chọn không hỗ trợ với
thông báo rõ; test lệnh được tạo theo phiên bản. Tài liệu phải phân biệt camera
burst `SAMPLES` với số mẫu Touch, không quảng bá một override chưa có hiệu lực.

### TKC-10 — Abort có giới hạn và bằng chứng

Tài liệu mô tả abort tức thời nhưng G-code đồng bộ có thể cản xử lý abort đang
xếp hàng. Chưa thử abort vật lý trên commit này; lỗi ở phiên bản trước chỉ là
lịch sử. Rà soát `cmd_CALIBRATION_ABORT` và cơ chế reactor/queue, xác định điểm
có thể hủy và cách backend đang chạy dừng. Test hủy khi chờ nhiệt, giữa tool,
trong đo và khi lỗi; công bố độ trễ đã đo. Không gọi cooperative abort là E-stop,
không hứa khả năng dừng mà backend không hỗ trợ.

### TKC-11 — Đồng bộ tài liệu và vòng đời cài/gỡ

- `docs/QUY_TRINH_VAN_HANH.md`: `TKC_STATUS` được mô tả có version/service nhưng
  handler hiện không cung cấp đầy đủ; ví dụ cần phân biệt minh họa và dữ liệu thật.
  Sửa tuyên bố abort theo TKC-10.
- `agent/WORKFLOW.md`: DRY_RUN mô tả dừng cao hơn station5mm nhưng nhánh Z thực tế
  bị bỏ qua; sửa theo hành vi thật hoặc triển khai đúng rồi test. Làm rõ model
  offset Touch, tránh trừ hai lần.
- `agent/SAFETY.md`: cập nhật clearance hai cấp theo TKC-06, không tuyên bố mọi XY
  luôn phải dùng cùng Z35 nếu mã có chính sách probe cục bộ khác.
- `agent/BACKUP.md`: sửa ví dụ file ở root/section `[tool1]` thành đường dẫn và
  schema thực tế phù hợp, gồm `[tool_offsets]` khi áp dụng.
- Gỡ cũ còn source/config có thể là chính sách giữ dữ liệu, không mặc nhiên là
  lỗi phải xóa hết. Installer/uninstaller cần báo đường dẫn đã xóa/giữ và manifest
  rõ; bảo toàn backup, offsets và cấu hình ngoài phạm vi TKC.
- Cài mới đã thành công; include/update manager cần thao tác theo output installer
  không được ghi thành lỗi cài đặt. Chỉ rà soát installer/uninstaller của TKC về
  bảo toàn dữ liệu. Script deploy All-Config nằm ngoài phạm vi sửa báo cáo này.

## 4. Số liệu thực tế để AI kiểm tra kết luận

Tất cả giá trị Z và range dưới đây dùng mm. Z production:

| Tool | Z lưu | Kết quả nhóm lạnh | Ghi chú |
|---|---:|---:|---|
| T0 | 0 | 0 theo định nghĩa reference | Không phải bằng chứng độ chính xác tuyệt đối |
| T1 | +0.236 | +0.266 | Range mẫu 0.010 |
| T2 | -0.316 | -0.326 | Raw range 0.166, selected range 0.002 |
| T3 | -0.1896 | Thất bại | 10 touches, raw range 0.682 |
| T4 | +0.120 | +0.196 | Chạy riêng T0,T4 sau phục hồi; range 0.002 |

T0 ban đầu ba lượt được chấp nhận, selected range 0.002/0.004/0.010.
T4 không được chạy trong group lỗi T3. Không lấy chênh lạnh–bộ lưu150/70 làm
“sai số hiệu chuẩn” vì điều kiện không tương đương.

T3 riêng **native Cartographer**, khác chuỗi TKC toàn bộ:

| Điều kiện | Median từng lượt | Selected range từng lượt |
|---|---|---|
| Lạnh, cố định XY174.325/168.525 | -0.165414; -0.165414 | 0.006; 0.002 |
| Setpoint nozzle150/bed70 | -0.206; -0.210; -0.222 | 0.006; 0.010; 0.002 |

Ba lượt nóng có mean **-0.212667**, range giữa lượt **0.016**;
mean trừ Z lưu = **-0.023067**. Độ dịch mean nóng so với hai lượt lạnh riêng khoảng
**-0.047253**, nhưng không thể quy toàn bộ cho nhiệt: còn thời gian, remount và
biến động cảm biến. Các lần probe được chấp nhận không đồng nghĩa ổn định toàn chuỗi.

Giữ target khoảng 8 phút, nhưng **không đạt cửa sổ ổn định liên tục 5 phút** đã
theo dõi. Trước lượt nóng1: T0 151.29°C, T3 149.81°C, bed71.59°C; sau lượt1/2/3,
T3 lần lượt150.12/150.19/150.31°C, bed70.81/70.06/69.87°C. Chưa thử đủ nhóm nóng
T0–T4 lặp nhiều vòng. Không áp kết quả này vào production.

## 5. Bằng chứng cần đọc

- [Báo cáo chi tiết, logic và đối chiếu tài liệu](https://github.com/IDcrazy123/All-Config-Voron/blob/8879af6/extras/experiments/tkc-f68dc99-20260908/REPORT.vi.md).
- [Log T0](https://github.com/IDcrazy123/All-Config-Voron/blob/8879af6/extras/experiments/tkc-f68dc99-20260908/evidence/t0-klippy-excerpt.txt),
  [log nhóm tool](https://github.com/IDcrazy123/All-Config-Voron/blob/8879af6/extras/experiments/tkc-f68dc99-20260908/evidence/final-measurement-klippy-excerpt.txt),
  [log T3 riêng](https://github.com/IDcrazy123/All-Config-Voron/blob/8879af6/extras/experiments/tkc-f68dc99-20260908/evidence/t3-isolated-excerpt.txt).
- [Snapshot trước nóng1](https://github.com/IDcrazy123/All-Config-Voron/blob/8879af6/extras/experiments/tkc-f68dc99-20260908/evidence/t3-hot-pre1.json),
  [sau nóng1](https://github.com/IDcrazy123/All-Config-Voron/blob/8879af6/extras/experiments/tkc-f68dc99-20260908/evidence/t3-hot-post1.json),
  [sau nóng2](https://github.com/IDcrazy123/All-Config-Voron/blob/8879af6/extras/experiments/tkc-f68dc99-20260908/evidence/t3-hot-post2.json),
  [sau nóng3](https://github.com/IDcrazy123/All-Config-Voron/blob/8879af6/extras/experiments/tkc-f68dc99-20260908/evidence/t3-hot-post3.json).
- [Quan sát ổn định nhiệt](https://github.com/IDcrazy123/All-Config-Voron/blob/8879af6/extras/experiments/tkc-f68dc99-20260908/evidence/thermal-soak-observed.jsonl),
  [request/response theo thời gian](https://github.com/IDcrazy123/All-Config-Voron/blob/8879af6/extras/experiments/tkc-f68dc99-20260908/evidence/requests.jsonl).
- [140 test upstream](https://github.com/IDcrazy123/All-Config-Voron/blob/8879af6/extras/experiments/tkc-f68dc99-20260908/evidence/tests.txt), [cài đặt](https://github.com/IDcrazy123/All-Config-Voron/blob/8879af6/extras/experiments/tkc-f68dc99-20260908/evidence/install.txt),
  [kiểm tra bảo vệ deploy](https://github.com/IDcrazy123/All-Config-Voron/blob/8879af6/extras/experiments/tkc-f68dc99-20260908/evidence/deployment-filters.txt).

Nếu chỉ gửi một file này, AI nhận việc vẫn có phạm vi và số liệu tóm tắt;
để tái hiện và đối chiếu đầy đủ, dùng các liên kết bằng chứng tại commit cố định
của All-Config-Voron. Đọc bằng chứng không yêu cầu sửa repository cấu hình.

## 6. Những điểm không được kết luận sai hoặc sửa lại mù

- Chưa tái hiện NameError `time`/crash status ở bản này; thời gian elapsed dương.
- Sai reference Y5mm trước đây đã xử lý; dấu cộng XY hiện phù hợp đường di chuyển raw.
- Không coi cảm biến trên shuttle khiến Touch không đo được nozzle; Touch khác Scan.
- Không trừ thêm model -0.05 vào kết quả đã bù; phải chứng minh bằng test công thức.
- Không báo lỗi “tất cả tool không ổn định”: T3 group lỗi, các phép đo khác có
  kết quả với giới hạn cụ thể; chưa đủ bằng chứng chấp nhận production.
- Không quy nguyên nhân outlier cho PID, cơ khí, CAN hoặc Cartographer khi chưa
  có kiểm tra phân biệt. Không dùng native T3 pass làm bằng chứng TKC all-tool pass.

## 7. Kế hoạch nghiệm thu bản sửa

1. Trong repository Tool-Klipper-Calibration, ghi SHA bắt đầu, diff với commit
   khảo sát, đọc hướng dẫn của TKC. Lập bảng từng ID:
   còn lỗi / đã sửa upstream / cần thêm bằng chứng. Chạy lại 140 test baseline.
2. Sửa P1 trước, thêm regression test có failure trước sửa và pass sau sửa;
   dùng trạng thái/API thực tế cho KTC và Cartographer. Không cần kiểm thử máy
   cho lỗi cache có thể tái hiện offline.
3. Sửa P2, cập nhật tài liệu cùng commit liên quan. Kiểm tra schema config, mặc
   định lưu, đường dẫn backup và tính tương thích phiên bản; không làm mất XY/Z cũ.
4. Bàn giao diff/commit thuộc TKC, kết quả test và giới hạn còn lại. Các bước 5–6
   là kịch bản đề xuất cho người vận hành, không phải lệnh triển khai hoặc chạy máy
   dành cho AI nhận yêu cầu sửa upstream này.
5. Kịch bản thử máy: T0 → T3 riêng lặp cùng tool → T0/T3 có đổi tool → đủ
   T0–T4 khi ổn định. Ghi nhiệt thực và heat-soak; dùng cùng điều kiện150/70 nếu
   so với bộ lưu và chỉ khi backend cho phép. Giữ `SAVE_CONFIG=0` trong xác minh.
6. Chỉ đánh giá lưu production sau khi có tiêu chí và kết quả lặp đạt, kiểm tra
   trạng thái phục hồi, kiểm chứng số liệu so sánh cùng điều kiện. Thử abort live
   là ca riêng có chuẩn bị, không chèn bất ngờ vào phép đo đang chạy.

**Đầu ra AI phải trả:** mã sửa + tests + tài liệu trong Tool-Klipper-Calibration;
bảng truy vết TKC-01…11;
bằng chứng test thực sự đã chạy; nội dung chưa kiểm chứng; hướng dẫn cập nhật và
rollback; báo cáo riêng kết quả phần cứng nếu sau này được thực hiện.
