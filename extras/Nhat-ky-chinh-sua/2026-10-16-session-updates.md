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

## 2. Sửa từng nhóm CFG và script theo audit, giữ nguyên mọi file Python

### Mục tiêu
Người dùng chấp thuận sửa lần lượt, yêu cầu rà soát/tra cứu trước và ưu tiên không can thiệp `.py` để giảm rủi ro sau cập nhật. Phạm vi thực hiện là repository và Git; chưa triển khai lên máy in.

### Sao lưu
- [Snapshot trước sửa](</D:/Desktop/All-Config-Voron-main/Voron 5 Tool/extras/backups/pre-cfg-software-hardening-20261016-200256/README.md>): 44 file gốc, giữ đường dẫn, đối chiếu SHA-256 trước ghi. Manifest cũng lưu hash33filePython để kiểm tra nguyên vẹn; không sửa backup có sẵn.

### Nhóm 1 — Start/end/cancel/resume
- `print-macros.cfg`: tắt nhiệt trước chuyển động kết thúc/hủy; chặn Z5 theo headroom vật lý rồi nâng phần còn lại bằng relative; clear mesh/live offset trước lift. Giữ retract10mm của tool nóng đang gắn.
- Bỏ restoreZtheotool khi UNSELECT qua `RESTORE_AXIS=`; helper đọc lại shuttle rỗng sau dock, giữ ít nhất cao độ thoát dock và minZyêucầu, không vượt trần. Sau bản in thấp shuttle đỗ cao thay vì hạ về cao độ thấp trước đây; cần quan sát khi commissioning.
- CANCEL_PRINT override do người dùng sở hữu hoàn tất native cancel trước các thao tác tùy chọn, nên dock thất bại không ngăn base cancel. Nhánh crash/unhomed/KTCerror không chạyXYZ/dock.
- `tool-crash.cfg`: latch required/tool; CONFIRM_TOOL_RECOVERY CONFIRM=1 chỉ clear sau initialize+verify+helperđọclại, khôngXYZ. Cho T=... rõràng nếu sự kiện không xác địnhtool. Cancel giữ latch; latch không lưu quaRESTART.
- KTCerrorhook user-owned đổi PAUSE cópark sang cùng handler noXYZ, không sửa readonly. LED saucancel/END có latch giữ báoerror.
- RESUME kiểm tra paused, latch, originaltool và sensorfilament; helperriêng đọc sau initialize và sauwait nhiệt, giữ policy sensor chủ độngdisable. G32/QGL chặn thao tác cạnhtranh nhưng vẫn dùng trongPRINT_START.
- PRINT_START preflight nhiệt từngtool/bed, filament dùng/T0purge vàphase trước sideeffect; mới virtualSDstateprinting vẫn hợp lệ. Ghi used_tool_count dùng cho exclusionguard.

### Nhóm 2 — Axiscope/exclusion/shaper bằng CFG
- `calibration-probe.cfg`: override public batchcommand và gọi lại các command/hook thấp của Axiscope; T0đođầutiên; lift trước T0cuối, reportkếtquảkhôngsave. Không gọi backendbatchcũ vốn đổiT0trướclift. Giữsamples5, geometry, heat150 và yêu cầuCONFIRM/attended.
- EXCLUDE_OBJECT wrapper chỉ chặn yêu cầu exclude ởjobnhiềutool/khôngrõ; query/RESET và singletoolđãkhai báo vẫn chạy. Giữobjectlabelscho mesh. Đây là mitigation; chưa sửa lỗiPythonstateE.
- `toolchanger-config.cfg`: defaultfrequency0 chọn cảprofileglobal, không để inheriteddamping0,1 ghiđèX0,124/Y0,080. Frequencydươngoptintừngaxis. SET_INPUT_SHAPER forwardnative vàinvalidatecache. Không thay giátrị đo hoặccurrent/limits; cần xácnhậnshapereffective trênmáy.
- `filament-dryer.cfg`: guard phase bao gồmcalibrating, tránh khởiđộng cạnhtranh.

### Nhóm 3 — Backup/deploy/test/tài liệu
- `Sync-OrcaProfiles.ps1`: validate destination trướcghi, backup timestamp+suffixunique, refuseexistingbackup; stage/commit chínhbackupphiênhiện tại. Testrepo tạm thực hiện2commit và giữunrelatedstaged/untracked đúngscope; không đồngbộAppDatathật.
- `install.sh`: từchốikhácSAVE_CONFIG trướcwrite vàrechecktrướcsao lưu. `VORON_ALLOW_CALIBRATION_REPLACE=1` chỉ cho replacement đãreview, vẫnbackupfirst. Không giảđịnhguard bảo vệ mọi giátrị manualởfilekhác; rsyncfixturesvẫnstub.
- Thêm `extras/tests/Test-ProductionCfg.ps1`: orchestration/testcode nhúng, giữ nguyên33file.py. Hai invariantsOct9khôngcònhợp lệ đượcđánhdấusupersededrõràng, thaybằngpreservation/semanticcontracts hiện tại. Cleanerfixture được cung cấp configheater thực để kiểmtraguardmới; khôngbỏassertioncleaner.
- Cập nhật tài liệu hiện hành vềPF4, inventory20preset, hướngdẫnrecovery/deploy và trạngthái localchưadeploy. Thêm `extras/docs/cfg-hardening-2026-10-16.md`. Báocáo/nhậtkýlịchsử giữbấtbiến.

### Kiểm tra
- Runnercuối:68bài,62đạt,6skip (4LinuxPTY,2invariantlịchsử đãthaythế),0failure/error; log `extras/audits/2026-10-16/hardening-tests.txt`.
- ReplayZ0,28/30/342/345/347, tooloffsetdương/âm vàmanualoffset, hot/cold, nohoming/error, crashcancel khôngXYZ; simulateddockfailure sau nativecancel/heateroff.
- Testresume sensorhết/disable, toolmismatch, waitnhiệt/freshhelper; AxiscopeT0first/final-lift; excludequery/reset/single/multi; shaperglobal/custom/cache; driftrefusal/optin; syncGitthậttrongrepo tạm.
- ParseJinja/includeliveoffline; bash -n riêng3script, PowerShellparse2script, JSON20preset và gitdiffcheck đạt.
- Một lượtintegrationfixture đầu chạy WindowsPowerShellcon thiếu Get-FileHash trong môi trường kếthừa; runnerđổi sangchínhPowerShellhostđangchạy và2commitfixtuređạt. Không thayfunctionhashscript thật để né lỗi môi trường.
- Hashxácnhận printer/SAVE_CONFIG, hardware,5tool,readonly,Mainsail,20JSON và33Python giữnguyên. Không gửiG-code/API/SSH/restart/gia nhiệt/chuyểnđộng hoặc deploy.

### Kết quả và phần còn lại
Các nhóm đã sửa được offline; chưa có chấpnhận vật lý. Trướcdeploy cần đọc trạngthái/driftlive, backupmáy, nạpCFGđồngbộ và kiểm alias/helper; sauđó thử ngắn cógiámsát, xemshapereffective/parkcao, commissionPF2 riêng. LỗiPythonexclude vẫn đượcguard, chưabackport. Timerwallclock/thermalsoak/primearea/tallpartroute và thaycảmbiếnT1 vẫnchờdữliệu/commissioning; khôngđoántham số.

Commit/push chỉ thayđổi của tácvụ vàsnapshotmới; giữAGENTS.md/ba thưmụcbackupuntracked từtrước. Không sửa `.agents/` ngoàiGit hoặc cácgiátrịphầncứng.
