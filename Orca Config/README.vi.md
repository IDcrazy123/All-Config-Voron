# Profile Production OrcaSlicer

[English](README.md) | [Tiếng Việt](README.vi.md) | [Tổng quan dự án](../README.vi.md)

Thư mục này phản chiếu profile OrcaSlicer active được chọn từ `%APPDATA%\OrcaSlicer\user`. Ngày 2026-09-27, profile được chọn có ID `838ce884-12ee-416b-9e1b-1c7503cf6b5f`; 19 file JSON đã được parse và đồng bộ.

## Danh sách active

Machine:

- `Voron Stealthchanger.json`

Process:

- `0.20mm ABS.json`
- `0.20mm Multicolor PetG.json`
- `0.20mm PETG.json`

Filament:

- `ABS Tpoimns Black.json`
- `ABS Tpoimns Pink.json`
- `ABS-Pro Tinmory Black.json`
- `PETG Bambu Basic Black.json`
- `PETG Bambu Basic White.json`
- `PETG Kabber Blue.json`
- `PETG Noname Antums.json`
- `PETG Tinmory Black.json`
- `PETG Tinmory.json`
- `PETG TPoimns Black.json`
- `PETG TPoimns Gray.json`
- `PETG TPoimns Orange.json`
- `PETG TPoimns Red.json`
- `PETG TPoimns White.json`
- `PETG TPoimns Yellow.json`

Sáu preset cũ chỉ còn trong repository đã bị loại trong đợt rà soát 2026-09-20 sau khi xác nhận không profile active nào kế thừa chúng. Byte gốc vẫn nằm trong backup trước rà soát và lịch sử Git.

## Thay đổi vừa đồng bộ

- Đồng bộ toàn bộ trạng thái active đã sửa ngày 2026-09-26, gồm Spiral Lift 0,15 mm, retraction/tool-change, process override và preset mới `PETG Bambu Basic White.json`.
- `Voron Stealthchanger.json`: đưa `retract_restart_extra` của cả năm tool từ 0,2 mm về 0 và bật phát quạt overhang sớm 0,5 giây.
- `PETG Kabber Blue.json`: giảm số lớp khóa quạt kế thừa từ 3 xuống 2 để lớp vật lý 3 có cooling overhang.
- `0.20mm Multicolor PetG.json`: bật xử lý small perimeter với threshold 5 mm và tốc độ 30 mm/s.
- Reslice cô lập `RoboOctopus_4Color.3mf` bằng OrcaSlicer 2.4.2 đã xác nhận toàn bộ 88 restart lớp 3 của Arm1–Arm8 dùng `E0.5` thay cho `E0.7`, đồng thời T1 có cooling 10%/90%.
- Hai alias trong `extras/Orcasilcer setting/` phản chiếu `Voron Stealthchanger.json` và `0.20mm Multicolor PetG.json`.

## Đồng bộ

Đồng bộ để review, không commit/push:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass `
  -File ".\Orca Config\Sync-OrcaProfiles.ps1"
```

Đồng bộ, commit đúng phạm vi và push bằng một lần nhấp:

```text
Orca Config\Sync-OrcaProfiles.cmd
```

Script chọn profile Orca được sửa gần nhất nếu không truyền `-ProfileId`. Nó parse mọi JSON machine/process/filament, từ chối tên đích phẳng bị trùng, chỉ chép byte thay đổi, sao lưu file bị thay, cập nhật hai alias phân tích và ghi nhật ký ngày.

| Switch | Hành vi |
| --- | --- |
| `-ProfileId <id>` | Chọn thư mục Orca user cụ thể |
| `-SkipAnalysisAliases` | Không cập nhật hai file trong `extras/Orcasilcer setting/` |
| `-IncludeDiagnostics` | Đưa G-code/log diagnostic thay đổi vào commit đúng phạm vi |
| `-Commit` | Chỉ stage đường dẫn do đồng bộ sở hữu và commit |
| `-Push` | Tự bật `-Commit`, sau đó push nhánh hiện tại |

Script cố ý không xóa JSON trong repository khi file biến mất khỏi AppData. Phải kiểm tra inheritance và reference trước khi retire preset bằng tay.

## Khôi phục vào OrcaSlicer

Đóng OrcaSlicer. Chép machine JSON vào `machine`, process JSON vào `process` và filament JSON vào `filament` dưới đúng profile ID:

```powershell
$profile = Join-Path $env:APPDATA 'OrcaSlicer\user\<profile-id>'
Copy-Item '.\Orca Config\Voron Stealthchanger.json' (Join-Path $profile 'machine')
Copy-Item '.\Orca Config\0.20mm Multicolor PetG.json' (Join-Path $profile 'process')
Copy-Item '.\Orca Config\PETG Bambu Basic Black.json' (Join-Path $profile 'filament')
```

Sau khi mở OrcaSlicer, kiểm tra printer, process, mapping năm filament, số tool, start G-code và prime tower trước khi slice job production.
