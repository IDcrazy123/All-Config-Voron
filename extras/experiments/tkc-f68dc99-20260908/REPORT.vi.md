# Báo cáo tích hợp và thử nghiệm TKC — 2026-09-08

## Kết luận

Đã dọn phần TKC cũ khỏi vị trí hoạt động, cài mới và tích hợp upstream
`f68dc99ff5bdc7307b2157532d9c97d25a3fc67f` vào máy `192.168.1.43` và kho cấu hình.
T0 đạt ba lượt ban đầu. Đã thử T0–T4: T1, T2 và T4 trả kết quả; T3 không đạt
độ lặp. **Chưa đủ điều kiện dùng kết quả làm Z offset production.**
Sau yêu cầu thử riêng, T3 native đạt hai lượt lạnh và ba lượt tại setpoint 150/70;
ba median nóng -0.206/-0.210/-0.222 mm, range giữa lượt 0.016 mm. Xem mục 8:
nhiệt bed còn dao động, không được coi chênh với bộ lưu là sai số tuyệt đối.
Không áp bất kỳ Z đo mới nào. Kiểm tra cuối xác nhận toàn bộ XYZ runtime và
khối SAVE_CONFIG giữ nguyên, máy ready, XYZ homed, active/detected T0, heater target 0.

Lỗi phần mềm đáng chú ý: cache mất bù XY sau lượt Z-only; khôi phục toolchanger
báo thành công dù máy vẫn uninitialized; một số hướng dẫn không khớp implementation.
Có mẫu nhiễu thực tế ở T2/T3, chưa xác định nguyên nhân phần cứng/cảm biến.

## 1. Phạm vi và điều kiện

- Đọc AGENTS.md và chín file quy tắc `.agents/`, KNOWN_ISSUES, TODO, DECISIONS;
  đối chiếu lịch sử ngày 2026-09-06/07, hướng dẫn TKC và mã đang cài thật.
- Máy Voron 2.4 / KTC-Easy, T0–T4; Cartographer V3 với plugin Python **1.9.0**.
- Người vận hành xác nhận bàn trống, không có vật cản, di chuyển thông thường không va chạm.
- Thử lạnh, target các heater 0; nhiệt nozzle khoảng 32–38 °C, bed khoảng 27 °C.
  Không thử heat-soak, in lớp đầu, hoặc hiệu chuẩn camera XY.
- Touch model hiện có: threshold 1819, z_offset -0.05; không thay threshold,
  số mẫu, dung sai, PID, dòng motor hoặc giới hạn chuyển động production.
- Mỗi phép đo dùng `SAVE_CONFIG=0 CLEAN_NOZZLE=0`; không coi DRY_RUN là phép đo thật.
- Điểm T0 X174/Y168; `EXPERIMENTAL_RANDOM_RADIUS=0` để hạn chế biến số vị trí.
  Secondary dùng XY production đã lưu để bù đúng điểm nozzle.

## 2. Dọn cũ và đánh giá cài đặt

Kiểm kê đầu phiên phát hiện source cũ `5e55137` và thư mục `config/tool_calibrator`
còn tồn tại; service system/user và liên kết extras TKC đã được gỡ, include bị comment.
Vì vậy đây là phần còn sót của lần gỡ trước, không phải một service TKC đang chạy.

Sao lưu config thật, config PC, moonraker.asvc, source Git bundle và archive TKC.
Chuyển source/cấu hình cũ vào remote backup rồi xác minh hai vị trí cũ không còn.
Không đụng Klipper, KTC-Easy, kTAMV, firmware hoặc kho backup lịch sử khác.
Đây là dọn sạch vị trí hoạt động bằng lưu trữ có thể phục hồi, không xóa mất backup.

Clone mới và chạy đúng `./scripts/install.sh --user-service`. Installer hoàn thành,
Python env riêng, links extras và user service hoạt động. Thêm include và Update Manager
thủ công theo chính output installer. Klipper nạp cấu hình thật thành công.
Moonraker nhận repo main pristine, không warning và không chậm commit ở lần kiểm tra.
Vision `/health` OK, camera_ready=true về cuối phiên; scale/matrix chưa được dạy.
Không đồng nhất service healthy với camera XY đã sẵn sàng hiệu chuẩn.

