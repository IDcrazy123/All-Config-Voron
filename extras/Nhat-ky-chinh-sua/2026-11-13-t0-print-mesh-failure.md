# 2026-11-13 — Chẩn đoán lỗi mesh khi thử in T0

- Job `A4T Stealthchanger_ABS_17m48s.gcode` bị hủy ở bước adaptive mesh lúc 15:21:21. Cartographer thu 2880 mẫu nhưng 195/195 điểm lưới không có khoảng cách hợp lệ. QGL và Touch đã hoàn tất trước đó; chưa tới bước prime hay in lớp đầu.
- Coil Cartographer báo khoảng −25°C lúc lỗi. Nhiệt cuộn âm đã thấy ở lần mesh thành công trước (khoảng −21,9°C), nhưng khác với nhiệt tham chiếu −21,41°C của scan model. Cần kiểm tra phần cứng probe và đối chiếu hiệu chuẩn; log không lưu raw frequency tại lần quét lỗi để kết luận nguyên nhân cuối cùng.
- Chỉ cập nhật `KNOWN_ISSUES.md` và báo cáo `extras/diagnostics/2026-11-13-t0-print-mesh-failure/REPORT.vi.md`. Không sửa/nạp lại cấu hình, không chạy lệnh chuyển động, gia nhiệt hoặc in. Sau hủy, Klipper `ready` nhưng KTC `uninitialized`, active tool `None`, T0 được detection pin báo trên shuttle.
- Bước chờ người vận hành: tắt nguồn, kiểm tra Cartographer coil/điện trở/cáp, sau đó kiểm tra lại scan model và mesh có giám sát. Không `RESUME` job đã hủy.
