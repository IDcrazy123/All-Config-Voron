# Cấu trúc thư mục

## Tổng quan

```
All-Config-Voron-main/                  ← Thư mục workspace gốc (chứa các công cụ AI)
│
├── .agents/                            ← Hệ thống quy tắc AI (bạn đang ở đây)
│   ├── AGENTS.md                       ← Điểm vào — đọc đầu tiên
│   ├── PROJECT.md                      ← Mô tả dự án & phần cứng thực tế
│   ├── DIRECTORY.md                    ← File này
│   ├── WORKFLOW.md                     ← Quy trình làm việc từng bước
│   ├── SAFETY.md                       ← Quy tắc an toàn
│   ├── STYLE.md                        ← Phong cách code & quy tắc ngôn ngữ
│   ├── BACKUP.md                       ← Quy tắc sao lưu
│   ├── LOGGING.md                      ← Mẫu nhật ký hàng ngày
│   ├── GIT_RULE.md                     ← Quy tắc Git
│   ├── PROMPTS.md                      ← Mẫu xử lý yêu cầu
│   ├── DECISIONS.md                    ← Nhật ký quyết định kỹ thuật
│   ├── KNOWN_ISSUES.md                 ← Lỗi đã biết & cách khắc phục
│   ├── CHANGELOG.md                    ← Nhật ký thay đổi phiên bản
│   └── TODO.md                         ← Công việc đang chờ
│
├── Voron 5 Tool/                       ← ⭐ THƯ MỤC GIT REPO CHÍNH & DUY NHẤT
│   ├── README.md                       ← Tài liệu tổng quan dự án (English - Phân tích 10 thuật toán lõi)
│   ├── README.vi.md                    ← Tài liệu tổng quan dự án (Tiếng Việt - Bản dịch đối ứng 1:1)
│   │
│   ├── config/                         ← ⭐ Cấu hình Klipper ĐANG VẬN HÀNH (Production)
│   │   ├── README.md                   ← Tài liệu cấu hình & pinout (English)
│   │   ├── printer.cfg                 ← Cấu hình chính (includes, kinematics, SAVE_CONFIG offsets)
│   │   ├── moonraker.conf              ← Cấu hình Moonraker API server & update manager
│   │   ├── crowsnest.conf              ← Cấu hình streaming camera (WebRTC camera-streamer)
│   │   ├── KlipperScreen.conf          ← Cấu hình màn hình KlipperScreen (vi)
│   │   ├── mainsail.cfg                ← Macro giao diện Mainsail
│   │   │
│   │   ├── Printer-Setup/             ← Cấu hình phần cứng & macro máy in
│   │   │   ├── hardware.cfg            ← Định nghĩa MCU (Manta M8P V2), stepper X/Y/Z, heater bed
│   │   │   ├── fans-leds.cfg           ← Cấu hình quạt thùng, quạt bed, LED trạng thái 10 mức, đèn buồng in 100%
│   │   │   ├── calibration-probe.cfg   ← Cartographer V3 Touch/Scan, bed mesh, Axiscope Z switch (`PF2`)
│   │   │   ├── ktamv.cfg               ← kTAMV căn chỉnh XY camera & macro tự động 5 tool theo tọa độ học
│   │   │   ├── input-shaper.cfg        ← Thông số input shaper riêng biệt từng tool và bộ đệm tham số
│   │   │   ├── nozzle-clean.cfg        ← Bambu A1 silicone brush & purge bucket (CLEAN_NOZZLE)
│   │   │   ├── prime-lines.cfg         ← Macro prime line pipeline chia slot động cho T0–T4
│   │   │   ├── print-macros.cfg        ← PRINT_START/END, ngâm nhiệt thích ứng, rút sợi an toàn
│   │   │   ├── filament-dryer.cfg      ← Chế độ sấy nhựa tích hợp buồng in 4 vùng có xả ẩm định kỳ
│   │   │   ├── tool-crash.cfg          ← Watchdog chống rơi tool có lọc xung nhiễu & safe pause
│   │   │   ├── test-speed.cfg          ← Macro kiểm tra tốc độ trục (TEST_SPEED, TEST_Z_SPEED)
│   │   │   └── tool-temp-bench.cfg     ← Macro benchmark tốc độ gia nhiệt đầu in (MEASURE_TOOL_HEATUP)
│   │   │
│   │   ├── toolchanger/               ← Cấu hình StealthChanger
│   │   │   ├── toolchanger-config.cfg   ← Cài đặt toolchanger chính & tọa độ dock/switch
│   │   │   ├── tools/                   ← Định nghĩa từng tool (T0.cfg – T4.cfg kèm CAN EBB36)
│   │   │   └── readonly-configs/        ← File do plugin KTC-Easy quản lý (KHÔNG ĐƯỢC SỬA)
│   │   │
│   │   └── scripts/                    ← Shell script quản lý & triển khai
│   │       ├── install.sh              ← Script cài đặt cấu hình lần đầu (Lean deployment)
│   │       ├── update.sh               ← Script cập nhật cấu hình & auto backup
│   │       ├── cleanup-voron.sh        ← Dọn dẹp các bản backup rác cũ
│   │       ├── patches/                ← Các bản vá mã nguồn (kTAMV, tool_crash)
│   │       └── ktamv/                  ← File systemd service cho máy chủ kTAMV (cổng 8086)
│   │
│   └── extras/                         ← Tài liệu bổ sung & dữ liệu vận hành
│       ├── backups/                    ← 🔒 Bản sao lưu timestamped trước mỗi lần sửa (đồng bộ Git)
│       ├── retired-configs/            ← 📦 Cấu hình đã nghỉ hưu (ToolVision, TKC, KCC...)
│       ├── Nhat-ky-chinh-sua/         ← 📓 Nhật ký chỉnh sửa hàng ngày (Tiếng Việt)
│       ├── logs/                       ← File nhật ký Klipper & Moonraker thu thập offline
│       ├── docs/                       ← Tài liệu hướng dẫn & sơ đồ phần cứng chi tiết
│       ├── pictures/                   ← Ảnh chụp phần cứng, sơ đồ chân, vị trí dock
│       ├── gcode/                      ← File G-code thử nghiệm
│       ├── experiments/                ← Báo cáo và dữ liệu thử nghiệm (TKC, Cartographer, KCV...)
│       ├── klipper-patches/            ← Tài liệu & bản vá mã nguồn Klipper/KTC
│       ├── tool_crash/                 ← Tài liệu & module chống rơi tool
│       ├── Axiscope-reference/         ← Module & tài liệu tham chiếu Axiscope
│       ├── axiscope-cartographer/      ← Dữ liệu hiệu chuẩn Axiscope & Cartographer
│       ├── Orcasilcer setting/         ← Profile OrcaSlicer đã xuất
│       └── Config download/            ← Cấu hình tham khảo đã tải về
│
├── Orca Config/                        ← Profile OrcaSlicer (quản lý PA theo filament)
└── [Tàn dư ở root]                    ← ⚠️ CẢNH BÁO: Các file như `printer.cfg`, `print-macros.cfg`,
                                           `.tkc-*`, `extras/` ở root là bản sao cũ/thử nghiệm.
                                           TUYỆT ĐỐI KHÔNG sửa các file này. Mọi thay đổi production
                                           PHẢI nằm trong `Voron 5 Tool/`.
```