Kiểm thử: `env/bin/python -m unittest discover -s tests -v`, **140 tests / OK**.
Python PC không có pytest; bài kiểm tra được thực hiện bằng unittest trong env thật
trên host, không cài thêm thư viện vào klippy-env production.

Điều chỉnh riêng máy trong master config: Touch nozzle, điểm 174/168, home không ngẫu nhiên;
macro tiện ích mặc định SAVE_CONFIG=0. Source TKC không có patch cục bộ.
Seed `[tool_offsets]` chỉ chứa XY production, không chứa Z mới. Mã Z-only không đọc
trực tiếp offset từ đối tượng `[tool Tn]`, nên bước seed là cần thiết ở cài mới.
Script All-Config bổ sung preflight runtime và giữ nguyên offsets, backups, manifest TKC
qua rsync. Bản seed trong Git là snapshot, không ghi đè file máy đã tồn tại.

Backup: `extras/backups/pre-tkc-install-20260908-200037/`; remote
`/home/voron/printer_data/config_backups/pre-tkc-install-20260908-200037/`.
Hướng dẫn sử dụng: [tkc-commissioning-20260908.md](../../docs/tkc-commissioning-20260908.md).

## 3. Kết quả đo

### T0 trước khi mở rộng

| Lượt | Số lần chạm | Biên độ nhóm được chọn (mm) | Median Touch trước cập nhật gốc Z (mm) |
|---|---:|---:|---:|
| T0-1 | 5 | 0.002 | -0.397434 |
| T0-2 | 5 | 0.004 | khoảng -0.0066 |
| T0-3 | 5 | 0.010 | khoảng +0.0066 |

Cả ba được Cartographer chấp nhận. Sau lượt đầu chuyển từ mốc scan-home sang Touch,
hai lần home kế tiếp hiệu chỉnh khoảng +0.007/-0.007 mm. Không coi -0.397 mm của
lượt đầu là sai số nozzle T0: hệ tọa độ trước Touch khác. TKC luôn gán T0=0 theo
định nghĩa, vì thế bảng summary T0 không phải phép đo độ lặp độc lập.

### So sánh phép đo lạnh với giá trị đang dùng

Đơn vị mm; chênh = TKC báo cáo trừ Z production. Người vận hành bổ sung rằng bộ lưu
được đo ở **hotend 150 °C, bed 70 °C**, trong khi bảng này đo lạnh.
**Không cùng điều kiện nhiệt: các chênh dưới đây không phải sai số hiệu chuẩn và
không chứng minh bộ lưu sai.** Đây cũng không phải so sánh với chuẩn đo lường tuyệt đối.

| Tool | Z production | Z TKC | Chênh | Kết quả |
|---|---:|---:|---:|---|
| T0 | 0.0000 | 0.000 | 0.000 | Mốc quy ước; ba lượt Touch đạt |
| T1 | +0.2360 | +0.266 | +0.030 | Đạt bộ chọn mẫu, một lượt |
| T2 | -0.3160 | -0.326 | -0.010 | Đạt bộ chọn mẫu nhưng có outlier |
| T3 | -0.1896 | Không hợp lệ | — | Không đạt sau 10 lần chạm |
| T4 | +0.1200 | +0.196 | +0.076 | Đạt bộ chọn mẫu, đo riêng sau phục hồi |

Lượt `TOOLS=0,1,2,3,4` dừng tại T3, `CONTINUE_ON_ERROR=0` hoạt động đúng.
Sau khi xác nhận detected T3 và chạy G28 phục hồi, lượt `TOOLS=0,4` đạt trong
115.29 s và trả về T0. T4 dùng T0 baseline mới, không dùng baseline cũ sau G28.

