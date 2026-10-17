# Chỉ mục Tài liệu

[English](README.md) | [Tiếng Việt](README.vi.md)

Tài liệu hiện hành mô tả code production đang được nạp được rà soát ngày 2026-10-09. Báo cáo lịch sử được giữ bất biến và tách rõ để không nhầm lệnh retired với quy trình active.

## Tài liệu hiện hành

| Chủ đề | English | Tiếng Việt |
| --- | --- | --- |
| CFG software hardening 2026-10-16 | [Changes and commissioning](cfg-hardening-2026-10-16.md) | Local/offline-verified; not deployed; Python files unchanged |
| Dọn dẹp, tổng hợp lỗi và phục hồi 12/10/2026 | [Summary](cleanup-2026-10-12.md) | [Tổng hợp](cleanup-2026-10-12.vi.md) |
| Tổng duyệt code và đối chiếu máy 2026-10-09 | [Báo cáo](project-audit-2026-10-09.md) | Bản kỹ thuật tiếng Anh |
| Phản hồi G-code khởi động và lỗi còn tiềm tàng | [Rà soát bổ sung](startup-response-and-risk-review-2026-10-09.md) | Đã xác minh bản vá runtime; lỗi motion/exclusion vẫn mở |
| Điều chỉnh cấu hình cho máy khác | [Hướng dẫn](machine-adaptation.md) | Bản kỹ thuật tiếng Anh |
| Chia sẻ riêng từng file CFG hiện có | [Hướng dẫn đã thực hiện](sharing-cfg-files.md) | Phụ thuộc/chỗ sửa tại file; đã nạp máy hiện tại, chưa thử chuyển động/nhiệt |
| Cơ sở thiết kế chia sẻ CFG | [Đề xuất đã điều chỉnh](stealthchanger-sharing-proposal.md) | Phạm vi thực hiện nằm trong hướng dẫn phía trên |
| Tổng quan dự án | [README](../../README.md) | [README](../../README.vi.md) |
| Payload config active | [README](../../config/README.md) | [README](../../config/README.vi.md) |
| Profile OrcaSlicer | [README](../../Orca%20Config/README.md) | [README](../../Orca%20Config/README.vi.md) |
| Vận hành StealthChanger | [Guide](huong-dan-he-thong-stealthchanger.en.md) | [Hướng dẫn](huong-dan-he-thong-stealthchanger.md) |
| Đối chiếu triển khai Mainsail | — | [Hướng dẫn](danh-sach-doi-chieu-va-huong-dan-update-mainsail.md) |
| Dấu hiệu nhận biết lỗi hiệu chuẩn cũ | [Guide](legacy-calibration-troubleshooting.md) | Cùng tài liệu kỹ thuật |
| Hiệu chuẩn Z đa tool Oxplow 2.3.2 | [Phương pháp đầy đủ](Oxplow-Z-Offset-Comprehensive-Method.md) | [Hướng dẫn nhanh](Oxplow-Z-Offset-Guide.md) |
| Đánh giá input shaper / tốc độ | — | [Báo cáo](danh-gia-input-shaper-va-test-speed-2026-09-04.md) |

## Tài liệu lịch sử

Các hướng dẫn sau mô tả tích hợp đã retired và được chuyển vào [`history/`](history/README.md):

- hướng dẫn/đối chiếu kTAMV bản Anh–Việt;
- ghi chú commissioning TKC ngày 2026-09-08.

Không dùng chúng để cài đặt hoặc hiệu chuẩn máy hiện tại.

## Bằng chứng bất biến

- `extras/Nhat-ky-chinh-sua/`: lịch sử kỹ thuật theo ngày.
- `extras/experiments/`: báo cáo và reproduction thô.
- `extras/retired-configs/`: chỉ mục phục hồi; bản cấu hình cũ đã được lưu ngoài checkout ngày 12/10/2026.
- `extras/backups/`: snapshot phục hồi được giữ và bản ghi dọn dẹp theo ngày.
- `extras/Config download/`: chỉ mục phục hồi snapshot máy cũ đã lưu trữ, không phải config active.
- `extras/Printables-Package/`: generator Oxplow và file release hiện tại; bản cũ tại `extras/gcode/` đã được lưu trữ.

Đợt 20/09 đã loại mười ZIP trùng và giữ các snapshot/backup khác tại thời điểm đó. Ngày 12/10, theo yêu cầu dọn file lỗi thời, 107 thư mục backup cũ, snapshot tải về (gồm ZIP 03/09 có dữ liệu ShakeTune riêng), bản cấu hình retired, G-code cũ và log offline đã được chuyển ra kho phục hồi cục bộ sau khi nén và kiểm tra. Dữ liệu vẫn nằm trong gói lưu trữ và, với file đã tracked, lịch sử Git. Xem [manifest từng file](cleanup-2026-10-12-manifest.csv) để tra link lịch sử vào các vị trí này. Report, reproduction, nhật ký và raw evidence thử nghiệm vẫn được giữ trong checkout.

## Quy tắc bảo trì

1. Đọc code đang nạp trước khi đổi tuyên bố hiện trạng.
2. Cập nhật cặp Anh–Việt cùng lúc.
3. Không hiện đại hóa journal, report thí nghiệm, record backup hoặc snapshot tải về tại chỗ.
4. Chuyển quy trình retired vào `history/` và thêm cảnh báo ngắn ở tài liệu hiện hành.
5. Khi hành vi code đổi, cập nhật tài liệu và nhật ký ngày trong cùng commit.

Oxplow 2.3.2: [machine profiles, G-code, SVG and reports](../Printables-Package/README.md). The upstream published toolkit is preserved unchanged; retired 2.0.0 files are retained separately.
