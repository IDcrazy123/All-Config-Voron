# Chỉ mục Tài liệu

[English](README.md) | [Tiếng Việt](README.vi.md)

Tài liệu hiện hành mô tả code production đang được nạp tại thời điểm 2026-09-21. Báo cáo lịch sử được giữ bất biến và tách rõ để không nhầm lệnh retired với quy trình active.

## Tài liệu hiện hành

| Chủ đề | English | Tiếng Việt |
| --- | --- | --- |
| Tổng quan dự án | [README](../../README.md) | [README](../../README.vi.md) |
| Payload config active | [README](../../config/README.md) | [README](../../config/README.vi.md) |
| Profile OrcaSlicer | [README](../../Orca%20Config/README.md) | [README](../../Orca%20Config/README.vi.md) |
| Vận hành StealthChanger | [Guide](huong-dan-he-thong-stealthchanger.en.md) | [Hướng dẫn](huong-dan-he-thong-stealthchanger.md) |
| Đối chiếu triển khai Mainsail | — | [Hướng dẫn](danh-sach-doi-chieu-va-huong-dan-update-mainsail.md) |
| Dấu hiệu nhận biết lỗi hiệu chuẩn cũ | [Guide](legacy-calibration-troubleshooting.md) | Cùng tài liệu kỹ thuật |
| Hiệu chuẩn Z đa tool Oxplow | [Phương pháp đầy đủ](Oxplow-Z-Offset-Comprehensive-Method.md) | [Hướng dẫn nhanh](Oxplow-Z-Offset-Guide.md) |
| Đánh giá input shaper / tốc độ | — | [Báo cáo](danh-gia-input-shaper-va-test-speed-2026-09-04.md) |

## Tài liệu lịch sử

Các hướng dẫn sau mô tả tích hợp đã retired và được chuyển vào [`history/`](history/README.md):

- hướng dẫn/đối chiếu kTAMV bản Anh–Việt;
- ghi chú commissioning TKC ngày 2026-09-08.

Không dùng chúng để cài đặt hoặc hiệu chuẩn máy hiện tại.

## Bằng chứng bất biến

- `extras/Nhat-ky-chinh-sua/`: lịch sử kỹ thuật theo ngày.
- `extras/experiments/`: báo cáo và reproduction thô.
- `extras/retired-configs/`: cấu hình cuối của backend đã gỡ.
- `extras/backups/`: snapshot phục hồi trước thay đổi.
- `extras/Config download/`: snapshot tải từ máy, không phải config active.

Mười ZIP trùng byte hoàn toàn với thư mục snapshot đã giải nén được loại trong đợt rà soát 2026-09-20. `config-20260903-080600.zip` được giữ vì có sáu file ShakeTune không tồn tại trong thư mục giải nén. Các ZIP độc lập và toàn bộ backup recovery cũng được giữ.

## Quy tắc bảo trì

1. Đọc code đang nạp trước khi đổi tuyên bố hiện trạng.
2. Cập nhật cặp Anh–Việt cùng lúc.
3. Không hiện đại hóa journal, report thí nghiệm, record backup hoặc snapshot tải về tại chỗ.
4. Chuyển quy trình retired vào `history/` và thêm cảnh báo ngắn ở tài liệu hiện hành.
5. Khi hành vi code đổi, cập nhật tài liệu và nhật ký ngày trong cùng commit.
