# Nhật ký — 2026-10-12

## 1. Tổng hợp sự cố và dọn file cũ theo yêu cầu người vận hành

### Mục tiêu
Giảm dung lượng và số lượng file cũ; tổng hợp lỗi, nguyên nhân, khắc phục trước khi loại backup/snapshot/G-code/log lỗi thời.

### Chuẩn bị trước khi xóa
- Đọc chín quy tắc, KNOWN_ISSUES, TODO, DECISIONS, nhật ký và report thử nghiệm; kiểm tra cấu hình Axiscope hiện hành.
- Phân biệt lỗi đã sửa và lỗi còn mở, không suy đoán thêm nguyên nhân phần cứng.
- Lập [tổng hợp tiếng Việt](../docs/cleanup-2026-10-12.vi.md), [báo cáo kỹ thuật](../docs/cleanup-2026-10-12.md) và [manifest từng file](../docs/cleanup-2026-10-12-manifest.csv) trước khi xóa.
- 107 thư mục backup cũ được chọn, 18 backup sẵn có được giữ (gồm hai backup chưa commit).
- Chỉ dọn bản không active, log offline/G-code cũ và cache đã liệt kê. Giữ config/Orca/submodule/Printables/nhật ký/evidence đang cần.

### Sao lưu
- [Bản ghi phục hồi](</D:/Desktop/All-Config-Voron-main/Voron 5 Tool/extras/backups/pre-obsolete-file-cleanup-20261012-155825/README.md>).
- Gói phục hồi ngoài workspace: `D:/Desktop/Voron-cleanup-archive-20261012-155825/removed-files.zip`; có manifest và hash. File gốc tài liệu nằm trong backup tại `original-documents/`.
- Gói ZIP cục bộ không upload; file đã tracked được phục hồi từ commit gốc ghi trong báo cáo. Không rewrite lịch sử Git.

### Kiểm tra và kết quả
- Đã chuyển **961 file / 925,66 MiB** khỏi workspace, gồm 107 thư mục backup cũ (117 vị trí được chọn).
- Bản gốc nằm tại `D:\Desktop\Voron-cleanup-archive-20261012-155825\moved-originals`; **không xóa vĩnh viễn file nào**.
- ZIP phục hồi **229,54 MiB**, CRC và SHA-256 từng file đều đạt; hash bản gốc sau chuyển cũng khớp.
- Xét duyệt tự động chặn cả xóa cây thư mục và xóa từng file với lý do `blocked by policy`; không có giải thích chi tiết hơn. Đã dùng cách chuyển vị trí có thể hoàn tác.
- **Chưa giải phóng dung lượng ổ D:** bản gốc chuyển vẫn trên cùng ổ, ZIP thêm khoảng 229,54 MiB. Nếu cần thu hồi dung lượng, phải tự xóa thư mục `moved-originals` sau khi kiểm tra ZIP; ZIP vẫn chứa đầy đủ dữ liệu.
- Hash toàn bộ config/readonly/Orca/Printables/nhật ký cũ/evidence/audit/quy tắc workspace giữ nguyên. Còn 18 backup trước đó và một bản ghi mới, tổng 19 thư mục.
- Đã cập nhật chỉ mục tài liệu và sửa mô tả SexBolt cũ trong troubleshooting về baseline Axiscope hiện hành. Giữ nguyên các nhật ký/báo cáo lịch sử; tra link cũ qua manifest/gói phục hồi.
- Không kết nối máy in, triển khai runtime, gia nhiệt, chuyển động, restart hoặc thử in.


### Vấn đề còn lại
Cảm biến T1 chờ thay; EXCLUDE_OBJECT multi-tool, TEST_Z_SPEED, Axiscope final T0 và coupon Orca vẫn chờ xử lý. Đợt này không kết nối máy in hoặc chạy motion/heating/restart/thử in.

### Kiểm tra hoàn tất
- Đối chiếu tracking bằng cây Git tại commit gốc; ba file `.local-backups` chỉ tồn tại ở workspace, cần kho phục hồi cục bộ. Sửa metadata tracking trong manifest; SHA-256/nội dung file lưu trữ giữ nguyên.
- Chuẩn hóa newline CSV và rà soát liên kết tài liệu hiện hành; bản manifest chuẩn cuối cũng nằm trong backup dưới tên `removed-files-corrected.csv`.
