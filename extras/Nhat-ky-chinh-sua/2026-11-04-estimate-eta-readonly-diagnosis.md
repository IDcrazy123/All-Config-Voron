# Chẩn đoán Estimate / ETA nhảy khi in — 04/11/2026

## Kết luận

Đã tái hiện trên tab Edge đang mở Mainsail của máy 192.168.1.43, trong bản in
`Voron Skirt_ABS_2h45m.gcode`. Nguyên nhân trực tiếp là phép ngoại suy thời gian
trong Mainsail từ tiến độ file và lượng nhựa, dùng thời gian đã bao gồm phần lớn
chu trình chuẩn bị sau lần extrusion đầu tiên. Hai dự báo sai lệch này cùng đi
vào Estimate và ETA. Mỗi lần tiến độ/nhựa thay đổi, giao diện tính lại ngay,
không có bộ lọc làm mượt hay tách thời gian chuẩn bị trong các getter này.

Đây là chẩn đoán đọc dữ liệu. Không sửa CFG, runtime, G-code trên máy, thiết lập
trình duyệt hay database; không gửi G-code, restart, pause hoặc deploy.

## Bằng chứng đang chạy

- Mainsail `v2.19.0`, Moonraker `v0.11.0-4-gb559b9a`; server không báo warning.
- Máy đang `printing`, homed `xyz`, toolchanger ready, active/detected đều T3,
  speed/flow factor 100%. Không cần đổi tool để tái hiện lỗi hiển thị.
- Metadata đọc được: `estimated_time=9870 s` (2:44:30),
  `filament_total=14903.14 mm`, G-code start/end byte `32562 / 21911132`.
  Footer file khớp thời gian và tổng nhựa `8764.52 + 6138.62 mm`.
- Executable lines của `PRINT_START` live và repository giống nhau sau khi bỏ
  comment, dòng trống và khoảng thụt đầu dòng.
- Namespace Mainsail chỉ ghi đè `general.printername`, không ghi đè phép tính.
  Bundle JavaScript đang được máy phục vụ xác nhận mặc định:
  `calcPrintProgress=file-relative`, `calcEstimateTime=[file,filament]`,
  `calcEtaTime=[file,filament,slicer]`.

Quan sát trực tiếp trên cùng tab trình duyệt:

| Tổng thời gian trên UI | Estimate còn lại | Slicer còn lại | ETA |
|---|---|---|---|
| 0:12:34 | 23:55:17 | 2:32:44 | 09:42 +1 |
| 0:13:52 | 21:42:35 | 2:31:26 | 08:15 +1 |

Chỉ 78 giây tổng thời gian trôi qua nhưng Estimate mất hơn 2 giờ. `+1` là ngày
05/11/2026 theo múi giờ máy khách Asia/Saigon, không phải bằng chứng đồng hồ sai.

24 mẫu GET, 16:55:44–16:57:45 giờ Việt Nam, đều đang in bằng extruder3:

| Giá trị | Mẫu đầu | Mẫu cuối |
|---|---:|---:|
| print_duration | 737.114 s | 858.191 s |
| tiến độ file tương đối | 0.62736% | 0.72173% |
| filament_used | 231.458 mm | 377.592 mm |
| dự báo File còn lại | 116757 s | 118049 s |
| dự báo Filament còn lại | 46724 s | 33014 s |
| Estimate trung bình | 81740.5 s | 75531.5 s |

File estimate tăng trong khi Filament estimate giảm; Estimate tổng vẫn có hai
lần tăng giữa các mẫu. Đây là biến động của dữ liệu đầu vào và công thức,
không chỉ là một ảnh UI bị cũ. Chuỗi thu thập giữ dữ liệu thô trong
`samples.jsonl`; `analyze.py` tái tính số thực trong `samples-calculated.jsonl`
và `summary.json`. Các mẫu API và hai lần đọc UI không được lấy đồng thời nên
không so từng giây giữa chúng.

## Cơ chế gây sai

Mainsail v2.19.0 tính thời gian còn lại:

```
File = print_duration / file_progress - print_duration
Filament = print_duration / (filament_used / filament_total) - print_duration
Slicer = estimated_time - print_duration
Estimate = trung bình các kết quả dương của File và Filament
ETA = hiện tại + trung bình các kết quả dương của File, Filament, Slicer
```

1. File đang in gọi `PRINT_START` ở dòng 430. Log ghi `sd_pos=32588` trong
   chu trình chuẩn bị: gần như đứng ngay đầu executable block trong khi macro
   chạy nhiều lệnh home, clean, chờ nhiệt, soak, QGL, Touch, mesh và prime.