| Tool | Mẫu thô đã ghi (mm, làm tròn 4 số) | Toàn bộ spread | Nhóm được chọn |
|---|---|---:|---:|
| T1 | 0.2561, 0.2661, 0.2661 | 0.0100 | 0.0100 |
| T2 | -0.3259, -0.3239, -0.1599, -0.3259 | 0.1660 | 0.0020 |
| T3 | -0.1459, -0.1579, 0.0001, -0.1179, -0.1439, 0.5241, -0.1519, -0.1359, 0.1901, -0.1419 | 0.6820 | Không có nhóm đạt |
| T4 | 0.1961, 0.1981, 0.1961 | 0.0020 | 0.0020 |

Cartographer tìm nhóm ba mẫu có biên độ nhỏ nhất trong cửa sổ năm mẫu gần nhất,
dừng khi nhóm đạt 0.010 mm, tối đa mười lần. T2 qua gate đúng implementation,
nhưng outlier vẫn cần điều tra. T3 lỗi trước bước tính delta của TKC; chưa thể quy
nguyên nhân cho CAN, cơ khí, nozzle bẩn hay phép trừ offset chỉ từ các mẫu này.
Không lặp thêm nhóm toàn bộ sau khi đã thấy T3 bất ổn và lỗi cache.

## 4. Đánh giá logic Z

1. Chọn T0, tới điểm tham chiếu và gọi TOUCH_HOME; Cartographer thực hiện tiếp xúc,
   lấy median đã bù touch-model và đặt lại gốc Z. TKC coi contact_ref=0 sau home.
2. Đổi tool với safe clearance rồi đưa carriage tới điểm T0 cộng XY offset nozzle.
   Lệnh `toolhead.manual_move` dùng tọa độ raw, không đi qua ToolGcodeTransform;
   dấu cộng khớp transform KTC-Easy đang cài, tránh bù hai lần.
3. TOUCH_PROBE của tool phụ không home lại. Plugin trả raw carriage contact đã trừ
   cùng touch-model offset. TKC dùng delta=measured_z-0 và làm tròn 0.001 mm.
4. Nếu model chung là m và trigger raw tương ứng h0, hn, sau T0 home mốc dịch
   h0-m thì kết quả tool phụ là hn-(h0-m)-m = hn-h0. Không tự trừ thêm -0.05 lần nữa.
   Điều này giả định cùng model, tọa độ và điều kiện chạm; không chứng minh từng tool
   có cùng độ biến dạng/độ nhạy cảm ứng khi chạm.
5. SAVE_CONFIG=0 bỏ cả lưu file lẫn áp runtime. Tuy nhiên vẫn thay mốc Z khi home,
   chuyển động, cache kết quả và đổi tool; không phải phép đọc thuần túy.

**Đính chính tài liệu cũ của All-Config:** nhận định “Cartographer gắn shuttle không
đo được chiều dài nozzle” chỉ đúng với đo Scan không tiếp xúc. Plugin 1.9.0 thật
cho thấy Touch dùng nozzle tiếp xúc, `TouchMode.offset=(0,0,0)`, homing touch threshold
và trigger carriage; vị trí gắn shuttle tự nó không loại khả năng đo tương đối.
Lý do chưa dùng production hiện nay là dữ liệu nhiễu và các lỗi phần mềm, không phải
chỉ vì cảm biến gắn shuttle. Không lấy mô tả “contactless” tổng quát của adapter
để suy luận hành vi riêng của Touch.

## 5. Lỗi, bất cập và đối chiếu tài liệu