## Quy tắc thư mục

### `Voron 5 Tool/` — Thư mục Git Repository duy nhất
- Đây là thư mục gốc của Git repository (`origin/main`).
- Mọi lệnh Git (`git add`, `git commit`, `git push`) đều phải chạy trong thư mục `Voron 5 Tool/`.
- Thư mục cha `All-Config-Voron-main/` chỉ là workspace container chứa IDE config (`.agents/`, `.cursorrules`, `.clinerules`) và không phải là git repo.

### `Voron 5 Tool/config/` — Chỉ dành cho cấu hình Production
- Thư mục này đồng bộ trực tiếp với máy in qua `scripts/install.sh` và `scripts/update.sh`.
- **Chỉ lưu file cấu hình đang vận hành (production-ready).**
- Không bao giờ lưu file tạm, script thử nghiệm, hoặc bản nháp cấu hình ở đây.
- Các file tài liệu (`README.md`, `*.md`) trong `config/` được các script tự động loại trừ (`--exclude`) khi đồng bộ sang `~/printer_data/config/` để đảm bảo máy in luôn gọn gàng.

### `Voron 5 Tool/config/toolchanger/readonly-configs/` — Không chạm vào
- Các file này do plugin `klipper-toolchanger-easy` quản lý.
- **Tuyệt đối không sửa đổi thủ công các file trong thư mục này.**
- Mọi thay đổi ở đây sẽ bị plugin ghi đè.

### `Voron 5 Tool/extras/Nhat-ky-chinh-sua/` — Nhật ký hàng ngày
- Mỗi ngày một file: `YYYY-MM-DD-session-updates.md`.
- Ghi lại tất cả thay đổi cấu hình, bảng số liệu đo đạc, phân tích và sự cố cần khắc phục.
- Xem `LOGGING.md` để biết mẫu bắt buộc.

### `Voron 5 Tool/extras/backups/` — Bản sao lưu hệ thống
- Bản sao lưu tự động được tạo trước mỗi lần sửa đổi file cấu hình.
- Đã được theo dõi trên Git (theo quyết định an toàn dữ liệu đám mây) để phòng trường hợp hỏng máy tính cá nhân.
- Xem `BACKUP.md` để biết quy tắc đặt tên và quản lý.

### `Voron 5 Tool/extras/logs/` — File nhật ký hệ thống
- Sao chép từ máy in để phân tích offline khi cần điều tra sự cố.
- Tránh commit các file log quá lớn trừ khi được yêu cầu.