2. `PRINT_START` purge T0 40 mm trước khi chờ bàn/soak/QGL. Klipper chỉ loại
   thời gian trước extrusion khỏi print_duration; sau extrusion đầu tiên,
   thời gian chờ tiếp theo cũng nằm trong print_duration. Live cho thấy
   `total_duration - print_duration` cố định khoảng 48.359 s, dù chuẩn bị
   thực tế kéo dài hơn 11 phút. Không phải toàn bộ thời gian heat bị loại.
3. Log bản này ghi soak ABS 90 s từ 16:49:22; QGL coarse rồi fine, fine phải
   đến `Retries: 8/10` lúc 16:52:31 mới đạt 0.006797 mm. Prime/đổi sang T3
   kết thúc khoảng 16:53:54; G-code sau PRINT_START chạy khoảng 16:53:56.
   Đây là các khoảng làm tăng tử số trong khi tiến độ file rất nhỏ.
4. Nhựa purge/prime trong macro cũng được tính vào filament_used nhưng không
   phải phần đường chạy model mà slicer dùng để dự báo. Thời gian trên mỗi mm
   nhựa và mỗi byte file còn khác nhau giữa first layer, travel, infill,
   chờ nhiệt và đổi tool. Công thức tỷ lệ không mô hình hóa các pha này.
5. Khi file tiếp tục chạy, tỷ lệ thay đổi nhanh nên dự báo có thể tụt hàng giờ
   hoặc tăng trở lại. ETA dùng chung hai kết quả này nên nhảy theo. Khi không
   in, bộ đếm và tiến độ không chạy như vậy, giải thích tính chất chỉ lúc in.

`M73 P... R...` đã có trong file; không có macro M73 ghi đè trong config live.
Giá trị R không được các getter Estimate/ETA này sử dụng. Việc thêm M73 đơn
thuần không giải quyết nguyên nhân đã quan sát. Chưa có bằng chứng phải sửa
network, đồng hồ hoặc phần cứng để chữa hai ô thời gian này.

## Hướng xử lý và giới hạn

- Để ETA ổn định trước mắt: dùng riêng nguồn Slicer cho ETA trong Mainsail.
  Đây vẫn chỉ là dự báo; slicer không biết đầy đủ thời gian macro/chờ nhiệt.
- Estimate v2.19.0 chỉ hỗ trợ File/Filament trong getter trung bình; đổi ETA
  sang Slicer không sửa riêng ô Estimate. Chọn Filament đơn lẻ có thể giảm
  ảnh hưởng file đầu nhỏ nhưng vẫn bị chuẩn bị/purge và tốc độ nhựa làm lệch.
- Muốn sửa thuật toán cần mốc bắt đầu in model, tách overhead chuẩn bị và
  làm mượt/giới hạn cập nhật dự báo; không reset thống kê bản in hoặc cắt
  chu trình vệ sinh/QGL chỉ để làm đẹp con số.
- Chưa áp dụng bất kỳ hướng xử lý nào. Chưa theo dõi hết bản in hay lần đổi
  tool về sau; kết luận xác nhận cơ chế gây sai và nhảy trong cửa sổ đã đo,
  không xác nhận độ chính xác dự báo cho toàn bộ job.

## File và nguồn đối chiếu

Evidence: `extras/diagnostics/20261104-time-estimate/`: status, configfile,
metadata, database Mainsail, update status, gcode store, active G-code,
JavaScript live và klippy.log. Snapshot cũ ngày 01/11 trong
`extras/diagnostics/20261101-time-estimate/` cũng ghi state starting,
filament_used 39.2 mm, print_duration 67.43 s; chỉ dùng làm bằng chứng tái diễn.

- [Mainsail v2.19.0: time getters](https://github.com/mainsail-crew/mainsail/blob/v2.19.0/src/store/printer/getters.ts#L547)
- [Klipper: print_stats](https://github.com/Klipper3d/klipper/blob/master/klippy/extras/print_stats.py#L96)

Mainsail được kiểm tra thêm bằng bundle live, không chỉ dựa vào upstream.
Nguồn print_stats upstream giải thích cơ chế; không tuyên bố đã tải và so hash
runtime Python cài trên máy. Dữ liệu live xác nhận phần thời gian bị giữ lại.

KNOWN_ISSUES được bổ sung sau khi sao lưu nguyên bản working tree hiện có tại
`extras/backups/pre-time-estimate-diagnosis-20261104-165754/`.