| Phát hiện | Bằng chứng / phân loại | Ảnh hưởng và hướng xử lý |
|---|---|---|
| T3 không đạt repeatability | Máy thật; 10 mẫu, spread 0.682 mm | Không lưu Z; điều tra coupling, độ cứng/nozzle và tín hiệu Touch có kiểm soát |
| T2 có outlier dù PASS | Máy thật; spread toàn bộ 0.166 vs nhóm 0.002 mm | Summary cần hiển thị cả mẫu bị loại, không chỉ delta |
| Khôi phục tool báo thành công sai | Máy thật: sau T3, `status=uninitialized`, `tool_number=-1`, detected=3; log vẫn “reconciled” | `_reconcile_toolchanger_state` không xác minh trạng thái sau fallback thất bại; cần adapter đúng KTC-Easy và kiểm tra hậu điều kiện |
| Z-only cache làm mất XY lần kế tiếp | Tái hiện offline bằng source nguyên bản, [reproduce_xy_cache.py](reproduce_xy_cache.py) | Cached `{z}` được ưu tiên hơn file XY; T2 từ 174.82/168.24 trở thành 174/168. Cần merge từng trục và fallback production |
| Cài mới không thừa kế XY trong tool objects | Kiểm tra code; placeholder offsets rỗng | Đã seed đúng production XY khi tích hợp; nên tự đọc từng `[tool Tn]` nếu thiếu dữ liệu TKC |
| Baseline cache không gắn với home/model epoch | Kiểm tra code: chỉ handler klippy:ready, không hủy baseline theo home/gốc/model | Không dùng lệnh tool phụ riêng sau đổi gốc Z; luôn kèm T0 mới |
| `carto_max_samples`/`samples` truyền MAX_SAMPLES nhưng plugin hiện tại không khai báo tham số này | Đối chiếu `TouchProbeMacroParams` 1.9.0 rỗng; số mẫu lấy từ TouchModeConfiguration | Không coi TKC SAMPLES là số Touch; cần kiểm tra khả năng API và tài liệu rõ phiên bản |
| Fallback probe có thể chọn lệnh home | Kiểm tra code `touch_probe_gcode` có fallback TOUCH_HOME/TOUCH | Trên hệ khác có thể reset gốc tool phụ; máy này đã chỉ định chính xác TOUCH_PROBE |
| Abort “ngay lập tức” chưa được bảo đảm | SOP khẳng định tức thì; G-code calibration chạy đồng bộ; không thử abort vật lý phiên này | Không dùng CALIBRATION_ABORT làm emergency stop; cần đường hủy độc lập và thử có kiểm soát |

Các sửa mới được xác minh: không còn NameError khi đọc status; elapsed dương trên
các snapshot đang chạy; điểm yêu cầu secondary theo baseline+bù XY (sai số tọa độ
thực tế vài micron); không tái hiện chênh Y=5 mm của bản trước. Cơ chế phục hồi
tool vẫn không đạt dù bài unit test upstream cho phần này đạt.

Đối chiếu Markdown upstream:

- `docs/HUONG_DAN_CAI_DAT_VA_CAP_NHAT.md` và output installer: bố cục một include,
  thư mục tool_calibrator và user service đúng với cài thực tế. Update Manager cần
  thêm rõ ràng, không suy từ “installer thành công” rằng toàn bộ tích hợp đã xong.
- `docs/QUY_TRINH_VAN_HANH.md`: phân biệt Touch nozzle với Scan là đúng; lệnh Z-only
  phù hợp. Bảng mẫu số liệu chỉ minh họa, không phải bằng chứng máy này. SAMPLES
  trong code chính là burst camera; macro Z không truyền nó cho Touch.
- `agent/WORKFLOW.md`: mô tả tính Z “dựa vào touch-model offset” thiếu giải thích
  model đã được plugin bù và triệt tiêu theo T0. Mô tả dry-run bay qua trạm Z cao
  thêm 5 mm không khớp code: nhánh Z bị bỏ hoàn toàn khi dry_run.
- `agent/SAFETY.md` vẫn mô tả nâng Safe_Z trước mọi XY, trong khi docs mới/code
  dùng hai mức và bypass lift ở Touch local. Cần cập nhật sơ đồ để tránh hiểu nhầm.
- `agent/BACKUP.md` phần đầu còn đường dẫn root tool_offsets.cfg và section `[tool 1]`,
  trong khi cài mới dùng `tool_calibrator/tool_offsets.cfg` / `[tool_offsets]`.
- SOP mô tả TKC_STATUS có version/service; handler hiện chủ yếu in trạng thái,
  Safe_Z/backend và cache. Muốn kiểm tra version/service phải đọc `/health`/Update Manager.

