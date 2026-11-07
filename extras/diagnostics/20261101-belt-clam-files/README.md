# Kiểm tra file Belt Clam — bổ sung 01/11/2026

Yêu cầu mới: file khác in tốt, chỉ các file Belt-Clam lỗi. Đọc trực tiếp thư mục `D:\Desktop\File-In-3D\Voron 2.4\Belt Clam`, so với G-code đã tải từ production và bản khối lập phương vừa hoàn tất 15:49.

## Kết quả chính

1. STL nguồn có lỗi mesh thật: 4.120 tam giác; 18 cặp trùng ngược mặt; 45 cạnh có bốn mặt; lỗi tập trung Z27–28,2 trong tọa độ STL gốc, tương đương 1,2 mm dưới cùng khi đặt lên bàn. Không có tam giác diện tích 0. Việc STL gốc nằm Z27–39 chỉ là tọa độ xuất CAD, không chứng minh slicer in lơ lửng.
2. 3MF hiện tại chứa bốn bản sao của STEP, mỗi mẫu có 4 mesh kín, winding nhất quán, không tam giác suy biến. Thân 4.084 mặt và 3 miếng đáy mỗi miếng 12 mặt. Sau component/build transforms, mỗi mẫu Z0–12, XY10×10. Mặt cắt các cao độ 0,01/0,125/0,25/0,6/1,1/1,3/5/11,9 mm không chồng thể tích giữa các part; diện tích đáy hợp nhất 92 mm². Đây là kiểm tra mesh STEP đã nhập trong 3MF, không phải chứng nhận mọi BRep của file STEP bằng CAD kernel.
3. T0 lớp đầu của các G-code đều Z0,25 và mức đùn phù hợp flow0,96. Tỷ lệ thể tích E trên tiết diện bead dự kiến có trung vị: hình trụ 0,960009; Belt27 0,959962; Belt29 0,960089; khối lập phương 0,959969. Sai khác lớn tương đối trên vài đoạn cực ngắn do làm tròn E không chứng minh overextrusion. Không có bằng chứng riêng CAD/G-code ép Z xuống dưới cao độ lớp đầu.
4. So toàn bộ config comments của bản khối lập phương tốt với Belt27: chỉ 4 mục khác, `enable_prime_tower` 0->1, `independent_support_layer_height` 1->0 và XY tower. Phần còn lại cùng first-layer-height, flow, nhiệt, tốc độ và Z offset.
5. Khác biệt đường vào: Belt27 dòng235, Belt29 dòng245 có `G1 Z.25 F21000` trước XY đầu tiên tới mẫu. Khối lập phương và hình trụ không có bước hạ sớm này. Sau PRIME_LINES máy đang ở Z5, vì vậy bản nhiều tool chạy XY tới mẫu ở Z0,25, rồi mới Z0,45/Z0,25. Đường này có thể đi qua vệt prime/vật cản, cần đối chứng thực tế; bản thân nó không làm Z0,25 thành một cao độ âm.
6. Bản hai tool còn prime T3 và gắp lại T0 sau Touch, khác bản một tool. Khối lập phương hoàn tất lúc15:49 và Touch lúc15:48:52 báo adjusted z by +0,489 mm. Dữ liệu này hạn chế kết luận trước: con số sửa mốc Touch lớn không đồng nghĩa lỗi lớp đầu, và chưa thể kết luận Cartographer là nguyên nhân chính khi file một tool in tốt.

## Đầu ra và xác minh

Đã tạo trong `D:\Desktop\File-In-3D\Voron 2.4\Belt Clam\Kiem-tra-Codex-20261101`:

- G-code safe-entry: so từng dòng với bản Belt27 đã tải, chỉ đúng dòng235 đổi thành comment; toàn bộ lệnh khác giữ nguyên.
- Project T0-only: tất cả extruder metadata=1; project setting chỉ đổi enable_prime_tower=0. Tất cả tài nguyên 3D giống byte với nguồn, zip integrity đạt. Bỏ plate JSON đã cache vì mô tả slice cũ; thumbnail cũ được giữ, model cần được Orca slice lại.
- STL một khối từ union bốn part; tọa độ đầu vào làm tròn 0,00001 mm trước union để tránh sliver khi xuất float32. Sau xuất rồi nạp lại: 4.060 mặt, mọi cạnh đúng hai mặt, kín, winding nhất quán, một thành phần, bounds[-5,-5,0]–[5,5,12], volume874,207731 mm³.
- README tiếng Việt hướng dẫn mục đích và cách phân biệt kết quả.

Orca đang mở là bản WindowsApps2.4.3; gọi trực tiếp executable CLI bị Access denied. Không điều khiển phiên Orca đang mở để tránh thay trạng thái làm việc của người dùng. Do đó project T0-only chưa slice, các file đối chứng chưa in và chưa được tuyên bố sửa hoàn toàn.

Giữ nguyên file gốc, không sửa/triển khai production, không phát G-code tới máy. `verification.json` ghi SHA256 các nguồn, số đo STL đầu ra và thay đổi project/G-code. `first-layer-paths.json`, `gcode-configs.json`, `gcode-store.json` giữ dữ liệu đối chiếu; `geometry-and-first-layer.png` là hình kiểm tra mặt cắt 3MF hiện tại và các đường đùn thực.
