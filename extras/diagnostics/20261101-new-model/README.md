# Đối chiếu mẫu mới và cảnh báo Orca — 01/11/2026

## Thông tin người vận hành

Mẫu hiện tại được vẽ mới hoàn toàn. Nam châm gây tool-crash đã được gắn lại; sự kiện đó được tách khỏi điều tra nozzle sát bàn, không dùng làm bằng chứng quy lỗi ngàm hoặc hình học.

## Bằng chứng mới thay đổi kết luận

- 16:28:49: `Voron Belt Clip Hex Remix_ABS_24m52s.gcode` completed. File này dùng T0/T3, bật tower và cũng có dòng hạ Z0,25 trước XY. Do đó hai tool/tower hoặc riêng dòng hạ Z sớm không phải điều kiện đủ gây lỗi. Bản safe-entry tạo trước chỉ là đối chứng đường đi, không phải sửa lỗi đã chứng minh.
- 17:30:00: bản Hex19m57 completed, chỉ T0, tower tắt.
- 19:27:25 và19:44:12: bản `Z belt clamp_ABS_31m13s.gcode` bị hủy, filament_used39,2 mm. Console tương ứng báo Toolhead stopped outside model range và Too many retries, trước in vật thể. Không được gọi hai lần này là lỗi CAD làm hỏng lớp đầu.
- 19:50:31: cùng bản mới bắt đầu in rồi hủy. Touch lúc19:55:25 adjusted z by+0,999 mm; con số này là sửa mốc home và không tự chứng minh độ lún nozzle. Tool T3 pickup lỗi sau đó là sự cố riêng theo thông tin người vận hành.
- So config comments của bản mới với bản Hex24m52 tốt: các thiết lập thực tế khác nhau ở first layer0,20 so với0,25 mm và vị trí tower. Có thêm chuỗi metadata different_settings_to_system khác, không phải thay đổi motion/flow riêng. Không tìm thấy lệnh G-code đặt offset Z âm trong các file.

## Kiểm tra 3MF đã lưu lúc19:27

- Bốn bản sao; mỗi bản một object có bốn part, gán T0 cho thân và T3 cho ba miếng đáy. print_sequence=by layer.
- Mesh mỗi part kín và winding nhất quán trước xử lý mirror. Transform build có phép mirror X nên signed volume khi chỉ biến đổi vertices có dấu âm; đó không phải bằng chứng mesh gốc lộn mặt.
- Mẫu assembled có kích thước10×11,546974×14,600000 mm; đáy Z0. Ba part nhỏ Z0–2,200000 mm. Không có chồng thể tích đáng kể tại các mặt cắt0,1/0,2/0,3/0,5/1/1,2/1,5 mm; phần giao khoảng10^-6 mm² là dung sai số học.
- Thân có tiết diện tăng từ58,123361 mm² tạiZ0,1 lên68,203894 mm² tạiZ0,5, phù hợp phần đáy vát; không phải diện tích đáy phẳng hoàn toàn của mẫu cũ. Chưa chứng minh đây là nguyên nhân sát bàn.

## Cảnh báo ảnh người dùng gửi

Ảnh báo các object `Z belt clamp.step_2`, `_3`, `_4` quá gần, có nguy cơ va chạm; đồng thời ghi đang chọn4 đối tượng. Đây là kiểm tra khoảng cách/cách tổ chức object của slicer, không phải phép đo khoảng nozzle–bàn. Nếu đó là4 body tạo nên một chi tiết, cần nhập hoặc Merge thành một object có4 part và giữ vị trí tương đối; không tách thành4 vật in độc lập. Nếu là4 sản phẩm riêng, phải bố trí chúng riêng và chọn print sequence thích hợp.

Trạng thái live Orca được đọc bằng computer-use sau ảnh: cửa sổ `*Belt-Clam - OrcaSlicer`, Plate1 chỉ hiển thị một object `Voron Belt Clip.stl`, không còn cây4 object như trong ảnh. Vì vậy không suy trạng thái unsaved hiện tại từ3MF đã lưu hoặc ảnh cũ. Không click hoặc thay đổi app.

Tài liệu chính thức Orca: https://github.com/OrcaSlicer/OrcaSlicer/wiki/prepare_assembly_tools — objects chưa merge vẫn được coi là vật thể độc lập, mỗi object phải có mặt tiếp xúc bàn; merge cho phép giữ chúng làm part của một object.

## Giới hạn kết luận

Đã loại lỗi STL cũ, sự cố nam châm và giả thuyết hai tool/early descent là nguyên nhân duy nhất. Cảnh báo object trong ảnh cần sửa cách nhập/nhóm, nhưng chưa chứng minh nó gây độ sát bàn trong G-code mới đã lưu, vốn đã có một object/bốn part. First layer0,20 của bản mới thấp hơn bản tốt0,05 mm theo lệnh có chủ ý; không tự kết luận đây là sai mốc Z. Cần kiểm chứng đường đùn thực lớp đầu và khoảng hở vật lý trong cùng điều kiện, hoặc slice đối chứng cùng mẫu với0,25 mm để tách thiết lập lớp đầu khỏi sai số mốc Z.

Không sửa file CAD/3MF gốc, profile, cấu hình production, không phát G-code chuyển động/gia nhiệt và không gửi in. API snapshots, G-code mới/tốt và config comments được giữ trong thư mục này.