Không coi các phát hiện static/offline là lỗi đã gây ra chuyển động nguy hiểm trên máy.
Không sửa source upstream trong phiên này; hướng khắc phục được cung cấp để review.

## 6. Checkpoint sau thử lạnh và bước tiếp theo

Klipper ready, XYZ homed, active/detected T0, X173.1/Y163.8/Z10, mọi heater target 0.
TKC service enabled/active; source pristine; đọc macro status và CHECK_OFFSETS thành công.
`verification.json` xác nhận Z và cả XY runtime giữ nguyên; SAVE_CONFIG không đổi.
Đã restart và G28 chuẩn sau thử nghiệm để kết thúc ở mốc home vận hành của máy.

Ưu tiên: sửa cache XY và recovery KTC, bổ sung hủy baseline theo epoch; sau đó điều tra
T3 và outlier T2 ở cùng điểm, điều kiện nozzle/thermal có kiểm soát. Chỉ khi nhiều lượt
độc lập đạt mới đánh giá in lớp đầu trước khi thay giá trị production. T1/T4 chỉ có
một kết quả chấp nhận mỗi tool, chưa chứng minh độ lặp dài hạn hoặc độ chính xác tuyệt đối.

## 7. Bằng chứng

- [Installation transcript](evidence/install.txt), [140 upstream tests](evidence/tests.txt).
- [T0 samples](evidence/t0-klippy-excerpt.txt), [T0–T4 samples and errors](evidence/final-measurement-klippy-excerpt.txt).
- [Failed group state](evidence/all-run1-final.json), [T4 completion](evidence/t4-run1-final.json).
- [XY cache reproduction](evidence/xy-cache-reproduction.txt), [verification](evidence/verification.json).
- `evidence/requests.jsonl`: requests/responses có timestamp; log thô `.log` giữ local,
  không đưa các log hệ thống lớn lên Git. Các excerpt chỉ giữ sự kiện liên quan phép đo.

## 8. Thử riêng T3 theo yêu cầu bổ sung

Sau checkpoint ở mục 6, người vận hành yêu cầu thử riêng T3 và làm rõ điều kiện
production 150 °C nozzle / 70 °C bed. Đã lấy T0 baseline mới rồi chuyển T3 tới
G-code X174/Y168, tương ứng raw X174.325/Y168.525 với XY đang dùng. Chạy native
`CARTOGRAPHER_TOUCH_PROBE` để tách khỏi vòng điều phối TKC.

Hai lượt lạnh độc lập tại cùng điểm trả cùng median -0.165414 mm. Lượt đầu
chọn nhóm có range 0.006 mm; lượt hai chọn nhóm range 0.002 mm nhưng có mẫu
-0.0594 mm, tức toàn bộ range 0.106 mm. Không kết luận lỗi T3 luôn tái hiện;
cũng không coi hai median bằng nhau là đủ loại nhiễu phần cứng/cảm biến.

Về Z35: source f68dc99 bỏ nâng 35 ở Touch local khi safe_z bị comment, nhưng
vẫn gọi `move_to_safe_z` trước đổi tool thật và `depart_station` khi lỗi.
Log toàn bộ cho thấy Z35 tại các ranh giới đổi tool và lỗi T3; native probe
lặp tại T3 không có Z35. Ở máy này KTC còn tự di chuyển tới dock Z khoảng 343.
Một fallback clearance 35 mm không được suy ra từ việc bed hiện trống; phần
điều phối chưa có cấu hình độc lập rõ ràng cho đường bed trống và đổi tool.
Không sửa global clearance trong phiên này; đã ghi nhận bất cập về chuyển động
dư thừa và khác biệt giữa hướng dẫn “speed-up” với trải nghiệm đổi tool thực tế.

`CALIBRATE_TOOL_Z TOOL=3` còn tự trả T0 cuối lệnh, nên nếu dùng macro này để đo
lặp T3 sẽ có đổi tool đi/về và hai lần clearance. Bài native giữ T3 tại chỗ loại
bỏ cả đổi tool và Z35 giữa các lượt; đây là phép thử cô lập, không phải thay đổi
đường đi mặc định của TKC.

