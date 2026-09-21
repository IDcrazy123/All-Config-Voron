# Profile Production OrcaSlicer

[English](README.md) | [Tiếng Việt](README.vi.md) | [Tổng quan dự án](../README.vi.md)

Thư mục này phản chiếu profile OrcaSlicer active được chọn từ `%APPDATA%\OrcaSlicer\user`. Ngày 2026-09-20, profile được chọn có ID `838ce884-12ee-416b-9e1b-1c7503cf6b5f`; 18 file JSON đã được parse và đồng bộ.

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

- `Voron Stealthchanger.json`: `z_hop` của cả năm tool đổi từ `0.6` xuống `0.4` mm theo profile Orca active.
- `0.20mm PETG.json`: đồng bộ override process Orca 2.4.0.2 đang dùng, gồm painted brim, preheat 6 giây, brim tháp 10 mm, prime tower 40 mm, prime volume 40 mm³ và tốc độ purge tower tối đa 50 mm³/s.
- Hai alias trong `extras/Orcasilcer setting/` hiện phản chiếu `Voron Stealthchanger.json` và `0.20mm Multicolor PetG.json`.

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