### T3 nóng — setpoint nozzle 150 °C / bed 70 °C

Chỉ gia nhiệt T0, T3 và bed; T1/T2/T4 target 0. Giữ setpoint trong quá trình theo
dõi rồi lấy lại T0 baseline nóng bằng native TOUCH_HOME; T3 native PROBE sử dụng
cùng hệ tọa độ và công thức delta của TKC nhưng không chạy vòng điều phối TKC.
Không thay giới hạn Cartographer: plugin 1.9.0 vẫn kiểm tra nhiệt độ/target với
epsilon nhiệt 2 °C nội tại. Không sửa PID, threshold, model hoặc dung sai mẫu.

Dự kiến giữ trong cửa sổ ổn nhiệt 5 phút liên tục, nhưng **không đạt** tiêu chí
bed ±0.5 °C; T0 cũng có dao động 150–151 °C. Bed đọc tới 75.41 °C dù target 70,
sau đó giảm. Không kết luận đó chắc chắn là nhiệt thật hay nhiễu ADC từ telemetry.
Đã kiểm tra log trước khi đo; không có lỗi heater mới trong đoạn kiểm tra.
Phép thử được thực hiện sau thời gian gia nhiệt/giữ setpoint, nhưng không được
gắn nhãn “heat-soak ổn định hoàn toàn”. Khi chuyển tool trước lượt 1, bed lại
đọc 71.59 °C; hạn chế này phải đi cùng mọi so sánh kết quả.

| Lượt native T3 | Mẫu thô (mm) | Median (mm) | Range nhóm chọn (mm) | T3 / bed sau lượt (°C) |
|---|---|---:|---:|---|
| Nóng 1 | -0.188, -0.210, -0.204, -0.206 | -0.206 | 0.006 | 150.12 / 70.81 |
| Nóng 2 | -0.216, -0.206, -0.210 | -0.210 | 0.010 | 150.19 / 70.06 |
| Nóng 3 | -0.212, -0.220, -0.230, -0.222, -0.222 | -0.222 | 0.002 | 150.31 / 69.87 |

Cả ba qua bộ chọn mẫu Cartographer. Mean ba median = **-0.212667 mm**;
range giữa lượt = **0.016 mm**. So với giá trị lưu T3 -0.1896 mm, mean lệch
-0.023067 mm. So với native T3 lạnh -0.165414 mm, mean nóng thấp hơn 0.047253 mm.
Không tách được đóng góp riêng của nhiệt, thời gian, lần gá tool và độ lặp cảm biến
bằng thiết kế thử này; không được quy toàn bộ chênh cho giãn nở nhiệt.

Kết luận bổ sung: T3 không phải luôn thất bại; các phép đo tại chỗ có thể đạt,
nhưng median nóng đang dịch dần và bed chưa ổn nhiệt chặt. Không mở rộng thêm
chuỗi nóng toàn bộ T0–T4 hoặc thay Z production từ ba lượt này. Cần thử ở điều kiện
nhiệt ổn định và nhiều lần tháo/gá sau khi xử lý vấn đề điều phối để đánh giá đầy đủ.

Bằng chứng: [isolated Touch samples](evidence/t3-isolated-excerpt.txt),
`t3-native1/2-console.json`, `t3-hot-native1/2/3-console.json`,
`t3-hot-pre1.json`, `t3-hot-post1/2/3.json`, `thermal-soak-observed.jsonl` và
telemetry có timestamp trong `requests.jsonl`. Đã trả T0 và tắt toàn bộ heater
sau phép thử nóng; không lưu hoặc áp dụng Z mới.

**Xác minh cuối sau thử nóng:** `verification-after-hot.json` ghi Klipper ready,
XYZ homed, active/detected T0, X173.6/Y166.5/Z10, mọi heater target 0.
Toàn bộ XYZ runtime và khối SAVE_CONFIG vẫn khớp trước cài đặt.
`config-hashes.json` xác nhận sáu file cấu hình/script đã triển khai khớp PC/máy.
